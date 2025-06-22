import os
import sys
import tempfile
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import glob

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import session logging utilities
from utils.session_logger import init_session_logger_manager, get_session_logger_manager

# WebSocket connection manager for real-time logs
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.log_handlers: Dict[str, Any] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Initialize session logger for this session
        session_logger = session_logger_manager.get_logger(session_id)
        session_logger.info(f"WebSocket connection established for session {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
            
            # Log the disconnection but don't cleanup logger yet
            # (cleanup happens when session is completed)
            session_logger = session_logger_manager.get_logger(session_id)
            session_logger.info(f"WebSocket connection closed for session {session_id}")
    
    async def send_log(self, session_id: str, message: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps({
                    "type": "log",
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error sending log to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def send_progress(self, session_id: str, progress: int, stage: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps({
                    "type": "progress",
                    "progress": progress,
                    "stage": stage,
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error sending progress to {session_id}: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

# Initialize session logger manager
session_logger_manager = init_session_logger_manager(manager)

# Authentication imports
from core.auth import get_current_user, firebase_auth, quota_manager

# Voice cloning imports
from core.voice_cloner import speak
from core.voice import F5TTSVoiceCloner

# Local imports
try:
    from core.agents_vertex import process_neomentor_request, NeoMentorPipeline
    VERTEX_AGENTS_AVAILABLE = True
    logger.info("Vertex AI agents imported successfully")
except ImportError as e:
    logger.warning(f"Vertex AI agents not available: {e}")
    try:
        from core.agents import (
            ProcessingContext, 
            FormatterAgent, 
            ResearchAgent, 
            VideoGenerationAgent, 
            FinalAgent,
            AgentOrchestrator
        )
        VERTEX_AGENTS_AVAILABLE = False
        logger.info("Using fallback agents")
    except ImportError as e2:
        logger.error(f"No agents available: {e2}")
        VERTEX_AGENTS_AVAILABLE = False

from utils.file_manager import FileManager
from utils.media_processor import MediaProcessor

app = FastAPI(title="NeoMentor API", version="1.0.0")

# CORS middleware - Hardcoded for deployment
allowed_origins = [
    "https://neomentor-frontend-140655189111.us-central1.run.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
logger.info(f"CORS allowed origins: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create directories
MEDIA_DIR = Path("generated_media")
UPLOADS_DIR = Path("uploads")
LOGS_DIR = Path("logs")
MEDIA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Initialize utilities
file_manager = FileManager()
media_processor = MediaProcessor()

# Request/Response models
class ProcessRequest(BaseModel):
    text_prompt: str
    requested_time: str = "15s"

class ProcessResponse(BaseModel):
    session_id: str
    status: str
    message: str
    result_video_url: Optional[str] = None

# Voice cloning request models
class VoiceCloneRequest(BaseModel):
    text: str
    voice_name: Optional[str] = "default"
    output_format: Optional[str] = "wav"

class VoiceCloneResponse(BaseModel):
    session_id: str
    status: str
    message: str
    audio_url: Optional[str] = None

# Analytics request models  
class AnalyticsRequest(BaseModel):
    user_id: str
    date_range: Dict[str, str]
    metrics: List[str]

class AnalyticsResponse(BaseModel):
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]

# Additional response models
class UserProfile(BaseModel):
    uid: str
    email: Optional[str]
    name: Optional[str]
    picture: Optional[str]
    total_sessions: int
    total_videos_generated: int
    subscription_tier: str
    created_at: Optional[str]
    last_login: Optional[str]

class SessionInfo(BaseModel):
    id: str
    status: str
    prompt: str
    created_at: str
    result_video_url: Optional[str] = None

class QuotaInfo(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    remaining_daily: Optional[int] = None
    remaining_monthly: Optional[int] = None

# Voice cloning request models
class VoiceCloneRequest(BaseModel):
    text: str
    voice_name: Optional[str] = "default"
    output_format: Optional[str] = "wav"

class VoiceCloneResponse(BaseModel):
    session_id: str
    status: str
    message: str
    audio_url: Optional[str] = None

# Analytics request models  
class AnalyticsRequest(BaseModel):
    user_id: str
    date_range: Dict[str, str]
    metrics: List[str]

class AnalyticsResponse(BaseModel):
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]

# Voice cloning request models
class VoiceCloneRequest(BaseModel):
    text: str
    voice_name: Optional[str] = "default"
    output_format: Optional[str] = "wav"

class VoiceCloneResponse(BaseModel):
    session_id: str
    status: str
    message: str
    audio_url: Optional[str] = None

# Analytics request models  
class AnalyticsRequest(BaseModel):
    user_id: str
    date_range: Dict[str, str]
    metrics: List[str]

class AnalyticsResponse(BaseModel):
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]

# Initialize the processing pipeline
if VERTEX_AGENTS_AVAILABLE:
    pipeline = NeoMentorPipeline()
    logger.info("Initialized Vertex AI pipeline")
else:
    orchestrator = AgentOrchestrator()
    logger.info("Initialized fallback orchestrator")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time logs"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)

async def collect_session_files(session_dir: Path, session_id: str) -> Dict[str, str]:
    """Collect all generated files from the session directory"""
    files_info = {}
    
    # Look for generated videos
    video_patterns = [
        f"*{session_id}*.mp4",
        "final_neomentor_video.mp4",
        "neomentor_video_*.mp4"
    ]
    
    for pattern in video_patterns:
        videos = list(session_dir.glob(pattern))
        if videos:
            files_info['final_video'] = str(videos[0])
            break
    
    # Look for intermediate video segments
    video_segments = list(session_dir.glob("video_segment_*.mp4"))
    for i, segment in enumerate(video_segments):
        files_info[f'intermediate_video_{i+1}'] = str(segment)
    
    # Look for audio segments
    audio_segments = list(session_dir.glob("audio_segment_*.wav"))
    for i, segment in enumerate(audio_segments):
        files_info[f'intermediate_audio_{i+1}'] = str(segment)
    
    # Look for frame images
    frame_images = list(session_dir.glob("last_frame_*.jpg"))
    for i, frame in enumerate(frame_images):
        files_info[f'frame_{i+1}'] = str(frame)
    
    # Look for other generated files
    other_files = list(session_dir.glob("*.json")) + list(session_dir.glob("*.txt"))
    for i, other in enumerate(other_files):
        files_info[f'metadata_{i+1}'] = str(other)
    
    return files_info

@app.post("/process", response_model=ProcessResponse)
async def process_request(
    prompt: str = Form(...),
    duration: Optional[int] = Form(8),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),  # Accept session_id from frontend
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Main endpoint to process NeoMentor requests (requires authentication)"""
    try:
        # Use provided session_id or generate one
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Get session logger for this specific session
        session_logger = session_logger_manager.get_logger(session_id)
        session_logger.info("🚀 Starting NeoMentor processing...")
        
        # Start capturing stdout for this session
        session_logger.capture_stdout()
        
        # Send initial log and progress
        await manager.send_log(session_id, "🚀 Starting NeoMentor processing...")
        await manager.send_progress(session_id, 5, "initialization")
        
        # Validate duration parameter
        if duration not in [8, 16, 24, 32, 40, 48, 56, 64]:
            duration = 8  # Default to 8 seconds if invalid
            session_logger.warning(f"Invalid duration {duration}, using default 8 seconds")
            
        # Check user quota first
        session_logger.info("🔍 Checking user quota...")
        await manager.send_log(session_id, "🔍 Checking user quota...")
        quota_result = await quota_manager.check_user_quota(current_user['uid'])
        if not quota_result['allowed']:
            session_logger.error(f"❌ Quota exceeded: {quota_result['reason']}")
            await manager.send_log(session_id, f"❌ Quota exceeded: {quota_result['reason']}")
            
            # Upload logs before returning
            await session_logger_manager.upload_session_logs(session_id)
            session_logger.stop_capture_stdout()
            
            return ProcessResponse(
                session_id="",
                status="quota_exceeded",
                message=f"❌ {quota_result['reason']}"
            )

        session_logger.info("✅ Quota check passed")
        await manager.send_progress(session_id, 10, "quota_check_complete")
        session_dir = UPLOADS_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Save uploaded files
        image_path = None
        audio_path = None
        uploaded_files = {}
        
        if image:
            session_logger.info(f"📁 Saving uploaded image: {image.filename}")
            await manager.send_log(session_id, f"📁 Saving uploaded image: {image.filename}")
            image_path = session_dir / f"image_{image.filename}"
            async with aiofiles.open(image_path, 'wb') as f:
                content = await image.read()
                await f.write(content)
            uploaded_files['input_image'] = str(image_path)
        
        if audio:
            session_logger.info(f"🎵 Saving uploaded audio: {audio.filename}")
            await manager.send_log(session_id, f"🎵 Saving uploaded audio: {audio.filename}")
            audio_path = session_dir / f"audio_{audio.filename}"
            async with aiofiles.open(audio_path, 'wb') as f:
                content = await audio.read()
                await f.write(content)
            uploaded_files['input_audio'] = str(audio_path)
        
        # Save session to database with uploaded files
        session_data = {
            'prompt': prompt,
            'duration': duration,
            'status': 'processing',
            'has_image': image is not None,
            'has_audio': audio is not None
        }
        
        session_logger.info("💾 Saving session to database...")
        await manager.send_log(session_id, "💾 Saving session to database...")
        await manager.send_progress(session_id, 15, "session_saved")
        
        # Use the new method that handles file uploads
        db_session_id = await firebase_auth.save_session_with_files(
            current_user['uid'], 
            session_data, 
            uploaded_files
        )
        
        session_logger.info("✅ Session and files saved to Firebase!")
        await manager.send_log(session_id, "✅ Session and files saved to Firebase!")
        await manager.send_progress(session_id, 20, "files_uploaded")
        
        # Process through the appropriate pipeline
        if VERTEX_AGENTS_AVAILABLE:
            # Use Vertex AI pipeline - STRICT upload validation
            if not image_path or not audio_path:
                missing_files = []
                if not image_path:
                    missing_files.append("image")
                if not audio_path:
                    missing_files.append("audio")
                
                session_logger.error(f"❌ Missing required files: {', '.join(missing_files)}")
                await manager.send_log(session_id, f"❌ Missing required files: {', '.join(missing_files)}")
                
                # Upload logs before returning
                await session_logger_manager.upload_session_logs(session_id)
                session_logger.stop_capture_stdout()
                
                return ProcessResponse(
                    session_id=session_id,
                    status="failed",
                    message=f"❌ Missing required uploads: {', '.join(missing_files)}. Both image and audio files are required for video generation."
                )
            
            session_logger.info("🤖 Starting AI video generation pipeline...")
            await manager.send_log(session_id, "🤖 Starting AI video generation pipeline...")
            await manager.send_progress(session_id, 25, "ai_processing_started")
            
            result = pipeline.process_request(
                topic=prompt,
                requested_time=f"{duration}s",
                image_path=str(image_path),
                audio_path=str(audio_path),
                session_id=session_id
            )
            
            if result.get("success", False):
                session_logger.info("✅ AI processing completed successfully!")
                await manager.send_log(session_id, "✅ AI processing completed successfully!")
                await manager.send_progress(session_id, 80, "ai_processing_complete")
                
                video_path = result.get("video_path", "")
                
                # Collect all generated files from the session
                session_logger.info("📂 Collecting generated files...")
                await manager.send_log(session_id, "📂 Collecting generated files...")
                generated_files = await collect_session_files(session_dir, session_id)
                
                # If we have a generated video, serve it
                if video_path and os.path.exists(video_path):
                    # Copy to media directory with session ID
                    demo_video_path = MEDIA_DIR / f"neomentor_video_{session_id}.mp4"
                    import shutil
                    shutil.copy2(video_path, demo_video_path)
                    
                    video_url = f"/media/neomentor_video_{session_id}.mp4"
                    generated_files['final_video'] = str(demo_video_path)
                    
                    session_logger.info("☁️ Uploading all generated files to Firebase...")
                    await manager.send_log(session_id, "☁️ Uploading all generated files to Firebase...")
                    await manager.send_progress(session_id, 90, "uploading_to_firebase")
                    
                    # Update session in database with all generated files
                    await firebase_auth.update_session_with_generated_files(
                        db_session_id, 
                        current_user['uid'],
                        'completed', 
                        {'video_url': video_url, 'video_path': str(demo_video_path)},
                        generated_files
                    )
                    
                    session_logger.info("🎉 Video generation completed! All files saved to Firebase.")
                    await manager.send_log(session_id, "🎉 Video generation completed! All files saved to Firebase.")
                    await manager.send_progress(session_id, 95, "uploading_logs")
                    
                    # Upload session logs to Firebase
                    log_url = await session_logger_manager.upload_session_logs(session_id)
                    if log_url:
                        session_logger.info(f"📋 Session logs uploaded: {log_url}")
                        # Update session in database with log URL
                        await firebase_auth.update_session_with_logs(db_session_id, current_user['uid'], log_url)
                    
                    await manager.send_progress(session_id, 100, "completed")
                    session_logger.stop_capture_stdout()
                    
                    return ProcessResponse(
                        session_id=session_id,
                        status="completed",
                        message=f"✅ {result.get('message', 'Video generated successfully using your uploaded files!')}",
                        result_video_url=video_url
                    )
                else:
                    # Still upload intermediate files even if final video failed
                    if generated_files:
                        session_logger.warning("☁️ Uploading intermediate files to Firebase...")
                        await manager.send_log(session_id, "☁️ Uploading intermediate files to Firebase...")
                        await firebase_auth.update_session_with_generated_files(
                            db_session_id, 
                            current_user['uid'],
                            'failed', 
                            {'error': 'No video generated'},
                            generated_files
                        )
                    else:
                        await firebase_auth.update_session_status(db_session_id, 'failed', {'error': 'No video generated'})
                    
                    session_logger.error("❌ Video generation failed - no final video created")
                    await manager.send_log(session_id, "❌ Video generation failed - no final video created")
                    
                    # Upload logs even on failure
                    await session_logger_manager.upload_session_logs(session_id)
                    session_logger.stop_capture_stdout()
                    
                    return ProcessResponse(
                        session_id=session_id,
                        status="failed",
                        message="❌ Video generation failed. No video file was created."
                    )
            else:
                session_logger.error(f"❌ AI processing failed: {result.get('error', 'Unknown error')}")
                await manager.send_log(session_id, f"❌ AI processing failed: {result.get('error', 'Unknown error')}")
                
                # Still try to collect and upload any intermediate files
                generated_files = await collect_session_files(session_dir, session_id)
                if generated_files:
                    await firebase_auth.update_session_with_generated_files(
                        db_session_id, 
                        current_user['uid'],
                        'failed', 
                        {'error': result.get("error", "Processing failed")},
                        generated_files
                    )
                else:
                    await firebase_auth.update_session_status(db_session_id, 'failed', {'error': result.get("error", "Processing failed")})
                
                # Upload logs on failure
                await session_logger_manager.upload_session_logs(session_id)
                session_logger.stop_capture_stdout()
                
                return ProcessResponse(
                    session_id=session_id,
                    status="failed",
                    message=result.get("error", "Processing failed")
                )
        else:
            # Use fallback orchestrator - ALSO requires uploads
            if not image_path or not audio_path:
                missing_files = []
                if not image_path:
                    missing_files.append("image")
                if not audio_path:
                    missing_files.append("audio")
                
                return ProcessResponse(
                    session_id=session_id,
                    status="failed",
                    message=f"❌ Missing required uploads: {', '.join(missing_files)}. Both image and audio files are required for video generation."
                )
            
            await manager.send_log(session_id, "🔄 Using fallback processing pipeline...")
            await manager.send_progress(session_id, 25, "fallback_processing_started")
            
            result = await orchestrator.process_request(
                session_id=session_id,
                prompt=prompt,
                duration_seconds=duration,
                image_path=str(image_path),
                audio_path=str(audio_path)
            )
            
            await manager.send_log(session_id, "📂 Collecting generated files from fallback processing...")
            generated_files = await collect_session_files(session_dir, session_id)
            
            if result.get("success", False):
                # NO TEMPLATE FALLBACK - Only use actual generated content
                generated_video = result.get("video_path")
                if generated_video and os.path.exists(generated_video):
                    demo_video_path = MEDIA_DIR / f"neomentor_video_{session_id}.mp4"
                    import shutil
                    shutil.copy2(generated_video, demo_video_path)
                    
                    video_url = f"/media/neomentor_video_{session_id}.mp4"
                    generated_files['final_video'] = str(demo_video_path)
                    
                    await manager.send_log(session_id, "☁️ Uploading all generated files to Firebase...")
                    await manager.send_progress(session_id, 90, "uploading_to_firebase")
                    
                    # Update session in database with all generated files
                    await firebase_auth.update_session_with_generated_files(
                        db_session_id, 
                        current_user['uid'],
                        'completed', 
                        {'video_url': video_url, 'video_path': str(demo_video_path)},
                        generated_files
                    )
                    
                    await manager.send_log(session_id, "🎉 Processing completed! All files saved to Firebase.")
                    await manager.send_progress(session_id, 100, "completed")
                    
                    return ProcessResponse(
                        session_id=session_id,
                        status="completed",
                        message=f"✅ {result.get('message', 'Video generated successfully using your uploaded files!')}",
                        result_video_url=video_url
                    )
                else:
                    # Upload intermediate files even if final video failed
                    if generated_files:
                        await firebase_auth.update_session_with_generated_files(
                            db_session_id, 
                            current_user['uid'],
                            'failed', 
                            {'error': 'No video generated'},
                            generated_files
                        )
                    else:
                        await firebase_auth.update_session_status(db_session_id, 'failed', {'error': 'No video generated'})
                    
                    await manager.send_log(session_id, "❌ Processing failed - no final video created")
                    return ProcessResponse(
                        session_id=session_id,
                        status="failed",
                        message="❌ Video generation failed. No video file was created."
                    )
            else:
                # Upload any intermediate files that were generated
                if generated_files:
                    await firebase_auth.update_session_with_generated_files(
                        db_session_id, 
                        current_user['uid'],
                        'failed', 
                        {'error': result.get("message", "Processing failed")},
                        generated_files
                    )
                else:
                    await firebase_auth.update_session_status(db_session_id, 'failed', {'error': result.get("message", "Processing failed")})
                
                await manager.send_log(session_id, f"❌ Processing failed: {result.get('message', 'Unknown error')}")
                return ProcessResponse(
                    session_id=session_id,
                    status="failed",
                    message=result.get("message", "Processing failed")
                )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        # Log to session logger if available
        if 'session_id' in locals():
            try:
                session_logger = session_logger_manager.get_logger(session_id)
                session_logger.error(f"❌ Critical error: {str(e)}")
                session_logger.stop_capture_stdout()
                
                # Upload logs even on critical error
                await session_logger_manager.upload_session_logs(session_id)
            except Exception as log_error:
                logger.error(f"Failed to handle session logging on error: {log_error}")
        
        await manager.send_log(session_id if 'session_id' in locals() else "unknown", f"❌ Critical error: {str(e)}")
        
        # Try to update session as failed if we have session_id
        try:
            if 'db_session_id' in locals():
                await firebase_auth.update_session_status(db_session_id, 'failed', {'error': str(e)})
        except Exception as db_error:
            logger.error(f"Failed to update session in database: {db_error}")
        
        return ProcessResponse(
            session_id=session_id if 'session_id' in locals() else "error",
            status="error", 
            message=f"Internal server error: {str(e)}"
        )

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "NeoMentor API is running",
        "cors_origins": ["https://neomentor-frontend-140655189111.us-central1.run.app", "http://localhost:3000", "http://127.0.0.1:3000"],
        "firebase_project": "eternal-argon-460400-i0"
    }

# Authentication endpoints
@app.get("/auth/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    profile = current_user.get('profile', {})
    
    # Convert datetime objects to strings
    created_at = profile.get('created_at')
    if created_at and hasattr(created_at, 'isoformat'):
        created_at = created_at.isoformat()
    
    last_login = profile.get('last_login')
    if last_login and hasattr(last_login, 'isoformat'):
        last_login = last_login.isoformat()
    
    return UserProfile(
        uid=current_user['uid'],
        email=current_user.get('email'),
        name=current_user.get('name'),
        picture=current_user.get('picture'),
        total_sessions=profile.get('total_sessions', 0),
        total_videos_generated=profile.get('total_videos_generated', 0),
        subscription_tier=profile.get('subscription_tier', 'free'),
        created_at=created_at,
        last_login=last_login
    )

@app.get("/auth/sessions", response_model=List[SessionInfo])
async def get_user_sessions(
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's processing sessions"""
    sessions = await firebase_auth.get_user_sessions(current_user['uid'], limit)
    return [
        SessionInfo(
            id=session['id'],
            status=session.get('status', 'unknown'),
            prompt=session.get('prompt', ''),
            created_at=session.get('created_at', ''),
            result_video_url=session.get('result', {}).get('video_url')
        )
        for session in sessions
    ]

@app.get("/auth/quota", response_model=QuotaInfo)
async def check_user_quota(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Check user's remaining quota"""
    quota_result = await quota_manager.check_user_quota(current_user['uid'])
    return QuotaInfo(**quota_result)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "vertex_ai": VERTEX_AGENTS_AVAILABLE,
            "firebase": True  # We'll assume it's working if we get here
        }
    }

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    session_dir = UPLOADS_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    files = list(session_dir.glob("*"))
    return {
        "session_id": session_id,
        "files": [f.name for f in files],
        "created": session_dir.stat().st_ctime
    }

@app.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get processing status of a specific session"""
    session_dir = UPLOADS_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": "completed",  # Mock status for now
        "progress": 100
    }

@app.get("/sessions/{session_id}/logs")
async def get_session_logs(session_id: str):
    """Get session logs content"""
    try:
        log_content = session_logger_manager.get_session_logs(session_id)
        if not log_content:
            # Try to read from file if session not active
            log_file = LOGS_DIR / f"{session_id}_logs.txt"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_content = f.read()
        
        if not log_content:
            raise HTTPException(status_code=404, detail="Session logs not found")
        
        return {
            "session_id": session_id,
            "logs": log_content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting session logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session logs")

@app.get("/sessions/{session_id}/logs/download")
async def download_session_logs(session_id: str):
    """Download session logs as a text file"""
    try:
        log_file = LOGS_DIR / f"{session_id}_logs.txt"
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="Session log file not found")
        
        return FileResponse(
            path=str(log_file),
            filename=f"session_{session_id}_logs.txt",
            media_type="text/plain"
        )
    except Exception as e:
        logger.error(f"Error downloading session logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to download session logs")

# Academic features endpoints
try:
    from core.academic_agents import academic_manager
    ACADEMIC_FEATURES_AVAILABLE = True
    logger.info("Academic agents imported successfully")
except ImportError as e:
    logger.warning(f"Academic agents not available: {e}")
    ACADEMIC_FEATURES_AVAILABLE = False

# Course Scheduler features
try:
    from core.scheduler_agents import scheduler_manager
    SCHEDULER_FEATURES_AVAILABLE = True
    logger.info("Course scheduler agents imported successfully")
except ImportError as e:
    logger.warning(f"Course scheduler agents not available: {e}")
    SCHEDULER_FEATURES_AVAILABLE = False

# Academic request models
class CourseScheduleRequest(BaseModel):
    courses: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    constraints: Dict[str, Any] = {}
    semester_start: str
    semester_end: str

class SyllabusRequest(BaseModel):
    course_info: Dict[str, Any]
    learning_objectives: List[str]
    student_level: str = "intermediate"
    duration_weeks: int = 16
    preferences: Dict[str, Any] = {}

@app.post("/academic/schedule")
async def create_course_schedule(
    request: CourseScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create an intelligent course schedule using the new Google ADK-based scheduler"""
    if not SCHEDULER_FEATURES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Course scheduler features not available")
    
    try:
        session_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log the request
        session_logger = session_logger_manager.get_logger(session_id)
        session_logger.info(f"Creating course schedule for user {current_user['uid']}")
        session_logger.info(f"Request contains {len(request.courses)} courses")
        
        # Process schedule request using new scheduler
        result = await scheduler_manager.create_schedule(
            request_data=request.dict(),
            user_id=current_user['uid'],
            session_id=session_id
        )
        
        session_logger.info("Course schedule created successfully")
        
        return {
            "session_id": session_id,
            "status": "success", 
            "message": "Course schedule created successfully with Google ADK",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error creating course schedule: {e}")
        if 'session_logger' in locals():
            session_logger.error(f"Schedule creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/academic/schedule/analytics")
async def get_schedule_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get course scheduling analytics for the current user"""
    if not SCHEDULER_FEATURES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Course scheduler features not available")
    
    try:
        analytics = await scheduler_manager.get_analytics(current_user['uid'])
        
        return {
            "status": "success",
            "message": "Schedule analytics retrieved successfully",
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/academic/syllabus")
async def generate_syllabus(
    request: SyllabusRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a personalized course syllabus using AI"""
    if not ACADEMIC_FEATURES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Academic features not available")
    
    try:
        session_id = f"syllabus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = await academic_manager.process_academic_request(
            request_type='generate_syllabus',
            user_id=current_user['uid'],
            session_id=session_id,
            data=request.dict()
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "session_id": session_id,
            "status": "success",
            "message": "Syllabus generated successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error generating syllabus: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/academic/features")
async def get_academic_features():
    """Get list of available academic features"""
    features = []
    available = False
    descriptions = {}
    
    # Check traditional academic features
    if ACADEMIC_FEATURES_AVAILABLE:
        try:
            academic_features = await academic_manager.get_available_features()
            features.extend(academic_features)
            descriptions.update({
                "generate_syllabus": "Personalized syllabus generation with Google Docs integration"
            })
            available = True
        except Exception as e:
            logger.error(f"Error getting academic features: {e}")
    
    # Check new scheduler features
    if SCHEDULER_FEATURES_AVAILABLE:
        scheduler_features = [
            "create_schedule",
            "schedule_analytics", 
            "schedule_optimization",
            "calendar_integration"
        ]
        features.extend(scheduler_features)
        descriptions.update({
            "create_schedule": "AI-powered course scheduling using Google ADK and Gemini 2.0 Flash",
            "schedule_analytics": "Schedule optimization analytics and insights",
            "schedule_optimization": "Intelligent schedule optimization based on preferences",
            "calendar_integration": "Google Calendar integration for automatic event creation"
        })
        available = True
    
    return {
        "features": features,
        "available": available,
        "description": descriptions,
        "scheduler_available": SCHEDULER_FEATURES_AVAILABLE,
        "academic_available": ACADEMIC_FEATURES_AVAILABLE
    }

@app.post("/voice/clone", response_model=VoiceCloneResponse)
async def clone_voice(
    text: str = Form(...),
    voice_name: str = Form("default"),
    reference_audio: Optional[UploadFile] = File(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Clone voice using F5-TTS technology (requires authentication)"""
    try:
        session_id = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        session_logger = session_logger_manager.get_logger(session_id)
        
        session_logger.info("🎤 Starting voice cloning process...")
        await manager.send_log(session_id, "🎤 Starting voice cloning process...")
        await manager.send_progress(session_id, 10, "voice_clone_started")
        
        # Check user quota
        quota_result = await quota_manager.check_user_quota(current_user['uid'])
        if not quota_result['allowed']:
            session_logger.error(f"❌ Quota exceeded: {quota_result['reason']}")
            return VoiceCloneResponse(
                session_id=session_id,
                status="quota_exceeded",
                message=f"❌ {quota_result['reason']}"
            )
        
        # Create session directory
        session_dir = UPLOADS_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Handle reference audio
        ref_audio_path = None
        if reference_audio:
            session_logger.info(f"🎵 Saving reference audio: {reference_audio.filename}")
            ref_audio_path = session_dir / f"ref_audio_{reference_audio.filename}"
            async with aiofiles.open(ref_audio_path, 'wb') as f:
                content = await reference_audio.read()
                await f.write(content)
        else:
            # Use default reference audio if available
            default_ref = session_dir.parent / "default_speaker.wav"
            if default_ref.exists():
                ref_audio_path = default_ref
            else:
                session_logger.warning("No reference audio provided, using fallback")
        
        await manager.send_progress(session_id, 30, "processing_audio")
        
        # Generate cloned voice
        if ref_audio_path and ref_audio_path.exists():
            audio_path, spectrogram, processed_text, seed = speak(
                ref_audio=str(ref_audio_path),
                important_text=text,
                output_filename=str(session_dir / f"cloned_voice_{session_id}.wav"),
                session_logger=session_logger
            )
            
            # Check if audio_path is valid before proceeding
            if audio_path and isinstance(audio_path, str) and os.path.exists(audio_path):
                # Move to media directory for serving
                final_audio_path = MEDIA_DIR / f"voice_clone_{session_id}.wav"
                import shutil
                shutil.copy2(audio_path, final_audio_path)
                
                audio_url = f"/media/voice_clone_{session_id}.wav"
                
                session_logger.info("✅ Voice cloning completed successfully!")
                await manager.send_progress(session_id, 100, "completed")
                
                # Save to database
                await firebase_auth.save_session_with_files(
                    current_user['uid'],
                    {
                        'type': 'voice_clone',
                        'text': text,
                        'voice_name': voice_name,
                        'status': 'completed'
                    },
                    {'audio_output': str(final_audio_path)}
                )
                
                return VoiceCloneResponse(
                    session_id=session_id,
                    status="completed",
                    message="✅ Voice cloning completed successfully!",
                    audio_url=audio_url
                )
            else:
                session_logger.error(f"❌ Voice cloning failed - invalid audio path: {audio_path}")
                await manager.send_progress(session_id, 100, "failed")
                return VoiceCloneResponse(
                    session_id=session_id,
                    status="failed",
                    message="❌ Failed to generate cloned voice - audio processing error"
                )
        else:
            session_logger.error("❌ No valid reference audio available")
            return VoiceCloneResponse(
                session_id=session_id,
                status="failed",
                message="❌ Reference audio is required for voice cloning"
            )
            
    except Exception as e:
        logger.error(f"Error in voice cloning: {str(e)}")
        return VoiceCloneResponse(
            session_id=session_id if 'session_id' in locals() else "error",
            status="error",
            message=f"Internal server error: {str(e)}"
        )

@app.get("/analytics/dashboard")
async def get_analytics_dashboard(
    date_range: str = "30d",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get analytics dashboard data for the user"""
    try:
        # Get user sessions and statistics
        sessions = await firebase_auth.get_user_sessions(current_user['uid'], limit=100)
        
        # Calculate analytics
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.get('status') == 'completed'])
        total_videos = len([s for s in sessions if s.get('result', {}).get('video_url')])
        
        # Calculate usage patterns
        usage_by_day = {}
        service_usage = {}
        
        for session in sessions:
            # Extract date
            created_at = session.get('created_at', '')
            if created_at:
                try:
                    date = created_at.split('T')[0]  # Get date part
                    usage_by_day[date] = usage_by_day.get(date, 0) + 1
                except:
                    pass
            
            # Count service types
            service_type = session.get('type', 'video_generation')
            service_usage[service_type] = service_usage.get(service_type, 0) + 1
        
        # Generate insights
        insights = []
        if total_sessions > 0:
            success_rate = (completed_sessions / total_sessions) * 100
            insights.append(f"Your success rate is {success_rate:.1f}%")
            
            if len(usage_by_day) > 1:
                most_active_day = max(usage_by_day, key=usage_by_day.get)
                insights.append(f"Most active day: {most_active_day}")
            
        # Generate recommendations based on usage
        recommendations = [
            "Try using different services to enhance your learning experience",
            "Upload high-quality reference materials for better results"
        ]
        
        # Add scheduler-specific recommendations if available
        if SCHEDULER_FEATURES_AVAILABLE:
            recommendations.extend([
                "Use the course scheduler for optimal time management",
                "Set up calendar integration for automated reminders",
                "Check schedule analytics for optimization insights"
            ])
        
        # Add general academic recommendations
        if service_usage.get('video_generation', 0) > service_usage.get('course_scheduling', 0):
            recommendations.append("Consider using the course scheduler to better organize your studies")
        
        return {
            "summary": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "total_videos": total_videos,
                "success_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            "usage_patterns": {
                "by_day": usage_by_day,
                "by_service": service_usage
            },
            "insights": insights,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics data")

@app.get("/features/available")
async def get_available_features():
    """Get all available NeoMentor features"""
    try:
        features = {
            "video_generation": {
                "name": "AI Video Generation",
                "description": "Create educational videos with AI avatars and voice synthesis",
                "available": VERTEX_AGENTS_AVAILABLE,
                "endpoints": ["/process"],
                "requirements": ["image", "audio", "text"]
            },
            "course_scheduling": {
                "name": "Smart Course Scheduler", 
                "description": "Advanced AI-powered course scheduling using Google ADK and Gemini 2.0 Flash",
                "available": SCHEDULER_FEATURES_AVAILABLE,
                "endpoints": ["/academic/schedule", "/academic/schedule/analytics"],
                "requirements": ["courses", "preferences", "constraints"],
                "features": [
                    "Google Calendar integration",
                    "Conflict resolution",
                    "Energy pattern optimization",
                    "Travel time consideration",
                    "Analytics and insights"
                ]
            },
            "syllabus_generation": {
                "name": "Dynamic Syllabus Generator",
                "description": "Personalized course syllabus creation with AI",
                "available": ACADEMIC_FEATURES_AVAILABLE,
                "endpoints": ["/academic/syllabus"],
                "requirements": ["course_info", "learning_objectives"]
            },
            "voice_cloning": {
                "name": "Voice Cloning",
                "description": "Clone voices using F5-TTS technology",
                "available": True,
                "endpoints": ["/voice/clone"],
                "requirements": ["text", "reference_audio"]
            },
            "analytics": {
                "name": "Learning Analytics",
                "description": "Detailed insights and progress tracking",
                "available": True,
                "endpoints": ["/analytics/dashboard"],
                "requirements": ["authentication"]
            }
        }
        
        return {
            "features": features,
            "total_available": len([f for f in features.values() if f["available"]]),
            "status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Error getting available features: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve features")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
