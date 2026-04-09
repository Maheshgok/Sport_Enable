# Relationship Management System Design
## Invite-Based Associations & Admin Approval

---

## Overview

A secure system where:
1. **Athletes** onboard with sport selection
2. **Coaches** can invite athletes (or vice versa) - requires acceptance
3. **Parents/Guardians** can be associated via invite mechanism
4. **All relationship changes** require super admin authorization via email request

---

## Key Principles

1. **No Direct Changes**: Users cannot directly modify relationships
2. **Invite-Accept Flow**: All associations start with invite → accept
3. **Admin Gatekeeper**: Super admin must approve all relationship changes
4. **Email Notifications**: All requests go through email to admin
5. **Audit Trail**: Complete history of all relationship changes

---

## Database Schema

### 1. Relationship Invitations

```sql
CREATE TABLE physio_app.relationship_invitations (
  invitation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Who is inviting whom
  inviter_id UUID REFERENCES physio_app.users(user_id),
  invitee_email VARCHAR(255) NOT NULL,
  invitee_id UUID REFERENCES physio_app.users(user_id), -- NULL until they register
  
  -- Relationship type
  relationship_type VARCHAR(50) NOT NULL 
    CHECK (relationship_type IN ('coach_athlete', 'parent_athlete', 'guardian_athlete', 'manager_athlete')),
  
  -- For coach_athlete: which is the athlete
  athlete_id UUID REFERENCES physio_app.athlete_profiles(athlete_id),
  coach_id UUID REFERENCES physio_app.coach_profiles(coach_id),
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending'
    CHECK (status IN ('pending', 'accepted', 'rejected', 'expired', 'revoked')),
  
  -- Message
  invitation_message TEXT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '7 days',
  responded_at TIMESTAMP,
  
  -- Tokens
  invitation_token VARCHAR(100) UNIQUE NOT NULL, -- For accepting invite
  
  CONSTRAINT valid_relationship CHECK (
    (relationship_type = 'coach_athlete' AND athlete_id IS NOT NULL AND coach_id IS NOT NULL) OR
    (relationship_type IN ('parent_athlete', 'guardian_athlete', 'manager_athlete') AND athlete_id IS NOT NULL)
  )
);

CREATE INDEX idx_invitations_invitee_email ON physio_app.relationship_invitations(invitee_email);
CREATE INDEX idx_invitations_status ON physio_app.relationship_invitations(status);
CREATE INDEX idx_invitations_token ON physio_app.relationship_invitations(invitation_token);
```

### 2. Relationship Change Requests

```sql
CREATE TABLE physio_app.relationship_change_requests (
  request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Request details
  request_type VARCHAR(50) NOT NULL
    CHECK (request_type IN ('add_relationship', 'remove_relationship', 'change_role')),
  
  -- Who is making the request
  requested_by UUID REFERENCES physio_app.users(user_id),
  
  -- Relationship details
  relationship_type VARCHAR(50) NOT NULL,
  user_a_id UUID REFERENCES physio_app.users(user_id),
  user_b_id UUID REFERENCES physio_app.users(user_id),
  
  -- Additional data
  request_data JSONB, -- Any additional info
  reason TEXT,
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending_admin'
    CHECK (status IN ('pending_admin', 'approved', 'rejected', 'cancelled')),
  
  -- Admin review
  reviewed_by UUID REFERENCES physio_app.users(user_id),
  reviewed_at TIMESTAMP,
  admin_notes TEXT,
  
  -- Notifications
  email_sent BOOLEAN DEFAULT false,
  email_sent_at TIMESTAMP,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_change_requests_status ON physio_app.relationship_change_requests(status);
CREATE INDEX idx_change_requests_requested_by ON physio_app.relationship_change_requests(requested_by);
```

### 3. Active Relationships

