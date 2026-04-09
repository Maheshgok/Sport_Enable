# Relationship Management Implementation Guide

## Quick Start

### 1. Run Database Migration

```powershell
cd database
psql -U postgres -d moove_db -f schema/07_relationships.sql
```

This creates:
- `relationship_invitations` table
- `relationship_change_requests` table
- `relationships` table (active relationships)
- `parent_guardian_profiles` table
- `relationship_audit_log` table
- Helper functions and views

### 2. Update Requirements

Add to `api/requirements.txt`:
```
flask-mail==0.9.1  # For email notifications
secrets  # For secure token generation
```

Install:
```powershell
cd api
pip install -r requirements.txt
```

### 3. Test the API

Start the API server:
```powershell
cd api
python app.py
```

---

## User Flows

### Flow 1: Athlete Onboards with Sport Selection

**Registration with sport:**
```bash
POST /api/auth/register
{
  "email": "athlete@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete"],
  "sport_id": "uuid-of-football",  // REQUIRED for athletes
  "position": "Forward"             // OPTIONAL
}
```

Response:
```json
{
  "success": true,
  "user": {
    "user_id": "...",
    "email": "athlete@example.com",
    "roles": ["athlete"],
    "athlete_profile": {
      "athlete_id": "...",
      "sport_id": "...",
      "position": "Forward"
    }
  },
  "token": "eyJ..."
}
```

---

### Flow 1b: Coach Onboards

**Registration as coach:**
```bash
POST /api/auth/register
{
  "email": "coach@example.com",
  "password": "SecurePass123!",
  "first_name": "Mike",
  "last_name": "Johnson",
  "roles": ["coach"],
  "specialization": "Football - Youth Development",  // OPTIONAL
  "years_of_experience": 10                          // OPTIONAL
}
```

Response includes `coach_profile` with `coach_id`.

**Coaches can invite:** Athletes, Parents, Physiotherapists, Other Coaches

---

### Flow 1c: Physiotherapist Onboards

**Registration as physiotherapist:**
```bash
POST /api/auth/register
{
  "email": "physio@example.com",
  "password": "SecurePass123!",
  "first_name": "Dr. Sarah",
  "last_name": "Williams",
  "roles": ["physiotherapist"],
  "specialization": "Sports Medicine",  // OPTIONAL
  "license_number": "PT-12345"          // OPTIONAL
}
```

Response includes `physiotherapist_profile` with `physiotherapist_id`.

**Physiotherapists can invite:** Athletes, Coaches

---

### Flow 1d: Parent/Guardian Onboards

**Registration as parent:**
```bash
POST /api/auth/register
{
  "email": "parent@example.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Doe",
  "roles": ["parent"],
  "guardian_type": "parent",                    // REQUIRED: parent, legal_guardian, manager, agent
  "relationship_to_athlete": "Mother"           // OPTIONAL
}
```

Response includes `guardian_profile` with `guardian_id`.

**⚠️ Important:** Parents can ONLY accept invitations, they CANNOT send invitations.

---

### Flow 2: Coach Invites Athlete

**Step 1: Coach sends invitation**
```bash
POST /api/invitations/send
Authorization: Bearer <coach-token>
{
  "invitee_email": "athlete@example.com",
  "relationship_type": "coach_athlete",
  "coach_id": "uuid-of-coach-profile",
  "athlete_id": "uuid-of-athlete-profile",
  "message": "Hi John, I'd like to coach you!"
}
```

Response:
```json
{
  "success": true,
  "invitation_id": "uuid",
  "expires_at": "2026-04-15T...",
  "message": "Invitation sent successfully"
}
```

**Step 2: Athlete receives email**
Email contains link: `https://app.moove.com/invitations/accept?token=abc123...`

**Step 3: Athlete checks invitation**
```bash
GET /api/invitations/<token>/details
```

Response:
```json
{
  "success": true,
  "invitation": {
    "invitation_id": "uuid",
    "relationship_type": "coach_athlete",
    "message": "Hi John, I'd like to coach you!",
    "inviter_name": "Coach Mike",
    "inviter_avatar": "https://...",
    "status": "pending",
    "created_at": "2026-04-08T...",
    "expires_at": "2026-04-15T...",
    "is_expired": false
  }
}
```

