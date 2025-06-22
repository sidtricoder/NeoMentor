"""
NeoMentor Agents - Multi-Agent AI System with Vertex AI Integration

This module contains the fully functional agent implementations using Vertex AI
for the NeoMentor system. Each agent has a specific responsibility in the 
processing pipeline for generating educational videos.
"""

import json
import os
import subprocess
import time
import mimetypes
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import asyncio
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Project configuration - Hardcoded for deployment
PROJECT_ID = "eternal-argon-460400-i0"
LOCATION = "us-central1"

# Initialize Vertex AI
VERTEX_AI_AVAILABLE = False
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part, FinishReason
    import vertexai.preview.generative_models as generative_models
    
    # Initialize Vertex AI with explicit project and location
    logger.info(f"Initializing Vertex AI with project: {PROJECT_ID}, location: {LOCATION}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Test the connection by creating a model instance
    test_model = GenerativeModel("gemini-2.0-flash-exp")
    logger.info("✅ Vertex AI model instance created successfully")
    
    VERTEX_AI_AVAILABLE = True
    logger.info("✅ Vertex AI initialized successfully")
    
except ImportError as e:
    logger.error(f"❌ Vertex AI libraries not available: {e}")
    logger.error("Please install: pip install google-cloud-aiplatform vertexai")
    VERTEX_AI_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ Failed to initialize Vertex AI: {e}")
    logger.error("Please check your Google Cloud authentication: gcloud auth application-default login")
    VERTEX_AI_AVAILABLE = False

def extract_last_frame(video_path: str, output_image_path: str) -> bool:
    """
    Extract the last frame from a video file using FFmpeg
    
    Args:
        video_path: Path to the input video file
        output_image_path: Path where the extracted frame should be saved
        
    Returns:
        bool: True if extraction successful, False otherwise
    """
    try:
        # FFmpeg command to extract the last frame
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite existing files
            '-sseof', '-1',  # Seek to 1 second before end of file
            '-i', video_path,  # Input video
            '-update', '1',  # Update single frame
            '-q:v', '1',  # Best quality
            '-vframes', '1',  # Extract only 1 frame
            output_image_path  # Output image
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(output_image_path):
            return True
        else:
            logger.error(f"Error extracting frame: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error extracting frame: {str(e)}")
        return False

def validate_and_format_input(topic: str, requested_time: str = "15s") -> str:
    """
    Formats user inputs into the required JSON structure.
    """
    if not topic.strip():
        return json.dumps({
            "status": "error",
            "message": "Main Topic is required. Please provide a topic to explain.",
            "help": "Usage: Provide a topic (required).",
        })
    
    # Validate time format
    try:
        time_seconds = int(requested_time.replace('s', '').strip())
        if time_seconds <= 0 or time_seconds > 120:
            time_seconds = 15
    except:
        time_seconds = 15
    
    return json.dumps({
        "status": "success",
        "Main Topic": topic.strip(),
        "Requested Time": f"{time_seconds}s",
        "segments_count": time_seconds // 5
    })

def generate_educational_content(formatted_data: str) -> str:
    """
    Generate educational content segments using Vertex AI Gemini 2.0 Flash
    """
    try:
        data = json.loads(formatted_data)
        
        if data.get("status") == "error":
            return formatted_data
        
        main_topic = data.get("Main Topic", "")
        requested_time = data.get("Requested Time", "15s")
        segments_count = data.get("segments_count", 3)
        
        if not VERTEX_AI_AVAILABLE:
            logger.error("Vertex AI not available for content generation")
            return json.dumps({
                "status": "error",
                "message": "Vertex AI not available for content generation"
            })
        
        # Initialize Gemini 2.0 Flash model
        model = GenerativeModel("gemini-2.0-flash-exp")
        
        # Create comprehensive prompt for educational content generation
        prompt = f"""Generate educational content about "{main_topic}" in JSON format.

CRITICAL: Return ONLY valid JSON, no other text or explanations.

Create {segments_count} segments, each 10-20 words for 5 seconds of speech.

Required JSON format:
{{
    "status": "success",
    "topic": "{main_topic}",
    "segments": [
        "Educational segment 1 text here - should be 10-20 words explaining the basic concept clearly and engagingly",
        "Educational segment 2 text here - should be 10-20 words building on segment 1 with more details",
        "Educational segment 3 text here - should be 10-20 words with practical examples and applications"
    ],
    "total_segments": {segments_count}
}}

Topic: {main_topic}
Make content accurate, educational, and engaging for general audience."""
        
        # Generate content using Vertex AI
        response = model.generate_content(
            prompt,
            generation_config=generative_models.GenerationConfig(
                max_output_tokens=1000,
                temperature=0.3,
                top_p=0.8,
                top_k=40,
            ),
        )
        
        # Extract the generated content
        generated_text = response.text.strip()
        logger.info(f"Raw AI response: {generated_text[:200]}...")
        
        # Try to extract JSON from the response
        try:
            # First, try to parse as direct JSON
            content_json = json.loads(generated_text)
            logger.info(f"✅ Successfully parsed JSON for: {main_topic}")
            return json.dumps(content_json)
        except json.JSONDecodeError:
            # Try to find JSON within the text
            logger.warning("Direct JSON parsing failed, attempting to extract JSON from text")
            
            # Look for JSON-like content between curly braces
            import re
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                try:
                    content_json = json.loads(json_match.group())
                    logger.info(f"✅ Successfully extracted JSON for: {main_topic}")
                    return json.dumps(content_json)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Create structured response from AI-generated text
            logger.warning("Creating structured response from AI text")
            
            # Split into segments based on sentences or natural breaks
            sentences = re.split(r'[.!?]+', generated_text)
            segments = []
            current_segment = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Remove common prefixes/suffixes
                sentence = re.sub(r'^(Here\'s|This is|The|A|An)\s+', '', sentence, flags=re.IGNORECASE)
                sentence = sentence.strip()
                
                if sentence:
                    test_segment = current_segment + " " + sentence if current_segment else sentence
                    word_count = len(test_segment.split())
                    
                    if word_count <= 40:
                        current_segment = test_segment
                    else:
                        if current_segment:
                            segments.append(current_segment.strip())
                        current_segment = sentence
                        
                    if len(segments) >= segments_count:
                        break
            
            # Add any remaining segment
            if current_segment and len(segments) < segments_count:
                segments.append(current_segment.strip())
            
            # Ensure we have the right number of segments
            while len(segments) < segments_count:
                segments.append(f"Additional educational information about {main_topic} and its key concepts.")
            
            segments = segments[:segments_count]  # Limit to requested count
            
            return json.dumps({
                "status": "success",
                "topic": main_topic,
                "segments": segments,
                "total_segments": len(segments)
            })
        
    except Exception as e:
        logger.error(f"Error generating educational content: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Content generation failed: {str(e)}"
        })

