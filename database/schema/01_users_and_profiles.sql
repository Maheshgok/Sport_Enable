-- ============================================
-- Users and Role Profiles
-- Schema: physio_app
-- Description: Core user accounts and role-specific profiles
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. BASE USER TABLE
-- ============================================
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  roles TEXT[] NOT NULL, -- Array of roles: athlete, physiotherapist, coach, caretaker
  
  -- Profile information
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  avatar VARCHAR(500), -- URL or base64 encoded initials
  phone VARCHAR(20),
  date_of_birth DATE,
  gender VARCHAR(20),
  
  -- Organization (for multi-tenant setups)
  organization_id UUID,
  
  -- Account status
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,
  
  -- Constraints
  CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
  CONSTRAINT at_least_one_role CHECK (array_length(roles, 1) > 0)
);

COMMENT ON TABLE users IS 'Base user accounts with authentication and profile data';
COMMENT ON COLUMN users.roles IS 'Array of user roles - a user can have multiple roles';

-- ============================================
-- 2. ATHLETE PROFILE
-- ============================================
CREATE TABLE athlete_profiles (
  athlete_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Sport information
  sport VARCHAR(100) NOT NULL,
  position VARCHAR(100),
  team VARCHAR(200),
  level VARCHAR(50) CHECK (level IN ('professional', 'collegiate', 'amateur', 'recreational')),
  
  -- Injury information
  current_injury VARCHAR(500),
  injury_date DATE,
  injury_type VARCHAR(100),
  injury_severity VARCHAR(20) CHECK (injury_severity IN ('mild', 'moderate', 'severe', 'critical')),
  recovery_timeline VARCHAR(200),
  
  -- Status
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'recovering', 'cleared', 'inactive')),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE athlete_profiles IS 'Athlete-specific profile data including sport and injury information';
COMMENT ON COLUMN athlete_profiles.user_id IS 'Links to base user account - enforces 1:1 relationship';

-- ============================================
-- 3. PHYSIOTHERAPIST PROFILE
-- ============================================
CREATE TABLE physiotherapist_profiles (
  physiotherapist_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Credentials
  license_number VARCHAR(100) UNIQUE NOT NULL,
  specializations TEXT[], -- Array of specialization areas
  certifications TEXT[], -- Array of certification names
  
  -- Caseload management
  max_caseload INTEGER DEFAULT 15 CHECK (max_caseload > 0),
  current_caseload INTEGER DEFAULT 0 CHECK (current_caseload >= 0),
  
  -- Availability
  timezone VARCHAR(50) DEFAULT 'UTC',
  schedule JSONB, -- Flexible schedule storage
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE physiotherapist_profiles IS 'Physiotherapist credentials and availability';
COMMENT ON COLUMN physiotherapist_profiles.current_caseload IS 'Auto-calculated count of assigned athletes';

-- ============================================
-- 4. COACH PROFILE
-- ============================================
CREATE TABLE coach_profiles (
  coach_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Coaching information
  sport VARCHAR(100) NOT NULL,
  specialization VARCHAR(200),
  years_experience INTEGER CHECK (years_experience >= 0),
  coaching_philosophy TEXT,
  
  -- Athlete management
  max_athletes INTEGER DEFAULT 20 CHECK (max_athletes > 0),
  current_athletes INTEGER DEFAULT 0 CHECK (current_athletes >= 0),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE coach_profiles IS 'Coach credentials and coaching information';
COMMENT ON COLUMN coach_profiles.current_athletes IS 'Auto-calculated count of assigned athletes';

-- ============================================
-- 5. CARETAKER PROFILE
-- ============================================
CREATE TABLE caretaker_profiles (
  caretaker_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Caretaker information
  caretaker_type VARCHAR(50) CHECK (caretaker_type IN ('nurse', 'assistant', 'trainer', 'family', 'other')),
  certifications TEXT[], -- Array of certification names
  qualifications TEXT,
  
  -- Athlete management
  max_athletes INTEGER DEFAULT 10 CHECK (max_athletes > 0),
  current_athletes INTEGER DEFAULT 0 CHECK (current_athletes >= 0),
  
  -- Shift schedule
  timezone VARCHAR(50) DEFAULT 'UTC',
  shift_schedule JSONB, -- Flexible schedule storage
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE caretaker_profiles IS 'Caretaker credentials and shift information';
COMMENT ON COLUMN caretaker_profiles.caretaker_type IS 'Type of caretaker role';

-- ============================================
-- 6. TRIGGER: UPDATE TIMESTAMPS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables
CREATE TRIGGER update_users_timestamp BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_athlete_profiles_timestamp BEFORE UPDATE ON athlete_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_physiotherapist_profiles_timestamp BEFORE UPDATE ON physiotherapist_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coach_profiles_timestamp BEFORE UPDATE ON coach_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_caretaker_profiles_timestamp BEFORE UPDATE ON caretaker_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 7. INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_organization ON users(organization_id) WHERE organization_id IS NOT NULL;

CREATE INDEX idx_athlete_profiles_user_id ON athlete_profiles(user_id);
CREATE INDEX idx_athlete_profiles_status ON athlete_profiles(status);

CREATE INDEX idx_physio_profiles_user_id ON physiotherapist_profiles(user_id);
CREATE INDEX idx_physio_profiles_license ON physiotherapist_profiles(license_number);

CREATE INDEX idx_coach_profiles_user_id ON coach_profiles(user_id);
CREATE INDEX idx_coach_profiles_sport ON coach_profiles(sport);

CREATE INDEX idx_caretaker_profiles_user_id ON caretaker_profiles(user_id);
CREATE INDEX idx_caretaker_profiles_type ON caretaker_profiles(caretaker_type);

-- ============================================
-- END OF SCRIPT
-- ============================================
