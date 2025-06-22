import os
import shutil
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Utility class for managing files and directories"""
    
    def __init__(self):
        self.base_path = Path("generated_media")
        self.uploads_path = Path("uploads")
        
        # Ensure directories exist
        self.base_path.mkdir(exist_ok=True)
        self.uploads_path.mkdir(exist_ok=True)
    
    def create_session_directory(self, session_id: str) -> Path:
        """Create a new session directory"""
        session_path = self.base_path / session_id
        session_path.mkdir(exist_ok=True)
        return session_path
    
    def list_session_files(self, session_id: str) -> List[str]:
        """List all files in a session directory"""
        session_path = self.base_path / session_id
        if not session_path.exists():
            return []
        
        return [f.name for f in session_path.iterdir() if f.is_file()]
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up session directory and files"""
        try:
            session_path = self.base_path / session_id
            if session_path.exists():
                shutil.rmtree(session_path)
            
            upload_path = self.uploads_path / session_id
            if upload_path.exists():
                shutil.rmtree(upload_path)
            
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {str(e)}")
            return False
    
    def get_file_path(self, session_id: str, filename: str) -> Optional[Path]:
        """Get full path to a file in session directory"""
        session_path = self.base_path / session_id
        file_path = session_path / filename
        
        if file_path.exists():
            return file_path
        return None
    
    def save_uploaded_file(self, session_id: str, filename: str, content: bytes) -> Path:
        """Save uploaded file content to session directory"""
        upload_session_path = self.uploads_path / session_id
        upload_session_path.mkdir(exist_ok=True)
        
        file_path = upload_session_path / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path
    
    def get_session_info(self, session_id: str) -> dict:
        """Get information about a session"""
        session_path = self.base_path / session_id
        upload_path = self.uploads_path / session_id
        
        info = {
            "session_id": session_id,
            "exists": session_path.exists(),
            "generated_files": [],
            "uploaded_files": [],
            "created_time": None
        }
        
        if session_path.exists():
            info["generated_files"] = [f.name for f in session_path.iterdir() if f.is_file()]
            info["created_time"] = session_path.stat().st_ctime
        
        if upload_path.exists():
            info["uploaded_files"] = [f.name for f in upload_path.iterdir() if f.is_file()]
            if not info["created_time"]:
                info["created_time"] = upload_path.stat().st_ctime
        
        return info
