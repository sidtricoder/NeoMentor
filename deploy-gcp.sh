#!/bin/bash

# NeoMentor GCP Deployment Script
# This script automates the deployment of NeoMentor to Google Cloud Platform

set -e  # Exit on any error

echo "🚀 NeoMentor GCP Deployment Script"
echo "=================================="

# Check if required tools are installed
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    if ! command -v gcloud &> /dev/null; then
        echo "❌ gcloud CLI is not installed. Please install it first."
        echo "   https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install it first."
        echo "   https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    echo "✅ All dependencies found"
}

# Get project configuration
setup_project() {
    echo ""
    echo "🔧 Project Configuration"
    echo "========================"
    
    # Get project ID
    if [ -z "$PROJECT_ID" ]; then
        echo "Enter your Google Cloud Project ID:"
        read -r PROJECT_ID
    fi
    
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ Project ID is required"
        exit 1
    fi
    
    echo "📝 Using Project ID: $PROJECT_ID"
    
    # Set project
    gcloud config set project "$PROJECT_ID"
    
    # Enable required APIs
    echo "🔌 Enabling required APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable storage.googleapis.com
    
    echo "✅ APIs enabled"
}

# Create Artifact Registry repository
setup_artifact_registry() {
    echo ""
    echo "📦 Setting up Artifact Registry"
    echo "==============================="
    
    # Check if repository exists
    if gcloud artifacts repositories describe neomentor-repo --location=us-central1 &> /dev/null; then
        echo "✅ Artifact Registry repository already exists"
    else
        echo "🏗️  Creating Artifact Registry repository..."
        gcloud artifacts repositories create neomentor-repo \
            --repository-format=docker \
            --location=us-central1 \
            --description="NeoMentor application images"
    fi
    
    # Configure Docker authentication
    echo "🔐 Configuring Docker authentication..."
    gcloud auth configure-docker us-central1-docker.pkg.dev
    
    echo "✅ Artifact Registry setup complete"
}

# Build and push Docker images
build_and_push() {
    echo ""
    echo "🏗️  Building and Pushing Docker Images"
    echo "======================================"
    
    # Build backend image
    echo "🔨 Building backend image..."
    sudo docker build -t "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/backend:latest" ./backend
    
    # Build frontend image with build args
    echo "🔨 Building frontend image..."
    sudo docker build \
        --build-arg REACT_APP_API_URL="https://neomentor-backend-140655189111.us-central1.run.app" \
        --build-arg REACT_APP_FIREBASE_API_KEY="AIzaSyA7XEOb9VUoC9LnQR5DOdKp7O45L2rwbmU" \
        --build-arg REACT_APP_FIREBASE_AUTH_DOMAIN="eternal-argon-460400-i0.firebaseapp.com" \
        --build-arg REACT_APP_FIREBASE_PROJECT_ID="eternal-argon-460400-i0" \
        --build-arg REACT_APP_FIREBASE_STORAGE_BUCKET="eternal-argon-460400-i0.firebasestorage.app" \
        --build-arg REACT_APP_FIREBASE_MESSAGING_SENDER_ID="140655189111" \
        --build-arg REACT_APP_FIREBASE_APP_ID="1:140655189111:web:d7f5eb2599c51624866fbf" \
        -t "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/frontend:latest" ./frontend
    
    # Push images
    echo "📤 Pushing backend image..."
    sudo docker push "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/backend:latest"
    
    echo "📤 Pushing frontend image..."
    sudo docker push "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/frontend:latest"
    
    echo "✅ Images built and pushed successfully"
}

