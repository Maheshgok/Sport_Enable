-- ============================================
-- Relationship Management Schema
-- Invite-based associations with admin approval
-- ============================================

SET search_path TO physio_app, public;

-- ============================================
-- 1. PARENT/GUARDIAN PROFILES
-- ============================================
CREATE TABLE parent_guardian_profiles (
  guardian_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Guardian type
  guardian_type VARCHAR(50) CHECK (guardian_type IN ('parent', 'legal_guardian', 'manager', 'family_member', 'agent')),
  relationship_to_athlete VARCHAR(100), -- "Mother", "Father", "Agent", etc.
  
  -- Contact information
  emergency_contact BOOLEAN DEFAULT false,
  alternate_phone VARCHAR(20),
  
  -- Capacity
  max_athletes INTEGER DEFAULT 5 CHECK (max_athletes > 0),
  current_athletes INTEGER DEFAULT 0 CHECK (current_athletes >= 0),
  
  -- Permissions (what they can do with athlete data)
  can_view_medical BOOLEAN DEFAULT false,
  can_view_videos BOOLEAN DEFAULT true,
  can_view_reports BOOLEAN DEFAULT true,
  can_upload_videos BOOLEAN DEFAULT false,
  can_schedule_sessions BOOLEAN DEFAULT false,
  
  -- Verification
  identity_verified BOOLEAN DEFAULT false,
  verified_at TIMESTAMP,
  verified_by UUID REFERENCES users(user_id),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE parent_guardian_profiles IS 'Parents, guardians, managers, and agents associated with athletes';

-- ============================================
-- 2. RELATIONSHIP INVITATIONS
-- ============================================
CREATE TABLE relationship_invitations (
  invitation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Who is inviting whom
  inviter_id UUID NOT NULL REFERENCES users(user_id),
  invitee_email VARCHAR(255) NOT NULL,
  invitee_id UUID REFERENCES users(user_id), -- NULL until they register/accept
  
  -- Relationship type
  relationship_type VARCHAR(50) NOT NULL 
    CHECK (relationship_type IN (
      'coach_athlete',
      'coach_parent',
      'coach_physiotherapist', 
      'coach_coach',
      'parent_athlete', 
      'guardian_athlete', 
      'manager_athlete',
      'physiotherapist_athlete',
      'physiotherapist_coach'
    )),
  
  -- Which profiles are involved
  athlete_id UUID REFERENCES athlete_profiles(athlete_id),
  coach_id UUID REFERENCES coach_profiles(coach_id),
  physiotherapist_id UUID REFERENCES physiotherapist_profiles(physiotherapist_id),
  
  -- Invitation details
  invitation_message TEXT,
  invitation_token VARCHAR(100) UNIQUE NOT NULL,
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending'
    CHECK (status IN ('pending', 'accepted', 'rejected', 'expired', 'revoked', 'cancelled')),
  
  -- Response
  response_message TEXT,
  responded_at TIMESTAMP,
  
  -- Expiration
  expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '7 days',
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Ensure at least one profile is specified
  CONSTRAINT must_have_profile CHECK (
    athlete_id IS NOT NULL OR coach_id IS NOT NULL OR physiotherapist_id IS NOT NULL
  )
);

COMMENT ON TABLE relationship_invitations IS 'Pending invitations to establish relationships between users';

CREATE INDEX idx_invitations_invitee_email ON relationship_invitations(invitee_email);
CREATE INDEX idx_invitations_invitee_id ON relationship_invitations(invitee_id);
CREATE INDEX idx_invitations_status ON relationship_invitations(status);
CREATE INDEX idx_invitations_token ON relationship_invitations(invitation_token);
CREATE INDEX idx_invitations_expires ON relationship_invitations(expires_at);

-- ============================================
-- 3. RELATIONSHIP CHANGE REQUESTS
-- ============================================
CREATE TABLE relationship_change_requests (
  request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Request type
  request_type VARCHAR(50) NOT NULL
    CHECK (request_type IN ('add_relationship', 'remove_relationship', 'modify_permissions')),
  
  -- Who is making the request
  requested_by UUID NOT NULL REFERENCES users(user_id),
  
  -- Relationship details
  relationship_type VARCHAR(50) NOT NULL,
  user_a_id UUID NOT NULL REFERENCES users(user_id),
  user_b_id UUID NOT NULL REFERENCES users(user_id),
  
  -- If this is following an invitation
  invitation_id UUID REFERENCES relationship_invitations(invitation_id),
  
  -- Request details
  reason TEXT,
  request_data JSONB, -- Additional data (e.g., new permissions)
  
  -- Supporting documents
  attachments JSONB, -- URLs to supporting documents
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending_admin'
    CHECK (status IN ('pending_admin', 'approved', 'rejected', 'cancelled', 'superseded')),
  
  -- Priority
  priority VARCHAR(20) DEFAULT 'normal'
    CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
  
  -- Admin review
  reviewed_by UUID REFERENCES users(user_id),
  reviewed_at TIMESTAMP,
  admin_notes TEXT,
  rejection_reason TEXT,
  
  -- Notifications
  email_sent_to_admin BOOLEAN DEFAULT false,
  email_sent_at TIMESTAMP,
  notification_count INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE relationship_change_requests IS 'Requests for relationship changes requiring admin approval';

CREATE INDEX idx_change_requests_status ON relationship_change_requests(status);
CREATE INDEX idx_change_requests_requested_by ON relationship_change_requests(requested_by);
CREATE INDEX idx_change_requests_priority ON relationship_change_requests(priority, status);
CREATE INDEX idx_change_requests_created ON relationship_change_requests(created_at DESC);

-- ============================================
-- 4. ACTIVE RELATIONSHIPS
-- ============================================
CREATE TABLE relationships (
  relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Relationship type
  relationship_type VARCHAR(50) NOT NULL
    CHECK (relationship_type IN (
      'coach_athlete',
      'coach_parent',
      'coach_physiotherapist',
      'coach_coach',
      'parent_athlete',
      'guardian_athlete', 
      'manager_athlete',
      'physiotherapist_athlete',
      'physiotherapist_coach'
    )),
  
  -- Users involved (primary and secondary)
  primary_user_id UUID NOT NULL REFERENCES users(user_id),
  secondary_user_id UUID NOT NULL REFERENCES users(user_id),
  
  -- Specific profiles
  athlete_id UUID REFERENCES athlete_profiles(athlete_id),
  coach_id UUID REFERENCES coach_profiles(coach_id),
  physiotherapist_id UUID REFERENCES physiotherapist_profiles(physiotherapist_id),
  guardian_id UUID REFERENCES parent_guardian_profiles(guardian_id),
  
  -- Status
  status VARCHAR(20) DEFAULT 'active'
    CHECK (status IN ('active', 'suspended', 'terminated', 'on_hold')),
  
  -- Permissions and access control
  permissions JSONB NOT NULL DEFAULT '{}',
  
  -- How was this established
  established_via UUID REFERENCES relationship_invitations(invitation_id),
  approved_by UUID NOT NULL REFERENCES users(user_id), -- Admin who approved
  approval_request_id UUID REFERENCES relationship_change_requests(request_id),
  
  -- Metadata
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  suspended_at TIMESTAMP,
  terminated_at TIMESTAMP,
  terminated_reason TEXT,
  
  -- Ensure unique relationships
  CONSTRAINT unique_active_relationship UNIQUE(relationship_type, primary_user_id, secondary_user_id),
  
  -- Ensure users are different
  CONSTRAINT different_users CHECK (primary_user_id != secondary_user_id)
);

COMMENT ON TABLE relationships IS 'Active relationships between users (coach-athlete, parent-athlete, etc.)';
COMMENT ON COLUMN relationships.primary_user_id IS 'The "owner" of the relationship (e.g., athlete)';
COMMENT ON COLUMN relationships.secondary_user_id IS 'The "associated" user (e.g., coach, parent)';

CREATE INDEX idx_relationships_primary ON relationships(primary_user_id);
CREATE INDEX idx_relationships_secondary ON relationships(secondary_user_id);
CREATE INDEX idx_relationships_athlete ON relationships(athlete_id);
CREATE INDEX idx_relationships_coach ON relationships(coach_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
CREATE INDEX idx_relationships_status ON relationships(status);

-- ============================================
-- 5. AUDIT LOG
-- ============================================
CREATE TABLE relationship_audit_log (
  log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- What happened
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(50) NOT NULL, -- 'invitation', 'request', 'relationship'
  entity_id UUID NOT NULL,
  
  -- Who did it
  actor_id UUID REFERENCES users(user_id),
  actor_role VARCHAR(50), -- Role at time of action
  
  -- Details
  old_data JSONB,
  new_data JSONB,
  changes JSONB, -- Specific fields that changed
  
  -- Context
  ip_address VARCHAR(50),
  user_agent TEXT,
  notes TEXT,
  
  -- Timestamp
  created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE relationship_audit_log IS 'Complete audit trail of all relationship-related actions';

CREATE INDEX idx_audit_entity ON relationship_audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_actor ON relationship_audit_log(actor_id);
CREATE INDEX idx_audit_created ON relationship_audit_log(created_at DESC);
CREATE INDEX idx_audit_action ON relationship_audit_log(action);

-- ============================================
-- 6. NOTIFICATION PREFERENCES
-- ============================================
CREATE TABLE relationship_notification_preferences (
  preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  
  -- Email notifications
  email_on_invitation BOOLEAN DEFAULT true,
  email_on_acceptance BOOLEAN DEFAULT true,
  email_on_rejection BOOLEAN DEFAULT true,
  email_on_approval BOOLEAN DEFAULT true,
  email_on_termination BOOLEAN DEFAULT true,
  
  -- In-app notifications
  inapp_on_invitation BOOLEAN DEFAULT true,
  inapp_on_acceptance BOOLEAN DEFAULT true,
  inapp_on_changes BOOLEAN DEFAULT true,
  
  -- Digest preferences
  send_daily_digest BOOLEAN DEFAULT false,
  send_weekly_digest BOOLEAN DEFAULT false,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_user_preferences UNIQUE(user_id)
);

-- ============================================
-- 7. FUNCTIONS
-- ============================================

-- Function: Create audit log entry
CREATE OR REPLACE FUNCTION log_relationship_action(
  p_action VARCHAR,
  p_entity_type VARCHAR,
  p_entity_id UUID,
  p_actor_id UUID,
  p_old_data JSONB DEFAULT NULL,
  p_new_data JSONB DEFAULT NULL,
  p_notes TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
  INSERT INTO relationship_audit_log (
    action, entity_type, entity_id, actor_id, old_data, new_data, notes
  ) VALUES (
    p_action, p_entity_type, p_entity_id, p_actor_id, p_old_data, p_new_data, p_notes
  );
END;
$$ LANGUAGE plpgsql;

-- Function: Generate invitation token
CREATE OR REPLACE FUNCTION generate_invitation_token() RETURNS VARCHAR AS $$
DECLARE
  token VARCHAR(100);
  token_exists BOOLEAN;
BEGIN
  LOOP
    -- Generate random token
    token := encode(gen_random_bytes(32), 'hex');
    
    -- Check if it already exists
    SELECT EXISTS(
      SELECT 1 FROM relationship_invitations WHERE invitation_token = token
    ) INTO token_exists;
    
    EXIT WHEN NOT token_exists;
  END LOOP;
  
  RETURN token;
END;
$$ LANGUAGE plpgsql;

-- Function: Expire old invitations
CREATE OR REPLACE FUNCTION expire_old_invitations() RETURNS INTEGER AS $$
DECLARE
  expired_count INTEGER;
BEGIN
  UPDATE relationship_invitations
  SET status = 'expired',
      updated_at = NOW()
  WHERE status = 'pending'
    AND expires_at < NOW();
  
  GET DIAGNOSTICS expired_count = ROW_COUNT;
  
  RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Get user's active relationships
CREATE OR REPLACE FUNCTION get_user_relationships(p_user_id UUID)
RETURNS TABLE (
  relationship_id UUID,
  relationship_type VARCHAR,
  other_user_id UUID,
  other_user_name VARCHAR,
  other_user_email VARCHAR,
  status VARCHAR,
  created_at TIMESTAMP
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    r.relationship_id,
    r.relationship_type,
    CASE 
      WHEN r.primary_user_id = p_user_id THEN r.secondary_user_id
      ELSE r.primary_user_id
    END as other_user_id,
    u.first_name || ' ' || u.last_name as other_user_name,
    u.email as other_user_email,
    r.status,
    r.created_at
  FROM relationships r
  JOIN users u ON (
    CASE 
      WHEN r.primary_user_id = p_user_id THEN r.secondary_user_id
      ELSE r.primary_user_id
    END = u.user_id
  )
  WHERE (r.primary_user_id = p_user_id OR r.secondary_user_id = p_user_id)
    AND r.status = 'active'
  ORDER BY r.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 8. TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_invitations_updated_at
  BEFORE UPDATE ON relationship_invitations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_requests_updated_at
  BEFORE UPDATE ON relationship_change_requests
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at
  BEFORE UPDATE ON relationships
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Log invitation status changes
CREATE OR REPLACE FUNCTION log_invitation_status_change()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'UPDATE' AND OLD.status != NEW.status) THEN
    PERFORM log_relationship_action(
      'invitation_status_changed',
      'invitation',
      NEW.invitation_id,
      NEW.invitee_id,
      row_to_json(OLD)::jsonb,
      row_to_json(NEW)::jsonb,
      'Status changed from ' || OLD.status || ' to ' || NEW.status
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_invitation_changes
  AFTER UPDATE ON relationship_invitations
  FOR EACH ROW
  EXECUTE FUNCTION log_invitation_status_change();

-- ============================================
-- 9. VIEWS
-- ============================================

-- View: Pending invitations by user
CREATE VIEW v_user_pending_invitations AS
SELECT 
  i.invitation_id,
  i.relationship_type,
  i.invitation_message,
  i.created_at,
  i.expires_at,
  u_inviter.user_id as inviter_id,
  u_inviter.first_name || ' ' || u_inviter.last_name as inviter_name,
  u_inviter.email as inviter_email,
  i.invitee_email,
  i.invitation_token
FROM relationship_invitations i
JOIN users u_inviter ON i.inviter_id = u_inviter.user_id
WHERE i.status = 'pending'
  AND i.expires_at > NOW();

-- View: Relationship change requests for admin
CREATE VIEW v_admin_pending_requests AS
SELECT 
  r.request_id,
  r.request_type,
  r.relationship_type,
  r.reason,
  r.priority,
  r.created_at,
  u_requester.first_name || ' ' || u_requester.last_name as requester_name,
  u_requester.email as requester_email,
  u_a.first_name || ' ' || u_a.last_name as user_a_name,
  u_b.first_name || ' ' || u_b.last_name as user_b_name,
  r.email_sent_to_admin,
  r.notification_count
FROM relationship_change_requests r
JOIN users u_requester ON r.requested_by = u_requester.user_id
JOIN users u_a ON r.user_a_id = u_a.user_id
JOIN users u_b ON r.user_b_id = u_b.user_id
WHERE r.status = 'pending_admin'
ORDER BY 
  CASE r.priority
    WHEN 'urgent' THEN 1
    WHEN 'high' THEN 2
    WHEN 'normal' THEN 3
    WHEN 'low' THEN 4
  END,
  r.created_at ASC;

-- View: User relationship summary
CREATE VIEW v_user_relationship_summary AS
SELECT 
  u.user_id,
  u.email,
  u.first_name || ' ' || u.last_name as name,
  COUNT(DISTINCT CASE WHEN r.relationship_type = 'coach_athlete' THEN r.relationship_id END) as coach_relationships,
  COUNT(DISTINCT CASE WHEN r.relationship_type IN ('parent_athlete', 'guardian_athlete') THEN r.relationship_id END) as guardian_relationships,
  COUNT(DISTINCT CASE WHEN r.relationship_type = 'physiotherapist_athlete' THEN r.relationship_id END) as physio_relationships,
  COUNT(DISTINCT CASE WHEN i.status = 'pending' THEN i.invitation_id END) as pending_invitations
FROM users u
LEFT JOIN relationships r ON (u.user_id = r.primary_user_id OR u.user_id = r.secondary_user_id)
LEFT JOIN relationship_invitations i ON (u.user_id = i.invitee_id OR u.email = i.invitee_email)
GROUP BY u.user_id, u.email, u.first_name, u.last_name;

-- ============================================
-- 10. INITIAL DATA & CONSTRAINTS
-- ============================================

-- Add parent/guardian role to valid roles
ALTER TABLE users DROP CONSTRAINT IF EXISTS at_least_one_role;
ALTER TABLE users ADD CONSTRAINT at_least_one_role 
  CHECK (array_length(roles, 1) > 0);

COMMENT ON SCHEMA physio_app IS 'Moove - Relationship management with invite system and admin approval';
