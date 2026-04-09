# Joint Angles Reference Guide

## Overview
The video annotation tool now tracks **14 different joint angles** across both sides of the body, providing comprehensive biomechanical analysis.

## Angles Tracked

### 🦵 Lower Body Angles

#### 1. Knee Angles (Hip-Knee-Ankle)
- **Left Knee Angle** & **Right Knee Angle**
- **Measures**: The angle between thigh and shin
- **Use Case**: Squat depth, running gait, jumping mechanics
- **Key Values**:
  - 180° = Fully extended (standing straight)
  - 90° = Right angle bend
  - <90° = Deep squat/bend
  - 0° = Completely bent (heel to buttock)

#### 2. Hip Angles (Shoulder-Hip-Knee)
- **Left Hip Angle** & **Right Hip Angle**
- **Measures**: The angle between torso and thigh
- **Use Case**: Hip flexion, sitting/standing, forward bends
- **Key Values**:
  - 180° = Standing straight
  - 90° = Seated position or leg raised to hip height
  - <90° = Deep hip flexion

#### 3. Ankle Angles (Knee-Ankle-Vertical)
- **Left Ankle Angle** & **Right Ankle Angle**
- **Measures**: Shin angle relative to vertical (approximation)
- **Use Case**: Dorsiflexion/plantarflexion, balance, landing mechanics
- **Note**: Approximation since MediaPipe doesn't track toes

### 💪 Upper Body Angles

#### 4. Elbow Angles (Shoulder-Elbow-Wrist)
- **Left Elbow Angle** & **Right Elbow Angle**
- **Measures**: The angle between upper arm and forearm
- **Use Case**: Pushups, bicep curls, throwing mechanics
- **Key Values**:
  - 180° = Fully extended arm
  - 90° = Right angle (halfway through curl)
  - 0° = Fully flexed (hand to shoulder)

#### 5. Shoulder Angles (Hip-Shoulder-Elbow)
- **Left Shoulder Angle** & **Right Shoulder Angle**
- **Measures**: Arm position relative to torso
- **Use Case**: Shoulder raises, arm swings, overhead movements
- **Key Values**:
  - ~180° = Arm straight down at side
  - ~90° = Arm extended horizontal/forward
  - <90° = Arm raised above horizontal

#### 6. Wrist Angles (Elbow-Wrist-Forward)
- **Left Wrist Angle** & **Right Wrist Angle**
- **Measures**: Wrist orientation (approximation)
- **Use Case**: Hand positioning, throwing, catching
- **Note**: Approximation based on forward direction

### 🧘 Posture Angles

#### 7. Neck Angle (Shoulders-Nose-Vertical)
- **Measures**: Head tilt/position relative to vertical
- **Use Case**: Posture analysis, head position during movements
- **Key Values**:
  - 180° = Head looking straight ahead
  - <180° = Head tilted forward or back

## Output Files Explained

### 1. Frame Data CSV (`frame_data_*.csv`)
Contains **every angle for every frame** in columns:
```
frame, timestamp_sec,
left_knee_angle, right_knee_angle,
left_elbow_angle, right_elbow_angle,
left_hip_angle, right_hip_angle,
left_shoulder_angle, right_shoulder_angle,
left_ankle_angle, right_ankle_angle,
left_wrist_angle, right_wrist_angle,
neck_angle,
... (plus x,y,z coordinates for all joints)
```

### 2. Joint Angles Min/Max CSV (`joint_angles_minmax_*.csv`)
**Dedicated angle summary** with columns:
- `joint_angle`: Name of the joint
- `minimum_angle_degrees`: Smallest angle (most bent/flexed)
- `maximum_angle_degrees`: Largest angle (most extended)
- `range_degrees`: Total range of motion
- `mean_angle_degrees`: Average angle throughout video
- `std_dev_degrees`: Standard deviation
- `min_angle_frame`: Frame number where minimum occurred
- `min_angle_timestamp_sec`: Time when minimum occurred
- `max_angle_frame`: Frame number where maximum occurred
- `max_angle_timestamp_sec`: Time when maximum occurred

**Example Row:**
```csv
Left Knee,45.23,178.56,133.33,112.45,25.67,342,5.70,891,14.85
```
This means:
- Left knee bent to minimum 45.23° at frame 342 (5.70 seconds)
- Left knee extended to maximum 178.56° at frame 891 (14.85 seconds)
- Range of motion: 133.33°

### 3. Summary Report TXT (`summary_report_*.txt`)
Human-readable report organized by joint type:
- **Knee Angles Section**: Both knees with min/max/mean
- **Elbow Angles Section**: Both elbows with min/max/mean
- **Hip Angles Section**: Both hips with min/max/mean
- **Shoulder Angles Section**: Both shoulders with min/max/mean
- **Ankle Angles Section**: Both ankles with min/max/mean
- **Wrist Angles Section**: Both wrists with min/max/mean
- **Neck Angle Section**: Head position with min/max/mean

Each entry shows exact frame and timestamp of min and max values.

## Practical Examples