# Deploy to Cloud Run
deploy_services() {
    echo ""
    echo "🚀 Deploying to Cloud Run"
    echo "========================="
    
    # Deploy backend first (without CORS initially)
    echo "🔧 Deploying backend service..."
    gcloud run deploy neomentor-backend \
        --image "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/backend:latest" \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,FIREBASE_PROJECT_ID=eternal-argon-460400-i0" \
        --memory=2Gi \
        --cpu=1 \
        --timeout=3600 \
        --concurrency=10 \
        --max-instances=5 \
        --quiet
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe neomentor-backend --region=us-central1 --format='value(status.url)')
    echo "✅ Backend deployed: $BACKEND_URL"
    
    # Deploy frontend
    echo "🔧 Deploying frontend service..."
    gcloud run deploy neomentor-frontend \
        --image "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/frontend:latest" \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars="REACT_APP_API_URL=$BACKEND_URL" \
        --memory=512Mi \
        --cpu=1 \
        --concurrency=80 \
        --max-instances=10 \
        --quiet
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe neomentor-frontend --region=us-central1 --format='value(status.url)')
    echo "✅ Frontend deployed: $FRONTEND_URL"
    
    # Redeploy backend with CORS configuration
    echo "🔧 Updating backend with CORS configuration..."
    ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,$FRONTEND_URL"
    
    # Read service account key and encode it as base64 for environment variable
    if [ -f "backend/service-account-key.json" ]; then
        FIREBASE_SERVICE_ACCOUNT_JSON=$(cat backend/service-account-key.json | base64 -w 0)
    else
        echo "⚠️  Warning: service-account-key.json not found. Authentication may not work properly."
    fi
    
    gcloud run deploy neomentor-backend \
        --image "us-central1-docker.pkg.dev/$PROJECT_ID/neomentor-repo/backend:latest" \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,FIREBASE_PROJECT_ID=eternal-argon-460400-i0,ALLOWED_ORIGINS=$ALLOWED_ORIGINS,FIREBASE_SERVICE_ACCOUNT_JSON_B64=$FIREBASE_SERVICE_ACCOUNT_JSON" \
        --memory=2Gi \
        --cpu=1 \
        --timeout=3600 \
        --concurrency=10 \
        --max-instances=5 \
        --quiet
    echo "✅ Backend updated with CORS configuration"
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================="
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL:  $BACKEND_URL"
}

# Setup monitoring and storage
setup_additional_services() {
    echo ""
    echo "🛠️  Setting up additional services"
    echo "================================="
    
    # Create Cloud Storage bucket for media
    BUCKET_NAME="$PROJECT_ID-neomentor-media"
    if gsutil ls -b "gs://$BUCKET_NAME" &> /dev/null; then
        echo "✅ Storage bucket already exists"
    else
        echo "🪣 Creating Cloud Storage bucket..."
        gsutil mb "gs://$BUCKET_NAME"
        gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"
        echo "✅ Storage bucket created: gs://$BUCKET_NAME"
    fi
    
    # Create service account
    SERVICE_ACCOUNT="neomentor-service@$PROJECT_ID.iam.gserviceaccount.com"
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" &> /dev/null; then
        echo "✅ Service account already exists"
    else
        echo "👤 Creating service account..."
        gcloud iam service-accounts create neomentor-service \
            --display-name="NeoMentor Service Account"
        
        # Grant permissions
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/aiplatform.user"
        
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/storage.admin"
        
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/firebase.admin"
        
        echo "✅ Service account created and configured"
    fi
    
    # Update backend service with service account
    echo "🔧 Updating backend service with service account..."
    gcloud run services update neomentor-backend \
        --service-account="$SERVICE_ACCOUNT" \
        --region us-central1 \
        --quiet
    
    echo "✅ Additional services configured"
}

# Verification
verify_deployment() {
    echo ""
    echo "🔍 Verifying Deployment"
    echo "======================"
    
    # Test backend health
    echo "🏥 Testing backend health..."
    if curl -s "$BACKEND_URL/health" &> /dev/null; then
        echo "✅ Backend is healthy"
    else
        echo "⚠️  Backend health check failed"
    fi
    
    # Test frontend
    echo "🌐 Testing frontend..."
    if curl -s "$FRONTEND_URL" &> /dev/null; then
        echo "✅ Frontend is accessible"
    else
        echo "⚠️  Frontend accessibility check failed"
    fi
    
    echo ""
    echo "🎊 Deployment Summary"
    echo "===================="
    echo "✅ Project: $PROJECT_ID"
    echo "✅ Frontend: $FRONTEND_URL"
    echo "✅ Backend:  $BACKEND_URL"
    echo "✅ Storage:  gs://$PROJECT_ID-neomentor-media"
    echo ""
    echo "🔗 Next Steps:"
    echo "1. Update Firebase authorized domains with: $(echo $FRONTEND_URL | sed 's|https://||')"
    echo "2. Configure your frontend .env with Firebase credentials"
    echo "3. Test the complete application workflow"
    echo "4. Set up monitoring and alerts"
}

# Main execution
main() {
    check_dependencies
    setup_project
    setup_artifact_registry
    build_and_push
    deploy_services
    setup_additional_services
    verify_deployment
}

# Run main function
main "$@"
