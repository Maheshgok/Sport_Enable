# Sport-Specific Analysis Architecture

## Overview

This document outlines the architecture for sport-specific motion analysis, where each sport has:
- **Different baselines** - Sport-specific performance standards
- **Different video types** - Sport-specific movements to analyze
- **Different analysis functions** - Separate Cloud Run function per sport
- **Different reports** - Parametric reports prescribed by physiotherapist
- **PDF generation** - Common markdown-to-PDF converter

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  - Sport selection during athlete profile creation              │
│  - Video upload based on sport + role                           │
│  - PDF report viewer                                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Flask)                         │
│  - Authentication & Authorization                                │
│  - Route videos to appropriate Cloud Run function               │
│  - Store results in database                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├──────────┬──────────┬──────────┬──────────┐
                 ▼          ▼          ▼          ▼          ▼
      ┌──────────────┬──────────────┬──────────────┬──────────────┐
      │   Football   │   Basketball │    Running   │    Cricket   │
      │  Analysis    │   Analysis   │   Analysis   │   Analysis   │
      │  Cloud Run   │  Cloud Run   │  Cloud Run   │  Cloud Run   │
      └──────────────┴──────────────┴──────────────┴──────────────┘
                 │          │          │          │
                 └──────────┴──────────┴──────────┴──────────────┐
                                                                  ▼
                                                   ┌────────────────────┐
                                                   │  Report Generator  │
                                                   │  (Markdown → PDF)  │
                                                   └────────────────────┘
