-- ============================================
-- Seed Assessment Prompts Database
-- Predefined clinical assessment templates
-- ============================================

SET search_path TO physio_app, public;

-- Insert predefined assessment prompts
INSERT INTO assessment_prompts (
  prompt_code, prompt_name, clinical_category, description,
  target_population, estimated_duration_minutes,
  clinical_indications, contraindications, preparation_instructions,
  video_instructions, required_views, duration_seconds, equipment_needed,
  analysis_config, baseline_metrics, risk_factors, report_template,
  based_on_evidence, created_by
) VALUES

-- SHOULDER ASSESSMENTS
(
  'shoulder_impingement',
  'Shoulder Impingement Assessment',
  'shoulder',
  'Comprehensive assessment for shoulder impingement syndrome during functional overhead movements',
  'athletes, overhead athletes, general population with shoulder pain',
  15,
  'Shoulder pain during overhead activities, suspected impingement, pre-season screening',
  'Acute shoulder injury, severe pain, recent surgery',
  'Ensure patient can perform overhead movements without severe pain. Have towel available if needed.',
  '{
    "setup": "Position camera 2m away at shoulder height, perpendicular to the movement plane",
    "athlete_instructions": [
      "Stand with arms relaxed at sides",
      "Slowly raise both arms forward and overhead",
      "Hold the overhead position for 2 seconds",
      "Slowly lower arms back to sides",
      "Repeat 3 times at comfortable speed"
    ],
    "physio_notes": "Observe for pain provocation, compensatory movements, or asymmetry"
  }',
  ARRAY['front', 'side'],
  30,
  ARRAY['none'],
  '{
    "joints_to_track": ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "neck"],
    "angles_to_measure": ["shoulder_elevation", "shoulder_horizontal_adduction", "elbow_extension"],
    "metrics_to_calculate": ["shoulder_asymmetry_index", "pain_provocation_score"],
    "movement_phases": ["resting", "elevation", "overhead_hold", "lowering"]
  }',
  '{
    "shoulder_elevation_max": {"male": {"min": 160, "max": 180}, "female": {"min": 155, "max": 175}},
    "shoulder_horizontal_adduction": {"min": -10, "max": 20},
    "elbow_extension": {"min": 170, "max": 180},
    "shoulder_asymmetry_index": {"max": 15}
  }',
  '{
    "impingement_risk": "shoulder_elevation > 170 AND shoulder_horizontal_adduction > 15",
    "asymmetry_concern": "shoulder_asymmetry_index > 15",
    "limited_elevation": "shoulder_elevation_max < 150",
    "pain_response": "pain_provocation_score > 3"
  }',
  '{
    "sections": [
      {"title": "Movement Quality", "fields": ["shoulder_elevation_max", "shoulder_asymmetry_index"]},
      {"title": "Risk Factors", "fields": ["impingement_risk", "asymmetry_concern"]},
      {"title": "Clinical Interpretation", "type": "free_text"}
    ],
    "summary_fields": ["overall_risk_level", "recommended_actions"]
  }',
  'Based on Hawkins-Kennedy test and clinical guidelines for shoulder impingement',
  NULL
),

(
  'knee_acl_risk',
  'ACL Injury Risk Assessment',
  'knee',
  'Dynamic assessment of lower extremity movement patterns associated with ACL injury risk',
  'young athletes, female athletes, athletes returning to sport',
  20,
  'Pre-season screening, return to play assessment, injury prevention programs',
  'Acute knee injury, severe knee pain, recent knee surgery',
  'Ensure proper warm-up. Patient should wear athletic clothing and athletic shoes.',
  '{
    "setup": "Position camera 3m away at knee height, capturing full body from front",
    "athlete_instructions": [
      "Stand on single leg (start with uninvolved side)",
      "Perform slow squat lowering body until knee is at 90 degrees",
      "Hold position for 2 seconds",
      "Return to standing",
      "Repeat 3 times per leg"
    ],
    "physio_notes": "Observe for dynamic knee valgus, hip internal rotation, or trunk displacement"
  }',
  ARRAY['front'],
  45,
  ARRAY['none'],
  '{
    "joints_to_track": ["left_knee", "right_knee", "left_hip", "right_hip", "left_ankle", "right_ankle"],
    "angles_to_measure": ["knee_flexion", "knee_valgus", "hip_internal_rotation", "trunk_lateral_flexion"],
    "metrics_to_calculate": ["knee_separation_distance", "trunk_displacement", "acl_risk_score"],
    "movement_phases": ["starting_position", "descent", "bottom_position", "ascent"]
  }',
  '{
    "knee_valgus_max": {"max": 8},
    "hip_internal_rotation": {"max": 15},
    "trunk_lateral_flexion": {"max": 10},
    "knee_separation_distance": {"min": 25},
    "acl_risk_score": {"max": 6}
  }',
  '{
    "high_acl_risk": "acl_risk_score > 6",
    "dynamic_valgus": "knee_valgus_max > 8",
    "hip_rotation": "hip_internal_rotation > 15",
    "trunk_instability": "trunk_lateral_flexion > 10",
    "knee_medial_collapse": "knee_separation_distance < 25"
  }',
  '{
    "sections": [
      {"title": "Movement Analysis", "fields": ["knee_valgus_max", "hip_internal_rotation", "trunk_lateral_flexion"]},
      {"title": "Risk Assessment", "fields": ["acl_risk_score", "high_acl_risk"]},
      {"title": "Recommendations", "type": "predefined_options"}
    ],
    "summary_fields": ["risk_level", "prevention_exercises"]
  }',
  'Based on Landing Error Scoring System (LESS) and ACL injury prevention research',
  NULL
),

