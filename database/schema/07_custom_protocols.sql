-- ============================================
-- Custom Test Protocols Schema
-- Allows physiotherapists to define custom baseline tests
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. CUSTOM TEST PROTOCOLS
-- ============================================
CREATE TABLE custom_test_protocols (
  protocol_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_by UUID REFERENCES physiotherapist_profiles(physiotherapist_id) ON DELETE CASCADE,
  sport_id VARCHAR(50) REFERENCES sports(sport_id),
  protocol_name VARCHAR(200) NOT NULL,
  description TEXT,
  test_category VARCHAR(100), -- e.g., 'baseline', 'rehab', 'performance'
  is_active BOOLEAN DEFAULT true,

  -- Video recording instructions
  video_instructions JSONB, -- What physio tells athlete to do
  required_views TEXT[], -- ['front', 'side', 'angle_45']
  duration_seconds INTEGER,
  equipment_needed TEXT[],

  -- Analysis configuration
  analysis_config JSONB, -- What to analyze (joints, metrics, etc.)
  baseline_metrics JSONB, -- Expected ranges for metrics
  risk_factors JSONB, -- What to flag as concerning

  -- Sample report template
  report_template JSONB, -- Structure for generated reports

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE custom_test_protocols IS 'Custom test protocols defined by physiotherapists';
COMMENT ON COLUMN custom_test_protocols.video_instructions IS 'Instructions for video recording setup and athlete actions';
COMMENT ON COLUMN custom_test_protocols.analysis_config IS 'Configuration for automated analysis (joints to track, calculations)';
COMMENT ON COLUMN custom_test_protocols.report_template IS 'Template structure for analysis reports';

-- ============================================
-- 2. CUSTOM PROTOCOL EXECUTIONS
-- ============================================
CREATE TABLE custom_protocol_executions (
  execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  protocol_id UUID REFERENCES custom_test_protocols(protocol_id) ON DELETE CASCADE,
  athlete_id UUID REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  prescribed_by UUID REFERENCES physiotherapist_profiles(physiotherapist_id),

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
  flagged_issues JSONB,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE custom_protocol_executions IS 'Executions of custom test protocols on athletes';

-- ============================================
-- 3. CLOUD RUN ANALYSIS JOBS
-- ============================================
CREATE TABLE cloud_run_analysis_jobs (
  job_id VARCHAR(100) PRIMARY KEY,
  execution_id UUID REFERENCES custom_protocol_executions(execution_id) ON DELETE CASCADE,
  protocol_id UUID REFERENCES custom_test_protocols(protocol_id),
  status VARCHAR(20) DEFAULT 'queued'
    CHECK (status IN ('queued', 'running', 'completed', 'failed')),
  service_url VARCHAR(500),
  input_data JSONB,
  output_data JSONB,
  error_message TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE cloud_run_analysis_jobs IS 'Cloud Run jobs for custom protocol analysis';

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_custom_protocols_created_by ON custom_test_protocols(created_by);
CREATE INDEX idx_custom_protocols_sport ON custom_test_protocols(sport_id);
CREATE INDEX idx_custom_executions_protocol ON custom_protocol_executions(protocol_id);
CREATE INDEX idx_custom_executions_athlete ON custom_protocol_executions(athlete_id);
CREATE INDEX idx_cloud_run_jobs_execution ON cloud_run_analysis_jobs(execution_id);

-- ============================================
-- TRIGGERS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_custom_protocols_updated_at
    BEFORE UPDATE ON custom_test_protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();