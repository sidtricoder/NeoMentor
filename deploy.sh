#!/bin/bash

# NeoMentor Complete Deployment Script
# Usage: ./deploy.sh [PROJECT_ID]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if project ID is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <PROJECT_ID>"
    print_error "Example: $0 eternal-argon-460400-i0"
    exit 1
fi

PROJECT_ID="$1"
REGION="us-central1"
REPOSITORY="neomentor-repo"
REGISTRY_URL="us-central1-docker.pkg.dev"

print_status "🚀 Starting NeoMentor deployment to Google Cloud"
print_status "Project ID: $PROJECT_ID"
print_status "Region: $REGION"
echo

# Set the project
print_status "Setting up Google Cloud project..."
gcloud config set project "$PROJECT_ID"

# Authenticate with Google Cloud (personal account for better permissions)
print_status "Authenticating with Google Cloud..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@gmail.com"; then
    print_warning "No personal account found. Please authenticate:"
    gcloud auth login
fi

# Set personal account as active
PERSONAL_ACCOUNT=$(gcloud auth list --filter="account~gmail.com" --format="value(account)" | head -n1)
if [ ! -z "$PERSONAL_ACCOUNT" ]; then
    print_status "Using personal account: $PERSONAL_ACCOUNT"
    gcloud config set account "$PERSONAL_ACCOUNT"
fi

# Set up application default credentials
print_status "Setting up application default credentials..."
gcloud auth application-default set-quota-project "$PROJECT_ID"

# Configure Docker authentication
print_status "Configuring Docker authentication..."
gcloud auth configure-docker "${REGISTRY_URL}" --quiet

# Additional Docker login for reliability
print_status "Authenticating Docker with access token..."
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin "${REGISTRY_URL}"

# Check if repository exists
print_status "Checking Artifact Registry repository..."
if ! gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" >/dev/null 2>&1; then
    print_warning "Repository $REPOSITORY does not exist. Creating it..."
    gcloud artifacts repositories create "$REPOSITORY" \
        --repository-format=docker \
        --location="$REGION" \
        --description="NeoMentor application images"
fi

print_success "Repository $REPOSITORY exists and is accessible"

# Build and push backend image
print_status "🔨 Building backend Docker image..."
docker build -t "${REGISTRY_URL}/${PROJECT_ID}/${REPOSITORY}/backend:latest" ./backend

print_status "📤 Pushing backend image to Artifact Registry..."
docker push "${REGISTRY_URL}/${PROJECT_ID}/${REPOSITORY}/backend:latest"

print_success "Backend image pushed successfully"

# Build and push frontend image
print_status "🔨 Building frontend Docker image..."
docker build -t "${REGISTRY_URL}/${PROJECT_ID}/${REPOSITORY}/frontend:latest" ./frontend

print_status "📤 Pushing frontend image to Artifact Registry..."
docker push "${REGISTRY_URL}/${PROJECT_ID}/${REPOSITORY}/frontend:latest"

print_success "Frontend image pushed successfully"

# Deploy backend service
print_status "🚀 Deploying backend service to Cloud Run..."
gcloud run deploy neomentor-backend \
    --image "${REGISTRY_URL}/${PROJECT_ID}/${REPOSITORY}/backend:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8000 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --max-instances 10

BACKEND_URL=$(gcloud run services describe neomentor-backend --region="$REGION" --format="value(status.url)")
print_success "Backend deployed successfully at: $BACKEND_URL"

# Deploy frontend service
print_status "🚀 Deploying frontend service to Cloud Run..."
gcloud run deploy neomentor-frontend \
    --image "${REGISTRY_URL}/${PROJECT_ID}/${REPOSITORY}/frontend:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 3000 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10

FRONTEND_URL=$(gcloud run services describe neomentor-frontend --region="$REGION" --format="value(status.url)")
print_success "Frontend deployed successfully at: $FRONTEND_URL"

# Display deployment summary
echo
print_success "🎉 Deployment completed successfully!"
echo
echo "=== DEPLOYMENT SUMMARY ==="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo
echo "=== NEXT STEPS ==="
echo "1. Environment variables are already hardcoded in the frontend"
echo "2. Test the application at: $FRONTEND_URL"
echo "3. Configure custom domain if needed"
echo
print_status "Deployment script completed!"
