-- ============================================
-- Athlete Team Relationships
-- Schema: physio_app
-- Description: Junction table enforcing 1:1:1:1 athlete-to-team relationships
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. ATHLETE TEAM (CARE TEAM)
-- ============================================
CREATE TABLE athlete_teams (
  team_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Core relationships (1:1:1:1)
  athlete_id UUID NOT NULL REFERENCES athlete_profiles(athlete_id) ON DELETE CASCADE,
  physiotherapist_id UUID NOT NULL REFERENCES physiotherapist_profiles(physiotherapist_id) ON DELETE RESTRICT,
  coach_id UUID NOT NULL REFERENCES coach_profiles(coach_id) ON DELETE RESTRICT,
  caretaker_id UUID NOT NULL REFERENCES caretaker_profiles(caretaker_id) ON DELETE RESTRICT,
  
  -- Team metadata
  assigned_date TIMESTAMP DEFAULT NOW(),
  start_date DATE NOT NULL DEFAULT CURRENT_DATE,
  end_date DATE,
  
  -- Status
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'completed')),
  
  -- Notes
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT end_date_after_start CHECK (end_date IS NULL OR end_date >= start_date)
);

COMMENT ON TABLE athlete_teams IS 'Care team assignments enforcing 1:1:1:1 relationships between athlete and professionals';
COMMENT ON COLUMN athlete_teams.status IS 'active = current team, inactive = paused, completed = finished recovery';

-- ============================================
-- 2. UNIQUE CONSTRAINT: ONE ACTIVE TEAM PER ATHLETE
-- ============================================
-- Only one active team per athlete at any time
CREATE UNIQUE INDEX idx_athlete_teams_active_unique 
  ON athlete_teams(athlete_id) 
  WHERE status = 'active';

COMMENT ON INDEX idx_athlete_teams_active_unique IS 'Ensures an athlete can only have one active care team at a time';

-- ============================================
-- 3. INDEXES FOR QUERY PERFORMANCE
-- ============================================
CREATE INDEX idx_athlete_teams_athlete ON athlete_teams(athlete_id);
CREATE INDEX idx_athlete_teams_physio ON athlete_teams(physiotherapist_id);
CREATE INDEX idx_athlete_teams_coach ON athlete_teams(coach_id);
CREATE INDEX idx_athlete_teams_caretaker ON athlete_teams(caretaker_id);
CREATE INDEX idx_athlete_teams_status ON athlete_teams(status);
CREATE INDEX idx_athlete_teams_dates ON athlete_teams(start_date, end_date);

-- ============================================
-- 4. TRIGGER: UPDATE CASELOAD COUNTS
-- ============================================
-- Automatically update professional caseload counts when teams are created/updated

CREATE OR REPLACE FUNCTION update_professional_caseloads()
RETURNS TRIGGER AS $$
BEGIN
  -- Handle INSERT or UPDATE to 'active'
  IF (TG_OP = 'INSERT' AND NEW.status = 'active') OR 
     (TG_OP = 'UPDATE' AND NEW.status = 'active' AND OLD.status != 'active') THEN
    
    -- Increment caseloads
    UPDATE physiotherapist_profiles SET current_caseload = current_caseload + 1 
      WHERE physiotherapist_id = NEW.physiotherapist_id;
    UPDATE coach_profiles SET current_athletes = current_athletes + 1 
      WHERE coach_id = NEW.coach_id;
    UPDATE caretaker_profiles SET current_athletes = current_athletes + 1 
      WHERE caretaker_id = NEW.caretaker_id;
      
  -- Handle UPDATE from 'active' to inactive
  ELSIF TG_OP = 'UPDATE' AND OLD.status = 'active' AND NEW.status != 'active' THEN
    
    -- Decrement caseloads
    UPDATE physiotherapist_profiles SET current_caseload = current_caseload - 1 
      WHERE physiotherapist_id = OLD.physiotherapist_id;
    UPDATE coach_profiles SET current_athletes = current_athletes - 1 
      WHERE coach_id = OLD.coach_id;
    UPDATE caretaker_profiles SET current_athletes = current_athletes - 1 
      WHERE caretaker_id = OLD.caretaker_id;
      
  -- Handle DELETE
  ELSIF TG_OP = 'DELETE' AND OLD.status = 'active' THEN
    
    -- Decrement caseloads
    UPDATE physiotherapist_profiles SET current_caseload = current_caseload - 1 
      WHERE physiotherapist_id = OLD.physiotherapist_id;
    UPDATE coach_profiles SET current_athletes = current_athletes - 1 
      WHERE coach_id = OLD.coach_id;
    UPDATE caretaker_profiles SET current_athletes = current_athletes - 1 
      WHERE caretaker_id = OLD.caretaker_id;
      
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_caseloads_trigger
  AFTER INSERT OR UPDATE OR DELETE ON athlete_teams
  FOR EACH ROW
  EXECUTE FUNCTION update_professional_caseloads();