```sql
CREATE TABLE physio_app.relationships (
  relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Relationship type
  relationship_type VARCHAR(50) NOT NULL
    CHECK (relationship_type IN ('coach_athlete', 'parent_athlete', 'guardian_athlete', 'manager_athlete')),
  
  -- Users involved
  user_a_id UUID REFERENCES physio_app.users(user_id),
  user_b_id UUID REFERENCES physio_app.users(user_id),
  
  -- For specific types
  athlete_id UUID REFERENCES physio_app.athlete_profiles(athlete_id),
  coach_id UUID REFERENCES physio_app.coach_profiles(coach_id),
  
  -- Status
  status VARCHAR(20) DEFAULT 'active'
    CHECK (status IN ('active', 'suspended', 'terminated')),
  
  -- How was this established
  established_via UUID REFERENCES physio_app.relationship_invitations(invitation_id),
  approved_by UUID REFERENCES physio_app.users(user_id), -- Admin who approved
  
  -- Permissions (what can each party do)
  permissions JSONB,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  terminated_at TIMESTAMP,
  
  CONSTRAINT unique_relationship UNIQUE(relationship_type, user_a_id, user_b_id)
);

CREATE INDEX idx_relationships_athlete ON physio_app.relationships(athlete_id);
CREATE INDEX idx_relationships_coach ON physio_app.relationships(coach_id);
CREATE INDEX idx_relationships_type ON physio_app.relationships(relationship_type);
CREATE INDEX idx_relationships_status ON physio_app.relationships(status);
```

### 4. Parent/Guardian Profiles

```sql
CREATE TABLE physio_app.parent_guardian_profiles (
  guardian_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES physio_app.users(user_id) ON DELETE CASCADE,
  
  -- Guardian type
  guardian_type VARCHAR(50) CHECK (guardian_type IN ('parent', 'legal_guardian', 'manager', 'family_member')),
  
  -- Contact information
  emergency_contact BOOLEAN DEFAULT false,
  relationship_to_athlete VARCHAR(100), -- "Mother", "Father", "Agent", etc.
  
  -- Can have multiple athletes
  max_athletes INTEGER DEFAULT 5,
  current_athletes INTEGER DEFAULT 0,
  
  -- Permissions
  can_view_medical BOOLEAN DEFAULT false,
  can_view_videos BOOLEAN DEFAULT true,
  can_view_reports BOOLEAN DEFAULT true,
  can_upload_videos BOOLEAN DEFAULT false,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE physio_app.parent_guardian_profiles IS 'Parents, guardians, and managers associated with athletes';
```

### 5. Audit Log

```sql
CREATE TABLE physio_app.relationship_audit_log (
  log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- What happened
  action VARCHAR(50) NOT NULL, -- 'invite_sent', 'invite_accepted', 'relationship_added', etc.
  
  -- Who did it
  actor_id UUID REFERENCES physio_app.users(user_id),
  
  -- Related records
  invitation_id UUID REFERENCES physio_app.relationship_invitations(invitation_id),
  relationship_id UUID REFERENCES physio_app.relationships(relationship_id),
  request_id UUID REFERENCES physio_app.relationship_change_requests(request_id),
  
  -- Details
  old_data JSONB,
  new_data JSONB,
  notes TEXT,
  
  -- Timestamp
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_actor ON physio_app.relationship_audit_log(actor_id);
CREATE INDEX idx_audit_created ON physio_app.relationship_audit_log(created_at DESC);
```

---

## User Flows

### Flow 1: Athlete Onboards with Sport Selection

```
1. Athlete registers → selects sport and position
2. Profile created with sport_id
3. No relationships yet
```

### Flow 2: Coach Invites Athlete

```
1. Coach finds athlete in system (by email/name)
2. Coach clicks "Invite Athlete"
3. System creates invitation record with token
4. Email sent to athlete with invite link
5. Athlete clicks link → sees invitation details
6. Athlete accepts invitation
7. System creates change request (pending_admin)
8. Email sent to super admin
9. Admin reviews and approves
10. Relationship created & both parties notified
```

### Flow 3: Athlete Invites Coach

```
Same as above, but initiated by athlete
```

### Flow 4: Parent/Guardian Association

```
1. Athlete (or existing guardian/coach) sends invite to parent's email
2. If parent not registered:
   - Email with invite link sent
   - Parent registers and invite auto-associates
3. If parent registered:
   - Parent sees pending invitation
   - Parent accepts
4. Change request created (pending_admin)
5. Super admin reviews and approves
6. Relationship established
```

### Flow 5: Remove Relationship

```
1. User requests relationship termination
2. Change request created (pending_admin)
3. Email to super admin with details
4. Admin reviews reason
5. Admin approves/rejects
6. If approved: relationship status → terminated
7. Both parties notified
```

---

## API Endpoints

### Invitation Management

```python
POST   /api/invitations/send
GET    /api/invitations/received
GET    /api/invitations/sent
POST   /api/invitations/{token}/accept
POST   /api/invitations/{token}/reject
GET    /api/invitations/{token}/details
```

