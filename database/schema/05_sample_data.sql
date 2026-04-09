-- ============================================
-- Sample Data for Development & Testing
-- Schema: physio_app
-- Description: Seed data matching the mock data from the frontend
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. SAMPLE USERS
-- ============================================

-- Create users (password: 'password123' - bcrypt hash shown below is example)
INSERT INTO users (user_id, email, password_hash, roles, first_name, last_name, date_of_birth, gender, status) VALUES
-- Athlete
('a1111111-1111-1111-1111-111111111111', 'sarah.johnson@example.com', '$2a$10$examplehash', ARRAY['athlete'], 'Sarah', 'Johnson', '1998-05-15', 'Female', 'active'),

-- Physiotherapist
('b1111111-1111-1111-1111-111111111111', 'dr.smith@physio.com', '$2a$10$examplehash', ARRAY['physiotherapist'], 'David', 'Smith', '1985-08-22', 'Male', 'active'),

-- Coach
('c1111111-1111-1111-1111-111111111111', 'coach.brown@sports.com', '$2a$10$examplehash', ARRAY['coach'], 'Michael', 'Brown', '1980-03-10', 'Male', 'active'),

-- Caretaker
('d1111111-1111-1111-1111-111111111111', 'mary.care@example.com', '$2a$10$examplehash', ARRAY['caretaker'], 'Mary', 'Williams', '1990-11-28', 'Female', 'active');

-- ============================================
-- 2. ATHLETE PROFILE
-- ============================================
INSERT INTO athlete_profiles (athlete_id, user_id, sport, position, team, level, current_injury, injury_date, injury_type, injury_severity, recovery_timeline, status) VALUES
('aa111111-1111-1111-1111-111111111111', 'a1111111-1111-1111-1111-111111111111', 
 'Basketball', 'Point Guard', 'University Tigers', 'collegiate',
 'ACL Tear', '2026-02-01', 'Ligament', 'severe',
 '8-12 weeks', 'recovering');

-- ============================================
-- 3. PROFESSIONAL PROFILES
-- ============================================

-- Physiotherapist
INSERT INTO physiotherapist_profiles (physiotherapist_id, user_id, license_number, specializations, certifications, max_caseload, timezone) VALUES
('bb111111-1111-1111-1111-111111111111', 'b1111111-1111-1111-1111-111111111111',
 'PT-2024-5678', 
 ARRAY['Sports Medicine', 'Orthopedics', 'ACL Rehabilitation'],
 ARRAY['CSCS', 'OCS', 'SCS'],
 15, 'Asia/Kolkata');

-- Coach
INSERT INTO coach_profiles (coach_id, user_id, sport, specialization, years_experience, max_athletes) VALUES
('cc111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111',
 'Basketball', 'Strength & Conditioning', 12, 20);

-- Caretaker
INSERT INTO caretaker_profiles (caretaker_id, user_id, caretaker_type, certifications, max_athletes, timezone) VALUES
('cd111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111',
 'nurse', ARRAY['RN', 'CPR', 'First Aid'], 10, 'Asia/Kolkata');

-- ============================================
-- 4. ATHLETE TEAM (Care Team Assignment)
-- ============================================
INSERT INTO athlete_teams (team_id, athlete_id, physiotherapist_id, coach_id, caretaker_id, start_date, status) VALUES
('deaa1111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 'cc111111-1111-1111-1111-111111111111',
 'cd111111-1111-1111-1111-111111111111',
 '2026-02-05', 'active');

-- ============================================
-- 5. ASSESSMENTS
-- ============================================
INSERT INTO assessments (assessment_id, athlete_id, physiotherapist_id, assessment_type, assessment_date, pain_level, findings, recommendations, status) VALUES
-- Initial assessment
('a5111111-1111-1111-1111-111111111111', 
 'aa111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 'initial', '2026-02-05', 7,
 'ACL reconstruction post-op day 3. Significant swelling and limited ROM. Patient reports 7/10 pain.',
 'Begin gentle ROM exercises. Ice and elevation protocol. Pain management as prescribed.',
 'completed'),

-- Progress assessment week 2
('ad222222-2222-2222-2222-222222222222',
 'aa111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 'progress', '2026-02-19', 5,
 'Improved ROM: knee flexion to 90 degrees. Swelling reduced significantly. Patient progressing well.',
 'Progress to phase 2 exercises. Introduction of weight-bearing activities.',
 'completed'),

-- Progress assessment week 4
('ad333333-3333-3333-3333-333333333333',
 'aa111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 'progress', '2026-03-05', 3,
 'Full ROM achieved. Strength improving. Balance test shows 87% of baseline.',
 'Continue strengthening program. Begin sport-specific movements.',
 'completed');

-- ============================================
-- 6. EXERCISE LIBRARY
-- ============================================
INSERT INTO exercise_library (exercise_id, name, description, category, difficulty_level, target_muscles, target_joints, duration_minutes, equipment_needed, is_active) VALUES
('e1111111-1111-1111-1111-111111111111', 
 'Quad Sets',
 'Isometric quadriceps contraction to maintain muscle activation',
 'strength', 'beginner',
 ARRAY['quadriceps'], ARRAY['knee'], 5,
 ARRAY['none'], TRUE),

