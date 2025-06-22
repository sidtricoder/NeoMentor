# NeoMentor - Multi-Agent AI System

![NeoMentor Banner](https://github.com/sidtricoder/NeoMentor/blob/master/icon.png)

## 🚀 Project Overview

NeoMentor is a fully functional multi-agent AI system that generates educational videos using Google's Vertex AI, Firebase for authentication and database, and advanced voice cloning technology. The system processes text prompts, images, and audio through a sophisticated pipeline of specialized agents to create high-quality educational content.

## ✨ Key Features

- 🎯 **Vertex AI Integration**: Uses Google's Gemini 2.0 Flash model for educational content generation
- 🎬 **Video Generation**: Google Veo 2.0 for professional educational video creation
- 🎤 **Voice Cloning**: F5-TTS for natural speech synthesis and voice generation
- 🤖 **Multi-Agent Pipeline**: Specialized agents for formatting, research, scheduling, analytics, media generation, and final assembly
- 📅 **Course & Syllabus Scheduling**: AI-powered course and syllabus scheduling
- 📊 **Analytics**: User and session analytics with insights and recommendations
- 🔄 **Frame Continuity**: Seamless video transitions using extracted frames
- ⚡ **Real-time Processing & Logs**: FastAPI backend with WebSocket support for live updates and log streaming
- 🔐 **Authentication**: Google Firebase Authentication
- 💾 **Database**: Firestore for session and user data storage
- 📱 **Modern Responsive UI**: Beautiful React TypeScript interface with Tailwind CSS
- 🧠 **Fully Functional**: Complete working system with actual AI models

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  Google ADK     │
│   (TypeScript)   │◄──►│    (Python)     │◄──►│   Agents        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

![Architecture](https://github.com/sidtricoder/NeoMentor/blob/master/final-diagram.png)

### Agent Pipeline Flow

1. **Formatter Agent**: Processes and formats input data
2. **Research Agent**: Conducts relevant research and fact-checking
3. **Scheduler Agent**: AI-powered course and syllabus scheduling
4. **Analytics Agent**: Provides user/session analytics and recommendations
5. **Video Generation Agent**: Creates video content based on inputs
6. **Final Agent**: Merges all components into the final output

## 🛠️ Technology Stack

### Frontend
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Custom NeoMentor branding** with integrated icon
- **Firebase SDK** for authentication

### Backend
-**Google ADK** for well built AI Agents
- **FastAPI** for high-performance API
- **Google Vertex AI** with Gemini 2.0 Flash
- **Firebase Admin SDK** for authentication
- **Firestore** for database operations
- **WebSockets** for real-time updates
- **F5-TTS** for voice cloning
- **FFmpeg** for media processing
- **Python 3.9+** with async/await support

## 📦 Quick Deployment Checklist

For immediate deployment, follow this checklist:

### ✅ Pre-deployment Steps
1. **Environment Setup**
   - [ ] Copy `.env.example` to `.env` in both backend and frontend directories
   - [ ] Configure all environment variables with your actual values
   - [ ] Place `service-account-key.json` in backend directory

2. **Firebase/Google Cloud Setup**
   - [ ] Create Firebase project and enable Authentication, Firestore
   - [ ] Enable Vertex AI API in Google Cloud Console
   - [ ] Create service account with proper permissions
   - [ ] Download service account JSON key

3. **Dependencies**
   - [ ] Install Docker and Docker Compose (for containerized deployment)
   - [ ] Or install Python 3.9+, Node.js 16+ (for local deployment)

### 🚀 Deployment Options

**Option 1: Docker (Recommended)**
```bash
docker-compose up -d
```

**Option 2: Local Development**
```bash
./start_dev.sh
```

**Option 3: Manual**
```bash
# Terminal 1
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2  
cd frontend && npm start
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** 
- **Node.js 16+** and npm
- **Google Cloud Account** with billing enabled
- **Firebase Project** (instructions below)
- **FFmpeg** installed on your system

### Google Cloud & Firebase Setup

#### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" → Enter name (e.g., "neomentor-app") → Create project

#### 2. Enable Authentication
1. In Firebase project → "Authentication" → "Get started"
2. Go to "Sign-in method" tab → Enable "Google" sign-in provider
3. Add your support email → Save

#### 3. Enable Firestore Database
1. Click "Firestore Database" → "Create database"
2. Choose "Start in test mode" → Select region → Done

#### 4. Enable Required APIs
Go to [Google Cloud Console](https://console.cloud.google.com/) and enable:
- Vertex AI API
- Firebase Admin SDK API
- Cloud Storage API

#### 5. Create Service Account
1. Go to "IAM & Admin" → "Service Accounts" → "Create Service Account"
2. Name: `neomentor-backend`
3. Grant roles:
   - **Firebase Admin SDK Administrator Service Agent**
   - **Cloud Datastore User**
   - **Vertex AI User**
4. Create and download JSON key → Save as `service-account-key.json` in backend folder

#### 6. Get Firebase Web Config
1. Project Settings → Scroll to "Your apps" → Add Web App
2. Register app → Copy the config object

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd NeoMentor
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**

   **Backend (.env)**
   ```env
   # Firebase Configuration
   GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
   FIREBASE_PROJECT_ID=your-project-id
   
   # Google Cloud
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   
   # Application Settings
   UPLOAD_FOLDER=./uploads
   GENERATED_MEDIA_FOLDER=./generated_media
   LOG_FOLDER=./logs
   MAX_FILE_SIZE=50MB
   ```

   **Frontend (.env)**
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_FIREBASE_API_KEY=your-api-key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=your-project-id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   REACT_APP_FIREBASE_APP_ID=your-app-id
   ```

### Initialize Firestore Collections (One-time setup)

```bash
cd backend
python -c "
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate('./service-account-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
db.collection('users').document('init').set({'created': True})
db.collection('sessions').document('init').set({'created': True})
print('Firestore collections initialized!')
"
```

### Running the Application

**Terminal 1 - Backend**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm start
```

**Or use the provided script:**
```bash
# Make executable and run
chmod +x start_dev.sh
./start_dev.sh
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Usage

1. **Enter a Text Prompt**: Describe what you want NeoMentor to create
2. **Upload an Image**: Provide visual context for your request
3. **Upload an Audio File**: Add audio elements to your content
4. **Click "Generate Video"**: Let the AI agents process your inputs
5. **View Real-time Logs**: Watch live progress and logs in the UI
6. **Download Your Video**: Get your personalized video content
7. **View Analytics**: Access analytics and recommendations for your sessions

## 🔧 Configuration

### Firebase Security Rules

**Firestore Rules (firestore.rules):**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Sessions - users can read/write their own sessions
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null && 
        (request.auth.uid == resource.data.user_id || request.auth.uid == request.resource.data.user_id);
    }
  }
}
```

**Storage Rules (storage.rules):**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /uploads/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /generated/{sessionId}/{allPaths=**} {
      allow read: if request.auth != null;
    }
  }
}
```

