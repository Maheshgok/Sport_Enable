# Video Annotation Tool Guide

## Overview
This tool uses Google MediaPipe to analyze human movement in videos, capturing pose landmarks frame-by-frame and calculating key joint movements and angles.

## Features

### 1. Pose Detection
- Detects 33 body landmarks using MediaPipe Pose
- Tracks key joints: shoulders, elbows, wrists, hips, knees, ankles, neck
- Provides x, y, z coordinates and visibility scores

### 2. Movement Analysis
- **Joint Angles**: Calculates angles for knees, elbows, hips
- **Relative Distances**: Measures distances between key points (e.g., knee-to-hip)
- **Movement Velocity**: Tracks speed of movement for each joint
- **Range of Motion**: Identifies min/max values for joints

### 3. Data Export
Generates multiple output files:
- `annotated_video_*.mp4`: Video with pose overlay visualization
- `frame_data_*.csv`: Complete landmark data for every frame
- `joint_velocities_*.csv`: Movement velocity analysis
- `movement_analysis_*.csv`: Statistical summary
- `summary_report_*.txt`: Human-readable analysis

## Installation

### Step 1: Install Python Dependencies
```powershell
pip install -r requirements_video_tool.txt
```

Or install individually:
```powershell
pip install opencv-python mediapipe numpy pandas
```

### Step 2: Verify Installation
```powershell
python -c "import cv2, mediapipe, numpy, pandas; print('All packages installed successfully!')"
```

## Usage

### Basic Usage
```powershell
python video_annotation_tool.py <video_path>
```

Example:
```powershell
python video_annotation_tool.py athlete_movement.mp4
```

### Specify Output Folder
```powershell
python video_annotation_tool.py athlete_movement.mp4 analysis_results
```

## Understanding the Outputs

### 1. Frame Data CSV (`frame_data_*.csv`)
Contains raw data for each frame with columns:
- `frame`: Frame number
- `timestamp_sec`: Time in seconds
- `{joint}_x`, `{joint}_y`, `{joint}_z`: 3D coordinates (normalized 0-1)
- `{joint}_visibility`: Detection confidence (0-1)
- `{joint}_angle`: Joint angles in degrees
- `{joint}_hip_distance`: Relative distances

**Key Joints Tracked:**
- nose, left_eye, right_eye, left_ear, right_ear
- left_shoulder, right_shoulder
- left_elbow, right_elbow
- left_wrist, right_wrist
- left_hip, right_hip
- left_knee, right_knee
- left_ankle, right_ankle

### 2. Joint Velocities CSV (`joint_velocities_*.csv`)
Shows movement speed for each joint:
- `joint`: Joint name
- `max_velocity`: Peak movement speed
- `mean_velocity`: Average movement speed
- `total_movement`: Cumulative movement

### 3. Movement Analysis CSV (`movement_analysis_*.csv`)
Statistical summary including:
- Min/max joint angles
- Mean angles
- Range of motion
- Knee-hip distance variations

### 4. Summary Report TXT (`summary_report_*.txt`)
Human-readable report with:
- Total frames and duration
- Joint angle ranges
- Most active joints ranked by movement

## Analyzing the Data

### Using Python/Pandas
```python
import pandas as pd

# Load frame data
df = pd.read_csv('output/frame_data_20260326_123456.csv')

# Find frame with maximum knee bend (left)
max_knee_bend_frame = df.loc[df['left_knee_angle'].idxmin()]
print(f"Maximum knee bend at frame {max_knee_bend_frame['frame']}")
print(f"Angle: {max_knee_bend_frame['left_knee_angle']:.2f}°")

# Track wrist movement over time
import matplotlib.pyplot as plt
plt.plot(df['timestamp_sec'], df['left_wrist_y'])
plt.xlabel('Time (seconds)')
plt.ylabel('Wrist Height (normalized)')
plt.title('Left Wrist Movement')
plt.show()
```

### Key Metrics to Look For

#### Knee Movement
- **Knee angle**: 180° = straight, <90° = deep bend
- **Knee-hip distance**: Negative = knee above hip, Positive = knee below hip

#### Shoulder Movement
- Track shoulder elevation/rotation via x, y coordinates
- Compare left vs right symmetry

#### Ankle/Wrist Velocity
- High velocity = fast movements
- Useful for tracking punches, kicks, jumps

## Advanced Configuration

### Modify Confidence Threshold
Edit `video_annotation_tool.py`, line with `confidence_threshold`:
```python
tool.process_video(video_path, output_folder, confidence_threshold=0.7)
```
Higher values (0.7-0.9) = stricter detection, fewer false positives

### Add Custom Measurements
Add custom calculations in the `process_video` method:
```python
# Example: Calculate arm extension
arm_extension = abs(landmarks[left_shoulder].x - landmarks[left_wrist].x)
frame_dict['left_arm_extension'] = arm_extension
```

## Common Use Cases

### 1. Athletic Performance Analysis
- Track squat depth (knee angles)
- Measure jump height (hip/ankle vertical movement)
- Analyze running gait (knee-hip relationship)

### 2. Physical Therapy
- Monitor range of motion improvements
- Track exercise form compliance
- Identify compensation patterns

### 3. Sports Coaching
- Compare athlete techniques
- Identify biomechanical inefficiencies
- Track progress over time

## Troubleshooting

### Issue: "Cannot open video file"
- Ensure video file path is correct
- Try converting video to MP4 format
- Check file permissions

### Issue: "No pose detected"
- Ensure person is clearly visible and well-lit
- Check if person is in full frame
- Lower confidence threshold
- Try a different video angle

### Issue: "Jittery/unstable landmarks"
- Enable landmark smoothing (already enabled in code)
- Increase `min_tracking_confidence` parameter
- Use higher quality video input

### Issue: "Slow processing"
- Reduce video resolution before processing
- Use `model_complexity=1` instead of 2 (line 102)
- Process shorter video clips

## Performance Tips

1. **Video Quality**: Use 720p-1080p for best results
2. **Lighting**: Ensure good lighting and contrast
3. **Camera Angle**: Front or side view works best
4. **Subject Distance**: Person should occupy 60-80% of frame
5. **Background**: Plain backgrounds improve detection

## Data Interpretation

### Coordinate System
- **X-axis**: Left (0) to Right (1)
- **Y-axis**: Top (0) to Bottom (1)
- **Z-axis**: Depth (negative = closer to camera)

### Joint Angles
- **0°**: Fully flexed/bent
- **180°**: Fully extended/straight
- Values calculated using law of cosines

### Converting to Real-World Measurements

To convert normalized coordinates to centimeters:
1. Measure a known reference (e.g., shoulder width = 40cm)
2. Calculate scale factor: `scale = 40 / shoulder_width_pixels`
3. Apply to all measurements

Example:
```python
# If shoulder width in frame = 0.25 (normalized) and real = 40cm
scale_factor = 40 / 0.25  # 160 cm per normalized unit

# Convert knee-hip distance
knee_hip_cm = df['left_knee_hip_distance'] * scale_factor
```

## Next Steps

1. **Batch Processing**: Loop through multiple videos
2. **Real-time Analysis**: Use webcam input instead of video file
3. **Comparative Analysis**: Compare multiple athletes side-by-side
4. **Machine Learning**: Use the extracted data to train movement classifiers

## Support

For issues or questions:
- Check MediaPipe documentation: https://google.github.io/mediapipe/
- OpenCV documentation: https://docs.opencv.org/

## License

This tool uses:
- MediaPipe (Apache License 2.0)
- OpenCV (Apache License 2.0)
