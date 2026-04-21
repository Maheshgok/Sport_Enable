-- ============================================
-- Assessment Prompts Database
-- Predefined clinical assessment templates
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. ASSESSMENT PROMPTS LIBRARY
-- ============================================
CREATE TABLE assessment_prompts (
  prompt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  prompt_code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'shoulder_impingement', 'acl_risk'
  prompt_name VARCHAR(200) NOT NULL,
  clinical_category VARCHAR(100), -- e.g., 'shoulder', 'knee', 'hip', 'spine'
  description TEXT,
  target_population TEXT, -- e.g., 'athletes', 'general_population', 'post_surgery'
  estimated_duration_minutes INTEGER,

  -- Clinical information
  clinical_indications TEXT, -- When to use this assessment
  contraindications TEXT, -- When NOT to use
  preparation_instructions TEXT, -- How to prepare patient

  -- Video recording requirements
  video_instructions JSONB, -- What physio tells patient
  required_views TEXT[], -- ['front', 'side', 'angle_45']
  duration_seconds INTEGER,
  equipment_needed TEXT[],

  -- Analysis configuration (predefined)
  analysis_config JSONB, -- Fixed config for this assessment type

  -- Clinical baselines and norms
  baseline_metrics JSONB, -- Age/gender/sport specific ranges
  risk_factors JSONB, -- What to flag automatically

  -- Report template
  report_template JSONB, -- Standardized report structure

  -- Metadata
  is_active BOOLEAN DEFAULT true,
  version_number INTEGER DEFAULT 1,
  based_on_evidence TEXT, -- Research/literature references
  created_by UUID REFERENCES physiotherapist_profiles(physiotherapist_id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE assessment_prompts IS 'Predefined clinical assessment templates with complete analysis configurations';
COMMENT ON COLUMN assessment_prompts.prompt_code IS 'Unique identifier for the assessment type';
COMMENT ON COLUMN assessment_prompts.analysis_config IS 'Fixed technical configuration for video analysis';
COMMENT ON COLUMN assessment_prompts.baseline_metrics IS 'Clinical norms and reference ranges';

-- ============================================
-- 2. PROMPT EXECUTIONS
-- ============================================
CREATE TABLE prompt_executions (
  execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  prompt_id UUID REFERENCES assessment_prompts(prompt_id),
  athlete_id UUID REFERENCES athlete_profiles(athlete_id),
  prescribed_by UUID REFERENCES physiotherapist_profiles(physiotherapist_id),

  -- Execution details
  execution_context JSONB, -- Additional clinical context
  custom_overrides JSONB, -- Any customizations for this execution

  -- Video files
  video_urls JSONB,

  -- Processing
  status VARCHAR(20) DEFAULT 'pending'
    CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  cloud_run_job_id VARCHAR(100),
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,

  -- Results
  analysis_results JSONB,
  report_data JSONB,
  clinical_interpretation JSONB, -- Physio's clinical notes

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE prompt_executions IS 'Executions of predefined assessment prompts';

-- ============================================
-- 3. PROMPT CATEGORIES AND SPECIALIZATIONS
-- ============================================
CREATE TABLE prompt_categories (
  category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category_name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  parent_category_id UUID REFERENCES prompt_categories(category_id),
  display_order INTEGER,
  is_active BOOLEAN DEFAULT true
);

CREATE TABLE prompt_category_mappings (
  prompt_id UUID REFERENCES assessment_prompts(prompt_id),
  category_id UUID REFERENCES prompt_categories(category_id),
  PRIMARY KEY (prompt_id, category_id)
);

-- ============================================
-- 4. PROMPT USAGE STATISTICS
-- ============================================
CREATE TABLE prompt_usage_stats (
  stat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  prompt_id UUID REFERENCES assessment_prompts(prompt_id),
  physio_id UUID REFERENCES physiotherapist_profiles(physiotherapist_id),
  usage_count INTEGER DEFAULT 1,
  last_used_at TIMESTAMP DEFAULT NOW(),
  average_completion_time_seconds INTEGER,
  success_rate DECIMAL(5,2),

  UNIQUE(prompt_id, physio_id)
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_assessment_prompts_code ON assessment_prompts(prompt_code);
CREATE INDEX idx_assessment_prompts_category ON assessment_prompts(clinical_category);
CREATE INDEX idx_prompt_executions_prompt ON prompt_executions(prompt_id);
CREATE INDEX idx_prompt_executions_athlete ON prompt_executions(athlete_id);
CREATE INDEX idx_prompt_executions_physio ON prompt_executions(prescribed_by);

-- ============================================
-- TRIGGERS
-- ============================================
CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON assessment_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_executions_updated_at
    BEFORE UPDATE ON prompt_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();