### Environment Variables

The application uses the following environment variables:

**Backend Environment Variables:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION`: Deployment region (e.g., us-central1)
- `UPLOAD_FOLDER`: Directory for user uploads
- `GENERATED_MEDIA_FOLDER`: Directory for generated content
- `LOG_FOLDER`: Directory for application logs
- `MAX_FILE_SIZE`: Maximum upload file size

**Frontend Environment Variables:**
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_FIREBASE_*`: Firebase configuration from console

## 📚 API Documentation

### Endpoints (New/Updated)

#### Analytics
```http
POST /analytics
Content-Type: application/json

Body:
{
  "user_id": "string",
  "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "metrics": ["sessions", "videos_generated", ...]
}
```

#### Real-time Logs
```http
GET /ws/logs/{session_id}
(WebSocket endpoint for real-time log streaming)
```

### Response Format

```json
{
  "session_id": "uuid",
  "status": "processing|completed|failed",
  "message": "Status message",
  "result_video_url": "https://...",
  "user_id": "firebase_user_id",
  "created_at": "timestamp",
  "processing_steps": [
    {
      "step": "formatter_agent",
      "status": "completed",
      "timestamp": "2025-06-20T10:30:00Z"
    }
  ]
}
```

## 🚀 Deployment

### Production Deployment Steps

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Configure Production Environment**
   - Update environment variables for production URLs
   - Set up Firebase project for production
   - Configure Google Cloud for production deployment

3. **Deploy Backend**
   ```bash
   # Using Docker (recommended)
   docker build -t neomentor-backend ./backend
   docker run -p 8000:8000 neomentor-backend
   
   # Or using cloud services
   # Google Cloud Run, AWS Lambda, etc.
   ```

4. **Deploy Frontend**
   ```bash
   # Upload build folder to your hosting service
   # Netlify, Vercel, Firebase Hosting, etc.
   ```

### Docker Deployment (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed
- Service account JSON file placed in backend directory
- Environment variables configured

**Quick Deploy:**
```bash
# 1. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Configure your environment variables in both .env files

# 3. Place your service-account-key.json in the backend directory

# 4. Deploy with Docker Compose
docker-compose up -d

# 5. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

**Production Deployment:**
```bash
# Build for production
docker-compose -f docker-compose.prod.yml up -d

# Or build individually
docker build -t neomentor-backend ./backend
docker build -t neomentor-frontend ./frontend

