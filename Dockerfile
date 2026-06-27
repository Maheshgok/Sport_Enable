# Cloud Run Dockerfile for Moove API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal API requirements
COPY api/requirements-minimal.txt .

# Install Python dependencies (minimal, no CV/ML libraries)
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy the Flask API application
COPY api/ ./api/

# Expose port (Cloud Run uses 8080)
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=api.app_firestore
ENV PORT=8080

# Run the Flask application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "api.app_firestore:app"]
