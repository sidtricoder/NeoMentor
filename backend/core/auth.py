"""
Authentication module using Firebase Auth and Firestore
"""

import os
import json
import logging
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from functools import wraps

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global firebase_initialized
    
    if firebase_initialized:
        return
    
    try:
        # Use Application Default Credentials for Cloud Run
        cred = credentials.ApplicationDefault()
        
        # Initialize with hardcoded storage bucket
        storage_bucket = "eternal-argon-460400-i0.firebasestorage.app"
        firebase_admin.initialize_app(cred, {
            'storageBucket': storage_bucket
        })
        firebase_initialized = True
        logger.info("✅ Firebase Admin SDK initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firebase: {e}")
        raise


class FirebaseStorageManager:
    """Firebase Storage manager for file uploads"""
    
    def __init__(self):
        initialize_firebase()
        self.bucket = storage.bucket()
    
    def upload_file_sync(self, local_file_path: str, storage_path: str) -> str:
        """Upload a file to Firebase Storage and return the download URL (synchronous)"""
        try:
            blob = self.bucket.blob(storage_path)
            
            # Upload the file
            blob.upload_from_filename(local_file_path)
            
            # Make it publicly readable
            blob.make_public()
            
            # Return the public URL
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading file to Firebase Storage: {e}")
            raise
    
    async def upload_file(self, local_file_path: str, storage_path: str) -> str:
        """Upload a file to Firebase Storage and return the download URL"""
        # Run the synchronous upload in a thread pool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.upload_file_sync, local_file_path, storage_path)
    
    async def upload_session_files(self, session_id: str, user_id: str, files_info: Dict[str, str]) -> Dict[str, str]:
        """Upload all session files to Firebase Storage"""
        uploaded_urls = {}
        
        for file_type, local_path in files_info.items():
            if local_path and os.path.exists(local_path):
                try:
                    # Create storage path: users/{user_id}/sessions/{session_id}/{file_type}/{filename}
                    filename = os.path.basename(local_path)
                    storage_path = f"users/{user_id}/sessions/{session_id}/{file_type}/{filename}"
                    
                    # Upload and get URL
                    url = await self.upload_file(local_path, storage_path)
                    uploaded_urls[file_type] = url
                    
                    logger.info(f"Uploaded {file_type} file to Firebase Storage: {storage_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to upload {file_type} file: {e}")
                    uploaded_urls[file_type] = None
        
        return uploaded_urls


