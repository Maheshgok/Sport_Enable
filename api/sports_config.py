"""
Sports Configuration
Defines all sport-specific settings, baselines, and analysis parameters
"""

SPORTS_CONFIG = {
    "football": {
        "sport_id": "football",
        "name": "Football/Soccer",
        "description": "Football/Soccer motion analysis",
        "is_active": True,
        
        "video_types": [
            {
                "id": "free_kick",
                "name": "Free Kick",
                "description": "Player performing a free kick",
                "required_views": ["front", "side"],
                "duration_seconds": 10,
                "instructions": "Capture the full free kick motion from approach to follow-through"
            },
            {
                "id": "sprint",
                "name": "Sprint",
                "description": "Player sprinting",
                "required_views": ["side"],
                "duration_seconds": 5,
                "instructions": "Capture 5 seconds of maximal sprinting from side view"
            },
            {
                "id": "dribbling",
                "name": "Dribbling",
                "description": "Player dribbling through cones",
                "required_views": ["front", "top"],
                "duration_seconds": 15,
                "instructions": "Capture dribbling through 5-6 cones"
            },
            {
                "id": "passing",
                "name": "Passing",
                "description": "Player making ground pass",
                "required_views": ["side"],
                "duration_seconds": 8,
                "instructions": "Capture passing motion with plant foot and follow-through"
            }
        ],
        
        "baseline_metrics": {
            "sprint_speed": {
                "name": "Sprint Speed",
                "min": 5.0,
                "max": 8.5,
                "optimal": 7.0,
                "unit": "m/s",
                "description": "Maximum sprint velocity"
            },
            "knee_flexion_angle": {
                "name": "Knee Flexion Angle",
                "min": 90,
                "max": 140,
                "optimal": 115,
                "unit": "degrees",
                "description": "Knee flexion during strike phase"
            },
            "hip_rotation": {
                "name": "Hip Rotation",
                "min": 30,
                "max": 60,
                "optimal": 45,
                "unit": "degrees",
                "description": "Hip rotation during kicking motion"
            },
            "ankle_dorsiflexion": {
                "name": "Ankle Dorsiflexion",
                "min": 15,
                "max": 25,
                "optimal": 20,
                "unit": "degrees",
                "description": "Ankle dorsiflexion during movement"
            },
            "plant_foot_distance": {
                "name": "Plant Foot Distance",
                "min": 10,
                "max": 30,
                "optimal": 20,
                "unit": "cm",
                "description": "Distance of plant foot from ball during kick"
            }
        },
        
        "analysis_parameters": {
            "track_joints": ["hip", "knee", "ankle", "shoulder", "elbow"],
            "detect_phases": ["approach", "plant", "strike", "follow_through"],
            "calculate_metrics": ["speed", "power", "balance", "symmetry", "timing"],
            "injury_risk_indicators": ["knee_valgus", "ankle_instability", "hip_asymmetry"]
        },
        
        "cloud_run_endpoint": "https://football-analysis-xxxxx.run.app",
        "positions": ["Forward", "Midfielder", "Defender", "Goalkeeper"]
    },
    
    "basketball": {
        "sport_id": "basketball",
        "name": "Basketball",
        "description": "Basketball motion analysis",
        "is_active": True,
        
        "video_types": [
            {
                "id": "jump_shot",
                "name": "Jump Shot",
                "description": "Player performing jump shot",
                "required_views": ["front", "side"],
                "duration_seconds": 8,
                "instructions": "Capture complete jump shot from set to landing"
            },
            {
                "id": "layup",
                "name": "Layup",
                "description": "Player performing layup",
                "required_views": ["side"],
                "duration_seconds": 5,
                "instructions": "Capture approach, jump, and layup motion"
            },
            {
                "id": "vertical_jump",
                "name": "Vertical Jump",
                "description": "Vertical jump test",
                "required_views": ["front", "side"],
                "duration_seconds": 3,
                "instructions": "Capture maximal vertical jump from standing position"
            },
            {
                "id": "defensive_slide",
                "name": "Defensive Slide",
                "description": "Lateral defensive movement",
                "required_views": ["front"],
                "duration_seconds": 10,
                "instructions": "Capture side-to-side defensive slides"
            }
        ],
        
        "baseline_metrics": {
            "vertical_jump_height": {
                "name": "Vertical Jump Height",
                "min": 40,
                "max": 80,
                "optimal": 60,
                "unit": "cm",
                "description": "Maximum vertical jump reach"
            },
            "elbow_angle_at_release": {
                "name": "Elbow Angle at Release",
                "min": 160,
                "max": 180,
                "optimal": 170,
                "unit": "degrees",
                "description": "Elbow extension angle at ball release"
            },
            "knee_flexion_depth": {
                "name": "Knee Flexion Depth",
                "min": 90,
                "max": 120,
                "optimal": 105,
                "unit": "degrees",
                "description": "Knee flexion during shot preparation"
            },
            "wrist_snap_angle": {
                "name": "Wrist Snap Angle",
                "min": 45,
                "max": 70,
                "optimal": 60,
                "unit": "degrees",
                "description": "Wrist flexion at release"
            },
            "shot_release_height": {
                "name": "Shot Release Height",
                "min": 200,
                "max": 280,
                "optimal": 240,
                "unit": "cm",
                "description": "Height of ball at release point"
            }
        },
        
        "analysis_parameters": {
            "track_joints": ["shoulder", "elbow", "wrist", "hip", "knee", "ankle"],
            "detect_phases": ["set", "dip", "jump", "release", "land"],
            "calculate_metrics": ["jump_height", "release_angle", "consistency", "landing_balance"],
            "injury_risk_indicators": ["landing_asymmetry", "knee_valgus", "ankle_instability"]
        },
        
        "cloud_run_endpoint": "https://basketball-analysis-xxxxx.run.app",
        "positions": ["Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"]
    },
    
    "running": {
        "sport_id": "running",
        "name": "Running/Athletics",
        "description": "Running gait and performance analysis",
        "is_active": True,
        
        "video_types": [
            {
                "id": "treadmill_run",
                "name": "Treadmill Running",
                "description": "Running on treadmill - side view",
                "required_views": ["side"],
                "duration_seconds": 30,
                "instructions": "Capture 30 seconds of steady-state running from side"
            },
            {
                "id": "outdoor_sprint",
                "name": "Outdoor Sprint",
                "description": "Sprint on track",
                "required_views": ["side", "front"],
                "duration_seconds": 10,
                "instructions": "Capture 100m sprint from side and front angles"
            },
            {
                "id": "gait_analysis",
                "name": "Gait Analysis",
                "description": "Walking gait assessment",
                "required_views": ["side", "front", "back"],
                "duration_seconds": 20,
                "instructions": "Capture normal walking pace from multiple angles"
            }
        ],
        
        "baseline_metrics": {
            "cadence": {
                "name": "Cadence",
                "min": 160,
                "max": 190,
                "optimal": 175,
                "unit": "steps/min",
                "description": "Steps per minute"
            },
            "stride_length": {
                "name": "Stride Length",
                "min": 1.2,
                "max": 2.0,
                "optimal": 1.6,
                "unit": "m",
                "description": "Distance covered per stride"
            },
            "knee_drive": {
                "name": "Knee Drive",
                "min": 70,
                "max": 100,
                "optimal": 85,
                "unit": "degrees",
                "description": "Maximum knee flexion during swing phase"
            },
            "ground_contact_time": {
                "name": "Ground Contact Time",
                "min": 180,
                "max": 250,
                "optimal": 200,
                "unit": "ms",
                "description": "Time foot is in contact with ground"
            },
            "vertical_oscillation": {
                "name": "Vertical Oscillation",
                "min": 6,
                "max": 12,
                "optimal": 8,
                "unit": "cm",
                "description": "Vertical movement of center of mass"
            }
        },
        
        "analysis_parameters": {
            "track_joints": ["hip", "knee", "ankle", "shoulder"],
            "detect_phases": ["heel_strike", "stance", "toe_off", "swing"],
            "calculate_metrics": ["cadence", "stride_length", "flight_time", "symmetry", "ground_contact_time"],
            "injury_risk_indicators": ["overstriding", "crossover_gait", "excessive_pronation", "asymmetry"]
        },
        
        "cloud_run_endpoint": "https://running-analysis-xxxxx.run.app",
        "positions": ["Sprinter", "Middle Distance", "Long Distance", "Marathon"]
    },
    
    "cricket": {
        "sport_id": "cricket",
        "name": "Cricket",
        "description": "Cricket bowling and batting analysis",
        "is_active": True,
        
        "video_types": [
            {
                "id": "bowling",
                "name": "Bowling Action",
                "description": "Bowler's delivery stride",
                "required_views": ["front", "side"],
                "duration_seconds": 8,
                "instructions": "Capture complete bowling action from run-up to follow-through"
            },
            {
                "id": "batting",
                "name": "Batting",
                "description": "Batsman playing a shot",
                "required_views": ["front", "side"],
                "duration_seconds": 5,
                "instructions": "Capture batting stroke from setup to follow-through"
            }
        ],
        
        "baseline_metrics": {
            "shoulder_rotation": {
                "name": "Shoulder Rotation",
                "min": 90,
                "max": 180,
                "optimal": 135,
                "unit": "degrees",
                "description": "Shoulder rotation during delivery"
            },
            "elbow_extension": {
                "name": "Elbow Extension",
                "min": 150,
                "max": 180,
                "optimal": 165,
                "unit": "degrees",
                "description": "Elbow angle at ball release (for legal action)"
            },
            "hip_rotation": {
                "name": "Hip Rotation",
                "min": 60,
                "max": 100,
                "optimal": 80,
                "unit": "degrees",
                "description": "Hip rotation during delivery stride"
            }
        },
        
        "analysis_parameters": {
            "track_joints": ["shoulder", "elbow", "wrist", "hip", "knee", "ankle"],
            "detect_phases": ["run_up", "bound", "delivery", "follow_through"],
            "calculate_metrics": ["release_speed", "elbow_angle", "shoulder_rotation", "hip_alignment"],
            "injury_risk_indicators": ["excessive_elbow_flexion", "shoulder_impingement", "back_hyperextension"]
        },
        
        "cloud_run_endpoint": "https://cricket-analysis-xxxxx.run.app",
        "positions": ["Fast Bowler", "Spin Bowler", "Batsman", "All-rounder", "Wicket Keeper"]
    }
}

def get_sport_config(sport_id):
    """Get configuration for a specific sport"""
    return SPORTS_CONFIG.get(sport_id)

def get_all_sports():
    """Get all active sports"""
    return {k: v for k, v in SPORTS_CONFIG.items() if v.get('is_active', True)}

def get_video_types_for_sport(sport_id):
    """Get all video types for a sport"""
    sport = get_sport_config(sport_id)
    return sport['video_types'] if sport else []

def get_baseline_metrics_for_sport(sport_id):
    """Get baseline metrics for a sport"""
    sport = get_sport_config(sport_id)
    return sport['baseline_metrics'] if sport else {}

def validate_video_type(sport_id, video_type_id):
    """Check if video type is valid for sport"""
    video_types = get_video_types_for_sport(sport_id)
    return any(vt['id'] == video_type_id for vt in video_types)