### Example 1: Analyzing Squat Depth
```python
import pandas as pd

df = pd.read_csv('output/frame_data_*.csv')

# Find deepest squat (minimum knee angle)
deepest_left = df['left_knee_angle'].min()
deepest_right = df['right_knee_angle'].min()

print(f"Left knee minimum: {deepest_left:.1f}°")
print(f"Right knee minimum: {deepest_right:.1f}°")

# Check if squat reached proper depth (< 90°)
if deepest_left < 90 and deepest_right < 90:
    print("✓ Proper squat depth achieved!")
```

### Example 2: Range of Motion Assessment
```python
import pandas as pd

# Load the min/max summary
angles_df = pd.read_csv('output/joint_angles_minmax_*.csv')

# Print range of motion for all joints
for _, row in angles_df.iterrows():
    print(f"{row['joint_angle']}: {row['range_degrees']:.1f}° ROM")
```

### Example 3: Finding Key Movement Frames
```python
import pandas as pd

angles_df = pd.read_csv('output/joint_angles_minmax_*.csv')

# Find when left knee was most bent
left_knee = angles_df[angles_df['joint_angle'] == 'Left Knee'].iloc[0]
print(f"Most bent at frame {left_knee['min_angle_frame']}")
print(f"Angle: {left_knee['minimum_angle_degrees']:.1f}°")
print(f"Time: {left_knee['min_angle_timestamp_sec']:.2f}s")

# You can then go to this frame in the video to see the exact position
```

### Example 4: Comparing Left vs Right Symmetry
```python
import pandas as pd

angles_df = pd.read_csv('output/joint_angles_minmax_*.csv')

# Compare knee angles
left_knee = angles_df[angles_df['joint_angle'] == 'Left Knee'].iloc[0]
right_knee = angles_df[angles_df['joint_angle'] == 'Right Knee'].iloc[0]

left_rom = left_knee['range_degrees']
right_rom = right_knee['range_degrees']

diff = abs(left_rom - right_rom)
print(f"Left ROM: {left_rom:.1f}°")
print(f"Right ROM: {right_rom:.1f}°")
print(f"Difference: {diff:.1f}°")

if diff < 10:
    print("✓ Good symmetry!")
else:
    print("⚠ Asymmetry detected")
```

## Understanding Angle Calculations

### How Angles Are Calculated
All angles use the **3-point method**:
1. Point A (proximal joint)
2. Point B (joint vertex/center)
3. Point C (distal joint)

The angle is calculated using vectors:
- Vector BA (from B to A)
- Vector BC (from B to C)
- Angle = arccos(dot product / (magnitude1 × magnitude2))

### Interpretation Tips

#### Knee & Elbow Angles
- **Near 180°**: Joint is straight/extended
- **~90°**: Right angle, moderate bend
- **<90°**: Deep flexion, significant bend
- **Lower values = more bent**

#### Hip & Shoulder Angles
- Context-dependent based on body position
- Compare to baseline (standing = ~180°)
- Track changes over time for meaningful analysis

#### Ankle & Wrist Angles
- These are approximations (limited to available landmarks)
- Useful for gross movement patterns
- Best compared relatively (change over time)

## Common Use Cases

### Athletic Performance
- **Sprint Analysis**: Track hip and knee angles during running
- **Jump Mechanics**: Measure knee flexion depth before jump
- **Swimming Strokes**: Monitor elbow and shoulder angles
- **Weightlifting**: Verify proper form (squat depth, elbow position)

### Physical Therapy
- **ROM Assessment**: Compare current vs target range of motion
- **Progress Tracking**: Monitor improvement week-over-week
- **Compensation Patterns**: Check for left-right asymmetry
- **Exercise Compliance**: Verify patient reaches target angles

### Biomechanics Research
- **Gait Analysis**: Full lower body angle tracking during walking
- **Posture Study**: Neck and hip angles during tasks
- **Ergonomics**: Shoulder and elbow angles during work activities
- **Movement Efficiency**: Compare angles between skilled/novice performers

## Tips for Accurate Measurements

1. **Camera Position**: Place camera perpendicular to movement plane
2. **Distance**: Subject should occupy 60-80% of frame
3. **Lighting**: Ensure all body parts are clearly visible
4. **Clothing**: Form-fitting clothes help landmark detection
5. **Background**: Plain background improves tracking accuracy
6. **Reference Movements**: Include known angles for calibration

## Troubleshooting

**Angles seem wrong or inconsistent?**
- Check if joints are fully visible in frame
- Verify camera angle is perpendicular to movement
- Look at visibility scores in frame_data CSV
- Compare left/right sides for reasonableness

**Missing angle data?**
- Ensure pose was detected (check annotated video)
- Some frames may have missing landmarks
- Filter by visibility threshold if needed

**Angles don't match expectations?**
- Remember: angles are in 2D projection
- Camera angle affects measurements significantly
- Use for relative comparisons rather than absolute values
- Consider adding reference measurements for calibration

## Next Steps

1. **Process your video**: `python video_annotation_tool.py your_video.mp4`
2. **Check joint_angles_minmax CSV**: Quick overview of all angle ranges
3. **Read summary_report.txt**: Detailed analysis with frame numbers
4. **Load frame_data CSV**: Frame-by-frame analysis for custom metrics
5. **Generate graphs**: `python analyze_movement.py output/frame_data_*.csv`

---

**Need more angles?** The tool can be extended to calculate additional angles by modifying the `video_annotation_tool.py` script to add custom angle calculations using the `calculate_angle()` function.
