# Complete Onboarding Guide
## All User Types - Registration & Permissions

---

## User Types Overview

| User Type | Can Send Invites? | Can Accept Invites? | Required Fields | Special Notes |
|-----------|------------------|---------------------|-----------------|---------------|
| **Athlete** | ✅ Yes (coaches, parents, physios) | ✅ Yes | `sport_id`, `position` | Core user type |
| **Coach** | ✅ Yes (athletes, parents, physios, coaches) | ✅ Yes | `specialization` (optional) | Can invite anyone |
| **Physiotherapist** | ✅ Yes (athletes, coaches) | ✅ Yes | `specialization`, `license_number` | Medical professional |
| **Parent/Guardian/Manager** | ❌ NO - Can ONLY accept | ✅ Yes | `guardian_type`, `relationship_to_athlete` | Passive role |
| **Caretaker** | ✅ Yes (limited) | ✅ Yes | - | Support staff |
| **Admin/Super User** | ✅ Yes (anyone) | ✅ Yes | - | Full control |

---

## Permission Matrix

### Who Can Invite Whom?

```
           │ To: Athlete │ To: Coach │ To: Physio │ To: Parent │
───────────┼─────────────┼───────────┼────────────┼────────────┤
From:      │             │           │            │            │
Coach      │     ✅      │    ✅     │     ✅     │     ✅     │
Athlete    │     ❌      │    ✅     │     ✅     │     ✅     │
Physio     │     ✅      │    ✅     │     ❌     │     ❌     │
Parent     │     ❌      │    ❌     │     ❌     │     ❌     │ ← CANNOT SEND
Admin      │     ✅      │    ✅     │     ✅     │     ✅     │
```

### Relationship Types

| Relationship Type | Description | Who Can Initiate |
|------------------|-------------|------------------|
| `coach_athlete` | Coach training athlete | Coach OR Athlete |
| `coach_parent` | Coach connected to parent/guardian | Coach ONLY |
| `coach_physiotherapist` | Coach working with physio | Coach OR Physio |
| `coach_coach` | Coaches collaborating | Coach ONLY |
| `parent_athlete` | Parent/guardian of athlete | Athlete ONLY |
| `guardian_athlete` | Legal guardian of athlete | Athlete ONLY |
| `manager_athlete` | Manager representing athlete | Athlete ONLY |
| `physiotherapist_athlete` | Physio treating athlete | Athlete OR Physio |
| `physiotherapist_coach` | Physio working with coach | Physio ONLY |

---

## Onboarding Flows

### 1. Athlete Registration

**Required Information:**
- Email, Password, Name
- **Sport selection** (mandatory)
- Position (optional)

**Example:**

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "athlete@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete"],
  "sport_id": "uuid-of-football",     ← REQUIRED
  "position": "Forward"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ...",
  "user": {
    "user_id": "uuid",
    "email": "athlete@example.com",
    "roles": ["athlete"],
    "athlete_profile": {
      "athlete_id": "uuid",
      "sport_id": "uuid-of-football",
      "position": "Forward"
    }
  }
}
```

**What Athletes Can Do:**
- ✅ Invite coaches to train them
- ✅ Invite parents/guardians to view their progress
- ✅ Invite physiotherapists for treatment
- ✅ Accept invitations from coaches and physios
- ✅ Upload and analyze videos
- ✅ View their own reports and progress

---

### 2. Coach Registration

**Required Information:**
- Email, Password, Name
- Specialization (optional)
- Years of experience (optional)

**Example:**

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "coach@example.com",
  "password": "SecurePass123!",
  "first_name": "Mike",
  "last_name": "Johnson",
  "roles": ["coach"],
  "specialization": "Football - Youth Development",
  "years_of_experience": 10
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ...",
  "user": {
    "user_id": "uuid",
    "email": "coach@example.com",
    "roles": ["coach"],
    "coach_profile": {
      "coach_id": "uuid"
    }
  }
}
```

