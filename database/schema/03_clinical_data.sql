-- ============================================
-- Clinical Data & Recovery Tracking
-- Schema: physio_app
-- Description: Assessments, exercises, progress tracking, and treatment plans
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. ASSESSMENTS
-- ============================================
CREATE TABLE assessments (
  assessment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  physiotherapist_id UUID NOT NULL REFERENCES physiotherapist_profiles(physiotherapist_id),
  
  -- Assessment details
  assessment_type VARCHAR(50) CHECK (assessment_type IN ('initial', 'progress', 'discharge', 'video', 'physical')),
  assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,
  
  -- Physical measurements
  range_of_motion JSONB, -- e.g., {"knee_flexion": 120, "knee_extension": 5}
  strength_scores JSONB, -- e.g., {"quadriceps": 4, "hamstring": 3}
  pain_level INTEGER CHECK (pain_level >= 0 AND pain_level <= 10),
  
  -- Video analysis (if applicable)
  video_url VARCHAR(500),
  video_s3_key VARCHAR(500), -- For storage reference
  movement_analysis JSONB, -- Keypoint data or analysis results
  
  -- AI/ML embeddings for similarity search
  movement_embedding vector(512), -- pgvector for biomechanical patterns
  
  -- Findings
  findings TEXT,
  recommendations TEXT,
  
  -- Status
  status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE assessments IS 'Physical and video assessments performed by physiotherapists';
COMMENT ON COLUMN assessments.movement_embedding IS 'Vector embedding for movement pattern similarity search';

-- ============================================
-- 2. EXERCISE LIBRARY
-- ============================================
CREATE TABLE exercise_library (
  exercise_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Exercise details
  name VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(100), -- e.g., "strength", "flexibility", "mobility", "balance"
  difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  
  -- Target areas
  target_muscles TEXT[], -- Array of muscle groups
  target_joints TEXT[], -- Array of joints
  injury_types TEXT[], -- What injuries this helps
  
  -- Media
  video_url VARCHAR(500),
  thumbnail_url VARCHAR(500),
  instruction_images TEXT[], -- Array of image URLs
  
  -- Instructions
  instructions TEXT,
  precautions TEXT,
  
  -- Metadata
  duration_minutes INTEGER,
  equipment_needed TEXT[],
  
  -- Embedding for exercise recommendation
  exercise_embedding vector(256),
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE exercise_library IS 'Master library of rehabilitation exercises';
COMMENT ON COLUMN exercise_library.exercise_embedding IS 'Vector embedding for exercise recommendation matching';

-- ============================================
-- 3. EXERCISE ASSIGNMENTS
-- ============================================
CREATE TABLE exercise_assignments (
  assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  exercise_id UUID NOT NULL REFERENCES exercise_library(exercise_id),
  prescribed_by UUID NOT NULL REFERENCES physiotherapist_profiles(physiotherapist_id),
  
  -- Prescription details
  sets INTEGER,
  reps INTEGER,
  hold_time_seconds INTEGER,
  frequency_per_week INTEGER,
  
  -- Schedule
  start_date DATE NOT NULL DEFAULT CURRENT_DATE,
  end_date DATE,
  
  -- Status
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled')),
  
  -- Progress tracking
  completion_count INTEGER DEFAULT 0,
  total_sessions_required INTEGER,
  
  -- Notes
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE exercise_assignments IS 'Exercises prescribed to athletes by physiotherapists';

-- ============================================
-- 4. EXERCISE SESSIONS (Completed Workouts)
-- ============================================
CREATE TABLE exercise_sessions (
  session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  assignment_id UUID NOT NULL REFERENCES exercise_assignments(assignment_id) ON DELETE CASCADE,
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  
  -- Session details
  session_date TIMESTAMP DEFAULT NOW(),
  duration_minutes INTEGER,
  
  -- Performance
  sets_completed INTEGER,
  reps_completed INTEGER,
  pain_level_during INTEGER CHECK (pain_level_during >= 0 AND pain_level_during <= 10),
  pain_level_after INTEGER CHECK (pain_level_after >= 0 AND pain_level_after <= 10),
  
  -- Quality metrics
  difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5),
  form_quality INTEGER CHECK (form_quality >= 1 AND form_quality <= 5),
  
  -- Video recording (optional)
  video_url VARCHAR(500),
  video_s3_key VARCHAR(500),
  
  -- Notes
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE exercise_sessions IS 'Individual exercise session logs completed by athletes';

-- ============================================
-- 5. DAILY TASKS
-- ============================================
CREATE TABLE daily_tasks (
  task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  assigned_by UUID NOT NULL, -- Can be physio, coach, or caretaker
  assigned_by_role VARCHAR(50) CHECK (assigned_by_role IN ('physiotherapist', 'coach', 'caretaker')),
  
  -- Task details
  task_type VARCHAR(50) CHECK (task_type IN ('exercise', 'medication', 'icing', 'stretching', 'rest', 'nutrition', 'other')),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Schedule
  scheduled_date DATE NOT NULL,
  scheduled_time TIME,
  
  -- Priority
  priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped', 'cancelled')),
  
  -- Completion
  completed_at TIMESTAMP,
  completed_notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE daily_tasks IS 'Daily tasks assigned to athletes by care team members';

-- ============================================
-- 6. PROGRESS MILESTONES
-- ============================================
CREATE TABLE progress_milestones (
  milestone_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  
  -- Milestone details
  milestone_type VARCHAR(50) CHECK (milestone_type IN ('pain_reduction', 'mobility_improvement', 'strength_gain', 'functional_achievement', 'discharge')),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  
  -- Target vs Actual
  target_date DATE,
  achieved_date DATE,
  
  -- Metrics
  target_value NUMERIC,
  achieved_value NUMERIC,
  unit VARCHAR(50), -- e.g., "degrees", "kg", "repetitions"
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'achieved', 'missed', 'cancelled')),
  
  -- Documentation
  notes TEXT,
  recorded_by UUID NOT NULL REFERENCES physiotherapist_profiles(physiotherapist_id),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE progress_milestones IS 'Recovery milestones and goals for athletes';

-- ============================================
-- 7. NOTES & OBSERVATIONS
-- ============================================
CREATE TABLE clinical_notes (
  note_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES users(user_id),
  author_role VARCHAR(50) CHECK (author_role IN ('physiotherapist', 'coach', 'caretaker')),
  
  -- Note details
  note_type VARCHAR(50) CHECK (note_type IN ('assessment', 'progress', 'concern', 'observation', 'communication')),
  title VARCHAR(200),
  content TEXT NOT NULL,
  
  -- Privacy
  is_private BOOLEAN DEFAULT FALSE, -- Only visible to author's role type
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE clinical_notes IS 'Clinical notes and observations from care team members';
COMMENT ON COLUMN clinical_notes.is_private IS 'If true, only visible to same role type';

-- ============================================
-- 8. TRIGGERS: UPDATE TIMESTAMPS
-- ============================================
CREATE TRIGGER update_assessments_timestamp BEFORE UPDATE ON assessments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercise_library_timestamp BEFORE UPDATE ON exercise_library
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercise_assignments_timestamp BEFORE UPDATE ON exercise_assignments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_tasks_timestamp BEFORE UPDATE ON daily_tasks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progress_milestones_timestamp BEFORE UPDATE ON progress_milestones
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinical_notes_timestamp BEFORE UPDATE ON clinical_notes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 9. INDEXES FOR PERFORMANCE
-- ============================================
-- Assessments
CREATE INDEX idx_assessments_athlete ON assessments(athlete_id);
CREATE INDEX idx_assessments_physio ON assessments(physiotherapist_id);
CREATE INDEX idx_assessments_date ON assessments(assessment_date DESC);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);

-- Exercise library
CREATE INDEX idx_exercise_library_name ON exercise_library(name);
CREATE INDEX idx_exercise_library_category ON exercise_library(category);
CREATE INDEX idx_exercise_library_active ON exercise_library(is_active);

-- Exercise assignments
CREATE INDEX idx_exercise_assignments_athlete ON exercise_assignments(athlete_id);
CREATE INDEX idx_exercise_assignments_exercise ON exercise_assignments(exercise_id);
CREATE INDEX idx_exercise_assignments_status ON exercise_assignments(status);
CREATE INDEX idx_exercise_assignments_dates ON exercise_assignments(start_date, end_date);

-- Exercise sessions
CREATE INDEX idx_exercise_sessions_assignment ON exercise_sessions(assignment_id);
CREATE INDEX idx_exercise_sessions_athlete ON exercise_sessions(athlete_id);
CREATE INDEX idx_exercise_sessions_date ON exercise_sessions(session_date DESC);

-- Daily tasks
CREATE INDEX idx_daily_tasks_athlete ON daily_tasks(athlete_id);
CREATE INDEX idx_daily_tasks_scheduled ON daily_tasks(scheduled_date);
CREATE INDEX idx_daily_tasks_status ON daily_tasks(status);
CREATE INDEX idx_daily_tasks_priority ON daily_tasks(priority);

-- Progress milestones
CREATE INDEX idx_progress_milestones_athlete ON progress_milestones(athlete_id);
CREATE INDEX idx_progress_milestones_status ON progress_milestones(status);
CREATE INDEX idx_progress_milestones_dates ON progress_milestones(target_date, achieved_date);

-- Clinical notes
CREATE INDEX idx_clinical_notes_athlete ON clinical_notes(athlete_id);
CREATE INDEX idx_clinical_notes_author ON clinical_notes(author_id);
CREATE INDEX idx_clinical_notes_created ON clinical_notes(created_at DESC);

-- Vector similarity search indexes (if pgvector is available)
-- CREATE INDEX idx_assessments_embedding ON assessments USING ivfflat (movement_embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX idx_exercise_embedding ON exercise_library USING ivfflat (exercise_embedding vector_cosine_ops) WITH (lists = 50);

-- ============================================
-- END OF SCRIPT
-- ============================================