-- HIP ASSESSMENTS
(
  'hip_flexor_tightness',
  'Hip Flexor Tightness Assessment',
  'hip',
  'Assessment of hip flexor muscle length and function',
  'runners, cyclists, sedentary individuals, athletes with lower back pain',
  10,
  'Suspected hip flexor tightness, lower back pain, running injuries',
  'Acute hip injury, severe hip pain',
  'Patient should be warmed up. Test both sides for comparison.',
  '{
    "setup": "Camera positioned to capture side view of patient",
    "athlete_instructions": [
      "Lie supine on examination table",
      "Bend one knee to 90 degrees with foot flat on table",
      "Slowly lift opposite knee toward chest",
      "Hold position while physio measures hip flexion angle",
      "Repeat on other side"
    ],
    "physio_notes": "Measure angle between thigh and table. Normal is 80-90 degrees."
  }',
  ARRAY['side'],
  20,
  ARRAY['examination_table', 'goniometer'],
  '{
    "joints_to_track": ["left_hip", "right_hip", "left_knee", "right_knee"],
    "angles_to_measure": ["hip_flexion", "knee_flexion"],
    "metrics_to_calculate": ["hip_flexor_length_ratio"],
    "movement_phases": ["starting_position", "end_range"]
  }',
  '{
    "hip_flexion_max": {"min": 80, "max": 120},
    "hip_flexor_length_ratio": {"min": 0.9, "max": 1.1}
  }',
  '{
    "tight_hip_flexors": "hip_flexion_max < 80",
    "asymmetry": "hip_flexor_length_ratio < 0.9 OR hip_flexor_length_ratio > 1.1"
  }',
  '{
    "sections": [
      {"title": "Range of Motion", "fields": ["hip_flexion_max_left", "hip_flexion_max_right"]},
      {"title": "Symmetry Analysis", "fields": ["hip_flexor_length_ratio"]},
      {"title": "Clinical Findings", "type": "free_text"}
    ],
    "summary_fields": ["tightness_level", "stretching_recommendations"]
  }',
  'Based on Thomas test and hip flexor length assessment protocols',
  NULL
),

-- SPINE ASSESSMENTS
(
  'lumbar_spine_mobility',
  'Lumbar Spine Mobility Assessment',
  'spine',
  'Assessment of lumbar spine flexion and extension mobility',
  'general population, athletes with back pain, pre-habilitation programs',
  12,
  'Back pain assessment, mobility screening, functional movement evaluation',
  'Acute back injury, severe pain, recent spinal surgery',
  'Ensure patient is warmed up. Perform on firm surface.',
  '{
    "setup": "Camera positioned to capture side view of full spine",
    "athlete_instructions": [
      "Stand with feet shoulder-width apart",
      "Slowly bend forward from hips, reaching toward floor",
      "Hold forward bend position for 2 seconds",
      "Slowly return to upright position",
      "Then bend backward gently",
      "Hold backward bend for 2 seconds"
    ],
    "physio_notes": "Observe for smooth movement, pain provocation, or compensatory patterns"
  }',
  ARRAY['side'],
  25,
  ARRAY['none'],
  '{
    "joints_to_track": ["left_hip", "right_hip", "neck"],
    "angles_to_measure": ["lumbar_flexion", "lumbar_extension", "hip_flexion"],
    "metrics_to_calculate": ["flexion_extension_ratio", "total_lumbar_mobility"],
    "movement_phases": ["neutral", "full_flexion", "full_extension"]
  }',
  '{
    "lumbar_flexion_max": {"min": 60, "max": 90},
    "lumbar_extension_max": {"min": 20, "max": 40},
    "flexion_extension_ratio": {"min": 1.5, "max": 4.5},
    "total_lumbar_mobility": {"min": 80, "max": 130}
  }',
  '{
    "reduced_flexion": "lumbar_flexion_max < 60",
    "reduced_extension": "lumbar_extension_max < 20",
    "imbalanced_mobility": "flexion_extension_ratio < 1.5 OR flexion_extension_ratio > 4.5",
    "hypomobility": "total_lumbar_mobility < 80"
  }',
  '{
    "sections": [
      {"title": "Range of Motion", "fields": ["lumbar_flexion_max", "lumbar_extension_max", "total_lumbar_mobility"]},
      {"title": "Movement Quality", "fields": ["flexion_extension_ratio"]},
      {"title": "Clinical Assessment", "type": "free_text"}
    ],
    "summary_fields": ["mobility_classification", "exercise_recommendations"]
  }',
  'Based on modified Schober test and lumbar mobility assessment protocols',
  NULL
);

-- Insert categories
INSERT INTO prompt_categories (category_name, description, display_order) VALUES
('Shoulder', 'Shoulder and upper extremity assessments', 1),
('Knee', 'Knee and lower extremity assessments', 2),
('Hip', 'Hip and pelvic girdle assessments', 3),
('Spine', 'Spinal mobility and function assessments', 4),
('Ankle', 'Ankle and foot assessments', 5),
('Elbow', 'Elbow and forearm assessments', 6),
('Wrist', 'Wrist and hand assessments', 7),
('Screening', 'General movement screening assessments', 8);

-- Map prompts to categories
INSERT INTO prompt_category_mappings (prompt_id, category_id)
SELECT p.prompt_id, c.category_id
FROM assessment_prompts p
CROSS JOIN prompt_categories c
WHERE (p.clinical_category = 'shoulder' AND c.category_name = 'Shoulder')
   OR (p.clinical_category = 'knee' AND c.category_name = 'Knee')
   OR (p.clinical_category = 'hip' AND c.category_name = 'Hip')
   OR (p.clinical_category = 'spine' AND c.category_name = 'Spine');