**What Coaches Can Do:**
- ✅ Invite athletes to coach them
- ✅ Invite parents (to keep them informed about athlete)
- ✅ Invite physiotherapists (for athlete care coordination)
- ✅ Invite other coaches (for collaboration)
- ✅ Accept invitations from athletes and physios
- ✅ View videos and reports of connected athletes
- ✅ Prescribe analyses and training plans

---

### 3. Physiotherapist Registration

**Required Information:**
- Email, Password, Name
- Specialization (recommended)
- License number (for verification)

**Example:**

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "physio@example.com",
  "password": "SecurePass123!",
  "first_name": "Dr. Sarah",
  "last_name": "Williams",
  "roles": ["physiotherapist"],
  "specialization": "Sports Medicine - Orthopedic",
  "license_number": "PT-12345"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ...",
  "user": {
    "user_id": "uuid",
    "email": "physio@example.com",
    "roles": ["physiotherapist"],
    "physiotherapist_profile": {
      "physiotherapist_id": "uuid"
    }
  }
}
```

**What Physiotherapists Can Do:**
- ✅ Invite athletes (for treatment)
- ✅ Invite coaches (for coordination)
- ✅ Accept invitations from athletes and coaches
- ✅ View medical data of connected athletes
- ✅ Prescribe specific movement analyses
- ✅ Generate medical assessment reports
- ✅ Track recovery progress

---

### 4. Parent/Guardian/Manager Registration

**Required Information:**
- Email, Password, Name
- **Guardian type** (mandatory): parent, legal_guardian, manager, agent, family_member
- Relationship to athlete (optional)

**Example:**

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "parent@example.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Doe",
  "roles": ["parent"],
  "guardian_type": "parent",                    ← REQUIRED
  "relationship_to_athlete": "Mother"           ← OPTIONAL
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ...",
  "user": {
    "user_id": "uuid",
    "email": "parent@example.com",
    "roles": ["parent"],
    "guardian_profile": {
      "guardian_id": "uuid",
      "guardian_type": "parent",
      "relationship_to_athlete": "Mother"
    }
  }
}
```

**What Parents/Guardians Can Do:**
- ✅ Accept invitations from athletes or coaches
- ✅ View videos and reports of connected athletes
- ✅ Receive progress notifications
- ❌ **CANNOT send invitations** - passive role only
- ⚙️ Permissions controlled per relationship:
  - `can_view_medical` (default: false)
  - `can_view_videos` (default: true)
  - `can_view_reports` (default: true)
  - `can_upload_videos` (default: false)

**Guardian Types:**
- `parent` - Mother or father
- `legal_guardian` - Legal guardian (not parent)
- `manager` - Sports agent or manager
- `agent` - Professional agent
- `family_member` - Other family member

---

### 5. Admin/Super User Registration

**Created via Script:**

```powershell
# Run the super user creation script
python create_super_user.py

# Or via API (only if you're already an admin):
POST /api/auth/register
{
  "email": "admin@example.com",
  "password": "SuperSecure123!",
  "first_name": "Admin",
  "last_name": "User",
  "roles": ["admin", "super_user"]
}
```

**What Admins Can Do:**
- ✅ Everything all other users can do
- ✅ Approve/reject all relationship change requests
- ✅ View all relationships and audit logs
- ✅ Override permissions
- ✅ Manage all users
- ✅ Access system configuration

---

## Complete Workflow Examples

### Example 1: Coach Onboards and Builds Team