class FirebaseAuth:
    """Firebase Authentication manager"""
    
    def __init__(self):
        initialize_firebase()
        self.db = firestore.client()
        self.storage_manager = FirebaseStorageManager()
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and return user info"""
        try:
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token['uid']
            
            # Get or create user profile in Firestore
            user_profile = await self.get_or_create_user_profile(user_id, decoded_token)
            
            return {
                'uid': user_id,
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'profile': user_profile
            }
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    
    async def get_or_create_user_profile(self, user_id: str, token_data: Dict) -> Dict[str, Any]:
        """Get or create user profile in Firestore"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                # Update last login
                user_ref.update({
                    'last_login': firestore.SERVER_TIMESTAMP,
                    'email': token_data.get('email'),
                    'name': token_data.get('name'),
                    'picture': token_data.get('picture')
                })
                return user_doc.to_dict()
            else:
                # Create new user profile
                profile_data = {
                    'uid': user_id,
                    'email': token_data.get('email'),
                    'name': token_data.get('name'),
                    'picture': token_data.get('picture'),
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'last_login': firestore.SERVER_TIMESTAMP,
                    'total_sessions': 0,
                    'total_videos_generated': 0,
                    'subscription_tier': 'free',
                    'preferences': {
                        'theme': 'light',
                        'default_voice': 'neutral',
                        'video_quality': 'high'
                    }
                }
                
                user_ref.set(profile_data)
                logger.info(f"Created new user profile: {user_id}")
                return profile_data
                
        except Exception as e:
            logger.error(f"Error managing user profile: {e}")
            return {}
    
    async def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's processing sessions"""
        try:
            sessions = (
                self.db.collection('sessions')
                .where(filter=FieldFilter('user_id', '==', user_id))
                .order_by('created_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            
            return [{'id': session.id, **session.to_dict()} for session in sessions]
        except Exception as e:
            logger.error(f"Error fetching user sessions: {e}")
            return []
    
    async def save_session_with_files(self, user_id: str, session_data: Dict[str, Any], files_info: Dict[str, str] = None) -> str:
        """Save processing session with file uploads to Firestore and Firebase Storage"""
        try:
            session_data.update({
                'user_id': user_id,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            # Upload files to Firebase Storage if provided
            if files_info:
                session_id_temp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                uploaded_urls = await self.storage_manager.upload_session_files(session_id_temp, user_id, files_info)
                session_data['uploaded_files'] = uploaded_urls
            
            doc_ref = self.db.collection('sessions').add(session_data)
            session_id = doc_ref[1].id
            
            # Update user stats
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'total_sessions': firestore.Increment(1)
            })
            
            logger.info(f"Saved session {session_id} for user {user_id} with file uploads")
            return session_id
            
        except Exception as e:
            logger.error(f"Error saving session with files: {e}")
            raise

    async def save_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Save processing session to Firestore"""
        try:
            session_data.update({
                'user_id': user_id,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            doc_ref = self.db.collection('sessions').add(session_data)
            session_id = doc_ref[1].id
            
            # Update user stats
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'total_sessions': firestore.Increment(1)
            })
            
            logger.info(f"Saved session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            raise
    
    async def update_session_with_generated_files(self, session_id: str, user_id: str, status: str, result_data: Optional[Dict] = None, generated_files: Dict[str, str] = None):
        """Update session status and upload generated files to Firebase Storage"""
        try:
            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Upload generated files to Firebase Storage
            if generated_files:
                uploaded_urls = await self.storage_manager.upload_session_files(session_id, user_id, generated_files)
                if 'result' not in update_data:
                    update_data['result'] = {}
                update_data['result']['generated_files'] = uploaded_urls
            
            if result_data:
                if 'result' not in update_data:
                    update_data['result'] = {}
                update_data['result'].update(result_data)
                
                # If video was generated successfully, update user stats
                if status == 'completed' and (result_data.get('video_url') or (generated_files and 'final_video' in generated_files)):
                    user_ref = self.db.collection('users').document(user_id)
                    user_ref.update({
                        'total_videos_generated': firestore.Increment(1)
                    })
            
            self.db.collection('sessions').document(session_id).update(update_data)
            logger.info(f"Updated session {session_id} status to {status} with generated files")
            
        except Exception as e:
            logger.error(f"Error updating session with generated files: {e}")
            raise

    async def update_session_status(self, session_id: str, status: str, result_data: Optional[Dict] = None):
        """Update session status and result"""
        try:
            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            if result_data:
                update_data['result'] = result_data
                
                # If video was generated successfully, update user stats
                if status == 'completed' and result_data.get('video_url'):
                    session_doc = self.db.collection('sessions').document(session_id).get()
                    if session_doc.exists:
                        user_id = session_doc.to_dict().get('user_id')
                        if user_id:
                            user_ref = self.db.collection('users').document(user_id)
                            user_ref.update({
                                'total_videos_generated': firestore.Increment(1)
                            })
            
            self.db.collection('sessions').document(session_id).update(update_data)
            logger.info(f"Updated session {session_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating session status: {e}")
            raise

    async def update_session_with_logs(self, session_id: str, user_id: str, log_url: str):
        """Update session with uploaded logs URL"""
        try:
            update_data = {
                'logs_url': log_url,
                'logs_uploaded_at': firestore.SERVER_TIMESTAMP
            }
            
            self.db.collection('sessions').document(session_id).update(update_data)
            logger.info(f"Updated session {session_id} with logs URL: {log_url}")
            
        except Exception as e:
            logger.error(f"Error updating session with logs: {e}")
            raise


# Security
security = HTTPBearer()
firebase_auth = FirebaseAuth()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    return await firebase_auth.verify_token(token)

def require_auth(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # This is handled by the Depends(get_current_user) in the endpoint
        return await f(*args, **kwargs)
    return decorated_function


class UserQuotaManager:
    """Manage user quotas and limits"""
    
    def __init__(self):
        initialize_firebase()
        self.db = firestore.client()
    
    async def check_user_quota(self, user_id: str) -> Dict[str, Any]:
        """Check if user has remaining quota"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {'allowed': False, 'reason': 'User not found'}
            
            user_data = user_doc.to_dict()
            subscription_tier = user_data.get('subscription_tier', 'free')
            
            # Define quotas per tier
            quotas = {
                'free': {'daily_videos': 3, 'monthly_videos': 10},
                'premium': {'daily_videos': 50, 'monthly_videos': 500},
                'enterprise': {'daily_videos': -1, 'monthly_videos': -1}  # Unlimited
            }
            
            if subscription_tier not in quotas:
                subscription_tier = 'free'
            
            tier_quota = quotas[subscription_tier]
            
            # Check daily quota
            if tier_quota['daily_videos'] > 0:
                today = datetime.now().date()
                daily_count = await self._get_daily_video_count(user_id, today)
                
                if daily_count >= tier_quota['daily_videos']:
                    return {
                        'allowed': False,
                        'reason': f'Daily limit of {tier_quota["daily_videos"]} videos reached'
                    }
            
            # Check monthly quota
            if tier_quota['monthly_videos'] > 0:
                monthly_count = await self._get_monthly_video_count(user_id)
                
                if monthly_count >= tier_quota['monthly_videos']:
                    return {
                        'allowed': False,
                        'reason': f'Monthly limit of {tier_quota["monthly_videos"]} videos reached'
                    }
            
            return {'allowed': True}
            
        except Exception as e:
            logger.error(f"Error checking user quota: {e}")
            return {'allowed': False, 'reason': 'Error checking quota'}
    
    async def _get_daily_video_count(self, user_id: str, date) -> int:
        """Get daily video generation count"""
        try:
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            sessions = (
                self.db.collection('sessions')
                .where(filter=FieldFilter('user_id', '==', user_id))
                .where(filter=FieldFilter('status', '==', 'completed'))
                .where(filter=FieldFilter('created_at', '>=', start_of_day))
                .where(filter=FieldFilter('created_at', '<=', end_of_day))
                .stream()
            )
            
            return len(list(sessions))
        except Exception as e:
            logger.error(f"Error getting daily video count: {e}")
            return 0
    
    async def _get_monthly_video_count(self, user_id: str) -> int:
        """Get monthly video generation count"""
        try:
            now = datetime.now()
            start_of_month = datetime(now.year, now.month, 1)
            
            sessions = (
                self.db.collection('sessions')
                .where(filter=FieldFilter('user_id', '==', user_id))
                .where(filter=FieldFilter('status', '==', 'completed'))
                .where(filter=FieldFilter('created_at', '>=', start_of_month))
                .stream()
            )
            
            return len(list(sessions))
        except Exception as e:
            logger.error(f"Error getting monthly video count: {e}")
            return 0


quota_manager = UserQuotaManager()