def generate_video_and_audio_segments(research_data: str, uploaded_image_path: str, uploaded_audio_path: str, session_id: str = None, duration_seconds: int = 5, session_logger=None) -> str:
    """
    Generate video and audio segments using ONLY uploaded media - NO PLACEHOLDERS
    """
    try:
        data = json.loads(research_data)
        
        if data.get("status") == "error":
            return research_data
        
        segments = data["segments"]
        topic = data["topic"]
        
        os.makedirs("generated_media", exist_ok=True)
        
        # Helper function for logging
        def log_info(message):
            logger.info(message)
            if session_logger:
                session_logger.info(message)
                # Force flush for real-time delivery
                for handler in session_logger.logger.handlers:
                    handler.flush()
        
        def log_error(message):
            logger.error(message)
            if session_logger:
                session_logger.error(message)
                # Force flush for real-time delivery
                for handler in session_logger.logger.handlers:
                    handler.flush()
        
        # STRICT VALIDATION - uploaded files must exist
        if not uploaded_image_path or not os.path.exists(uploaded_image_path):
            error_msg = f"❌ Required uploaded image not found: {uploaded_image_path}"
            log_error(error_msg)
            return json.dumps({
                "status": "error",
                "message": error_msg
            })
            
        if not uploaded_audio_path or not os.path.exists(uploaded_audio_path):
            error_msg = f"❌ Required uploaded audio not found: {uploaded_audio_path}"
            log_error(error_msg)
            return json.dumps({
                "status": "error",
                "message": error_msg
            })
        
        log_info(f"✅ Using UPLOADED image: {uploaded_image_path}")
        log_info(f"✅ Using UPLOADED audio: {uploaded_audio_path}")

        video_results = []
        audio_results = []
        
        # Import video and audio generation modules
        try:
            from .video_gen import GoogleVeo2VideoGenerator
            video_generator = GoogleVeo2VideoGenerator()
            VIDEO_GEN_AVAILABLE = True
            log_info("Video generation module loaded successfully")
        except ImportError as e:
            log_error(f"Video generation not available: {e}")
            VIDEO_GEN_AVAILABLE = False
        
        try:
            from .voice_cloner import speak as clone_voice
            VOICE_CLONE_AVAILABLE = True
            log_info("Voice cloning module loaded successfully")
        except ImportError as e:
            log_error(f"Voice cloning not available: {e}")
            VOICE_CLONE_AVAILABLE = False
        
        # FAIL if modules are not available - no fallbacks
        if not VIDEO_GEN_AVAILABLE:
            error_msg = "❌ Video generation module not available. Cannot proceed without video generation capabilities."
            log_error(error_msg)
            return json.dumps({
                "status": "error",
                "message": error_msg
            })
            
        if not VOICE_CLONE_AVAILABLE:
            error_msg = "❌ Voice cloning module not available. Cannot proceed without audio generation capabilities."
            log_error(error_msg)
            return json.dumps({
                "status": "error",
                "message": error_msg
            })
        
        # Generate media for each segment using ONLY uploaded files
        current_reference_image = uploaded_image_path
        
        for i, segment_text in enumerate(segments):
            video_filename = f"video_segment_{session_id}_{i+1}.mp4" if session_id else f"video_segment_{i+1}.mp4"
            audio_filename = f"audio_segment_{session_id}_{i+1}.wav" if session_id else f"audio_segment_{i+1}.wav"
            
            # AUDIO GENERATION FIRST - using uploaded audio
            try:
                log_info(f"🔊 Starting audio generation for segment {i+1}...")
                audio_path, _, _, _ = clone_voice(
                    ref_audio=uploaded_audio_path,
                    important_text=segment_text.strip(),
                    output_filename=audio_filename,
                    session_logger=session_logger
                )
                
                if audio_path and audio_path != "None" and os.path.exists(audio_path):
                    audio_results.append(audio_path)
                    log_info(f"✅ Generated audio segment {i+1}: {audio_path}")
                else:
                    error_msg = f"❌ Audio generation failed for segment {i+1}"
                    log_error(error_msg)
                    return json.dumps({
                        "status": "error",
                        "message": error_msg
                    })
                    
            except Exception as e:
                error_msg = f"❌ Audio generation error for segment {i+1}: {str(e)}"
                log_error(error_msg)
                return json.dumps({
                    "status": "error",
                    "message": error_msg
                })
            
            # VIDEO GENERATION - only proceed if audio generation was successful
            try:
                log_info(f"🎬 Starting video generation for segment {i+1}...")
                refined_prompt = (
                    f"Educational Video Segment {i+1} about {topic}:\n"
                    f"{segment_text.strip()}"
                    f"Generate a high-quality, professional educational video where the subject in the provided image passionately explains the given concept.\n\n"
                    f"If the subject is a human:\n"
                    f"Show the person from head to toe, using authentic body language and facial expressions.\n"
                    f"The person should speak continuously and naturally throughout the video, without pauses or interruptions.\n"
                    f"Emphasize full-body shots with occasional smooth transitions, avoiding repetitive actions or stiff movements.\n"
                    f"Maintain soft, cinematic lighting and realistic indoor or neutral backgrounds.\n"
                    f"Do not include any text, subtitles, overlays, transitions, music, or sound effects — only the person talking.\n\n"
                    f"If the subject is a non-human object or character:\n"
                    f"Animate the object into a lively, anthropomorphic character with eyes, mouth, and hands.\n"
                    f"The character should be expressive and engaging, like explaining the concept to a curious child.\n"
                    f"The object should move and gesture naturally without looping or repetitive actions.\n"
                    f"Ensure the tone remains educational, friendly, and full of personality.\n"
                    f"Again, no text or external elements should appear — only the character talking.\n\n"
                    f"Focus on dynamic presentation, emotional clarity, and storytelling energy throughout.\n\n"
                )
                
                if i == 0:
                    # First segment: use uploaded reference image
                    video_path = video_generator.generate_video(
                        prompt=refined_prompt,
                        image_path=uploaded_image_path,
                        output_filename=video_filename,
                        duration_seconds=duration_seconds
                    )
                else:
                    # Subsequent segments: use extracted frame from previous video
                    if current_reference_image and os.path.exists(current_reference_image):
                        with open(current_reference_image, 'rb') as f:
                            image_data = f.read()
                        
                        mime_type, _ = mimetypes.guess_type(current_reference_image)
                        if not mime_type:
                            mime_type = 'image/jpeg'
                        
                        video_path = video_generator.generate_video_with_image_data(
                            prompt=refined_prompt,
                            image_data=image_data,
                            image_mime_type=mime_type,
                            output_filename=video_filename,
                            duration_seconds=duration_seconds
                        )
                    else:
                        # Fallback to original uploaded image
                        video_path = video_generator.generate_video(
                            prompt=refined_prompt,
                            image_path=uploaded_image_path,
                            output_filename=video_filename,
                            duration_seconds=duration_seconds
                        )
                
                if video_path and os.path.exists(video_path):
                    video_results.append(video_path)
                    log_info(f"✅ Generated video segment {i+1}: {video_path}")
                    
                    # Extract last frame for next iteration
                    if i < len(segments) - 1:
                        frame_filename = f"generated_media/last_frame_segment_{session_id}_{i+1}.jpg" if session_id else f"generated_media/last_frame_segment_{i+1}.jpg"
                        if extract_last_frame(video_path, frame_filename):
                            current_reference_image = frame_filename
                            log_info(f"Extracted last frame from segment {i+1}")
                else:
                    error_msg = f"❌ Video generation failed for segment {i+1}"
                    log_error(error_msg)
                    return json.dumps({
                        "status": "error",
                        "message": error_msg
                    })
                    
            except Exception as e:
                error_msg = f"❌ Video generation error for segment {i+1}: {str(e)}"
                log_error(error_msg)
                return json.dumps({
                    "status": "error",
                    "message": error_msg
                })

        return json.dumps({
            "status": "success",
            "video_segments": video_results,
            "audio_segments": audio_results,
            "segments_processed": len(segments),
            "video_files_created": len(video_results),
            "audio_files_created": len(audio_results),
            "frame_continuity": "Enabled - using last frame of previous video for next segment",
            "notes": f"Video and audio generation completed successfully using ONLY uploaded files: {os.path.basename(uploaded_image_path)} and {os.path.basename(uploaded_audio_path)}"
        })
        
    except Exception as e:
        error_msg = f"❌ Media generation failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({
            "status": "error", 
            "message": error_msg
        })