# Run with proper environment variables
docker run -d -p 8000:8000 --env-file backend/.env neomentor-backend  
docker run -d -p 3000:80 --env-file frontend/.env neomentor-frontend
```

### Docker Compose Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    image: neomentor-backend
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
      - UPLOAD_FOLDER=/app/uploads
      - GENERATED_MEDIA_FOLDER=/app/generated_media
      - LOG_FOLDER=/app/logs
      - MAX_FILE_SIZE=50MB

  frontend:
    image: neomentor-frontend
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/app
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_FIREBASE_API_KEY=${REACT_APP_FIREBASE_API_KEY}
      - REACT_APP_FIREBASE_AUTH_DOMAIN=${REACT_APP_FIREBASE_AUTH_DOMAIN}
      - REACT_APP_FIREBASE_PROJECT_ID=${REACT_APP_FIREBASE_PROJECT_ID}
      - REACT_APP_FIREBASE_STORAGE_BUCKET=${REACT_APP_FIREBASE_STORAGE_BUCKET}
      - REACT_APP_FIREBASE_MESSAGING_SENDER_ID=${REACT_APP_FIREBASE_MESSAGING_SENDER_ID}
      - REACT_APP_FIREBASE_APP_ID=${REACT_APP_FIREBASE_APP_ID}
```

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  backend:
    image: neomentor-backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
      - UPLOAD_FOLDER=/app/uploads
      - GENERATED_MEDIA_FOLDER=/app/generated_media
      - LOG_FOLDER=/app/logs
      - MAX_FILE_SIZE=50MB

  frontend:
    image: neomentor-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_FIREBASE_API_KEY=${REACT_APP_FIREBASE_API_KEY}
      - REACT_APP_FIREBASE_AUTH_DOMAIN=${REACT_APP_FIREBASE_AUTH_DOMAIN}
      - REACT_APP_FIREBASE_PROJECT_ID=${REACT_APP_FIREBASE_PROJECT_ID}
      - REACT_APP_FIREBASE_STORAGE_BUCKET=${REACT_APP_FIREBASE_STORAGE_BUCKET}
      - REACT_APP_FIREBASE_MESSAGING_SENDER_ID=${REACT_APP_FIREBASE_MESSAGING_SENDER_ID}
      - REACT_APP_FIREBASE_APP_ID=${REACT_APP_FIREBASE_APP_ID}
```

## 🌐 Google Cloud Platform Deployment

### Quick GCP Deployment

For detailed GCP deployment instructions, see `GCP_DEPLOYMENT_GUIDE.md`.

**One-Command Deployment:**
```bash
# Make sure you have gcloud CLI and Docker installed
./deploy-gcp.sh
```

**Manual Deployment Steps:**
```bash
# 1. Set up your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com

# 3. Create artifact repository
gcloud artifacts repositories create neomentor-repo --repository-format=docker --location=us-central1

# 4. Build and deploy
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/backend ./backend
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/frontend ./frontend

# 5. Deploy to Cloud Run
gcloud run deploy neomentor-backend --image us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/backend --region us-central1 --allow-unauthenticated
gcloud run deploy neomentor-frontend --image us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/frontend --region us-central1 --allow-unauthenticated
```

### Production Configuration

**Required Environment Variables:**
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `GOOGLE_CLOUD_LOCATION`: Deployment region (us-central1)
- Service account JSON for backend authentication

**Estimated Costs:**
- **Cloud Run**: ~$10-50/month (depending on usage)
- **Cloud Storage**: ~$5-20/month (for media files)
- **Vertex AI**: ~$20-100/month (for AI processing)
- **Firebase**: Free tier for authentication

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
cd backend
flake8 .
black .

# TypeScript checking
cd frontend
npm run type-check
```

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify service account JSON file is correctly placed
   - Check Firebase project ID matches environment variables
   - Ensure required APIs are enabled in Google Cloud Console

2. **File Upload Issues**
   - Check file size limits (default 50MB)
   - Verify supported file types (audio: .wav, .mp3; images: .jpg, .png, .gif)
   - Ensure upload directory exists and has write permissions

3. **Agent Processing Failures**
   - Verify Vertex AI API is enabled and accessible
   - Check Google Cloud quotas and billing
   - Review logs for specific error messages

4. **Video Generation Issues**
   - Ensure FFmpeg is installed and accessible
   - Check generated_media directory permissions
   - Verify sufficient disk space for processing

5. **WebSocket Connection Issues**
   - Check firewall settings for WebSocket connections
   - Verify backend is running on correct port
   - Review CORS configuration

6. **Firebase Connection Issues**
   - Verify Firestore rules allow authenticated access
   - Check network connectivity to Firebase services
   - Ensure service account has proper permissions

### Debug Mode

Enable debug logging:

**Backend:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**View Logs:**
```bash
# Check application logs
tail -f backend/logs/neomentor.log

# Check session logs
ls backend/logs/sessions/
```

### Performance Optimization

1. **Media Processing**
   - Optimize image sizes before upload
   - Use compressed audio formats when possible
   - Monitor generated_media directory size

2. **Database Queries**
   - Implement proper Firestore indexing
   - Use pagination for large result sets
   - Cache frequently accessed data

3. **API Response Times**
   - Monitor agent processing times
   - Implement request timeouts
   - Use background tasks for long-running processes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Agent Development Kit team
- React and FastAPI communities
- All contributors to this project
- [F5TTS-HuggingFace](https://huggingface.co/spaces/mrfakename/E2-F5-TTS)

## 📞 Support

For support, email your-email@example.com or join our [Discord community](https://discord.gg/neomentor).

---

Made with ❤️ by the NeoMentor Team