**Step 4: Athlete accepts**
```bash
POST /api/invitations/<token>/accept
Authorization: Bearer <athlete-token>
{
  "response_message": "Looking forward to working with you!"
}
```

Response:
```json
{
  "success": true,
  "message": "Invitation accepted. Pending admin approval.",
  "request_id": "uuid"
}
```

**Step 5: Super admin receives email**
Email: "New relationship change request requires approval"

**Step 6: Admin reviews request**
```bash
GET /api/admin/relationship-requests
Authorization: Bearer <admin-token>
```

Response:
```json
{
  "success": true,
  "requests": [
    {
      "request_id": "uuid",
      "request_type": "add_relationship",
      "relationship_type": "coach_athlete",
      "requester": {
        "name": "John Doe",
        "email": "athlete@example.com"
      },
      "users": {
        "user_a": "Coach Mike",
        "user_b": "John Doe"
      },
      "reason": "Accepted invitation from ...",
      "priority": "normal",
      "created_at": "2026-04-08T..."
    }
  ],
  "count": 1
}
```

**Step 7: Admin approves**
```bash
POST /api/admin/relationship-requests/<request_id>/approve
Authorization: Bearer <admin-token>
{
  "admin_notes": "Verified coach credentials. Approved."
}
```

Response:
```json
{
  "success": true,
  "message": "Relationship created: uuid"
}
```

**Step 8: Both users notified**
- Email to coach: "Your relationship with John Doe has been approved"
- Email to athlete: "Your relationship with Coach Mike has been approved"

---

### Flow 3: Parent/Guardian Association

**Step 1: Athlete or coach invites parent**
```bash
POST /api/invitations/send
Authorization: Bearer <athlete-token>
{
  "invitee_email": "parent@example.com",
  "relationship_type": "parent_athlete",
  "athlete_id": "uuid-of-athlete",
  "message": "Hi Mom, please join to view my progress!"
}
```

**Step 2: Parent receives email**

If parent not registered:
- Email: "You've been invited to join Moove"
- Link: `https://app.moove.com/register?invite=<token>`

If parent already registered:
- Email: "New invitation from John Doe"
- Link goes to dashboard with invitation notification

**Step 3: Parent registers (if new user)**
```bash
POST /api/auth/register
{
  "email": "parent@example.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Doe",
  "roles": ["parent"],
  "guardian_type": "parent",           // NEW field
  "relationship_to_athlete": "Mother"  // NEW field
}
```

**Step 4: Parent accepts invitation**
```bash
POST /api/invitations/<token>/accept
Authorization: Bearer <parent-token>
```

**Step 5: Admin approval process** (same as coach flow)

**Step 6: Parent can now view athlete's data**
```bash
GET /api/relationships/mine
Authorization: Bearer <parent-token>
```

Response:
```json
{
  "success": true,
  "relationships": [
    {
      "relationship_id": "uuid",
      "relationship_type": "parent_athlete",
      "other_user": {
        "user_id": "uuid",
        "name": "John Doe",
        "email": "athlete@example.com"
      },
      "status": "active",
      "created_at": "2026-04-08T..."
    }
  ],
  "count": 1
}
```

---

### Flow 4: Request Relationship Termination

**Step 1: User requests termination**
```bash
POST /api/relationships/request-change
Authorization: Bearer <user-token>
{
  "request_type": "remove_relationship",
  "relationship_id": "uuid",
  "reason": "Athlete is moving to a different coach"
}
```

Response:
```json
{
  "success": true,
  "request_id": "uuid",
  "message": "Change request submitted for admin approval"
}
```

**Step 2: Admin receives email**

**Step 3: Admin reviews and approves/rejects**
```bash
POST /api/admin/relationship-requests/<request_id>/approve
Authorization: Bearer <admin-token>
{
  "admin_notes": "Valid reason provided. Approved."
}
```

**Step 4: Relationship terminated**
Both users notified that relationship has been terminated.

---

## Admin Dashboard

### View All Pending Requests

```bash
GET /api/admin/relationship-requests
Authorization: Bearer <admin-token>
```

Returns prioritized list of all pending requests.

### Bulk Operations

