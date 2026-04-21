# Protocol Analysis Cloud Run Service

This Cloud Run service analyzes athlete videos according to custom physiotherapist-defined protocols.

## Features

- **Custom Protocol Analysis**: Analyzes videos based on configurable protocols
- **MediaPipe Integration**: Uses Google's MediaPipe for pose detection and landmark tracking
- **Flexible Metrics**: Calculates joint angles, positions, and custom metrics
- **Automated Reporting**: Generates reports with flagged issues and recommendations
- **GCS Integration**: Downloads videos from Google Cloud Storage
- **Firestore Integration**: Stores results in Firestore

## API Endpoints

### POST /analyze
Analyzes videos according to a protocol configuration.

**Request Body:**
```json
{
  "execution_id": "uuid-of-execution",
  "protocol_config": {
    "joints_to_track": ["left_knee", "right_hip"],
    "angles_to_measure": ["knee_flexion", "hip_angle"],
    "baseline_metrics": {
      "knee_flexion_avg": {"min": 120, "max": 160}
    }
  },
  "video_urls": {
    "front": "gs://bucket/path/to/video.mp4",
    "side": "gs://bucket/path/to/video.mp4"
  }
}
```

**Response:**
```json
{
  "success": true,
  "execution_id": "uuid",
  "analysis_results": {...},
  "report": {...}
}
```

## Deployment

1. Set up Google Cloud Project with:
   - Cloud Run API enabled
   - Firestore enabled
   - Storage API enabled

2. Run the deployment script:
   ```powershell
   .\deploy.ps1 -ProjectId "your-project-id"
   ```

3. Update your main API with the Cloud Run service URL.

## Local Development

```bash
pip install -r requirements.txt
python main.py
```

## Protocol Configuration

Protocols define:
- **Video Instructions**: What physio tells athlete, camera setup
- **Analysis Config**: Which joints/angles to track
- **Baseline Metrics**: Normal ranges for measurements
- **Risk Factors**: What to flag as concerning
- **Report Template**: How to structure the output report

Example protocol for knee assessment:
```json
{
  "protocol_name": "Knee Flexion Test",
  "video_instructions": {
    "setup": "Position camera 3m away at knee height",
    "athlete_actions": ["Stand straight", "Bend knee slowly", "Return to start"]
  },
  "analysis_config": {
    "joints_to_track": ["left_knee", "right_knee", "left_hip", "right_hip"],
    "angles_to_measure": ["knee_flexion", "hip_angle"]
  },
  "baseline_metrics": {
    "knee_flexion_avg": {"min": 130, "max": 150}
  }
}
```