#!/bin/bash

# Deploy Video Analysis API to Google Cloud Run
# Prerequisites: 
# - Google Cloud SDK installed
# - Project created and billing enabled
# - Authenticated with: gcloud auth login

# Configuration
PROJECT_ID="watch-mail-trial"  # Change to your GCP project ID
SERVICE_NAME="video-analysis-api"
REGION="us-central1"  # Change to your preferred region
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================="
echo "Deploying Video Analysis API"
echo "========================================="
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo ""

# Set the project
echo "Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build Docker image
echo ""
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Push image to Google Container Registry
echo ""
echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed!"
    exit 1
fi

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --set-env-vars "PORT=8080"

if [ $? -ne 0 ]; then
    echo "❌ Cloud Run deployment failed!"
    exit 1
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Next steps:"
echo "1. Update your .env file with: VITE_API_URL=${SERVICE_URL}"
echo "2. Test the API: curl ${SERVICE_URL}/health"
echo "3. Rebuild and redeploy your frontend"
echo ""
