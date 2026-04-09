# Phase Analysis - Quick Reference Card

## 🎯 Three Phases Analyzed

| Phase | Description | Key Characteristics |
|-------|-------------|---------------------|
| **LANDING** 🔴 | Initial ground contact | Ankle at lowest point, knee flexing, absorbing impact |
| **MID-STANCE** 🟢 | Maximum knee flexion | Peak load absorption, body over support foot |
| **PUSH-OFF** 🔵 | Toe-off/takeoff | Ankle plantarflexed, knee extending, generating power |

---

## 📊 Data Available Per Phase

### Angles Captured (degrees):
- ✅ Knee angle (Hip-Knee-Ankle)
- ✅ Hip angle (Shoulder-Hip-Knee)
- ✅ Ankle angle (Knee-Ankle-Vertical)
- ✅ Shoulder angle (Hip-Shoulder-Elbow)
- ✅ Elbow angle (Shoulder-Elbow-Wrist)

### Velocities Captured (normalized):
- ✅ Knee velocity
- ✅ Hip velocity
- ✅ Ankle velocity
- ✅ Shoulder velocity
- ✅ Elbow velocity

### Timestamps:
- ✅ Frame number
- ✅ Precise timestamp (seconds)

---

## 📁 Where to Find the Data

| File | What's Inside | Best For |
|------|--------------|----------|
| `phase_analysis_*.csv` | All angles & velocities in table format | Excel analysis, statistics |
| `phase_analysis_*.json` | Complete structured data | Programming, APIs |
| `summary_report_*.txt` | Human-readable breakdown | Quick review, reports |
| `phase_timeline_*.png` | Visual timeline of phases | Understanding timing |
| `phase_angles_*.png` | Angle progression charts | Comparing cycles |
| `phase_avg_angles_*.png` | Average comparison bars | Quick insights |

---

## 🏃 Typical Values (Running)

### LANDING Phase
```
Knee:     165-175° (slightly bent)
Hip:      170-180° (nearly straight)
Ankle:    85-95°   (dorsiflexed)
Duration: Beginning of stance
```

### MID-STANCE Phase
```
Knee:     140-150° (maximum bend)
Hip:      155-165° (flexed)
Ankle:    90-100°  (neutral)
Duration: ~40% through stance
```

### PUSH-OFF Phase
```
Knee:     165-175° (extending)
Hip:      175-185° (extended)
Ankle:    110-130° (plantarflexed - pointed)
Duration: End of stance
```

---

## 🔍 Quick Checks

### ✅ Good Running Form Indicators:
- [ ] Consistent values across cycles (±5-10°)
- [ ] Left/right symmetry (within 10°)
- [ ] Smooth progression: Landing → Mid-Stance → Push-Off
- [ ] Adequate knee flexion at mid-stance (20-30° from landing)
- [ ] Strong ankle plantarflexion at push-off (20-40° from mid-stance)

### ⚠️ Red Flags:
- [ ] Large cycle-to-cycle variation (>15°)
- [ ] Significant left/right asymmetry (>15°)
- [ ] Limited knee flexion (<15° range)
- [ ] Minimal ankle movement (<10° range)
- [ ] Inconsistent phase timing

---

## 💡 Use Cases

### Compare Cycles
```csv
cycle,phase,knee_angle_deg
1,landing,165.2
2,landing,164.8
3,landing,166.1
→ Check consistency
```

### Compare Sides
```csv
side,phase,knee_angle_deg
left,landing,165.2
right,landing,168.5
→ Check symmetry (3.3° difference)
```

### Track Progress
```csv
session,phase,knee_angle_deg
Week1,landing,160.2
Week4,landing,165.5
→ Improvement in landing mechanics
```

---

## 🚀 Getting Started

1. **Process your video** through the annotation tool
2. **Open** `phase_timeline_*.png` to verify accurate detection
3. **Review** `summary_report_*.txt` for detailed breakdown
4. **Analyze** `phase_analysis_*.csv` in Excel for deeper insights
5. **Compare** left vs right, cycle to cycle, or session to session

---

## 📈 Example CSV Analysis (Excel)

### Create Pivot Table:
- **Rows**: Phase (Landing, Mid-Stance, Push-Off)
- **Columns**: Side (Left, Right)
- **Values**: Average of knee_angle_deg
- **Result**: Quick symmetry comparison

### Create Charts:
- **Line chart**: Knee angle across cycles by phase
- **Bar chart**: Average angles per phase
- **Scatter**: Knee vs hip angle at landing

---

## 🎓 Key Insights to Extract

1. **Landing Mechanics**
   - Is knee angle sufficient for shock absorption?
   - Are left/right landing angles symmetric?

2. **Stance Stability**
   - Does knee flex adequately at mid-stance?
   - Is hip position stable?

3. **Push-Off Power**
   - Is ankle plantarflexion strong?
   - Is knee extending properly?

4. **Movement Consistency**
   - Do angles stay consistent across cycles?
   - Is timing regular?

5. **Side-to-Side Balance**
   - Are left/right mechanics similar?
   - Any compensations visible?

---

## ⚡ Pro Tips

- **Focus on mid-stance** for injury risk assessment
- **Compare landing angles** between left/right for asymmetry
- **Track push-off power** with ankle angle + velocity
- **Monitor consistency** across cycles for fatigue detection
- **Use visualizations first**, then dive into CSV data

---

**Need Help?** See `PHASE_ANALYSIS_GUIDE.md` for comprehensive documentation.