def merge_final_video(media_data: str, session_logger=None) -> str:
    """
    Final agent that intelligently merges all video and audio segments using FFmpeg.
    Only processes actual generated files, no placeholders.
    """
    try:
        data = json.loads(media_data)
        
        if data.get("status") == "error":
            return media_data
        
        # Helper function for logging
        def log_info(message):
            logger.info(message)
            if session_logger:
                session_logger.info(message)
                # Force flush for real-time delivery
                for handler in session_logger.logger.handlers:
                    handler.flush()
        
        def log_error(message):
            logger.error(message)
            if session_logger:
                session_logger.error(message)
                # Force flush for real-time delivery
                for handler in session_logger.logger.handlers:
                    handler.flush()
        
        video_segments = data.get("video_segments", [])
        audio_segments = data.get("audio_segments", [])
        
        # Filter out error segments to get only successful generations
        valid_video_segments = [v for v in video_segments if not v.startswith("Error:") and os.path.exists(v)]
        valid_audio_segments = [a for a in audio_segments if not a.startswith("Error:") and os.path.exists(a)]
        
        log_info(f"Valid video segments: {len(valid_video_segments)}")
        log_info(f"Valid audio segments: {len(valid_audio_segments)}")
        
        if not valid_video_segments and not valid_audio_segments:
            return json.dumps({
                "status": "error",
                "message": "No valid media segments were generated. Please upload both image and audio files to enable media generation."
            })
        
        if len(valid_video_segments) != len(valid_audio_segments):
            return json.dumps({
                "status": "error",
                "message": f"Mismatch between valid video ({len(valid_video_segments)}) and audio ({len(valid_audio_segments)}) segments."
            })

        # Create directory for combined segments
        combined_segments_dir = "generated_media/combined_segments"
        os.makedirs(combined_segments_dir, exist_ok=True)
        
        combined_segments_paths = []
        
        # Combine each valid video with its corresponding audio
        for i, (video_path, audio_path) in enumerate(zip(valid_video_segments, valid_audio_segments)):
            combined_output_path = os.path.join(combined_segments_dir, f"combined_segment_{i+1}.mp4")
            
            # Get audio and video duration to determine the best strategy
            try:
                # Check if ffprobe is available
                import shutil
                if not shutil.which('ffprobe'):
                    log_error("FFprobe not available - using default audio/video combination")
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-i', audio_path,
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-shortest',
                        combined_output_path
                    ]
                else:
                    # Get audio duration
                    audio_duration_cmd = [
                        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', audio_path
                    ]
                    audio_duration_result = subprocess.run(audio_duration_cmd, capture_output=True, text=True)
                    audio_duration = float(audio_duration_result.stdout.strip()) if audio_duration_result.returncode == 0 else 0
                    
                    # Get video duration
                    video_duration_cmd = [
                        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', video_path
                    ]
                    video_duration_result = subprocess.run(video_duration_cmd, capture_output=True, text=True)
                    video_duration = float(video_duration_result.stdout.strip()) if video_duration_result.returncode == 0 else 0
                    
                    log_info(f"Segment {i+1}: Video duration = {video_duration:.2f}s, Audio duration = {audio_duration:.2f}s")
                    
                    # Strategy: If audio is longer than video, loop/extend the video to match audio duration
                    if audio_duration > video_duration and video_duration > 0:
                        log_info(f"Audio is longer than video, extending video to match audio duration")
                        
                        # Calculate how many times to loop the video
                        loop_count = int(audio_duration / video_duration) + 1
                        
                        # FFmpeg command to loop video and match audio duration
                        cmd = [
                            'ffmpeg', '-y',
                            '-stream_loop', str(loop_count),
                            '-i', video_path,
                            '-i', audio_path,
                            '-c:v', 'libx264',
                            '-c:a', 'aac',
                            '-map', '0:v:0',
                            '-map', '1:a:0',
                            '-t', str(audio_duration),  # Trim to audio duration
                            '-shortest',
                            combined_output_path
                        ]
                    else:
                        # Standard combination - video is longer or equal to audio
                        cmd = [
                            'ffmpeg', '-y',
                            '-i', video_path,
                            '-i', audio_path,
                            '-c:v', 'copy',
                            '-c:a', 'aac',
                            '-map', '0:v:0',
                            '-map', '1:a:0',
                            '-shortest',
                            combined_output_path
                        ]
                
            except Exception as e:
                log_error(f"Could not determine durations for segment {i+1}, using default approach: {e}")
                # Fallback to default approach
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-i', audio_path,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-shortest',
                    combined_output_path
                ]
            
            try:
                log_info(f"Combining segment {i+1} with command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                
                if result.returncode == 0 and os.path.exists(combined_output_path):
                    combined_segments_paths.append(combined_output_path)
                    log_info(f"Successfully combined segment {i+1}")
                else:
                    log_error(f"FFmpeg failed for segment {i+1}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                log_error(f"FFmpeg timeout for segment {i+1}")
                continue
            except Exception as e:
                log_error(f"Error combining segment {i+1}: {str(e)}")
                continue

        if not combined_segments_paths:
            return json.dumps({
                "status": "error",
                "message": "No segments were successfully combined."
            })

        # Create final merged video
        final_output = "generated_media/final_neomentor_video.mp4"
        
        if len(combined_segments_paths) == 1:
            # Single segment - just copy it
            import shutil
            shutil.copy(combined_segments_paths[0], final_output)
            log_info("Single segment copied as final video")
        else:
            # Multiple segments - concatenate them
            video_list_file = "generated_media/video_list.txt"
            with open(video_list_file, 'w') as f:
                for video_path in combined_segments_paths:
                    abs_path = os.path.abspath(video_path)
                    f.write(f"file '{abs_path}'\n")
            
            concat_cmd = [
                "ffmpeg", "-f", "concat", "-safe", "0", "-i", video_list_file,
                "-c", "copy", final_output, "-y"
            ]
            
            result = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                log_error(f"FFmpeg concatenation failed: {result.stderr}")
                return json.dumps({
                    "status": "error",
                    "message": f"FFmpeg concatenation failed: {result.stderr}"
                })
            
            log_info("Successfully concatenated all segments")
        
        return json.dumps({
            "status": "success",
            "final_video_path": final_output,
            "message": "NeoMentor video generated successfully!",
            "segments_merged": len(combined_segments_paths)
        })
        
    except Exception as e:
        error_msg = f"Video merging failed: {str(e)}"
        logger.error(error_msg)
        if session_logger:
            session_logger.error(error_msg)
        return json.dumps({
            "status": "error",
            "message": error_msg
        })

def handle_pipeline_completion(result_data: str) -> str:
    """Handle the completion of the NeoMentor pipeline"""
    try:
        data = json.loads(result_data)
        
        if data.get("status") == "success":
            return json.dumps({
                "status": "completed",
                "message": "🎉 NeoMentor pipeline completed successfully!",
                "final_video": data.get("final_video_path", "generated_media/final_neomentor_video.mp4"),
                "segments_merged": data.get("segments_merged", 0),
                "details": "Your educational video has been generated and is ready for viewing."
            })
        else:
            error_msg = data.get("message", "Unknown error occurred")
            return json.dumps({
                "status": "error",
                "message": f"❌ Pipeline error: {error_msg}",
                "suggestion": "Please check your inputs and try again."
            })
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error processing pipeline result: {str(e)}"
        })

