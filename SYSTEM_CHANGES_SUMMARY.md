# System Changes Summary
## From Sport-Specific Analysis to Relationship Management

---

## What Changed?

### Previous Focus (v1)
- ✅ Authentication system with JWT tokens
- ✅ User registration with role-based access
- ✅ Sport-specific video analysis architecture
- ❌ **No relationship management**
- ❌ **Direct user associations**
- ❌ **No admin approval workflow**

### Current Focus (v2)
- ✅ Everything from v1 PLUS:
- ✅ **Invite-based relationship system**
- ✅ **Admin approval for all relationship changes**
- ✅ **Parent/Guardian profiles**
- ✅ **Complete audit trail**
- ✅ **Email notification workflow**

---

## Key Architectural Changes

### 1. User Registration Enhanced

**Before:**
```json
POST /api/auth/register
{
  "email": "athlete@example.com",
  "password": "password",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete"]
}
```

**After:**
```json
POST /api/auth/register
{
  "email": "athlete@example.com",
  "password": "password",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete"],
  "sport_id": "football-uuid",     ← NEW: Required for athletes
  "position": "Forward"             ← NEW: Optional
}

// OR for parent/guardian:
{
  "email": "parent@example.com",
  "password": "password",
  "first_name": "Jane",
  "last_name": "Doe",
  "roles": ["parent"],
  "guardian_type": "parent",        ← NEW: Required for parents
  "relationship_to_athlete": "Mother"  ← NEW: Optional
}
```

### 2. New Database Tables

**Added 5 new tables:**

1. **`parent_guardian_profiles`**
   - Guardian type (parent, legal_guardian, manager, agent)
   - Permissions (can view medical, videos, reports)
   - Capacity limits (max athletes)

2. **`relationship_invitations`**
   - Pending invites with secure tokens
   - Expiration (7 days default)
   - Status tracking (pending, accepted, rejected, expired)

3. **`relationship_change_requests`**
   - All relationship changes (add, remove, modify)
   - Admin approval workflow
   - Priority levels (low, normal, high, urgent)

4. **`relationships`**
   - Active connections between users
   - Permission sets per relationship
   - Audit trail (who approved, when, why)

5. **`relationship_audit_log`**
   - Complete history of all relationship actions
   - Old/new data snapshots
   - Actor tracking with IP and user agent

### 3. New API Endpoints

**Added 10 new endpoints:**

```
# Invitation Management
POST   /api/invitations/send              ← Send invite
GET    /api/invitations/received          ← View received invites
GET    /api/invitations/sent              ← View sent invites
POST   /api/invitations/{token}/accept    ← Accept invite
POST   /api/invitations/{token}/reject    ← Reject invite
GET    /api/invitations/{token}/details   ← Public invite details

# Relationship Management
GET    /api/relationships/mine             ← View my connections
POST   /api/relationships/request-change   ← Request termination

# Admin Endpoints
GET    /api/admin/relationship-requests           ← View pending requests
POST   /api/admin/relationship-requests/{id}/approve  ← Approve change
POST   /api/admin/relationship-requests/{id}/reject   ← Reject change
```

### 4. New User Flows

**Coach → Athlete Association:**

1. Coach sends invitation → Email to athlete
2. Athlete accepts → Change request created
3. Email to super admin → Admin reviews
4. Admin approves → Relationship created
5. Both parties notified → Connection active

**Parent → Athlete Association:**

1. Athlete or coach invites parent
2. Parent registers (if new) and accepts
3. Change request created → Admin approval
4. Admin approves → Parent can view athlete data

**Relationship Termination:**

1. User requests termination → Change request created
2. Email to admin → Admin reviews reason
3. Admin approves → Relationship terminated
4. Both parties notified

---

## Files Created/Modified

### New Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `database/schema/07_relationships.sql` | Relationship management schema | 500+ |
| `api/relationships.py` | Relationship endpoints | 600+ |
| `RELATIONSHIP_SYSTEM_DESIGN.md` | Complete system design | 400+ |
| `RELATIONSHIP_IMPLEMENTATION_GUIDE.md` | Step-by-step implementation | 800+ |
| `QUICKSTART_RELATIONSHIPS.md` | Quick start guide | 600+ |
| `SYSTEM_CHANGES_SUMMARY.md` | This file | - |

