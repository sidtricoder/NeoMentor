import sys
import logging
from typing import Dict, Set
from datetime import datetime
import json

class WebSocketLogHandler(logging.Handler):
    """Custom log handler that sends logs to WebSocket connections"""
    
    def __init__(self, connection_manager):
        super().__init__()
        self.connection_manager = connection_manager
        self.active_sessions: Set[str] = set()
    
    def add_session(self, session_id: str):
        """Add a session to receive logs"""
        self.active_sessions.add(session_id)
    
    def remove_session(self, session_id: str):
        """Remove a session from receiving logs"""
        self.active_sessions.discard(session_id)
    
    def emit(self, record):
        """Send log record to all active WebSocket connections"""
        try:
            log_message = self.format(record)
            timestamp = datetime.now().isoformat()
            
            # Send to all active sessions
            for session_id in self.active_sessions.copy():
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(
                            self.connection_manager.send_log(session_id, log_message)
                        )
                except Exception as e:
                    # Remove problematic sessions
                    self.active_sessions.discard(session_id)
        except Exception:
            # Ignore errors in log handler to prevent recursion
            pass

class ConsoleCapture:
    """Capture console output and send to WebSocket"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.active_sessions: Set[str] = set()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def add_session(self, session_id: str):
        """Add a session to receive console output"""
        self.active_sessions.add(session_id)
    
    def remove_session(self, session_id: str):
        """Remove a session from receiving console output"""
        self.active_sessions.discard(session_id)
    
    def write(self, text: str):
        """Capture and forward console output"""
        # Write to original console
        self.original_stdout.write(text)
        
        # Send to WebSocket if it's meaningful content
        if text.strip() and self.active_sessions:
            for session_id in self.active_sessions.copy():
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(
                            self.connection_manager.send_log(session_id, text.strip())
                        )
                except Exception:
                    self.active_sessions.discard(session_id)
    
    def flush(self):
        """Flush the original stdout"""
        self.original_stdout.flush()

def setup_log_streaming(connection_manager):
    """Setup log streaming to WebSocket"""
    
    # Create WebSocket log handler
    ws_handler = WebSocketLogHandler(connection_manager)
    ws_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ws_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(ws_handler)
    
    # Setup console capture
    console_capture = ConsoleCapture(connection_manager)
    
    return ws_handler, console_capture