### Relationship Management

```python
GET    /api/relationships/mine
GET    /api/athletes/{id}/relationships
GET    /api/coaches/{id}/relationships

POST   /api/relationships/request-change
GET    /api/relationships/requests/pending
```

### Admin Endpoints

```python
GET    /api/admin/relationship-requests
GET    /api/admin/relationship-requests/{id}
POST   /api/admin/relationship-requests/{id}/approve
POST   /api/admin/relationship-requests/{id}/reject

GET    /api/admin/relationships
GET    /api/admin/audit-log
```

---

## Permission Matrix

| User Type | Can Invite Coach | Can Invite Athlete | Can Invite Guardian | Can Invite Physio | View Own Relations | Admin Approval |
|-----------|------------------|-------------------|---------------------|-------------------|-------------------|----------------|
| Athlete   | ✅ Yes           | ❌ No             | ✅ Yes              | ✅ Yes            | ✅ Yes            | ✅ Required    |
| Coach     | ✅ Yes           | ✅ Yes            | ✅ Yes              | ✅ Yes            | ✅ Yes            | ✅ Required    |
| Physio    | ✅ Yes           | ✅ Yes            | ❌ No               | ❌ No             | ✅ Yes            | ✅ Required    |
| Parent    | ❌ NO            | ❌ NO             | ❌ NO               | ❌ NO             | ✅ Yes            | ✅ Required    |
| Guardian  | ❌ NO            | ❌ NO             | ❌ NO               | ❌ NO             | ✅ Yes            | ✅ Required    |
| Admin     | ✅ Yes           | ✅ Yes            | ✅ Yes              | ✅ Yes            | ✅ Yes            | ❌ Not Needed  |

**Key Rule:** Parents/Guardians can ONLY accept invitations. They cannot initiate any invitations.

---

## Email Templates

### Invitation Email

```
Subject: You've been invited to join [Athlete Name] on Moove

Hi [Recipient],

[Inviter Name] has invited you to connect on Moove as their [coach/parent/guardian].

Athlete: [Athlete Name]
Sport: [Sport]
Message: [Personal message]

[Accept Invitation Button] [Decline Button]

This invitation expires in 7 days.

If you don't have an account, you'll be able to create one when you accept.
```

### Admin Approval Request Email

```
Subject: Relationship Change Request Requires Approval

Hi Admin,

A new relationship change request requires your review:

Request Type: [Add/Remove Relationship]
Requested By: [Name] ([email])
Relationship: [Type]
Between: [User A] and [User B]
Reason: [Provided reason]

Date: [Timestamp]

[Review Request Button]

Please review this request in the admin portal.
```

### Approval Notification Email

```
Subject: Your relationship change request has been approved

Hi [User],

Good news! Your request to [add/remove] [relationship type] with [other user] 
has been approved by a system administrator.

You can now [access features based on relationship].

View your connections: [Dashboard Link]
```

---

## Security Considerations

1. **Token-based invites**: Unique, expiring tokens for each invitation
2. **Email verification**: Ensure invitee email is valid
3. **Rate limiting**: Prevent spam invitations
4. **Admin audit**: All relationship changes logged
5. **No direct modifications**: Users cannot bypass admin approval
6. **Permission boundaries**: Clear permission sets per relationship type

---

## Implementation Priority

### Phase 1: Core Invitation System
- Database schema
- Send/accept invitation endpoints
- Email notifications
- Basic invitation UI

### Phase 2: Admin Approval System  
- Change request creation
- Admin review interface
- Approval/rejection workflow
- Email to admins

### Phase 3: Relationship Management
- View relationships
- Request termination
- Permission enforcement
- Audit logging

### Phase 4: Guardian System
- Parent/guardian profiles
- Guardian-specific permissions
- Multiple athlete support
- Emergency contact features

---

## Key Differences from Previous Design

| Aspect | Previous | New Design |
|--------|----------|------------|
| Relationship Creation | Direct | Invite → Accept → Admin Approval |
| Coach-Athlete Link | Direct assignment | Mutual invitation |
| Parent Access | Not defined | Invite-based with permissions |
| Changes | User can modify | Super admin only |
| Audit | Basic | Complete audit trail |
| Workflow | Simple | Email-based approval chain |

---

This design ensures **complete control** over relationships while maintaining a **user-friendly invitation system** and **admin gatekeeper** for all changes.