```
1. Coach Registration
   POST /api/auth/register
   { "roles": ["coach"], "specialization": "Football" }
   
2. Coach Invites Athlete #1
   POST /api/invitations/send
   { "relationship_type": "coach_athlete", "invitee_email": "athlete1@..." }
   
3. Athlete #1 Accepts
   POST /api/invitations/{token}/accept
   
4. Admin Approves
   POST /api/admin/relationship-requests/{id}/approve
   
5. Relationship Active ✅
   
6. Coach Invites Athlete's Parent
   POST /api/invitations/send
   { "relationship_type": "coach_parent", "invitee_email": "parent@..." }
   
7. Parent Accepts (parent already registered)
   POST /api/invitations/{token}/accept
   
8. Admin Approves
   POST /api/admin/relationship-requests/{id}/approve
   
9. Coach Invites Physiotherapist
   POST /api/invitations/send
   { "relationship_type": "coach_physiotherapist", "invitee_email": "physio@..." }
   
10. Physio Accepts
    POST /api/invitations/{token}/accept
    
11. Admin Approves
    POST /api/admin/relationship-requests/{id}/approve
    
Result: Coach now has network of:
- Athletes (can view their videos, assign training)
- Parents (can communicate updates)
- Physiotherapist (can coordinate care)
```

### Example 2: Athlete Onboards and Builds Support Team

```
1. Athlete Registration
   POST /api/auth/register
   { "roles": ["athlete"], "sport_id": "football-uuid", "position": "Forward" }
   
2. Athlete Invites Coach
   POST /api/invitations/send
   { "relationship_type": "coach_athlete", "invitee_email": "coach@..." }
   
3. Coach Accepts
   POST /api/invitations/{token}/accept
   
4. Admin Approves
   ✅ Relationship active
   
5. Athlete Invites Parent
   POST /api/invitations/send
   { "relationship_type": "parent_athlete", "invitee_email": "mom@..." }
   
6. Parent Receives Email with Registration Link
   (If parent not registered yet)
   
7. Parent Registers
   POST /api/auth/register
   { "roles": ["parent"], "guardian_type": "parent" }
   
8. Parent Accepts Invitation
   POST /api/invitations/{token}/accept
   
9. Admin Approves
   ✅ Relationship active
   
10. Athlete Invites Physiotherapist
    POST /api/invitations/send
    { "relationship_type": "physiotherapist_athlete", "invitee_email": "physio@..." }
    
11. Physio Accepts
    POST /api/invitations/{token}/accept
    
12. Admin Approves
    ✅ Relationship active
    
Result: Athlete now has:
- Coach (for training)
- Parent (for oversight)
- Physiotherapist (for medical care)
```

### Example 3: Parent Onboarding (Passive Flow)

```
1. Parent Receives Invitation Email
   From: Athlete or Coach
   Subject: "You've been invited to join Moove"
   
2. Parent Clicks Link
   Redirects to: /register?invite={token}
   
3. Parent Registers
   POST /api/auth/register
   {
     "email": "parent@example.com",
     "password": "...",
     "first_name": "Jane",
     "last_name": "Doe",
     "roles": ["parent"],
     "guardian_type": "parent"      ← REQUIRED
   }
   
4. Parent Auto-Sees Invitation in Dashboard
   GET /api/invitations/received
   
5. Parent Accepts Invitation
   POST /api/invitations/{token}/accept
   
6. Change Request Created (pending admin)
   
7. Admin Approves
   POST /api/admin/relationship-requests/{id}/approve
   
8. Parent Can Now View Athlete Data
   (Based on permissions granted in relationship)
   
Important: Parent CANNOT initiate invitations themselves
```

---

## API Validation Rules

### Registration Validation

**For Athletes:**
```json
{
  "roles": ["athlete"],
  "sport_id": "required",     ← Will return 400 if missing
  "position": "optional"
}
```

**For Parents:**
```json
{
  "roles": ["parent"],
  "guardian_type": "required", ← Will return 400 if missing
  "relationship_to_athlete": "optional"
}
```

**For Coaches:**
```json
{
  "roles": ["coach"],
  "specialization": "optional",
  "years_of_experience": "optional"
}
```

**For Physiotherapists:**
```json
{
  "roles": ["physiotherapist"],
  "specialization": "optional",
  "license_number": "optional"
}
```

### Invitation Validation

