import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import logging
import tempfile
import json
import mimetypes

try:
    import cv2
    import numpy as np
    from PIL import Image
    import librosa
    import soundfile as sf
except ImportError as e:
    logging.warning(f"Optional dependency not available: {e}")

logger = logging.getLogger(__name__)

class MediaProcessor:
    """Utility class for processing media files"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "neomentor"
        self.temp_dir.mkdir(exist_ok=True)
    
    def validate_image(self, image_path: str) -> bool:
        """Validate if image file is valid"""
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image {image_path}: {str(e)}")
            return False
    
    def validate_audio(self, audio_path: str) -> bool:
        """Validate if audio file is valid"""
        try:
            data, sample_rate = librosa.load(audio_path, sr=None)
            return len(data) > 0 and sample_rate > 0
        except Exception as e:
            logger.error(f"Invalid audio {audio_path}: {str(e)}")
            return False
    
    def get_image_info(self, image_path: str) -> dict:
        """Get image file information"""
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": os.path.getsize(image_path)
                }
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return {}
    
    def get_audio_info(self, audio_path: str) -> dict:
        """Get audio file information"""
        try:
            data, sample_rate = librosa.load(audio_path, sr=None)
            duration = len(data) / sample_rate
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": 1 if len(data.shape) == 1 else data.shape[1],
                "size_bytes": os.path.getsize(audio_path)
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
            return {}
    
    def resize_image(self, image_path: str, target_size: Tuple[int, int]) -> str:
        """Resize image to target size"""
        try:
            with Image.open(image_path) as img:
                resized = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Save to temp file
                temp_path = self.temp_dir / f"resized_{Path(image_path).name}"
                resized.save(temp_path)
                
                return str(temp_path)
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return image_path
    
    def merge_videos_ffmpeg(self, video_files: List[str], output_path: str) -> bool:
        """Merge video files using FFmpeg"""
        try:
            # Create file list for FFmpeg
            file_list_path = self.temp_dir / "video_list.txt"
            
            with open(file_list_path, 'w') as f:
                for video_file in video_files:
                    f.write(f"file '{video_file}'\n")
            
            # FFmpeg command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-c', 'copy',
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully merged videos to {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error merging videos: {str(e)}")
            return False
        finally:
            # Cleanup temp file
            if file_list_path.exists():
                file_list_path.unlink()
    
    def create_video_from_image_and_audio(self, image_path: str, audio_path: str, 
                                        output_path: str, duration: Optional[float] = None) -> bool:
        """
        Create video from image and audio using FFmpeg.
        Automatically extends video duration to match audio length by cloning the last frame.
        """
        try:
            # Get audio duration to determine video length
            audio_duration = self.get_media_duration(audio_path)
            if audio_duration == 0.0:
                logger.error("Could not determine audio duration")
                return False
            
            # Use specified duration or audio duration
            video_duration = duration if duration else audio_duration
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', image_path,  # Loop the image
                '-i', audio_path,                # Audio input
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac', 
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-t', str(video_duration),       # Set exact duration
                '-shortest',                     # Stop when shortest stream ends
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully created video: {output_path} (duration: {video_duration}s)")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            return False
    
    def extract_audio_segment(self, audio_path: str, start_time: float, 
                            duration: float, output_path: str) -> bool:
        """Extract audio segment using FFmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully extracted audio segment: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error extracting audio segment: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
    
    def get_media_duration(self, file_path: str) -> float:
        """Get duration of media file in seconds using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error getting media duration for {file_path}: {e}")
            return 0.0

    def sync_video_with_audio(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Synchronize video with audio by extending video duration if needed.
        If audio is longer than video, extends video by cloning the last frame.
        If video is longer or same length, uses standard combination.
        """
        try:
            video_duration = self.get_media_duration(video_path)
            audio_duration = self.get_media_duration(audio_path)
            
            if video_duration == 0.0 or audio_duration == 0.0:
                logger.error("Could not determine media durations")
                return False
            
            logger.info(f"Video duration: {video_duration}s, Audio duration: {audio_duration}s")
            
            if audio_duration <= video_duration:
                # Audio is shorter or same length, combine normally
                cmd = [
                    'ffmpeg', '-y', 
                    '-i', video_path, 
                    '-i', audio_path,
                    '-c:v', 'copy', 
                    '-c:a', 'aac', 
                    '-map', '0:v:0',  # Take video from first input
                    '-map', '1:a:0',  # Take audio from second input
                    '-shortest',      # Stop when shortest stream ends
                    output_path
                ]
                logger.info("Audio is shorter than or equal to video - using standard combination")
            else:
                # Audio is longer, extend video by cloning last frame
                extension_duration = audio_duration - video_duration
                logger.info(f"Extending video by {extension_duration:.2f} seconds using last frame")
                
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-i', audio_path,
                    '-filter_complex',
                    f'[0:v]tpad=stop_mode=clone:stop_duration={extension_duration}[v]',
                    '-map', '[v]',
                    '-map', '1:a:0',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'medium',  # Good balance of speed and quality
                    '-crf', '23',         # Good quality setting
                    output_path
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                final_duration = self.get_media_duration(output_path)
                logger.info(f"Successfully synced video and audio. Final duration: {final_duration}s")
                return True
            else:
                logger.error(f"FFmpeg error during sync: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing video with audio: {e}")
            return False
    
    def convert_image_to_jpeg(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert any image format to JPEG.
        
        Args:
            input_path: Path to input image file
            output_path: Optional output path. If not provided, creates temp file
            
        Returns:
            Path to converted JPEG file
        """
        try:
            if not output_path:
                output_path = str(self.temp_dir / f"converted_{Path(input_path).stem}.jpeg")
            
            # Open and convert image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary (for formats like PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPEG with high quality
                img.save(output_path, 'JPEG', quality=95, optimize=True)
                
            logger.info(f"Successfully converted image to JPEG: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting image to JPEG: {str(e)}")
            return input_path  # Return original path if conversion fails
    
    def convert_audio_to_wav(self, input_path: str, output_path: Optional[str] = None, 
                           trim_to_seconds: int = 30) -> str:
        """
        Convert any audio format to WAV and trim to specified duration.
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path. If not provided, creates temp file
            trim_to_seconds: Maximum duration in seconds (default: 30)
            
        Returns:
            Path to converted WAV file
        """
        try:
            if not output_path:
                output_path = str(self.temp_dir / f"converted_{Path(input_path).stem}.wav")
            
            # Use FFmpeg for reliable audio conversion and trimming
            cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-i', input_path,
                '-t', str(trim_to_seconds),  # Trim to specified duration
                '-ar', '44100',  # Set sample rate to 44.1kHz
                '-ac', '2',      # Convert to stereo
                '-c:a', 'pcm_s16le',  # Use 16-bit PCM encoding
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully converted audio to WAV: {output_path} (trimmed to {trim_to_seconds}s)")
                return output_path
            else:
                logger.error(f"FFmpeg error during audio conversion: {result.stderr}")
                return input_path  # Return original path if conversion fails
                
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {str(e)}")
            return input_path  # Return original path if conversion fails
    
    def get_file_format(self, file_path: str) -> Tuple[str, str]:
        """
        Get file format information.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (file_type, file_extension) where file_type is 'image', 'audio', or 'unknown'
        """
        try:
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            if mime_type:
                if mime_type.startswith('image/'):
                    return ('image', file_extension)
                elif mime_type.startswith('audio/'):
                    return ('audio', file_extension)
            
            # Fallback based on file extension
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
            audio_extensions = {'.wav', '.mp3', '.aac', '.ogg', '.flac', '.m4a', '.wma'}
            
            if file_extension in image_extensions:
                return ('image', file_extension)
            elif file_extension in audio_extensions:
                return ('audio', file_extension)
            
            return ('unknown', file_extension)
            
        except Exception as e:
            logger.error(f"Error determining file format: {str(e)}")
            return ('unknown', '')
    
    def should_convert_image(self, file_path: str) -> bool:
        """Check if image needs conversion to JPEG."""
        file_type, extension = self.get_file_format(file_path)
        return file_type == 'image' and extension.lower() not in {'.jpg', '.jpeg'}
    
    def should_convert_audio(self, file_path: str) -> bool:
        """Check if audio needs conversion to WAV."""
        file_type, extension = self.get_file_format(file_path)
        return file_type == 'audio' and extension.lower() != '.wav'
