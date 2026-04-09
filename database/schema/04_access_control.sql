-- ============================================
-- Access Control & Security Functions
-- Schema: physio_app
-- Description: Row-level security policies and helper functions for data access control
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. HELPER FUNCTIONS
-- ============================================

-- Get user's role profile IDs
CREATE OR REPLACE FUNCTION get_user_profile_ids(p_user_id UUID)
RETURNS TABLE (
  athlete_id UUID,
  physiotherapist_id UUID,
  coach_id UUID,
  caretaker_id UUID
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ap.athlete_id,
    pp.physiotherapist_id,
    cp.coach_id,
    cap.caretaker_id
  FROM users u
    LEFT JOIN athlete_profiles ap ON u.user_id = ap.user_id
    LEFT JOIN physiotherapist_profiles pp ON u.user_id = pp.user_id
    LEFT JOIN coach_profiles cp ON u.user_id = cp.user_id
    LEFT JOIN caretaker_profiles cap ON u.user_id = cap.user_id
  WHERE u.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_user_profile_ids IS 'Returns all role profile IDs for a user';

-- Check if user can access athlete data
CREATE OR REPLACE FUNCTION can_access_athlete(p_user_id UUID, p_athlete_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_can_access BOOLEAN;
  v_user_roles TEXT[];
BEGIN
  -- Get user roles
  SELECT roles INTO v_user_roles FROM users WHERE user_id = p_user_id;
  
  -- If user is the athlete themselves
  IF EXISTS (
    SELECT 1 FROM athlete_profiles 
    WHERE athlete_id = p_athlete_id AND user_id = p_user_id
  ) THEN
    RETURN TRUE;
  END IF;
  
  -- If user is assigned physiotherapist
  IF 'physiotherapist' = ANY(v_user_roles) THEN
    IF EXISTS (
      SELECT 1 FROM athlete_teams at
        JOIN physiotherapist_profiles pp ON at.physiotherapist_id = pp.physiotherapist_id
      WHERE at.athlete_id = p_athlete_id 
        AND pp.user_id = p_user_id 
        AND at.status = 'active'
    ) THEN
      RETURN TRUE;
    END IF;
  END IF;
  
  -- If user is assigned coach
  IF 'coach' = ANY(v_user_roles) THEN
    IF EXISTS (
      SELECT 1 FROM athlete_teams at
        JOIN coach_profiles cp ON at.coach_id = cp.coach_id
      WHERE at.athlete_id = p_athlete_id 
        AND cp.user_id = p_user_id 
        AND at.status = 'active'
    ) THEN
      RETURN TRUE;
    END IF;
  END IF;
  
  -- If user is assigned caretaker
  IF 'caretaker' = ANY(v_user_roles) THEN
    IF EXISTS (
      SELECT 1 FROM athlete_teams at
        JOIN caretaker_profiles cap ON at.caretaker_id = cap.caretaker_id
      WHERE at.athlete_id = p_athlete_id 
        AND cap.user_id = p_user_id 
        AND at.status = 'active'
    ) THEN
      RETURN TRUE;
    END IF;
  END IF;
  
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION can_access_athlete IS 'Checks if a user has access to athlete data based on active team assignments';

-- Get all accessible athletes for a user
CREATE OR REPLACE FUNCTION get_accessible_athletes(p_user_id UUID)
RETURNS TABLE (athlete_id UUID) AS $$
DECLARE
  v_user_roles TEXT[];
BEGIN
  SELECT roles INTO v_user_roles FROM users WHERE user_id = p_user_id;
  
  -- If user is an athlete, return only themselves
  IF 'athlete' = ANY(v_user_roles) THEN
    RETURN QUERY
    SELECT ap.athlete_id FROM athlete_profiles ap WHERE ap.user_id = p_user_id;
    RETURN;
  END IF;
  
  -- If user is a physiotherapist, return assigned athletes
  IF 'physiotherapist' = ANY(v_user_roles) THEN
    RETURN QUERY
    SELECT DISTINCT at.athlete_id 
    FROM athlete_teams at
      JOIN physiotherapist_profiles pp ON at.physiotherapist_id = pp.physiotherapist_id
    WHERE pp.user_id = p_user_id AND at.status = 'active';
    RETURN;
  END IF;
  
  -- If user is a coach, return assigned athletes
  IF 'coach' = ANY(v_user_roles) THEN
    RETURN QUERY
    SELECT DISTINCT at.athlete_id 
    FROM athlete_teams at
      JOIN coach_profiles cp ON at.coach_id = cp.coach_id
    WHERE cp.user_id = p_user_id AND at.status = 'active';
    RETURN;
  END IF;
  
  -- If user is a caretaker, return assigned athletes
  IF 'caretaker' = ANY(v_user_roles) THEN
    RETURN QUERY
    SELECT DISTINCT at.athlete_id 
    FROM athlete_teams at
      JOIN caretaker_profiles cap ON at.caretaker_id = cap.caretaker_id
    WHERE cap.user_id = p_user_id AND at.status = 'active';
    RETURN;
  END IF;
  
  -- No access
  RETURN;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_accessible_athletes IS 'Returns all athlete IDs accessible to a user based on their role';

-- ============================================
-- 2. ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS on all sensitive tables
ALTER TABLE athlete_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE clinical_notes ENABLE ROW LEVEL SECURITY;

-- Policy: Athlete Profiles
CREATE POLICY athlete_profiles_access_policy ON athlete_profiles
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
  );

COMMENT ON POLICY athlete_profiles_access_policy ON athlete_profiles IS 'Users can only access athlete profiles they are authorized for';

-- Policy: Assessments
CREATE POLICY assessments_access_policy ON assessments
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
  );