class VertexAIAgent:
    """Base class for Vertex AI agents"""
    
    def __init__(self, name: str, description: str, model_name: str = "gemini-2.0-flash-exp"):
        self.name = name
        self.description = description
        self.model_name = model_name
        self.model = None
        
        if VERTEX_AI_AVAILABLE:
            try:
                self.model = GenerativeModel(model_name)
                logger.info(f"Initialized {name} with {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Vertex AI"""
        if not self.model:
            raise Exception(f"Model not available for {self.name}")
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generative_models.GenerationConfig(
                    max_output_tokens=kwargs.get('max_output_tokens', 1000),
                    temperature=kwargs.get('temperature', 0.3),
                    top_p=kwargs.get('top_p', 0.8),
                    top_k=kwargs.get('top_k', 40),
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating content in {self.name}: {e}")
            raise

class FormatterAgent(VertexAIAgent):
    """Formats user inputs into the required JSON structure"""
    
    def __init__(self):
        super().__init__("formatter_agent", "Formats user inputs into required JSON structure")
        self.tools = [validate_and_format_input]
    
    def process(self, topic: str, requested_time: str = "15s") -> str:
        """Process and format user input"""
        logger.info(f"[{self.name}] Processing topic: {topic}")
        return validate_and_format_input(topic, requested_time)

class ResearchAgent(VertexAIAgent):
    """Generates educational content using Vertex AI Gemini 2.0 Flash"""
    
    def __init__(self):
        super().__init__("research_agent", "Generates educational content using Vertex AI")
        self.tools = [generate_educational_content]
    
    def process(self, formatted_data: str) -> str:
        """Generate educational content from formatted data"""
        logger.info(f"[{self.name}] Generating educational content")
        return generate_educational_content(formatted_data)

class MediaGenerationAgent(VertexAIAgent):
    """Generates video and audio segments - ONLY from uploaded media"""
    
    def __init__(self):
        super().__init__("media_generation_agent", "Generates video and audio segments from uploaded files ONLY")
        self.tools = [generate_video_and_audio_segments]
    
    def process(self, research_data: str, uploaded_image_path: str, uploaded_audio_path: str, session_id: str = None, duration_seconds: int = 5, session_logger=None) -> str:
        """Generate video and audio segments using ONLY uploaded files"""
        logger.info(f"[{self.name}] Generating media segments from uploaded files")
        logger.info(f"Using uploaded image: {uploaded_image_path}")
        logger.info(f"Using uploaded audio: {uploaded_audio_path}")
        logger.info(f"Duration: {duration_seconds} seconds")
        
        return generate_video_and_audio_segments(
            research_data, 
            uploaded_image_path=uploaded_image_path,
            uploaded_audio_path=uploaded_audio_path,
            session_id=session_id,
            duration_seconds=duration_seconds,
            session_logger=session_logger
        )

class FinalAgent(VertexAIAgent):
    """Merges video and audio segments into final output"""
    
    def __init__(self):
        super().__init__("final_agent", "Merges segments into final video")
        self.tools = [merge_final_video]
    
    def process(self, media_data: str, session_logger=None) -> str:
        """Merge segments into final video"""
        logger.info(f"[{self.name}] Merging final video")
        return merge_final_video(media_data, session_logger=session_logger)

class NeoMentorPipeline:
    """Main pipeline orchestrator for NeoMentor - STRICTLY uses only uploaded media"""
    
    def __init__(self):
        self.formatter_agent = FormatterAgent()
        self.research_agent = ResearchAgent()
        self.media_generation_agent = MediaGenerationAgent()
        self.final_agent = FinalAgent()
        
        logger.info("NeoMentor Pipeline initialized with Vertex AI agents - UPLOAD ONLY MODE")
    
    def process_request(self, topic: str, requested_time: str = "15s", 
                       image_path: Optional[str] = None, 
                       audio_path: Optional[str] = None,
                       session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a complete request through the pipeline - REQUIRES uploaded media"""
        try:
            # Get session logger if available
            session_logger = None
            try:
                from utils.session_logger import get_session_logger_manager
                if session_id:
                    session_logger_manager = get_session_logger_manager()
                    session_logger = session_logger_manager.get_logger(session_id)
            except ImportError:
                pass
            
            def log_info(message):
                logger.info(message)
                if session_logger:
                    session_logger.info(message)
                    # Force flush to ensure real-time delivery
                    for handler in session_logger.logger.handlers:
                        handler.flush()
            
            def log_error(message):
                logger.error(message)
                if session_logger:
                    session_logger.error(message)
                    # Force flush to ensure real-time delivery
                    for handler in session_logger.logger.handlers:
                        handler.flush()
            
            def log_warning(message):
                logger.warning(message)
                if session_logger:
                    session_logger.warning(message)
                    # Force flush to ensure real-time delivery
                    for handler in session_logger.logger.handlers:
                        handler.flush()
            
            log_info(f"Starting NeoMentor pipeline for topic: {topic}")
            log_info(f"Image upload: {image_path}")
            log_info(f"Audio upload: {audio_path}")
            
            # STRICT VALIDATION - No uploads = No media generation
            if not image_path or not audio_path:
                missing = []
                if not image_path:
                    missing.append("image")
                if not audio_path:
                    missing.append("audio")
                
                error_msg = f"❌ Missing required uploads: {', '.join(missing)}. NeoMentor requires BOTH image and audio files to generate videos."
                log_error(error_msg)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "suggestion": "Please upload both an image file and an audio file to proceed with video generation."
                }
            
            # Verify uploaded files exist
            if not os.path.exists(image_path):
                error_msg = f"❌ Uploaded image file not found: {image_path}"
                log_error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "suggestion": "Please re-upload your image file."
                }
                
            if not os.path.exists(audio_path):
                error_msg = f"❌ Uploaded audio file not found: {audio_path}"
                log_error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "suggestion": "Please re-upload your audio file."
                }
            
            log_info("✅ All required uploads validated successfully")
            
            # Extract duration from requested_time
            try:
                duration_seconds = int(requested_time.replace('s', '').strip())
                if duration_seconds <= 0 or duration_seconds > 120:
                    duration_seconds = 8  # Default fallback
            except:
                duration_seconds = 8  # Default fallback
            
            log_info(f"Video duration set to: {duration_seconds} seconds")
            
            # Step 1: Format input
            log_info("🔄 Step 1: Formatting input...")
            formatted_data = self.formatter_agent.process(topic, requested_time)
            log_info("✅ Step 1: Input formatted successfully")
            
            # Step 2: Generate educational content
            log_info("🔄 Step 2: Generating educational content...")
            research_data = self.research_agent.process(formatted_data)
            log_info("✅ Step 2: Educational content generated")
            
            # Step 3: Generate media segments with ONLY uploaded files
            log_info("🔄 Step 3: Generating media segments...")
            media_data = self.media_generation_agent.process(
                research_data, 
                uploaded_image_path=image_path,
                uploaded_audio_path=audio_path,
                session_id=session_id,
                duration_seconds=duration_seconds,
                session_logger=session_logger
            )
            log_info("✅ Step 3: Media segments generated using ONLY uploaded files")
            
            # Step 4: Merge final video
            log_info("🔄 Step 4: Merging final video...")
            final_result = self.final_agent.process(media_data, session_logger=session_logger)
            log_info("✅ Step 4: Final video merged")
            
            # Handle completion
            log_info("🔄 Finalizing pipeline completion...")
            completion_result = handle_pipeline_completion(final_result)
            
            result = json.loads(completion_result)
            
            if result.get("status") == "completed":
                log_info("🎉 Pipeline completed successfully!")
                return {
                    "success": True,
                    "video_path": result.get("final_video"),
                    "message": result.get("message"),
                    "details": result.get("details")
                }
            else:
                log_error(f"Pipeline failed: {result.get('message')}")
                return {
                    "success": False,
                    "error": result.get("message"),
                    "suggestion": result.get("suggestion")
                }
                
        except Exception as e:
            log_error(f"Pipeline error: {str(e)}")
            return {
                "success": False,
                "error": f"Pipeline processing failed: {str(e)}",
                "suggestion": "Please check your inputs and try again."
            }

# Initialize the pipeline
pipeline = NeoMentorPipeline()

# Export the main processing function
def process_neomentor_request(topic: str, requested_time: str = "15s") -> Dict[str, Any]:
    """Main function to process NeoMentor requests"""
    return pipeline.process_request(topic, requested_time)
