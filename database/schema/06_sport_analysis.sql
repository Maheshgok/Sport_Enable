-- ============================================
-- Sport-Specific Analysis Schema
-- Adds support for sport-specific analysis with baselines
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. SPORTS MASTER TABLE
-- ============================================
CREATE TABLE sports (
  sport_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  configuration JSONB NOT NULL, -- Full sport configuration
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE sports IS 'Master table of supported sports with configurations';
COMMENT ON COLUMN sports.configuration IS 'Complete sport config including video types, baselines, and analysis parameters';

-- ============================================
-- 2. SPORT VIDEO TYPES
-- ============================================
CREATE TABLE sport_video_types (
  video_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sport_id VARCHAR(50) REFERENCES sports(sport_id) ON DELETE CASCADE,
  type_code VARCHAR(50) NOT NULL, -- e.g., 'free_kick', 'jump_shot'
  name VARCHAR(100) NOT NULL,
  description TEXT,
  required_views TEXT[], -- ['front', 'side', 'top']
  duration_seconds INTEGER,
  instructions TEXT,
  configuration JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_sport_video_type UNIQUE(sport_id, type_code)
);

COMMENT ON TABLE sport_video_types IS 'Video capture types specific to each sport';

-- ============================================
-- 3. SPORT BASELINE METRICS
-- ============================================
CREATE TABLE sport_baselines (
  baseline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sport_id VARCHAR(50) REFERENCES sports(sport_id) ON DELETE CASCADE,
  metric_name VARCHAR(100) NOT NULL,
  metric_type VARCHAR(50), -- 'angle', 'speed', 'distance', 'time', 'force'
  min_value DECIMAL(10,2),
  max_value DECIMAL(10,2),
  optimal_value DECIMAL(10,2),
  unit VARCHAR(20),
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_sport_metric UNIQUE(sport_id, metric_name)
);

COMMENT ON TABLE sport_baselines IS 'Baseline performance metrics for each sport';
COMMENT ON COLUMN sport_baselines.optimal_value IS 'Target value for optimal performance';

-- ============================================
-- 4. UPDATE ATHLETE PROFILES FOR SPORT
-- ============================================
ALTER TABLE athlete_profiles
ADD COLUMN sport_id VARCHAR(50) REFERENCES sports(sport_id),
ADD COLUMN position_in_sport VARCHAR(100),
ADD COLUMN baseline_assessment_date DATE,
ADD COLUMN custom_baselines JSONB, -- Athlete-specific baseline overrides
ADD COLUMN sport_level VARCHAR(50) CHECK (sport_level IN ('beginner', 'intermediate', 'advanced', 'professional'));

COMMENT ON COLUMN athlete_profiles.sport_id IS 'Primary sport of the athlete';
COMMENT ON COLUMN athlete_profiles.custom_baselines IS 'Athlete-specific baseline adjustments';

-- ============================================
-- 5. VIDEO ANALYSIS SESSIONS
-- ============================================
CREATE TABLE video_analyses (
  analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  athlete_id UUID REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  uploaded_by UUID REFERENCES users(user_id),
  prescribed_by UUID REFERENCES physiotherapist_profiles(physiotherapist_id), -- Optional
  
  -- Sport and video type
  sport_id VARCHAR(50) REFERENCES sports(sport_id),
  video_type_id UUID REFERENCES sport_video_types(video_type_id),
  video_type_code VARCHAR(50), -- Denormalized for quick access
  
  -- Video files (stored in GCS)
  video_urls JSONB, -- {"front": "gs://bucket/...", "side": "gs://..."}
  
  -- Processing status
  status VARCHAR(20) DEFAULT 'pending' 
    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
  cloud_run_endpoint VARCHAR(500),
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,
  error_message TEXT,
  
  -- Results
  results JSONB, -- Complete analysis results
  report_markdown TEXT, -- Markdown content of report
  report_pdf_url VARCHAR(500), -- GCS URL to PDF report
  
  -- Metadata
  athlete_height_cm DECIMAL(5,2),
  athlete_weight_kg DECIMAL(5,2),
  test_conditions JSONB, -- Temperature, surface, equipment, etc.
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE video_analyses IS 'Video analysis sessions and results';
COMMENT ON COLUMN video_analyses.prescribed_by IS 'Physiotherapist who prescribed this analysis';
COMMENT ON COLUMN video_analyses.results IS 'Complete JSON results from analysis function';

CREATE INDEX idx_video_analyses_athlete ON video_analyses(athlete_id);
CREATE INDEX idx_video_analyses_status ON video_analyses(status);
CREATE INDEX idx_video_analyses_sport ON video_analyses(sport_id);
CREATE INDEX idx_video_analyses_created ON video_analyses(created_at DESC);

-- ============================================
-- 6. ANALYSIS METRICS (INDIVIDUAL MEASUREMENTS)
-- ============================================
CREATE TABLE analysis_metrics (
  metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID REFERENCES video_analyses(analysis_id) ON DELETE CASCADE,
  
  -- Metric details
  metric_name VARCHAR(100) NOT NULL,
  metric_type VARCHAR(50), -- 'angle', 'speed', 'distance', 'time'
  
  -- Values
  measured_value DECIMAL(10,2),
  baseline_min DECIMAL(10,2),
  baseline_max DECIMAL(10,2),
  baseline_optimal DECIMAL(10,2),
  deviation_percent DECIMAL(5,2),
  unit VARCHAR(20),
  
  -- Assessment
  is_within_baseline BOOLEAN,
  severity VARCHAR(20) CHECK (severity IN ('normal', 'attention', 'warning', 'critical')),
  confidence_score DECIMAL(3,2), -- 0.00 to 1.00
  
  -- Context
  phase VARCHAR(50), -- Which movement phase this metric is from
  notes TEXT,
  
  created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE analysis_metrics IS 'Individual metric measurements from video analysis';
COMMENT ON COLUMN analysis_metrics.confidence_score IS 'AI confidence in this measurement (0-1)';

CREATE INDEX idx_analysis_metrics_analysis ON analysis_metrics(analysis_id);
CREATE INDEX idx_analysis_metrics_severity ON analysis_metrics(severity);

-- ============================================
-- 7. PHYSIOTHERAPIST PRESCRIPTIONS
-- ============================================
CREATE TABLE analysis_prescriptions (
  prescription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  physiotherapist_id UUID REFERENCES physiotherapist_profiles(physiotherapist_id),
  athlete_id UUID REFERENCES athlete_profiles(athlete_id),
  
  -- What to analyze
  sport_id VARCHAR(50) REFERENCES sports(sport_id),
  video_type_id UUID REFERENCES sport_video_types(video_type_id),
  
  -- Focus areas
  focus_metrics TEXT[], -- Specific metrics to focus on
  special_instructions TEXT,
  frequency VARCHAR(50), -- 'once', 'weekly', 'biweekly', 'monthly'
  
  -- Status
  status VARCHAR(20) DEFAULT 'active' 
    CHECK (status IN ('active', 'completed', 'cancelled')),
  
  -- Related analyses
  completed_analyses UUID[], -- Array of analysis_ids that fulfilled this prescription
  
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP
);

COMMENT ON TABLE analysis_prescriptions IS 'Physiotherapist prescriptions for specific analyses';

-- ============================================
-- 8. REPORT TEMPLATES
-- ============================================
CREATE TABLE report_templates (
  template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sport_id VARCHAR(50) REFERENCES sports(sport_id),
  video_type_code VARCHAR(50),
  
  -- Template details
  name VARCHAR(100) NOT NULL,
  description TEXT,
  template_markdown TEXT NOT NULL, -- Jinja2 template
  css_styles TEXT, -- Custom CSS for PDF
  
  -- Sections to include
  sections JSONB, -- Configuration of report sections
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  is_default BOOLEAN DEFAULT false,
  
  created_by UUID REFERENCES users(user_id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE report_templates IS 'Customizable report templates for different sports and analyses';

-- ============================================
-- 9. SEED INITIAL SPORTS DATA
-- ============================================
INSERT INTO sports (sport_id, name, description, is_active, configuration) VALUES
('football', 'Football/Soccer', 'Football/Soccer motion analysis', true, '{}'),
('basketball', 'Basketball', 'Basketball motion analysis', true, '{}'),
('running', 'Running/Athletics', 'Running gait and performance analysis', true, '{}'),
('cricket', 'Cricket', 'Cricket bowling and batting analysis', true, '{}');

-- ============================================
-- 10. VIEWS FOR EASY QUERYING
-- ============================================

-- View: Latest analysis per athlete
CREATE VIEW v_athlete_latest_analyses AS
SELECT DISTINCT ON (athlete_id, sport_id, video_type_code)
  analysis_id,
  athlete_id,
  sport_id,
  video_type_code,
  status,
  report_pdf_url,
  processing_completed_at,
  created_at
FROM video_analyses
WHERE status = 'completed'
ORDER BY athlete_id, sport_id, video_type_code, created_at DESC;

-- View: Athlete analysis summary
CREATE VIEW v_athlete_analysis_summary AS
SELECT 
  a.athlete_id,
  u.first_name,
  u.last_name,
  a.sport_id,
  s.name as sport_name,
  COUNT(va.analysis_id) as total_analyses,
  COUNT(CASE WHEN va.status = 'completed' THEN 1 END) as completed_analyses,
  MAX(va.created_at) as last_analysis_date
FROM athlete_profiles a
JOIN users u ON a.user_id = u.user_id
LEFT JOIN video_analyses va ON a.athlete_id = va.athlete_id
LEFT JOIN sports s ON a.sport_id = s.sport_id
GROUP BY a.athlete_id, u.first_name, u.last_name, a.sport_id, s.name;

-- View: Metric trends (for tracking progress over time)
CREATE VIEW v_metric_trends AS
SELECT 
  va.athlete_id,
  va.sport_id,
  am.metric_name,
  am.measured_value,
  am.unit,
  am.severity,
  va.created_at as measurement_date
FROM analysis_metrics am
JOIN video_analyses va ON am.analysis_id = va.analysis_id
WHERE va.status = 'completed'
ORDER BY va.athlete_id, am.metric_name, va.created_at;

-- ============================================
-- 11. FUNCTIONS
-- ============================================

-- Function: Get athlete's baseline for a metric
CREATE OR REPLACE FUNCTION get_athlete_baseline(
  p_athlete_id UUID,
  p_metric_name VARCHAR
) RETURNS TABLE (
  min_value DECIMAL,
  max_value DECIMAL,
  optimal_value DECIMAL,
  unit VARCHAR
) AS $$
BEGIN
  -- First try athlete-specific custom baselines
  -- Then fall back to sport baselines
  RETURN QUERY
  WITH athlete_sport AS (
    SELECT sport_id FROM athlete_profiles WHERE athlete_id = p_athlete_id
  )
  SELECT 
    sb.min_value,
    sb.max_value,
    sb.optimal_value,
    sb.unit
  FROM sport_baselines sb
  JOIN athlete_sport asport ON sb.sport_id = asport.sport_id
  WHERE sb.metric_name = p_metric_name
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate deviation from baseline
CREATE OR REPLACE FUNCTION calculate_deviation_percent(
  measured_value DECIMAL,
  baseline_min DECIMAL,
  baseline_max DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
  IF measured_value BETWEEN baseline_min AND baseline_max THEN
    RETURN 0;
  ELSIF measured_value < baseline_min THEN
    RETURN ((baseline_min - measured_value) / baseline_min * 100) * -1;
  ELSE
    RETURN (measured_value - baseline_max) / baseline_max * 100;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 12. TRIGGERS
-- ============================================

-- Update athlete profile updated_at on custom baseline change
CREATE OR REPLACE FUNCTION update_athlete_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER athlete_profile_update
  BEFORE UPDATE ON athlete_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_athlete_profile_timestamp();

-- Update video analysis updated_at
CREATE TRIGGER video_analysis_update
  BEFORE UPDATE ON video_analyses
  FOR EACH ROW
  EXECUTE FUNCTION update_athlete_profile_timestamp();

COMMENT ON SCHEMA physio_app IS 'Moove - Sport-specific motion analysis platform';