Approve multiple requests:
```bash
POST /api/admin/relationship-requests/bulk-approve
Authorization: Bearer <admin-token>
{
  "request_ids": ["uuid1", "uuid2", "uuid3"],
  "admin_notes": "Batch approval after verification"
}
```

---

## Frontend Integration

### Registration Form Update

Add sport selection for athletes:

```jsx
// Login.jsx
const [sport, setSport] = useState('');
const [position, setPosition] = useState('');

// In registration form, when role is 'athlete':
{selectedRoles.includes('athlete') && (
  <>
    <div>
      <label>Sport</label>
      <select value={sport} onChange={(e) => setSport(e.target.value)}>
        <option value="">Select Sport</option>
        <option value="football-uuid">Football</option>
        <option value="basketball-uuid">Basketball</option>
        <option value="running-uuid">Running</option>
        <option value="cricket-uuid">Cricket</option>
      </select>
    </div>
    <div>
      <label>Position</label>
      <input 
        type="text" 
        value={position}
        onChange={(e) => setPosition(e.target.value)}
        placeholder="e.g., Forward, Midfielder"
      />
    </div>
  </>
)}

// Include in registration payload:
const payload = {
  // ... existing fields
  sport_id: sport,
  position: position
};
```

### Invitations Component

```jsx
// components/InvitationsPanel.jsx
import React, { useState, useEffect } from 'react';
import { authFetch } from './auth/Login';

const InvitationsPanel = () => {
  const [invitations, setInvitations] = useState([]);
  
  useEffect(() => {
    loadInvitations();
  }, []);
  
  const loadInvitations = async () => {
    const response = await authFetch('/api/invitations/received');
    const data = await response.json();
    if (data.success) {
      setInvitations(data.invitations);
    }
  };
  
  const acceptInvitation = async (token) => {
    const response = await authFetch(`/api/invitations/${token}/accept`, {
      method: 'POST'
    });
    const data = await response.json();
    if (data.success) {
      alert('Invitation accepted! Pending admin approval.');
      loadInvitations();
    }
  };
  
  const rejectInvitation = async (token) => {
    const response = await authFetch(`/api/invitations/${token}/reject`, {
      method: 'POST'
    });
    const data = await response.json();
    if (data.success) {
      alert('Invitation rejected.');
      loadInvitations();
    }
  };
  
  return (
    <div className="invitations-panel">
      <h3>Pending Invitations ({invitations.length})</h3>
      {invitations.map(inv => (
        <div key={inv.invitation_id} className="invitation-card">
          <div className="inviter-info">
            <img src={inv.inviter.avatar} alt={inv.inviter.name} />
            <div>
              <strong>{inv.inviter.name}</strong>
              <span>{inv.inviter.email}</span>
            </div>
          </div>
          <div className="invitation-details">
            <p><strong>Type:</strong> {inv.relationship_type.replace('_', ' ')}</p>
            {inv.message && <p className="message">{inv.message}</p>}
            <p className="expires">Expires: {new Date(inv.expires_at).toLocaleDateString()}</p>
          </div>
          <div className="actions">
            <button onClick={() => acceptInvitation(inv.token)} className="btn-accept">
              Accept
            </button>
            <button onClick={() => rejectInvitation(inv.token)} className="btn-reject">
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default InvitationsPanel;
```

### My Relationships Component

```jsx
// components/MyRelationships.jsx
import React, { useState, useEffect } from 'react';
import { authFetch } from './auth/Login';

const MyRelationships = () => {
  const [relationships, setRelationships] = useState([]);
  
  useEffect(() => {
    loadRelationships();
  }, []);
  
  const loadRelationships = async () => {
    const response = await authFetch('/api/relationships/mine');
    const data = await response.json();
    if (data.success) {
      setRelationships(data.relationships);
    }
  };
  
  const requestTermination = async (relationshipId) => {
    const reason = prompt('Reason for termination:');
    if (!reason) return;
    
    const response = await authFetch('/api/relationships/request-change', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_type: 'remove_relationship',
        relationship_id: relationshipId,
        reason: reason
      })
    });
    
    const data = await response.json();
    if (data.success) {
      alert('Termination request submitted for admin approval.');
    }
  };
  
  return (
    <div className="relationships">
      <h3>My Connections ({relationships.length})</h3>
      <div className="relationship-list">
        {relationships.map(rel => (
          <div key={rel.relationship_id} className="relationship-card">
            <div className="user-info">
              <strong>{rel.other_user.name}</strong>
              <span>{rel.other_user.email}</span>
            </div>
            <div className="rel-details">
              <span className="badge">{rel.relationship_type.replace('_', ' ')}</span>
              <span className="status">{rel.status}</span>
              <span className="date">Since {new Date(rel.created_at).toLocaleDateString()}</span>
            </div>
            <button 
              onClick={() => requestTermination(rel.relationship_id)}
              className="btn-terminate"
            >
              Request Removal
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyRelationships;
```