-- Policy: Exercise Assignments
CREATE POLICY exercise_assignments_access_policy ON exercise_assignments
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
  );

-- Policy: Exercise Sessions
CREATE POLICY exercise_sessions_access_policy ON exercise_sessions
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
  );

-- Policy: Daily Tasks
CREATE POLICY daily_tasks_access_policy ON daily_tasks
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
  );

-- Policy: Progress Milestones
CREATE POLICY progress_milestones_access_policy ON progress_milestones
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
  );

-- Policy: Clinical Notes (with privacy check)
CREATE POLICY clinical_notes_access_policy ON clinical_notes
  FOR ALL
  USING (
    athlete_id IN (SELECT get_accessible_athletes(current_setting('app.current_user_id')::UUID))
    AND (
      NOT is_private 
      OR author_id = current_setting('app.current_user_id')::UUID
    )
  );

COMMENT ON POLICY clinical_notes_access_policy ON clinical_notes IS 'Access clinical notes with privacy enforcement';

-- ============================================
-- 3. APPLICATION USER SESSION SETUP
-- ============================================

-- Function to set current user ID in session (called by application)
CREATE OR REPLACE FUNCTION set_current_user(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
  PERFORM set_config('app.current_user_id', p_user_id::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION set_current_user IS 'Sets the current user ID in session for RLS policies. Call this at the start of each request.';

-- ============================================
-- 4. AUDIT FUNCTIONS
-- ============================================

-- Audit log table
CREATE TABLE audit_log (
  log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(user_id),
  action VARCHAR(50) NOT NULL, -- SELECT, INSERT, UPDATE, DELETE
  table_name VARCHAR(100) NOT NULL,
  record_id UUID,
  old_data JSONB,
  new_data JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);

COMMENT ON TABLE audit_log IS 'Audit trail of sensitive data access and modifications';

-- Generic audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
  v_user_id UUID;
BEGIN
  -- Get current user ID from session
  BEGIN
    v_user_id := current_setting('app.current_user_id')::UUID;
  EXCEPTION WHEN OTHERS THEN
    v_user_id := NULL;
  END;
  
  -- Log the action
  IF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log (user_id, action, table_name, record_id, old_data)
    VALUES (v_user_id, 'DELETE', TG_TABLE_NAME, OLD.athlete_id, row_to_json(OLD)::JSONB);
    RETURN OLD;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_log (user_id, action, table_name, record_id, old_data, new_data)
    VALUES (v_user_id, 'UPDATE', TG_TABLE_NAME, NEW.athlete_id, row_to_json(OLD)::JSONB, row_to_json(NEW)::JSONB);
    RETURN NEW;
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO audit_log (user_id, action, table_name, record_id, new_data)
    VALUES (v_user_id, 'INSERT', TG_TABLE_NAME, NEW.athlete_id, row_to_json(NEW)::JSONB);
    RETURN NEW;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_athlete_profiles AFTER INSERT OR UPDATE OR DELETE ON athlete_profiles
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_assessments AFTER INSERT OR UPDATE OR DELETE ON assessments
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_clinical_notes AFTER INSERT OR UPDATE OR DELETE ON clinical_notes
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

COMMENT ON FUNCTION audit_trigger_function IS 'Generic audit trigger for tracking data changes';

-- ============================================
-- 5. USAGE EXAMPLES
-- ============================================

-- Example 1: Set current user at start of request
-- SELECT set_current_user('user-uuid-here');

-- Example 2: Check if user can access athlete
-- SELECT can_access_athlete('user-uuid', 'athlete-uuid');

-- Example 3: Get all accessible athletes for current user
-- SELECT * FROM get_accessible_athletes('user-uuid');

-- Example 4: Query with RLS automatically applied (after setting current user)
-- SELECT set_current_user('physio-user-uuid');
-- SELECT * FROM athlete_profiles; -- Only returns accessible athletes

-- ============================================
-- END OF SCRIPT
-- ============================================