('e2222222-2222-2222-2222-222222222222',
 'Heel Slides',
 'Gentle knee flexion exercise to improve range of motion',
 'mobility', 'beginner',
 ARRAY['hamstrings', 'quadriceps'], ARRAY['knee'], 10,
 ARRAY['towel'], TRUE),

('e2333333-3333-3333-3333-333333333333',
 'Straight Leg Raises',
 'Hip flexion with knee extended to strengthen quadriceps',
 'strength', 'intermediate',
 ARRAY['quadriceps', 'hip flexors'], ARRAY['hip', 'knee'], 10,
 ARRAY['none'], TRUE),

('e2444444-4444-4444-4444-444444444444',
 'Balance Board Single Leg',
 'Single leg balance on unstable surface for proprioception',
 'balance', 'advanced',
 ARRAY['core', 'ankle stabilizers'], ARRAY['ankle', 'knee'], 15,
 ARRAY['balance board'], TRUE),

('e2555555-5555-5555-5555-555555555555',
 'Mini Squats',
 'Partial squats to build strength and functional movement',
 'strength', 'intermediate',
 ARRAY['quadriceps', 'glutes', 'hamstrings'], ARRAY['knee', 'hip'], 10,
 ARRAY['none'], TRUE);

-- ============================================
-- 7. EXERCISE ASSIGNMENTS
-- ============================================
INSERT INTO exercise_assignments (assignment_id, athlete_id, exercise_id, prescribed_by, sets, reps, frequency_per_week, start_date, status, total_sessions_required) VALUES
-- Week 1-2: Basic exercises
('ea111111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 'e1111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 3, 10, 7, '2026-02-05', 'completed', 14),

('ea222222-2222-2222-2222-222222222222',
 'aa111111-1111-1111-1111-111111111111',
 'e2222222-2222-2222-2222-222222222222',
 'bb111111-1111-1111-1111-111111111111',
 3, 15, 7, '2026-02-05', 'completed', 14),

-- Week 3-4: Progressive exercises
('ea333333-3333-3333-3333-333333333333',
 'aa111111-1111-1111-1111-111111111111',
 'e2333333-3333-3333-3333-333333333333',
 'bb111111-1111-1111-1111-111111111111',
 3, 12, 5, '2026-02-19', 'active', 15),

('ea444444-4444-4444-4444-444444444444',
 'aa111111-1111-1111-1111-111111111111',
 'e2555555-5555-5555-5555-555555555555',
 'bb111111-1111-1111-1111-111111111111',
 3, 10, 5, '2026-03-05', 'active', 15);