```

---

## 1. Sport Configuration System

### 1.1 Sport Definitions

Each sport has:
- **Sport ID** - Unique identifier
- **Display Name** - User-facing name
- **Video Types** - Required video captures
- **Baseline Metrics** - Sport-specific performance standards
- **Analysis Parameters** - What to measure and report
- **Cloud Run Endpoint** - Dedicated analysis function

### 1.2 Sport Configuration Structure

```python
SPORTS_CONFIG = {
    "football": {
        "name": "Football/Soccer",
        "video_types": [
            {
                "id": "free_kick",
                "name": "Free Kick",
                "description": "Player performing a free kick",
                "required_views": ["front", "side"],
                "duration_seconds": 10
            },
            {
                "id": "sprint",
                "name": "Sprint",
                "description": "Player sprinting",
                "required_views": ["side"],
                "duration_seconds": 5
            },
            {
                "id": "dribbling",
                "name": "Dribbling",
                "description": "Player dribbling through cones",
                "required_views": ["front", "top"],
                "duration_seconds": 15
            }
        ],
        "baseline_metrics": {
            "sprint_speed": {"min": 5.0, "max": 8.5, "unit": "m/s"},
            "knee_flexion_angle": {"min": 90, "max": 140, "unit": "degrees"},
            "hip_rotation": {"min": 30, "max": 60, "unit": "degrees"},
            "ankle_dorsiflexion": {"min": 15, "max": 25, "unit": "degrees"}
        },
        "analysis_parameters": {
            "track_joints": ["hip", "knee", "ankle", "shoulder"],
            "detect_phases": ["approach", "plant", "strike", "follow_through"],
            "calculate_metrics": ["speed", "power", "balance", "symmetry"]
        },
        "cloud_run_endpoint": "https://football-analysis-xxxxx.run.app"
    },
    
    "basketball": {
        "name": "Basketball",
        "video_types": [
            {
                "id": "jump_shot",
                "name": "Jump Shot",
                "description": "Player performing jump shot",
                "required_views": ["front", "side"],
                "duration_seconds": 8
            },
            {
                "id": "layup",
                "name": "Layup",
                "description": "Player performing layup",
                "required_views": ["side"],
                "duration_seconds": 5
            },
            {
                "id": "vertical_jump",
                "name": "Vertical Jump",
                "description": "Vertical jump test",
                "required_views": ["front", "side"],
                "duration_seconds": 3
            }
        ],
        "baseline_metrics": {
            "vertical_jump_height": {"min": 40, "max": 80, "unit": "cm"},
            "elbow_angle_at_release": {"min": 160, "max": 180, "unit": "degrees"},
            "knee_flexion_depth": {"min": 90, "max": 120, "unit": "degrees"},
            "wrist_snap_angle": {"min": 45, "max": 70, "unit": "degrees"}
        },
        "analysis_parameters": {
            "track_joints": ["shoulder", "elbow", "wrist", "knee", "ankle"],
            "detect_phases": ["set", "dip", "jump", "release", "land"],
            "calculate_metrics": ["jump_height", "release_angle", "consistency"]
        },
        "cloud_run_endpoint": "https://basketball-analysis-xxxxx.run.app"
    },
    
    "running": {
        "name": "Running/Athletics",
        "video_types": [
            {
                "id": "treadmill_run",
                "name": "Treadmill Running",
                "description": "Running on treadmill - side view",
                "required_views": ["side"],
                "duration_seconds": 30
            },
            {
                "id": "outdoor_sprint",
                "name": "Outdoor Sprint",
                "description": "Sprint on track",
                "required_views": ["side", "front"],
                "duration_seconds": 10
            }
        ],
        "baseline_metrics": {
            "cadence": {"min": 160, "max": 190, "unit": "steps/min"},
            "stride_length": {"min": 1.2, "max": 2.0, "unit": "m"},
            "knee_drive": {"min": 70, "max": 100, "unit": "degrees"},
            "ground_contact_time": {"min": 180, "max": 250, "unit": "ms"}
        },
        "analysis_parameters": {
            "track_joints": ["hip", "knee", "ankle"],
            "detect_phases": ["stance", "toe_off", "swing", "heel_strike"],
            "calculate_metrics": ["cadence", "stride_length", "flight_time", "symmetry"]
        },
        "cloud_run_endpoint": "https://running-analysis-xxxxx.run.app"
    },
    
    "cricket": {
        "name": "Cricket",
        "video_types": [
            {
                "id": "bowling",
                "name": "Bowling Action",
                "description": "Bowler's delivery stride",
                "required_views": ["front", "side"],
                "duration_seconds": 8
            },
            {
                "id": "batting",
                "name": "Batting",
                "description": "Batsman playing a shot",
                "required_views": ["front", "side"],
                "duration_seconds": 5
            }
        ],
        "baseline_metrics": {
            "shoulder_rotation": {"min": 90, "max": 180, "unit": "degrees"},
            "elbow_extension": {"min": 150, "max": 180, "unit": "degrees"},
            "hip_rotation": {"min": 60, "max": 100, "unit": "degrees"}
        },
        "analysis_parameters": {
            "track_joints": ["shoulder", "elbow", "wrist", "hip", "knee"],
            "detect_phases": ["run_up", "bound", "delivery", "follow_through"],
            "calculate_metrics": ["release_speed", "elbow_angle", "shoulder_rotation"]
        },
        "cloud_run_endpoint": "https://cricket-analysis-xxxxx.run.app"
    }
}
```

---

## 2. Database Schema Extensions

### 2.1 Sports Configuration Table

```sql
-- Sports master table
CREATE TABLE physio_app.sports (
  sport_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  configuration JSONB NOT NULL, -- Full sport config
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Video types per sport
CREATE TABLE physio_app.sport_video_types (
  video_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sport_id VARCHAR(50) REFERENCES physio_app.sports(sport_id),
  type_code VARCHAR(50) NOT NULL, -- e.g., 'free_kick', 'jump_shot'
  name VARCHAR(100) NOT NULL,
  description TEXT,
  required_views TEXT[], -- ['front', 'side', 'top']
  duration_seconds INTEGER,
  configuration JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Baseline metrics per sport
CREATE TABLE physio_app.sport_baselines (
  baseline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sport_id VARCHAR(50) REFERENCES physio_app.sports(sport_id),
  metric_name VARCHAR(100) NOT NULL,
  metric_type VARCHAR(50), -- 'angle', 'speed', 'distance', 'time'
  min_value DECIMAL(10,2),
  max_value DECIMAL(10,2),
  optimal_value DECIMAL(10,2),
  unit VARCHAR(20),
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 Athlete Profile Enhancement

```sql
-- Add sport to athlete profile
ALTER TABLE physio_app.athlete_profiles
ADD COLUMN sport_id VARCHAR(50) REFERENCES physio_app.sports(sport_id),
ADD COLUMN position_specific_data JSONB,
ADD COLUMN baseline_assessment_date DATE,
ADD COLUMN custom_baselines JSONB; -- Athlete-specific overrides
```

### 2.3 Video Analysis Records

```sql
-- Video analysis sessions
CREATE TABLE physio_app.video_analyses (
  analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID REFERENCES physio_app.athlete_profiles(athlete_id),
  uploaded_by UUID REFERENCES physio_app.users(user_id),
  sport_id VARCHAR(50) REFERENCES physio_app.sports(sport_id),
  video_type_id UUID REFERENCES physio_app.sport_video_types(video_type_id),
  
  -- Video files
  video_urls JSONB, -- {"front": "gs://...", "side": "gs://..."}
  
  -- Processing
  status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
  cloud_run_endpoint VARCHAR(500),
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,
  
  -- Results
  results JSONB, -- Full analysis results
  report_url VARCHAR(500), -- URL to generated PDF
  
  -- Metadata
  athlete_height_cm DECIMAL(5,2),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Analysis metrics (individual measurements)
CREATE TABLE physio_app.analysis_metrics (
  metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID REFERENCES physio_app.video_analyses(analysis_id),
  metric_name VARCHAR(100) NOT NULL,
  measured_value DECIMAL(10,2),
  baseline_value DECIMAL(10,2),
  deviation_percent DECIMAL(5,2),
  unit VARCHAR(20),
  is_within_baseline BOOLEAN,
  severity VARCHAR(20), -- normal, concern, warning, critical
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 3. Cloud Run Function Architecture

### 3.1 Function Structure

Each sport has a dedicated Cloud Run function:

```
/cloud-functions/
  ├── football-analysis/
  │   ├── main.py           # Entry point
  │   ├── analyzer.py       # Sport-specific analysis
  │   ├── baseline.json     # Football baselines
  │   ├── requirements.txt
  │   └── Dockerfile
  │
  ├── basketball-analysis/
  │   ├── main.py
  │   ├── analyzer.py
  │   ├── baseline.json
  │   ├── requirements.txt
  │   └── Dockerfile
  │
  ├── running-analysis/
  │   └── ...
  │
  └── cricket-analysis/
      └── ...
```

### 3.2 Common Base Class

```python
# base_analyzer.py (shared by all sport functions)
class BaseSportAnalyzer:
    def __init__(self, sport_config):
        self.sport = sport_config['sport_id']
        self.baselines = sport_config['baseline_metrics']
        self.analysis_params = sport_config['analysis_parameters']
        
    def process_video(self, video_url, video_type, athlete_data):
        """Main processing pipeline"""
        # 1. Download video from GCS
        video_path = self.download_video(video_url)
        
        # 2. Extract pose landmarks
        landmarks = self.extract_pose(video_path)
        
        # 3. Sport-specific analysis
        analysis = self.analyze_movement(landmarks, video_type)
        
        # 4. Compare to baselines
        comparison = self.compare_to_baseline(analysis, athlete_data)
        
        # 5. Generate insights
        insights = self.generate_insights(comparison)
        
        # 6. Create report data
        report_data = self.create_report_data(analysis, comparison, insights)
        
        return report_data
    
    def analyze_movement(self, landmarks, video_type):
        """Sport-specific analysis - Override in subclass"""
        raise NotImplementedError
    
    def compare_to_baseline(self, analysis, athlete_data):
        """Compare metrics to sport baselines"""
        comparison = {}
        for metric_name, measured_value in analysis.items():
            if metric_name in self.baselines:
                baseline = self.baselines[metric_name]
                deviation = self.calculate_deviation(
                    measured_value, 
                    baseline['min'], 
                    baseline['max']
                )
                comparison[metric_name] = {
                    'measured': measured_value,
                    'baseline_min': baseline['min'],
                    'baseline_max': baseline['max'],
                    'deviation': deviation,
                    'status': self.get_status(deviation),
                    'unit': baseline['unit']
                }
        return comparison
```

### 3.3 Football-Specific Analyzer Example

```python
# football-analysis/analyzer.py
from base_analyzer import BaseSportAnalyzer

class FootballAnalyzer(BaseSportAnalyzer):
    def analyze_movement(self, landmarks, video_type):
        """Football-specific analysis"""
        if video_type == 'free_kick':
            return self.analyze_free_kick(landmarks)
        elif video_type == 'sprint':
            return self.analyze_sprint(landmarks)
        elif video_type == 'dribbling':
            return self.analyze_dribbling(landmarks)
    
    def analyze_free_kick(self, landmarks):
        """Analyze free kick technique"""
        # Detect phases
        phases = self.detect_kick_phases(landmarks)
        
        # Calculate metrics
        metrics = {
            'approach_angle': self.calculate_approach_angle(phases['approach']),
            'plant_foot_distance': self.calculate_plant_distance(phases['plant']),
            'knee_flexion': self.calculate_knee_angle(phases['strike']),
            'hip_rotation': self.calculate_hip_rotation(phases),
            'follow_through_height': self.calculate_follow_through(phases)
        }
        
        return metrics
    
    def analyze_sprint(self, landmarks):
        """Analyze sprinting mechanics"""
        return {
            'sprint_speed': self.calculate_speed(landmarks),
            'stride_length': self.calculate_stride_length(landmarks),
            'knee_drive': self.calculate_knee_drive(landmarks),
            'arm_swing': self.calculate_arm_swing(landmarks)
        }
```

---

## 4. Report Generation System

### 4.1 Report Structure

Each analysis generates a structured report:

```python
REPORT_TEMPLATE = {
    "athlete_info": {
        "name": "",
        "sport": "",
        "position": "",
        "date": ""
    },
    "executive_summary": {
        "overall_status": "",  # Excellent, Good, Needs Attention, Critical
        "key_findings": [],
        "recommendations": []
    },
    "motion_analysis": {
        "video_type": "",
        "phases_detected": [],
        "metrics": []
    },
    "parametric_analysis": {
        # Physiotherapist-defined parameters
        "rom_analysis": {},      # Range of Motion
        "strength_indicators": {},
        "asymmetry_detection": {},
        "injury_risk_markers": {}
    },
    "baseline_comparison": {
        "metrics": []  # Each with deviation from baseline
    },
    "visualizations": {
        "charts": [],
        "annotated_frames": []
    },
    "physiotherapist_notes": {
        "prescribing_physio": "",
        "specific_parameters": [],
        "focus_areas": []
    },
    "recommendations": {
        "immediate_actions": [],
        "rehabilitation_exercises": [],
        "follow_up_timeline": ""
    }
}
```

### 4.2 Markdown to PDF Converter

```python
# report_generator.py (Common service)
import markdown
import pdfkit
from jinja2 import Template

class ReportGenerator:
    def __init__(self):
        self.template = self.load_template()
    
    def generate_pdf(self, analysis_data, athlete_data, sport_config):
        """Generate PDF report from analysis data"""
        
        # 1. Create markdown content
        markdown_content = self.create_markdown(
            analysis_data, 
            athlete_data, 
            sport_config
        )
        
        # 2. Convert to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # 3. Apply template
        templated_html = self.template.render(
            content=html_content,
            athlete=athlete_data,
            sport=sport_config['name'],
            date=datetime.now()
        )
        
        # 4. Convert to PDF
        pdf_bytes = pdfkit.from_string(
            templated_html,
            False,  # Return bytes instead of file
            options=self.get_pdf_options()
        )
        
        # 5. Upload to GCS
        pdf_url = self.upload_to_gcs(pdf_bytes, analysis_data['analysis_id'])
        
        return pdf_url
    
    def create_markdown(self, analysis_data, athlete_data, sport_config):
        """Create markdown report"""
        md = f"""
# Motion Analysis Report
## {athlete_data['name']} - {sport_config['name']}

**Date:** {analysis_data['date']}  
**Video Type:** {analysis_data['video_type']}  
**Analyzed By:** Moove AI Platform

---

## Executive Summary

**Overall Status:** {analysis_data['overall_status']}

### Key Findings
{self.format_findings(analysis_data['key_findings'])}

---

## Motion Analysis

### Detected Phases
{self.format_phases(analysis_data['phases'])}

### Measured Metrics

| Metric | Measured | Baseline Range | Status |
|--------|----------|----------------|--------|
{self.format_metrics_table(analysis_data['metrics'])}

---

## Baseline Comparison

![Metrics Chart](data:image/png;base64,{analysis_data['chart_base64']})

{self.format_deviations(analysis_data['deviations'])}

---

## Parametric Analysis

### Range of Motion (ROM)
{self.format_rom_analysis(analysis_data['rom'])}

### Asymmetry Detection
{self.format_asymmetry(analysis_data['asymmetry'])}

---

## Recommendations

### Priority Actions
{self.format_recommendations(analysis_data['recommendations'])}

### Rehabilitation Exercises
{self.format_exercises(analysis_data['exercises'])}

---

*Report generated by Moove AI Platform*  
*For medical decisions, please consult with a qualified healthcare professional*
"""
        return md
```

---

## 5. Integration with Login System

### 5.1 Role-Based Video Upload

```python
# Role determines which video types they can upload
ROLE_PERMISSIONS = {
    "athlete": {
        "can_upload": True,
        "can_view_own": True,
        "can_view_others": False
    },
    "physiotherapist": {
        "can_upload": True,
        "can_view_own": False,
        "can_view_others": True,
        "can_prescribe_analysis": True
    },
    "coach": {
        "can_upload": True,
        "can_view_own": False,
        "can_view_assigned": True
    },
    "admin": {
        "can_upload": True,
        "can_view_all": True,
        "can_manage_sports": True
    }
}
```

### 5.2 API Endpoint Updates

```python
@app.route('/api/upload-analysis-video', methods=['POST'])
@require_auth(roles=['athlete', 'physiotherapist', 'coach'])
def upload_analysis_video():
    """Upload video for sport-specific analysis"""
    current_user = request.current_user
    
    # Get athlete sport
    athlete_id = request.form.get('athlete_id')
    athlete = get_athlete_with_sport(athlete_id)
    
    # Get sport config
    sport_config = SPORTS_CONFIG[athlete['sport_id']]
    
    # Validate video type
    video_type = request.form.get('video_type')
    if video_type not in [vt['id'] for vt in sport_config['video_types']]:
        return jsonify({'error': 'Invalid video type for this sport'}), 400
    
    # Upload videos
    videos = upload_videos_to_gcs(request.files)
    
    # Create analysis record
    analysis_id = create_analysis_record(
        athlete_id, 
        sport_config['sport_id'],
        video_type,
        videos
    )
    
    # Trigger appropriate Cloud Run function
    trigger_analysis(
        cloud_run_endpoint=sport_config['cloud_run_endpoint'],
        analysis_id=analysis_id,
        videos=videos,
        athlete_data=athlete
    )
    
    return jsonify({
        'success': True,
        'analysis_id': analysis_id,
        'status': 'processing'
    })
```

---

## 6. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- ✅ Login system (already done)
- [ ] Add sport selection to athlete profiles
- [ ] Create sports configuration table
- [ ] Update database schema

### Phase 2: Sport Configuration (Week 3)
- [ ] Define all sport configurations
- [ ] Create baseline metrics for each sport
- [ ] Define video types per sport
- [ ] Build admin UI for sport management

### Phase 3: Cloud Functions (Week 4-5)
- [ ] Create base analyzer class
- [ ] Implement football analyzer
- [ ] Implement basketball analyzer
- [ ] Deploy to Cloud Run
- [ ] Test each function

### Phase 4: Report Generation (Week 6)
- [ ] Build markdown report generator
- [ ] Implement PDF converter
- [ ] Create report templates
- [ ] Test PDF generation

### Phase 5: Integration (Week 7)
- [ ] Update API endpoints
- [ ] Build frontend upload UI
- [ ] Implement report viewer
- [ ] End-to-end testing

### Phase 6: Additional Sports (Week 8+)
- [ ] Add running analysis
- [ ] Add cricket analysis
- [ ] Add tennis, swimming, etc.

---

## 7. Cost Considerations

### Cloud Run Pricing (per sport function)
- **CPU:** 1 vCPU @ $0.00002400/vCPU-second
- **Memory:** 2 GB @ $0.00000250/GB-second
- **Requests:** $0.40 per million requests
- **Estimated:** ~$0.10-0.50 per video analysis

### Storage Costs
- **Video Storage:** ~$0.02/GB/month
- **Report PDFs:** ~$0.01/GB/month

### Total Estimated Cost
- **100 analyses/day:** ~$15-30/day = $450-900/month
- **Scalable:** Pay only for what you use

---

## Next Steps

1. **Decide on initial sports** - Which sports to support first?
2. **Define baseline metrics** - Work with physiotherapists to define proper baselines
3. **Create sport configs** - Implement the SPORTS_CONFIG structure
4. **Update database** - Add sport tables and athlete sport selection
5. **Build first analyzer** - Start with one sport (e.g., football)
6. **Test end-to-end** - Upload → analyze → report → PDF

Would you like me to start implementing any specific part of this architecture?