### Admin Approval Dashboard

```jsx
// pages/admin/RelationshipApprovals.jsx
import React, { useState, useEffect } from 'react';
import { authFetch } from '../../components/auth/Login';

const RelationshipApprovals = () => {
  const [requests, setRequests] = useState([]);
  
  useEffect(() => {
    loadRequests();
  }, []);
  
  const loadRequests = async () => {
    const response = await authFetch('/api/admin/relationship-requests');
    const data = await response.json();
    if (data.success) {
      setRequests(data.requests);
    }
  };
  
  const approveRequest = async (requestId) => {
    const notes = prompt('Admin notes (optional):');
    
    const response = await authFetch(
      `/api/admin/relationship-requests/${requestId}/approve`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_notes: notes })
      }
    );
    
    const data = await response.json();
    if (data.success) {
      alert('Request approved!');
      loadRequests();
    }
  };
  
  const rejectRequest = async (requestId) => {
    const reason = prompt('Rejection reason:');
    if (!reason) return;
    
    const notes = prompt('Additional admin notes (optional):');
    
    const response = await authFetch(
      `/api/admin/relationship-requests/${requestId}/reject`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rejection_reason: reason,
          admin_notes: notes
        })
      }
    );
    
    const data = await response.json();
    if (data.success) {
      alert('Request rejected.');
      loadRequests();
    }
  };
  
  return (
    <div className="admin-approvals">
      <h2>Relationship Change Requests</h2>
      <p>Pending requests: {requests.length}</p>
      
      <div className="requests-list">
        {requests.map(req => (
          <div key={req.request_id} className={`request-card priority-${req.priority}`}>
            <div className="request-header">
              <span className="badge">{req.request_type}</span>
              <span className="priority">{req.priority}</span>
              <span className="date">{new Date(req.created_at).toLocaleDateString()}</span>
            </div>
            
            <div className="request-body">
              <p><strong>Type:</strong> {req.relationship_type.replace('_', ' ')}</p>
              <p><strong>Requested by:</strong> {req.requester.name} ({req.requester.email})</p>
              <p><strong>Between:</strong> {req.users.user_a} and {req.users.user_b}</p>
              {req.reason && (
                <div className="reason">
                  <strong>Reason:</strong>
                  <p>{req.reason}</p>
                </div>
              )}
            </div>
            
            <div className="request-actions">
              <button 
                onClick={() => approveRequest(req.request_id)}
                className="btn-approve"
              >
                Approve
              </button>
              <button 
                onClick={() => rejectRequest(req.request_id)}
                className="btn-reject"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RelationshipApprovals;
```

---

## Email Notifications

### Setup Flask-Mail

In `api/app.py`:

```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@moove.com')

mail = Mail(app)
```

### Update `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@moove.com
APP_BASE_URL=http://localhost:3000
```

### Implement Email Helpers

Create `api/email_templates.py`:

```python
from flask_mail import Message
from flask import current_app, render_template_string

def send_invitation_email(invitee_email, inviter_name, relationship_type, 
                         invitation_token, message=None):
    """Send invitation email"""
    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:3000')
    accept_url = f"{base_url}/invitations/accept?token={invitation_token}"
    
    subject = f"You've been invited by {inviter_name} on Moove"
    
    body = f"""
    Hi,
    
    {inviter_name} has invited you to connect on Moove as their {relationship_type.replace('_', ' ')}.
    
    {f'Personal message: {message}' if message else ''}
    
    Accept invitation: {accept_url}
    
    This invitation expires in 7 days.
    
    If you don't have an account, you'll be able to create one when you accept.
    
    Best regards,
    Moove Team
    """
    
    msg = Message(subject, recipients=[invitee_email], body=body)
    mail.send(msg)

