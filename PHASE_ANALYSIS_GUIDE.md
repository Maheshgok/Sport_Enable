# Movement Phase Analysis Guide

## Overview

The video annotation tool now includes comprehensive **movement phase analysis** that automatically detects and analyzes three critical phases of movement:

1. **LANDING** - Initial foot contact with the ground
2. **MID-STANCE** - Point of maximum knee flexion during stance phase
3. **PUSH-OFF** - Toe-off as foot leaves the ground

For each phase, the system captures detailed biomechanical data including joint angles and velocities.

## What's Been Added

### 🎯 Phase Detection

The system automatically identifies movement cycles by analyzing ankle and knee positions:
- **Landing Detection**: Identifies when the foot makes contact with the ground (ankle reaches lowest vertical position)
- **Mid-Stance Detection**: Finds the point of maximum knee flexion between landing and push-off
- **Push-Off Detection**: Identifies when the foot leaves the ground (ankle reaches highest position before flight)

### 📊 Data Captured Per Phase

For each detected phase, the following data is captured:

#### Joint Angles (in degrees):
- Knee angle
- Hip angle  
- Ankle angle
- Shoulder angle
- Elbow angle

#### Joint Velocities (normalized):
- Knee velocity
- Hip velocity
- Ankle velocity
- Shoulder velocity
- Elbow velocity

### 📁 Output Files

The analysis generates the following new files:

#### 1. `phase_analysis_TIMESTAMP.json`
Complete phase analysis data in JSON format:
```json
{
  "left_side": {
    "cycles_detected": 5,
    "cycles": [
      {
        "cycle_number": 1,
        "side": "left",
        "landing": {
          "frame": 45,
          "timestamp": 1.5,
          "angles": {
            "knee": 165.2,
            "hip": 172.8,
            "ankle": 88.4
          },
          "velocities": {
            "knee": 0.0234,
            "hip": 0.0187
          }
        },
        "mid_stance": { ... },
        "push_off": { ... }
      }
    ]
  },
  "right_side": { ... }
}
```

#### 2. `phase_analysis_TIMESTAMP.csv`
Tabular format for easy analysis in Excel/spreadsheets:
| side | cycle | phase | frame | timestamp_sec | knee_angle_deg | hip_angle_deg | ankle_angle_deg | knee_velocity | hip_velocity |
|------|-------|-------|-------|---------------|----------------|---------------|-----------------|---------------|--------------|
| left | 1 | landing | 45 | 1.50 | 165.2 | 172.8 | 88.4 | 0.0234 | 0.0187 |
| left | 1 | mid_stance | 52 | 1.73 | 142.5 | 158.3 | 92.1 | 0.0156 | 0.0143 |
| left | 1 | push_off | 58 | 1.93 | 168.7 | 175.2 | 115.3 | 0.0312 | 0.0289 |

#### 3. Enhanced `summary_report_TIMESTAMP.txt`
The summary report now includes a detailed phase analysis section:
- Overview of cycles detected for each side
- Cycle-by-cycle breakdown with all angles and velocities
- Average values for each phase across all cycles
- Easy-to-read format for quick insights

### 📈 Visualizations

#### 1. Phase Timeline (`phase_timeline_TIMESTAMP.png`)
Shows the complete timeline of detected phases:
- Ankle vertical position over time
- Colored markers for each phase:
  - 🔴 Red circles = Landing
  - 🟢 Green squares = Mid-Stance
  - 🔵 Blue triangles = Push-Off
- Shaded regions showing stance phase duration
- Separate plots for left and right sides

#### 2. Phase Angles (`phase_angles_TIMESTAMP.png`)
Displays how joint angles change across cycles:
- Line plots showing knee, hip, and ankle angles
- Separate traces for each phase (color-coded)
- Cycle-by-cycle comparison
- Left and right side comparison

#### 3. Average Phase Angles (`phase_avg_angles_TIMESTAMP.png`)
Bar chart comparing average angles:
- Grouped bars for Landing, Mid-Stance, Push-Off
- Easy comparison across joints
- Separate charts for left and right sides

## Use Cases