**Permission Check:**
```javascript
// Parents trying to send invitation
POST /api/invitations/send
Response: 403 Forbidden
{
  "error": "You do not have permission to send this type of invitation",
  "detail": "Parents can only accept invitations, not send them"
}

// Coach inviting athlete (allowed)
POST /api/invitations/send
{ "relationship_type": "coach_athlete", "invitee_email": "..." }
Response: 201 Created

// Athlete inviting parent (allowed)
POST /api/invitations/send
{ "relationship_type": "parent_athlete", "invitee_email": "..." }
Response: 201 Created

// Parent inviting coach (blocked)
POST /api/invitations/send
{ "relationship_type": "coach_parent", "invitee_email": "..." }
Response: 403 Forbidden
```

---

## Permission Details

### Parent/Guardian Permissions

Each parent relationship has configurable permissions:

```json
{
  "can_view_medical": false,      // Default: Cannot view medical data
  "can_view_videos": true,        // Default: Can view videos
  "can_view_reports": true,       // Default: Can view reports
  "can_upload_videos": false,     // Default: Cannot upload
  "can_schedule_sessions": false  // Default: Cannot schedule
}
```

**Setting Permissions (Admin or during invite):**
```bash
POST /api/invitations/send
{
  "relationship_type": "parent_athlete",
  "invitee_email": "parent@example.com",
  "permissions": {
    "can_view_medical": true,    ← Grant medical access
    "can_upload_videos": true    ← Allow video uploads
  }
}
```

---

## Testing All User Types

### Test Script

```powershell
# 1. Register Athlete
$athlete = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "athlete@test.com"
  password = "Test123!"
  first_name = "John"
  last_name = "Doe"
  roles = @("athlete")
  sport_id = "football-uuid"
  position = "Forward"
} | ConvertTo-Json) -ContentType "application/json"

# 2. Register Coach
$coach = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "coach@test.com"
  password = "Test123!"
  first_name = "Mike"
  last_name = "Johnson"
  roles = @("coach")
  specialization = "Football"
} | ConvertTo-Json) -ContentType "application/json"

# 3. Register Physiotherapist
$physio = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "physio@test.com"
  password = "Test123!"
  first_name = "Sarah"
  last_name = "Williams"
  roles = @("physiotherapist")
  specialization = "Sports Medicine"
  license_number = "PT-12345"
} | ConvertTo-Json) -ContentType "application/json"

# 4. Register Parent
$parent = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "parent@test.com"
  password = "Test123!"
  first_name = "Jane"
  last_name = "Doe"
  roles = @("parent")
  guardian_type = "parent"
  relationship_to_athlete = "Mother"
} | ConvertTo-Json) -ContentType "application/json"

# 5. Coach invites athlete
$headers = @{ "Authorization" = "Bearer $($coach.token)" }
$invite1 = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/send" -Method POST -Headers $headers -Body (@{
  invitee_email = "athlete@test.com"
  relationship_type = "coach_athlete"
  message = "Let's work together!"
} | ConvertTo-Json) -ContentType "application/json"

# 6. Athlete invites parent
$headers = @{ "Authorization" = "Bearer $($athlete.token)" }
$invite2 = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/send" -Method POST -Headers $headers -Body (@{
  invitee_email = "parent@test.com"
  relationship_type = "parent_athlete"
  message = "Hi Mom!"
} | ConvertTo-Json) -ContentType "application/json"

# 7. Coach invites physiotherapist
$headers = @{ "Authorization" = "Bearer $($coach.token)" }
$invite3 = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/send" -Method POST -Headers $headers -Body (@{
  invitee_email = "physio@test.com"
  relationship_type = "coach_physiotherapist"
  message = "Need your expertise!"
} | ConvertTo-Json) -ContentType "application/json"

# 8. Test parent CANNOT send invitation (should fail)
$headers = @{ "Authorization" = "Bearer $($parent.token)" }
try {
  $fail = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/send" -Method POST -Headers $headers -Body (@{
    invitee_email = "coach@test.com"
    relationship_type = "coach_parent"
  } | ConvertTo-Json) -ContentType "application/json"
  Write-Host "❌ ERROR: Parent should not be able to send invites!"
} catch {
  Write-Host "✅ PASS: Parent correctly blocked from sending invites"
}

Write-Host "All user types registered successfully!"
```