### Modified Files

| File | Changes |
|------|---------|
| `api/app.py` | • Added `import relationships`<br>• Added 10 new route handlers<br>• Enhanced registration endpoint for sport_id and guardian_type<br>• Added profile creation logic |
| `api/requirements.txt` | • Added `flask-mail==0.9.1` for email notifications |

---

## Migration Path

### Step 1: Database Migration

```powershell
cd database
psql -U postgres -d moove_db -f schema/07_relationships.sql
```

**Verifies:**
- 5 new tables created
- 3 new views created
- 4 new functions created
- Triggers configured

### Step 2: Install Dependencies

```powershell
cd api
pip install -r requirements.txt
```

**Installs:**
- `flask-mail==0.9.1` (new)
- All existing dependencies

### Step 3: Configure Email

Add to `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@moove.com
APP_BASE_URL=http://localhost:3000
```

### Step 4: Test Backend

```powershell
python app.py
```

Verify:
- Server starts without errors
- New routes are accessible
- Database connection works

### Step 5: Frontend Updates

**Components to create:**
- `InvitationsPanel.jsx` - Show pending invitations
- `MyRelationships.jsx` - Display active relationships
- `RelationshipApprovals.jsx` (admin) - Approve/reject requests

**Components to update:**
- `Login.jsx` - Add sport selection for athletes, guardian type for parents
- `Dashboard.jsx` - Add invitations badge/counter

---

## Backward Compatibility

### What Still Works

✅ **All previous authentication endpoints:**
- `/api/auth/register` (enhanced with new optional fields)
- `/api/auth/login`
- `/api/auth/me`
- `/api/auth/change-password`

✅ **All user management endpoints:**
- `/api/users` (list)
- `/api/users/{id}` (get, update, delete)

✅ **All video endpoints:**
- `/api/upload`
- `/api/process/{id}`
- `/api/results/{id}`

### What's New

🆕 **Athlete registration now supports:**
- `sport_id` (required for athletes)
- `position` (optional)

🆕 **New parent/guardian role:**
- `roles: ["parent"]` with `guardian_type` field

🆕 **Relationship management:**
- Complete invite/accept/approve workflow
- Admin approval for all changes

---

## Breaking Changes

### ⚠️ Registration Changes

**Before (still works):**
```json
{
  "roles": ["athlete"]
}
```

**After (recommended for athletes):**
```json
{
  "roles": ["athlete"],
  "sport_id": "uuid",  ← Now captured during registration
  "position": "Forward"
}
```

**Impact:** 
- Existing code still works
- New athlete registrations should include sport_id for full functionality
- Can be added later via profile update

### ⚠️ Direct Relationship Creation No Longer Allowed

**Before:**
- Users could directly associate with others

**After:**
- All associations require invite → accept → admin approval
- Direct modifications blocked

**Migration for existing relationships:**
```sql
-- If you have existing direct relationships, they need to be migrated
INSERT INTO physio_app.relationships (
  relationship_type, primary_user_id, secondary_user_id, approved_by, status
)
SELECT 
  'coach_athlete',
  coach_user_id,
  athlete_user_id,
  (SELECT user_id FROM physio_app.users WHERE 'super_user' = ANY(roles) LIMIT 1),
  'active'
FROM old_coach_athlete_table;
```

---

## Testing Checklist

### Backend

- [ ] Database migration runs successfully
- [ ] All new tables exist with correct schema
- [ ] Server starts without import errors
- [ ] Health check endpoint works: `GET /health`
- [ ] Can register athlete with sport_id
- [ ] Can register parent with guardian_type
- [ ] Can send invitation
- [ ] Can accept invitation
- [ ] Change request created after acceptance
- [ ] Admin can view pending requests
- [ ] Admin can approve/reject requests
- [ ] Relationship created after approval
- [ ] Can view active relationships

### Frontend