-- ============================================
-- 8. EXERCISE SESSIONS (Sample completions)
-- ============================================
INSERT INTO exercise_sessions (session_id, assignment_id, athlete_id, session_date, duration_minutes, sets_completed, reps_completed, pain_level_during, pain_level_after, difficulty_rating, form_quality, notes) VALUES
-- Quad sets sessions
('e5111111-1111-1111-1111-111111111111',
 'ea111111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 '2026-02-06 09:00:00', 8, 3, 10, 5, 4, 3, 4, 'Morning session - some discomfort'),

('e5111112-1111-1111-1111-111111111111',
 'ea111111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 '2026-02-07 09:15:00', 8, 3, 10, 4, 3, 3, 4, 'Feeling better today'),

-- Heel slides sessions
('ed222221-2222-2222-2222-222222222222',
 'ea222222-2222-2222-2222-222222222222',
 'aa111111-1111-1111-1111-111111111111',
 '2026-02-06 09:15:00', 12, 3, 15, 6, 5, 4, 3, 'ROM improving slowly'),

-- Straight leg raises
('ed333331-3333-3333-3333-333333333333',
 'ea333333-3333-3333-3333-333333333333',
 'aa111111-1111-1111-1111-111111111111',
 '2026-03-20 10:00:00', 12, 3, 12, 3, 2, 2, 4, 'Feeling strong');

-- ============================================
-- 9. DAILY TASKS
-- ============================================
INSERT INTO daily_tasks (task_id, athlete_id, assigned_by, assigned_by_role, task_type, title, description, scheduled_date, priority, status) VALUES
-- Today's tasks
('d7111111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 'physiotherapist', 'exercise',
 'Complete morning exercise routine',
 'Quad sets (3x10), Heel slides (3x15), Ankle pumps (3x20)',
 CURRENT_DATE, 'high', 'completed'),

('de222222-2222-2222-2222-222222222222',
 'aa111111-1111-1111-1111-111111111111',
 'cd111111-1111-1111-1111-111111111111',
 'caretaker', 'icing',
 'Ice knee 3 times',
 '20 minutes each session, with 2 hours between sessions',
 CURRENT_DATE, 'medium', 'in_progress'),

('de333333-3333-3333-3333-333333333333',
 'aa111111-1111-1111-1111-111111111111',
 'bb111111-1111-1111-1111-111111111111',
 'physiotherapist', 'stretching',
 'Evening stretching routine',
 'Hamstring stretch, Calf stretch, Hip flexor stretch',
 CURRENT_DATE, 'medium', 'pending'),

-- Tomorrow's tasks
('de444444-4444-4444-4444-444444444444',
 'aa111111-1111-1111-1111-111111111111',
 'cc111111-1111-1111-1111-111111111111',
 'coach', 'exercise',
 'Balance training session',
 'Single leg balance exercises as per program',
 CURRENT_DATE + INTERVAL '1 day', 'medium', 'pending');

-- ============================================
-- 10. PROGRESS MILESTONES
-- ============================================
INSERT INTO progress_milestones (milestone_id, athlete_id, milestone_type, title, description, target_date, achieved_date, target_value, achieved_value, unit, status, recorded_by) VALUES
-- Achieved milestones
('a7111111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 'mobility_improvement', 'Full knee flexion',
 'Achieve 135 degrees of knee flexion',
 '2026-03-01', '2026-02-28', 135, 138, 'degrees', 'achieved',
 'bb111111-1111-1111-1111-111111111111'),

('a7222222-2222-2222-2222-222222222222',
 'aa111111-1111-1111-1111-111111111111',
 'pain_reduction', 'Pain level below 3',
 'Reduce daily pain to manageable levels',
 '2026-03-15', '2026-03-12', 3, 2, 'pain scale', 'achieved',
 'bb111111-1111-1111-1111-111111111111'),

-- Pending milestones
('a7333333-3333-3333-3333-333333333333',
 'aa111111-1111-1111-1111-111111111111',
 'strength_gain', 'Quadriceps strength 80% of baseline',
 'Achieve 80% strength compared to uninjured leg',
 '2026-04-15', NULL, 80, 65, 'percent', 'in_progress',
 'bb111111-1111-1111-1111-111111111111'),

('a7444444-4444-4444-4444-444444444444',
 'aa111111-1111-1111-1111-111111111111',
 'functional_achievement', 'Return to running',
 'Begin light jogging program',
 '2026-04-30', NULL, 100, 40, 'percent', 'pending',
 'bb111111-1111-1111-1111-111111111111');

-- ============================================
-- 11. CLINICAL NOTES
-- ============================================
INSERT INTO clinical_notes (note_id, athlete_id, author_id, author_role, note_type, title, content, is_private) VALUES
('c8111111-1111-1111-1111-111111111111',
 'aa111111-1111-1111-1111-111111111111',
 'b1111111-1111-1111-1111-111111111111',
 'physiotherapist', 'progress',
 'Week 7 Progress Update',
 'Patient showing excellent progress. ROM fully restored. Strength at 65% of baseline. Balance improving. Ready to progress to next phase of rehabilitation.',
 FALSE),

('c8222222-2222-2222-2222-222222222222',
 'aa111111-1111-1111-1111-111111111111',
 'c1111111-1111-1111-1111-111111111111',
 'coach', 'observation',
 'Mental readiness assessment',
 'Athlete demonstrating strong mental resilience. Eager to progress. May need to manage expectations around return-to-play timeline.',
 FALSE),

('c8333333-3333-3333-3333-333333333333',
 'aa111111-1111-1111-1111-111111111111',
 'd1111111-1111-1111-1111-111111111111',
 'caretaker', 'observation',
 'Home compliance excellent',
 'Patient completing all home exercises and icing protocols consistently. Sleep quality improving.',
 FALSE);

-- ============================================
-- 12. VERIFY DATA
-- ============================================

-- Display summary
SELECT 'Users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Athlete Profiles', COUNT(*) FROM athlete_profiles
UNION ALL
SELECT 'Physiotherapist Profiles', COUNT(*) FROM physiotherapist_profiles
UNION ALL
SELECT 'Coach Profiles', COUNT(*) FROM coach_profiles
UNION ALL
SELECT 'Caretaker Profiles', COUNT(*) FROM caretaker_profiles
UNION ALL
SELECT 'Athlete Teams', COUNT(*) FROM athlete_teams
UNION ALL
SELECT 'Assessments', COUNT(*) FROM assessments
UNION ALL
SELECT 'Exercise Library', COUNT(*) FROM exercise_library
UNION ALL
SELECT 'Exercise Assignments', COUNT(*) FROM exercise_assignments
UNION ALL
SELECT 'Exercise Sessions', COUNT(*) FROM exercise_sessions
UNION ALL
SELECT 'Daily Tasks', COUNT(*) FROM daily_tasks
UNION ALL
SELECT 'Progress Milestones', COUNT(*) FROM progress_milestones
UNION ALL
SELECT 'Clinical Notes', COUNT(*) FROM clinical_notes;

-- ============================================
-- END OF SCRIPT
-- ============================================