COMMENT ON FUNCTION update_professional_caseloads IS 'Auto-updates current caseload counts for professionals when team assignments change';

-- ============================================
-- 5. TRIGGER: UPDATE TIMESTAMPS
-- ============================================
CREATE TRIGGER update_athlete_teams_timestamp 
  BEFORE UPDATE ON athlete_teams
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 6. HELPER VIEWS
-- ============================================

-- View: Active care teams with professional names
CREATE VIEW v_active_care_teams AS
SELECT 
  at.team_id,
  at.athlete_id,
  au.first_name || ' ' || au.last_name AS athlete_name,
  ap.sport,
  ap.current_injury,
  
  at.physiotherapist_id,
  pu.first_name || ' ' || pu.last_name AS physiotherapist_name,
  pp.license_number AS physio_license,
  
  at.coach_id,
  cu.first_name || ' ' || cu.last_name AS coach_name,
  cp.sport AS coach_sport,
  
  at.caretaker_id,
  cau.first_name || ' ' || cau.last_name AS caretaker_name,
  cap.caretaker_type,
  
  at.start_date,
  at.assigned_date,
  at.created_at
FROM athlete_teams at
  JOIN athlete_profiles ap ON at.athlete_id = ap.athlete_id
  JOIN users au ON ap.user_id = au.user_id
  
  JOIN physiotherapist_profiles pp ON at.physiotherapist_id = pp.physiotherapist_id
  JOIN users pu ON pp.user_id = pu.user_id
  
  JOIN coach_profiles cp ON at.coach_id = cp.coach_id
  JOIN users cu ON cp.user_id = cu.user_id
  
  JOIN caretaker_profiles cap ON at.caretaker_id = cap.caretaker_id
  JOIN users cau ON cap.user_id = cau.user_id
WHERE at.status = 'active';

COMMENT ON VIEW v_active_care_teams IS 'Denormalized view of active care teams with all professional names';

-- View: Professional workload summary
CREATE VIEW v_professional_workloads AS
SELECT 
  'physiotherapist' AS role_type,
  pp.physiotherapist_id AS professional_id,
  u.first_name || ' ' || u.last_name AS name,
  pp.current_caseload AS current_load,
  pp.max_caseload AS max_load,
  ROUND((pp.current_caseload::NUMERIC / pp.max_caseload) * 100, 2) AS utilization_percent
FROM physiotherapist_profiles pp
  JOIN users u ON pp.user_id = u.user_id
UNION ALL
SELECT 
  'coach' AS role_type,
  cp.coach_id AS professional_id,
  u.first_name || ' ' || u.last_name AS name,
  cp.current_athletes AS current_load,
  cp.max_athletes AS max_load,
  ROUND((cp.current_athletes::NUMERIC / cp.max_athletes) * 100, 2) AS utilization_percent
FROM coach_profiles cp
  JOIN users u ON cp.user_id = u.user_id
UNION ALL
SELECT 
  'caretaker' AS role_type,
  cap.caretaker_id AS professional_id,
  u.first_name || ' ' || u.last_name AS name,
  cap.current_athletes AS current_load,
  cap.max_athletes AS max_load,
  ROUND((cap.current_athletes::NUMERIC / cap.max_athletes) * 100, 2) AS utilization_percent
FROM caretaker_profiles cap
  JOIN users u ON cap.user_id = u.user_id;

COMMENT ON VIEW v_professional_workloads IS 'Summary of all professionals and their current workload utilization';

-- ============================================
-- END OF SCRIPT
-- ============================================
