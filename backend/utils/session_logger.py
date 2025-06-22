"""
Session-based logging system that saves logs to files, streams to frontend,
and uploads to Firebase Storage.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Set, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
from io import StringIO

# Firebase imports
try:
    from firebase_admin import storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class SessionLogger:
    """Manages logging for individual sessions"""
    
    def __init__(self, session_id: str, connection_manager=None):
        self.session_id = session_id
        self.connection_manager = connection_manager
        self.log_file_path = Path(f"logs/{session_id}_logs.txt")
        self.log_file_path.parent.mkdir(exist_ok=True)
        
        # Create session-specific logger
        self.logger = logging.getLogger(f"session_{session_id}")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplication
        self.logger.handlers.clear()
        
        # File handler for persistent logging
        self.file_handler = logging.FileHandler(self.log_file_path)
        self.file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(file_formatter)
        self.logger.addHandler(self.file_handler)
        
        # WebSocket handler for real-time streaming
        if connection_manager:
            self.ws_handler = SessionWebSocketHandler(session_id, connection_manager)
            self.ws_handler.setLevel(logging.INFO)
            ws_formatter = logging.Formatter('%(levelname)s - %(message)s')
            self.ws_handler.setFormatter(ws_formatter)
            self.logger.addHandler(self.ws_handler)
        
        # Console capture for stdout/stderr
        self.console_capture = SessionConsoleCapture(self)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        self.logger.info(f"Session logger initialized for {session_id}")
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def capture_stdout(self):
        """Start capturing stdout for this session"""
        self.console_capture.start_capture()
    
    def stop_capture_stdout(self):
        """Stop capturing stdout for this session"""
        self.console_capture.stop_capture()
    
    async def upload_to_firebase(self) -> Optional[str]:
        """Upload log file to Firebase Storage"""
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase not available, skipping log upload")
            return None
        
        try:
            # Ensure file is flushed
            self.file_handler.flush()
            
            # Upload to Firebase Storage
            bucket = storage.bucket()
            blob_name = f"session_logs/{self.session_id}_logs.txt"
            blob = bucket.blob(blob_name)
            
            # Upload file
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                blob.upload_from_filename,
                str(self.log_file_path)
            )
            
            # Make the blob publicly readable (optional)
            blob.make_public()
            
            download_url = blob.public_url
            self.logger.info(f"Log file uploaded to Firebase: {download_url}")
            return download_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload log file to Firebase: {e}")
            return None
    
    def get_logs_content(self) -> str:
        """Get the content of the log file"""
        try:
            # Flush the file handler first
            self.file_handler.flush()
            
            with open(self.log_file_path, 'r') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read log file: {e}")
            return ""
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Remove handlers
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
            
            # Stop console capture
            self.console_capture.stop_capture()
            
            # Shutdown executor
            self.executor.shutdown(wait=False)
            
        except Exception as e:
            logging.error(f"Error during session logger cleanup: {e}")

class SessionWebSocketHandler(logging.Handler):
    """Log handler that sends logs to WebSocket for a specific session"""
    
    def __init__(self, session_id: str, connection_manager):
        super().__init__()
        self.session_id = session_id
        self.connection_manager = connection_manager
    
    def emit(self, record):
        """Send log record to WebSocket immediately"""
        try:
            log_message = self.format(record)
            
            # Send to WebSocket asynchronously with immediate delivery
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create task and ensure it runs immediately
                    task = asyncio.create_task(
                        self.connection_manager.send_log(self.session_id, log_message)
                    )
                    # Don't await here to avoid blocking, but schedule for immediate execution
                else:
                    # If no event loop, try to create one for this log
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        new_loop.run_until_complete(
                            self.connection_manager.send_log(self.session_id, log_message)
                        )
                        new_loop.close()
                    except Exception:
                        pass
            except Exception:
                # If no event loop, skip WebSocket sending
                pass
                
        except Exception:
            # Ignore errors in log handler to prevent recursion
            pass

class SessionConsoleCapture:
    """Capture console output for a specific session"""
    
    def __init__(self, session_logger):
        self.session_logger = session_logger
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.capturing = False
        self.capture_buffer = StringIO()
        self._lock = threading.Lock()
    
    def start_capture(self):
        """Start capturing console output"""
        with self._lock:
            if not self.capturing:
                self.capturing = True
                sys.stdout = self
                sys.stderr = self
    
    def stop_capture(self):
        """Stop capturing console output"""
        with self._lock:
            if self.capturing:
                self.capturing = False
                sys.stdout = self.original_stdout
                sys.stderr = self.original_stderr
    
    def write(self, text: str):
        """Capture and forward console output"""
        # Write to original console
        self.original_stdout.write(text)
        
        # Log meaningful content
        if text.strip() and self.capturing:
            # Clean up the text
            clean_text = text.strip().replace('\n', ' ').replace('\r', '')
            if clean_text:
                self.session_logger.info(f"CONSOLE: {clean_text}")
    
    def flush(self):
        """Flush the original stdout"""
        self.original_stdout.flush()

class SessionLoggerManager:
    """Manages multiple session loggers"""
    
    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager
        self.session_loggers: Dict[str, SessionLogger] = {}
        self._lock = threading.Lock()
    
    def get_logger(self, session_id: str) -> SessionLogger:
        """Get or create a session logger"""
        with self._lock:
            if session_id not in self.session_loggers:
                self.session_loggers[session_id] = SessionLogger(
                    session_id, self.connection_manager
                )
            return self.session_loggers[session_id]
    
    def remove_logger(self, session_id: str):
        """Remove and cleanup a session logger"""
        with self._lock:
            if session_id in self.session_loggers:
                logger = self.session_loggers[session_id]
                logger.cleanup()
                del self.session_loggers[session_id]
    
    async def upload_session_logs(self, session_id: str) -> Optional[str]:
        """Upload session logs to Firebase"""
        if session_id in self.session_loggers:
            return await self.session_loggers[session_id].upload_to_firebase()
        return None
    
    def get_session_logs(self, session_id: str) -> str:
        """Get session logs content"""
        if session_id in self.session_loggers:
            return self.session_loggers[session_id].get_logs_content()
        return ""
    
    def cleanup_all(self):
        """Cleanup all session loggers"""
        with self._lock:
            for logger in self.session_loggers.values():
                logger.cleanup()
            self.session_loggers.clear()

# Global session logger manager
session_logger_manager = None

def get_session_logger_manager() -> SessionLoggerManager:
    """Get the global session logger manager"""
    global session_logger_manager
    if session_logger_manager is None:
        session_logger_manager = SessionLoggerManager()
    return session_logger_manager

def init_session_logger_manager(connection_manager):
    """Initialize the global session logger manager"""
    global session_logger_manager
    session_logger_manager = SessionLoggerManager(connection_manager)
    return session_logger_manager
