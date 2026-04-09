# Quick Reference: User Permissions

---

## Who Can Invite Whom?

```
┌─────────────────────────────────────────────────────────────┐
│                    INVITATION PERMISSIONS                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FROM: COACH                                                │
│  ├─ ✅ Can invite Athletes                                  │
│  ├─ ✅ Can invite Parents/Guardians                         │
│  ├─ ✅ Can invite Physiotherapists                          │
│  └─ ✅ Can invite Other Coaches                             │
│                                                             │
│  FROM: ATHLETE                                              │
│  ├─ ✅ Can invite Coaches                                   │
│  ├─ ✅ Can invite Parents/Guardians                         │
│  ├─ ✅ Can invite Physiotherapists                          │
│  └─ ❌ Cannot invite other Athletes                         │
│                                                             │
│  FROM: PHYSIOTHERAPIST                                      │
│  ├─ ✅ Can invite Athletes                                  │
│  ├─ ✅ Can invite Coaches                                   │
│  ├─ ❌ Cannot invite Parents                                │
│  └─ ❌ Cannot invite other Physios                          │
│                                                             │
│  FROM: PARENT/GUARDIAN                                      │
│  └─ ❌ CANNOT SEND ANY INVITATIONS                          │
│     (Can only accept invitations from others)               │
│                                                             │
│  FROM: ADMIN                                                │
│  └─ ✅ Can do anything                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Registration Requirements

| User Type | Role Value | Required Fields | Optional Fields |
|-----------|-----------|-----------------|-----------------|
| **Athlete** | `"athlete"` | • `sport_id`<br>• `position` (recommended) | - |
| **Coach** | `"coach"` | - | • `specialization`<br>• `years_of_experience` |
| **Physiotherapist** | `"physiotherapist"` | - | • `specialization`<br>• `license_number` |
| **Parent/Guardian** | `"parent"` | • `guardian_type` | • `relationship_to_athlete` |

### Guardian Types
- `"parent"` - Mother or Father
- `"legal_guardian"` - Legal guardian (not parent)
- `"manager"` - Sports manager
- `"agent"` - Professional agent  
- `"family_member"` - Other family member

---

## Relationship Types

| Type | Description | Who Can Initiate |
|------|-------------|------------------|
| `coach_athlete` | Coach training athlete | Coach OR Athlete |
| `coach_parent` | Coach-parent connection | **Coach ONLY** |
| `coach_physiotherapist` | Coach-physio coordination | Coach OR Physio |
| `coach_coach` | Coach collaboration | **Coach ONLY** |
| `parent_athlete` | Parent of athlete | **Athlete ONLY** |
| `guardian_athlete` | Guardian of athlete | **Athlete ONLY** |
| `manager_athlete` | Manager of athlete | **Athlete ONLY** |
| `physiotherapist_athlete` | Physio treating athlete | Athlete OR Physio |
| `physiotherapist_coach` | Physio-coach coordination | **Physio ONLY** |

---

## Workflow States

### Invitation States
- `pending` - Awaiting response
- `accepted` - Accepted by invitee
- `rejected` - Rejected by invitee
- `expired` - Past 7-day expiration
- `revoked` - Cancelled by inviter
- `cancelled` - Cancelled by system

### Change Request States
- `pending_admin` - Awaiting admin approval
- `approved` - Admin approved
- `rejected` - Admin rejected
- `cancelled` - User cancelled
- `superseded` - Replaced by newer request

### Relationship States
- `active` - Currently active
- `suspended` - Temporarily suspended
- `terminated` - Permanently ended
- `on_hold` - On hold (future use)

---

## API Quick Reference

### Registration
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete|coach|physiotherapist|parent"],
  
  # If athlete:
  "sport_id": "uuid",
  "position": "Forward",
  
  # If parent:
  "guardian_type": "parent|legal_guardian|manager|agent",
  "relationship_to_athlete": "Mother",
  
  # If coach:
  "specialization": "Football",
  "years_of_experience": 10,
  
  # If physiotherapist:
  "specialization": "Sports Medicine",
  "license_number": "PT-12345"
}
```