### 🏃 Running Analysis
- Identify landing mechanics (heel vs forefoot strike)
- Measure knee flexion at mid-stance (shock absorption)
- Analyze push-off power (ankle angle and velocity)
- Compare left/right symmetry

### 🏋️ Exercise Form Analysis
- Squat depth analysis at mid-stance
- Landing mechanics in jump exercises
- Push-off power in explosive movements
- Movement consistency across repetitions

### 🩺 Clinical Assessment
- Gait analysis for rehabilitation
- Identify asymmetries between sides
- Track progress over time
- Quantify movement patterns

### ⚽ Sports Performance
- Sprint mechanics optimization
- Jump technique analysis
- Agility movement patterns
- Fatigue detection (changes across cycles)

## How to Read the Results

### Normal Running Patterns

**Landing Phase:**
- Knee angle: 165-175° (slight flexion)
- Hip angle: 170-180° (nearly extended)
- Ankle angle: 85-95° (dorsiflexed)

**Mid-Stance Phase:**
- Knee angle: 140-150° (maximum flexion)
- Hip angle: 155-165° (flexed)
- Ankle angle: 90-100° (neutral to slight dorsiflexion)

**Push-Off Phase:**
- Knee angle: 165-175° (extending)
- Hip angle: 175-185° (extended)
- Ankle angle: 110-130° (plantarflexed)

### Key Metrics to Watch

1. **Cycle Duration**: Normal running stride ~0.6-1.0 seconds
2. **Knee Flexion Range**: Landing to mid-stance ~20-30°
3. **Ankle Plantarflexion**: Mid-stance to push-off ~20-40°
4. **Left/Right Symmetry**: Angles should be within 5-10° between sides

## Implementation Details

### Phase Detection Algorithm

The system uses a multi-step approach:

1. **Signal Smoothing**: Gaussian filter to reduce noise
2. **Peak Detection**: Identifies local maxima/minima in ankle position
3. **Cycle Matching**: Pairs landing and push-off frames
4. **Mid-Stance Identification**: Finds maximum knee flexion between landing and push-off

### Parameters

- `min_cycle_frames`: Minimum frames between phases (default: 15)
- `sigma`: Gaussian smoothing parameter (default: 2)
- `prominence`: Peak detection sensitivity (default: 0.005)

## Tips for Best Results

1. **Camera Position**: 
   - Side view provides best ankle/knee tracking
   - Ensure full body is visible
   - Stable camera position

2. **Video Quality**:
   - Good lighting
   - Clear view of legs/feet
   - Minimal background motion

3. **Movement Type**:
   - Works best for cyclical movements (running, walking, jumping)
   - Requires clear ground contact phases
   - Multiple cycles give better analysis

4. **Interpretation**:
   - Always view visualizations alongside data
   - Compare across cycles for consistency
   - Look for left/right asymmetries
   - Consider the context of the activity

## Example Analysis Workflow

1. **Record Video**: Capture movement from side view
2. **Process Video**: Run through annotation tool
3. **Review Timeline**: Check `phase_timeline_*.png` to verify detections
4. **Analyze Angles**: Review `phase_angles_*.png` for patterns
5. **Check CSV Data**: Open `phase_analysis_*.csv` in spreadsheet
6. **Read Report**: Review `summary_report_*.txt` for detailed breakdown
7. **Compare Sides**: Look for asymmetries in left vs right
8. **Track Progress**: Compare multiple sessions over time

## Troubleshooting

### No Cycles Detected
- Ensure video shows clear foot contact/liftoff
- Check if movement is cyclical enough
- Verify MediaPipe can detect body landmarks

### Too Many/Few Detections
- May need to adjust video quality
- Ensure stable camera position
- Check if full movement cycles are visible

### Inconsistent Data
- Review video quality
- Check for occlusions
- Ensure good lighting

## Future Enhancements

Potential additions in future versions:
- Ground reaction force estimation
- Stride length calculation
- Cadence analysis
- Fatigue detection
- Injury risk indicators
- Real-time feedback

---

**Note**: This phase analysis is designed for research and training purposes. For clinical diagnosis, always consult with qualified healthcare professionals.