def send_admin_approval_email(request_id):
    """Send approval request email to all super admins"""
    from db import execute_query
    
    # Get all super admins
    admins = execute_query("""
        SELECT email, first_name FROM physio_app.users
        WHERE 'super_user' = ANY(roles) OR 'admin' = ANY(roles)
    """, fetch_all=True)
    
    # Get request details
    request = execute_query("""
        SELECT * FROM physio_app.v_admin_pending_requests
        WHERE request_id = %s
    """, (request_id,), fetch_one=True)
    
    if not request:
        return
    
    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:3000')
    review_url = f"{base_url}/admin/relationship-requests/{request_id}"
    
    subject = "Relationship Change Request Requires Approval"
    
    for admin in admins:
        body = f"""
        Hi {admin['first_name']},
        
        A new relationship change request requires your review:
        
        Request Type: {request['request_type']}
        Requested By: {request['requester_name']} ({request['requester_email']})
        Relationship: {request['relationship_type'].replace('_', ' ')}
        Between: {request['user_a_name']} and {request['user_b_name']}
        Reason: {request['reason']}
        Priority: {request['priority']}
        
        Review request: {review_url}
        
        Best regards,
        Moove System
        """
        
        msg = Message(subject, recipients=[admin['email']], body=body)
        mail.send(msg)
```

---

## Testing

### Test Invitation Flow

```powershell
# 1. Register coach
$coach = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "coach@test.com"
  password = "Test123!"
  first_name = "Coach"
  last_name = "Mike"
  roles = @("coach")
} | ConvertTo-Json) -ContentType "application/json"

# 2. Register athlete
$athlete = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -Body (@{
  email = "athlete@test.com"
  password = "Test123!"
  first_name = "John"
  last_name = "Doe"
  roles = @("athlete")
  sport_id = "football-uuid"
  position = "Forward"
} | ConvertTo-Json) -ContentType "application/json"

# 3. Coach sends invitation
$headers = @{ "Authorization" = "Bearer $($coach.token)" }
$invitation = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/send" -Method POST -Headers $headers -Body (@{
  invitee_email = "athlete@test.com"
  relationship_type = "coach_athlete"
  coach_id = $coach.user.coach_profile.coach_id
  athlete_id = $athlete.user.athlete_profile.athlete_id
  message = "Let's work together!"
} | ConvertTo-Json) -ContentType "application/json"

# 4. Athlete checks invitations
$headers = @{ "Authorization" = "Bearer $($athlete.token)" }
$invitations = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/received" -Headers $headers

# 5. Athlete accepts
$token = $invitations.invitations[0].token
$accept = Invoke-RestMethod -Uri "http://localhost:8080/api/invitations/$token/accept" -Method POST -Headers $headers

# 6. Admin checks pending requests
$headers = @{ "Authorization" = "Bearer $($admin.token)" }
$requests = Invoke-RestMethod -Uri "http://localhost:8080/api/admin/relationship-requests" -Headers $headers

# 7. Admin approves
$requestId = $requests.requests[0].request_id
$approve = Invoke-RestMethod -Uri "http://localhost:8080/api/admin/relationship-requests/$requestId/approve" -Method POST -Headers $headers -Body (@{
  admin_notes = "Approved"
} | ConvertTo-Json) -ContentType "application/json"

# 8. Athlete views relationships
$headers = @{ "Authorization" = "Bearer $($athlete.token)" }
$relationships = Invoke-RestMethod -Uri "http://localhost:8080/api/relationships/mine" -Headers $headers
```

---

## Summary

This system provides:
- ✅ Athlete onboarding with sport selection
- ✅ Invite-based coach-athlete associations
- ✅ Invite-based parent/guardian associations
- ✅ Admin approval for all relationship changes
- ✅ Email notifications at each step
- ✅ Complete audit trail
- ✅ Secure token-based invitations
- ✅ Protection against unauthorized changes

All relationship changes go through super admin approval, ensuring complete control and security.
