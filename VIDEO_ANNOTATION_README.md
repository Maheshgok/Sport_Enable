# Video Annotation Tool - Quick Start

## 🎯 What This Tool Does
Analyzes human movement in videos using Google MediaPipe to track joints, calculate angles, and measure movement patterns.

## 📦 Quick Installation

```powershell
# Install required packages
pip install opencv-python mediapipe numpy pandas matplotlib
```

## 🚀 Quick Start

### 1. Process a Video
```powershell
python video_annotation_tool.py your_video.mp4
```

This will create an `output/` folder with:
- Annotated video with pose overlay
- CSV files with movement data
- Analysis report

### 2. Analyze the Results
```powershell
python analyze_movement.py output/frame_data_*.csv
```

This generates:
- Statistical analysis
- Movement graphs
- Left vs Right comparison

## 📊 What You Get

### Output Files
1. **`annotated_video_*.mp4`** - Video with skeleton overlay
2. **`frame_data_*.csv`** - Complete landmark data (x, y, z coordinates)
3. **`joint_angles_minmax_*.csv`** - **NEW!** Min/Max angles for every joint with frame/timestamp
4. **`joint_velocities_*.csv`** - Movement speed for each joint
5. **`movement_analysis_*.csv`** - Min/max/mean statistics
6. **`summary_report_*.txt`** - Human-readable summary with detailed angle breakdown
7. **`*.png`** - Movement visualization graphs (from analyze_movement.py)

### Key Metrics Captured

#### Joint Angles (Now Expanded!)
- **Knee angles** (left & right): Hip-Knee-Ankle (squat depth, bend)
- **Elbow angles** (left & right): Shoulder-Elbow-Wrist (arm flexion)
- **Hip angles** (left & right): Shoulder-Hip-Knee (torso-leg angle)
- **Shoulder angles** (left & right): Hip-Shoulder-Elbow (arm position)
- **Ankle angles** (left & right): Knee-Ankle-Vertical (foot position)
- **Wrist angles** (left & right): Elbow-Wrist-Forward (wrist orientation)
- **Neck angle**: Head position relative to shoulders
- Range: 0° (fully bent) to 180° (straight)
- **For each angle**: Min, Max, Mean, Standard Deviation, and exact frame/time of min/max

#### Position Tracking
- **X, Y, Z coordinates** for all joints
- **Visibility score** (confidence level)
- **Frame-by-frame** tracking

#### Movement Analysis
- **Velocity**: Speed of each joint
- **Range of motion**: Min/max positions
- **Symmetry**: Left vs right comparison
- **Relative distances**: Joint relationships (e.g., knee-to-hip)

## 📖 Example Use Cases

### Athletic Training
```powershell
# Analyze squat form
python video_annotation_tool.py squat_video.mp4
python analyze_movement.py output/frame_data_*.csv
# Check knee angles: should reach ~90° for proper depth
```

### Physical Therapy
```powershell
# Track range of motion improvement
python video_annotation_tool.py patient_exercise.mp4
# Compare weekly progress via CSV files
```

### Biomechanics Research
```powershell
# Extract all pose data for custom analysis
python video_annotation_tool.py movement_study.mp4
# Use frame_data CSV in your own analysis scripts
```

## 🔍 Understanding the Data

### Coordinate System
- **X**: 0 (left) to 1 (right)
- **Y**: 0 (top) to 1 (bottom) - *inverted*
- **Z**: negative (closer) to positive (farther)

### Key Joints Tracked
- Head: nose, eyes, ears
- Upper body: shoulders, elbows, wrists
- Core: hips
- Lower body: knees, ankles

### Reading CSV Data
```python
import pandas as pd

# Load data
df = pd.read_csv('output/frame_data_20260326_123456.csv')

# Find maximum knee bend
max_bend = df['left_knee_angle'].min()
max_bend_frame = df.loc[df['left_knee_angle'].idxmin(), 'frame']
print(f"Max knee bend: {max_bend:.1f}° at frame {max_bend_frame}")

# Track wrist height over time
print(df[['timestamp_sec', 'left_wrist_y', 'right_wrist_y']])
```

## ⚙️ Configuration Options

### Video Quality
For best results:
- Resolution: 720p or 1080p
- Lighting: Well-lit, even lighting
- Camera angle: Front or side view
- Subject size: 60-80% of frame

### Adjust Sensitivity
Edit `video_annotation_tool.py`:
```python
# Line ~102 - Change confidence threshold
min_detection_confidence=0.5,  # Lower = more detections (0.3-0.9)
min_tracking_confidence=0.5,   # Lower = less stable (0.3-0.9)
```

## 🆘 Troubleshooting

**No pose detected?**
- Ensure person is fully visible in frame
- Check lighting quality
- Try lowering confidence threshold

**Slow processing?**
- Reduce video resolution
- Use shorter video clips
- Set `model_complexity=1` (line 102)

**Jittery landmarks?**
- Increase `min_tracking_confidence`
- Use higher quality video

## 📚 Full Documentation
See [VIDEO_ANNOTATION_GUIDE.md](VIDEO_ANNOTATION_GUIDE.md) for complete documentation.

## 💡 Pro Tips

1. **Batch Processing**: Process multiple videos in a loop
2. **Export to Excel**: Open CSV files directly in Excel
3. **Custom Metrics**: Edit script to add your own measurements
4. **Real-time**: Modify to use webcam instead of video file
5. **Comparison**: Use pandas to compare multiple sessions

## 🎬 Example Workflow

```powershell
# 1. Process video
python video_annotation_tool.py athlete_jump.mp4

# 2. Analyze results  
python analyze_movement.py output/frame_data_20260326_120000.csv

# 3. Review outputs
# - Watch annotated_video_*.mp4
# - Read summary_report_*.txt
# - Check movement graphs (*.png)
# - Open frame_data_*.csv in Excel for custom analysis
```

## 🔧 Requirements
- Python 3.8+
- opencv-python
- mediapipe
- numpy
- pandas
- matplotlib (for analysis script)

---

**Ready to start?** Just run:
```powershell
python video_annotation_tool.py your_video.mp4
```