- [ ] Registration form shows sport selector for athletes
- [ ] Registration form shows guardian type for parents
- [ ] Invitations panel displays pending invites
- [ ] Can accept/reject invitations from UI
- [ ] My Relationships page shows connections
- [ ] Admin dashboard shows pending requests
- [ ] Admin can approve/reject from UI
- [ ] Notifications shown for key events

### Email (Optional for MVP)

- [ ] Invitation emails sent correctly
- [ ] Admin approval emails sent
- [ ] Approval notification emails sent
- [ ] Email templates formatted properly

---

## Future Enhancements

### Phase 1 (Current)
✅ Invite-based relationships
✅ Admin approval workflow
✅ Basic email notifications

### Phase 2 (Planned)
⏳ Sport-specific video analysis
⏳ Cloud Run function per sport
⏳ PDF report generation
⏳ Baseline comparisons

### Phase 3 (Planned)
⏳ Real-time notifications (WebSocket)
⏳ Mobile app integration
⏳ Advanced analytics dashboard
⏳ Bulk operations for admins

### Phase 4 (Planned)
⏳ Machine learning baseline suggestions
⏳ Automated report generation
⏳ Integration with wearable devices
⏳ Video conferencing (coach-athlete)

---

## Rollback Plan

If you need to rollback:

### 1. Revert Database Changes

```sql
-- Drop new tables
DROP TABLE IF EXISTS physio_app.relationship_audit_log CASCADE;
DROP TABLE IF EXISTS physio_app.relationships CASCADE;
DROP TABLE IF EXISTS physio_app.relationship_change_requests CASCADE;
DROP TABLE IF EXISTS physio_app.relationship_invitations CASCADE;
DROP TABLE IF EXISTS physio_app.parent_guardian_profiles CASCADE;

-- Drop new functions
DROP FUNCTION IF EXISTS physio_app.log_relationship_action;
DROP FUNCTION IF EXISTS physio_app.generate_invitation_token;
DROP FUNCTION IF EXISTS physio_app.expire_old_invitations;
DROP FUNCTION IF EXISTS physio_app.get_user_relationships;
```

### 2. Revert Code Changes

```powershell
# Restore previous version of app.py
git checkout HEAD~1 api/app.py

# Restore previous requirements.txt
git checkout HEAD~1 api/requirements.txt

# Reinstall dependencies
pip install -r api/requirements.txt

# Restart server
python app.py
```

### 3. Remove New Files

```powershell
Remove-Item api/relationships.py
Remove-Item RELATIONSHIP_SYSTEM_DESIGN.md
Remove-Item RELATIONSHIP_IMPLEMENTATION_GUIDE.md
Remove-Item QUICKSTART_RELATIONSHIPS.md
```

---

## Support & Questions

### Common Questions

**Q: Do existing users need to re-register?**
A: No, existing users work as-is. New fields are optional for existing users.

**Q: Can I bypass admin approval for testing?**
A: Yes, create a test admin and approve immediately. Or modify the workflow in `relationships.py` to auto-approve (not recommended for production).

**Q: How do I invite multiple users at once?**
A: Currently one-by-one. Bulk invites can be added in Phase 3.

**Q: Can athletes have multiple coaches?**
A: Yes! Each coach-athlete pair is a separate relationship. Each requires admin approval.

**Q: What happens to pending invitations when they expire?**
A: They're automatically marked `expired` by the `expire_old_invitations()` function (can be run as cron job).

---

## Summary

### What You Built

🎉 **Complete relationship management system with:**
- Secure invite-based associations
- Admin-gated approval workflow
- Parent/guardian support with permissions
- Complete audit trail
- Email notification pipeline
- Role-based access control

### What You Can Do Now

✅ Athletes onboard with sport selection
✅ Coaches invite athletes (mutual acceptance)
✅ Parents/guardians connect via invites
✅ Admins review all relationship changes
✅ Complete transparency and control
✅ Email notifications keep everyone informed

### What's Next

🚀 Ready to implement:
1. Run database migration
2. Start backend server
3. Test invite workflow
4. Build frontend components
5. Configure email notifications
6. Deploy to production

---

**System is now fully designed and ready for implementation!** 🎊

All relationship management is gated by admin approval, providing the security and control you requested.