### Send Invitation
```bash
POST /api/invitations/send
Authorization: Bearer {token}
{
  "invitee_email": "user@example.com",
  "relationship_type": "coach_athlete",
  "message": "Optional message"
}

# Returns 403 if user doesn't have permission
```

### View Invitations
```bash
GET /api/invitations/received    # Invitations I received
GET /api/invitations/sent        # Invitations I sent
```

### Accept/Reject
```bash
POST /api/invitations/{token}/accept
POST /api/invitations/{token}/reject
```

### View Relationships
```bash
GET /api/relationships/mine      # My active relationships
```

### Admin Approval
```bash
GET  /api/admin/relationship-requests              # View pending
POST /api/admin/relationship-requests/{id}/approve  # Approve
POST /api/admin/relationship-requests/{id}/reject   # Reject
```

---

## Permission Matrix

|  | Coach | Athlete | Physio | Parent | Admin |
|---|:---:|:---:|:---:|:---:|:---:|
| **Send Invitations** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ NO | ✅ Yes |
| **Accept Invitations** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Invite Athletes** | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Invite Coaches** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Invite Parents** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Invite Physios** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Approve Changes** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Error Codes

### 400 Bad Request
- Missing required fields
- Invalid email format
- Invalid relationship type

### 403 Forbidden
- User doesn't have permission to send invite
- Parent trying to send invitation
- Non-admin trying to approve

### 404 Not Found
- Invitation not found
- Invitation expired
- User not found

### 409 Conflict
- Email already registered
- Invitation already pending
- Relationship already exists

---

## Email Triggers

| Event | Recipients | Subject |
|-------|-----------|---------|
| Invitation sent | Invitee | "You've been invited by [Name]" |
| Invitation accepted | Admin(s) | "Relationship change requires approval" |
| Request approved | Both users | "Your relationship has been approved" |
| Request rejected | Requester | "Your request was not approved" |
| Relationship terminated | Both users | "Relationship terminated" |

---

## Default Permissions (Parent/Guardian)

```json
{
  "can_view_medical": false,      // No medical access by default
  "can_view_videos": true,        // Can view videos
  "can_view_reports": true,       // Can view reports
  "can_upload_videos": false,     // Cannot upload
  "can_schedule_sessions": false  // Cannot schedule
}
```

Permissions can be customized during invitation or by admin.

---

## Common Workflows

### 1. Coach Builds Team
```
Coach → Invite Athlete → Athlete Accepts → Admin Approves ✅
Coach → Invite Parent  → Parent Accepts  → Admin Approves ✅
Coach → Invite Physio  → Physio Accepts  → Admin Approves ✅
```

### 2. Athlete Builds Support Network
```
Athlete → Invite Coach  → Coach Accepts  → Admin Approves ✅
Athlete → Invite Parent → Parent Accepts → Admin Approves ✅
Athlete → Invite Physio → Physio Accepts → Admin Approves ✅
```

### 3. Parent Joins (Passive)
```
[Receives invitation from Athlete or Coach]
Parent → Registers → Accepts Invite → Admin Approves ✅
Parent → Cannot send invitations ❌
```

---

## Testing Checklist

✅ Athlete registration with sport_id  
✅ Coach registration with specialization  
✅ Parent registration with guardian_type  
✅ Physio registration with license_number  
✅ Coach can invite athlete  
✅ Coach can invite parent  
✅ Athlete can invite coach  
✅ Athlete can invite parent  
✅ **Parent CANNOT send invitation (403)**  
✅ Admin can approve requests  
✅ Admin can reject requests  
✅ Users can view their relationships  

---

## Quick Commands

```powershell
# Run migration
psql -U postgres -d moove_db -f database/schema/07_relationships.sql

# Install dependencies
pip install -r api/requirements.txt

# Create admin
python create_super_user.py

# Start server
python app.py

# Test registration
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","roles":["athlete"],"sport_id":"football-uuid"}'
```

---

**Print this page for quick reference during development!** 📋