---

## Frontend Implementation

### Registration Form (Dynamic Fields)

```jsx
// components/auth/Register.jsx
const [selectedRole, setSelectedRole] = useState('');
const [sport, setSport] = useState('');
const [guardianType, setGuardianType] = useState('');

return (
  <form onSubmit={handleRegister}>
    {/* Common fields */}
    <input type="email" name="email" required />
    <input type="password" name="password" required />
    <input type="text" name="first_name" required />
    <input type="text" name="last_name" required />
    
    {/* Role selection */}
    <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
      <option value="">Select User Type</option>
      <option value="athlete">Athlete</option>
      <option value="coach">Coach</option>
      <option value="physiotherapist">Physiotherapist</option>
      <option value="parent">Parent/Guardian</option>
    </select>
    
    {/* Athlete-specific fields */}
    {selectedRole === 'athlete' && (
      <>
        <label>Sport *</label>
        <select value={sport} onChange={(e) => setSport(e.target.value)} required>
          <option value="">Select Sport</option>
          <option value="football-uuid">Football</option>
          <option value="basketball-uuid">Basketball</option>
          <option value="running-uuid">Running</option>
        </select>
        
        <label>Position</label>
        <input type="text" placeholder="e.g., Forward" />
      </>
    )}
    
    {/* Coach-specific fields */}
    {selectedRole === 'coach' && (
      <>
        <label>Specialization</label>
        <input type="text" placeholder="e.g., Football - Youth Development" />
        
        <label>Years of Experience</label>
        <input type="number" min="0" />
      </>
    )}
    
    {/* Physiotherapist-specific fields */}
    {selectedRole === 'physiotherapist' && (
      <>
        <label>Specialization</label>
        <input type="text" placeholder="e.g., Sports Medicine" />
        
        <label>License Number</label>
        <input type="text" placeholder="PT-12345" />
      </>
    )}
    
    {/* Parent-specific fields */}
    {selectedRole === 'parent' && (
      <>
        <label>Guardian Type *</label>
        <select value={guardianType} onChange={(e) => setGuardianType(e.target.value)} required>
          <option value="">Select Type</option>
          <option value="parent">Parent</option>
          <option value="legal_guardian">Legal Guardian</option>
          <option value="manager">Manager</option>
          <option value="agent">Agent</option>
        </select>
        
        <label>Relationship to Athlete</label>
        <input type="text" placeholder="e.g., Mother, Father, Agent" />
        
        <div className="info-box">
          ℹ️ Parents can only accept invitations from athletes or coaches
        </div>
      </>
    )}
    
    <button type="submit">Register</button>
  </form>
);
```

---

## Summary

### Key Takeaways

1. **All user types can register** with role-specific required fields
2. **Coaches have maximum invite permissions** - can invite anyone
3. **Parents are passive** - can ONLY accept invites, cannot send
4. **Athletes and physios have moderate permissions** - can invite some roles
5. **All relationships require admin approval** - complete gatekeeping
6. **Flexible permission system** - each relationship can have custom permissions

### Registration Requirements

| Role | Required Fields | Optional Fields |
|------|----------------|-----------------|
| Athlete | `sport_id` | `position` |
| Coach | - | `specialization`, `years_of_experience` |
| Physiotherapist | - | `specialization`, `license_number` |
| Parent | `guardian_type` | `relationship_to_athlete` |

### Next Steps

1. ✅ Run database migration with updated relationship types
2. ✅ Test all user type registrations
3. ✅ Test invitation permissions (especially parent restrictions)
4. ✅ Build dynamic registration form in frontend
5. ✅ Implement admin dashboard for approvals

---

**System is now ready for multi-role onboarding!** 🎉
