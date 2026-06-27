# Sprint 2 Implementation — Superadmin Approval Dashboard

## What was built

### Backend (Flask)
- **Protocol Request Model**: `api/v1/models/protocol_request.py` — Domain model with request/approval/rejection lifecycle
- **Request Schemas**: `api/v1/schemas/protocol_request.py` — Pydantic validation for requests and responses
- **Request Routes**: `api/v1/routes/protocol_requests.py` — FastAPI endpoints for viewing and deciding on requests
- **Protocol Route Updates**: Modified `protocols.py` to create request when protocol is submitted

### Frontend (React)
- **ApprovalDashboard**: `src/pages/superadmin/v2/ApprovalDashboard.jsx` — Superadmin dashboard for reviewing and approving/rejecting protocols

---

## Integration Steps

### 1. Add the protocol-requests router to Flask app

Open `api/app_firestore.py` and add:

```python
from api.v1.routes.protocol_requests import router as protocol_requests_router

# In the FastAPI app setup:
app.include_router(protocol_requests_router)
```

### 2. Update App.jsx with approval dashboard route

```jsx
import ApprovalDashboard from './pages/superadmin/v2/ApprovalDashboard';

// In your route configuration:
<Route path="/superadmin/approvals" element={<ApprovalDashboard currentUser={currentUser} />} />
```

### 3. Add navigation link in the sidebar

Add a link to the approval dashboard for superadmins:

```jsx
{currentUser?.role === 'superadmin' && (
  <Link to="/superadmin/approvals" className="...">
    <CheckCircle2 className="w-5 h-5" />
    <span>Protocol Approvals</span>
  </Link>
)}
```

---

## API Workflow

### When a physiotherapist submits a protocol:

```
POST /api/v1/protocols/{id}/submit
  → Protocol status: DRAFT → SUBMITTED
  → Creates ProtocolRequest in PENDING status
  → Returns updated Protocol
```

### When a superadmin views pending requests:

```
GET /api/v1/protocol-requests/pending
  → Returns list of all PENDING requests
  → Each request shows protocol_id, requested_by, created_at
```

### When a superadmin approves:

```
POST /api/v1/protocol-requests/{request_id}/approve
  → Request status: PENDING → APPROVED
  → Protocol status: SUBMITTED → APPROVED (published)
  → Returns updated ProtocolRequest with decision info
```

### When a superadmin rejects:

```
POST /api/v1/protocol-requests/{request_id}/reject
  → Request status: PENDING → REJECTED
  → Protocol status: remains SUBMITTED (not rejected directly)
  → Physiotherapist can edit and resubmit
  → Returns updated ProtocolRequest with rejection reason
```

---

## Testing

### 1. Backend API

Test the approval workflow:

```bash
# List pending requests
curl http://localhost:8080/api/v1/protocol-requests/pending \
  -H "Authorization: Bearer superadmin_123"

# Get request details
curl http://localhost:8080/api/v1/protocol-requests/req_abc \
  -H "Authorization: Bearer superadmin_123"

# Approve
curl -X POST http://localhost:8080/api/v1/protocol-requests/req_abc/approve \
  -H "Authorization: Bearer superadmin_123" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Looks good!"}'

# Reject
curl -X POST http://localhost:8080/api/v1/protocol-requests/req_abc/reject \
  -H "Authorization: Bearer superadmin_123" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Need to specify baseline metrics"}'
```

### 2. Frontend Full Workflow

1. Log in as physiotherapist
2. Navigate to `/physiotherapist/protocols/v2`
3. Create a protocol and fill in all fields
4. Click "Save Draft"
5. Click "Submit for Approval"
   - Should see success message
   - Protocol should disappear from "Your Drafts" (now in SUBMITTED state)

6. Log out and log in as superadmin
7. Navigate to `/superadmin/approvals`
8. Should see the protocol in pending list
9. Click on it to view details
10. Click "Approve Protocol"
    - Should see success message
    - Request should disappear from list

11. Log back in as physiotherapist
12. Navigate to `/physiotherapist/protocols` (list view for published)
13. Should see the approved protocol

---

## Database Schema (Firestore)

### `protocol_requests_v1` collection

```json
{
  "request_id": "uuid",
  "protocol_id": "uuid",
  "requested_by": "user_123",
  "status": "pending|approved|rejected",
  "created_at": "2026-06-26T12:00:00Z",
  "decision": {
    "decided_by": "superadmin_456",
    "decision": "approved",
    "reason": "Looks good",
    "decided_at": "2026-06-26T12:30:00Z"
  }
}
```

### `protocols_v1` collection (updated)

When a protocol is approved, the existing document's status changes:

```json
{
  "status": "approved",  // Changed from "submitted"
  "updated_at": "2026-06-26T12:30:00Z"
}
```

---

## Logging Output

### Physiotherapist submits protocol

```json
{
  "timestamp": "2026-06-26T12:15:00Z",
  "service": "moove-backend",
  "event": "protocol.submitted",
  "severity": "info",
  "correlation_id": "c-123",
  "user_id": "user_123",
  "entity_type": "protocol",
  "entity_id": "proto_abc",
  "extra": {"request_id": "req_789"},
  "message": "Protocol submitted for approval"
}
```

### Superadmin approves

```json
{
  "timestamp": "2026-06-26T12:20:00Z",
  "service": "moove-backend",
  "event": "protocol_request.approved",
  "severity": "info",
  "correlation_id": "c-456",
  "user_id": "superadmin_456",
  "entity_type": "protocol_request",
  "entity_id": "req_789",
  "message": "Protocol approved and published"
}
```

---

## Key Points

1. **Request = Approval Decision Point**: When a protocol is submitted, a `ProtocolRequest` is created. This decouples the protocol lifecycle from the approval lifecycle.

2. **Protocol Status Changes**: Only the superadmin approval changes the protocol status to APPROVED. Rejections don't change the protocol status (it stays SUBMITTED so the creator can edit and resubmit).

3. **Notification TODO**: Both `protocol_requests.py` and `protocols.py` have `# TODO: Emit event for notification`. This is where you'll hook in event emitter for real-time notifications to physiotherapists and coaches.

4. **Authorization**: Superadmin endpoint checks authorization header but relies on role checking in the `require_superadmin` dependency. Update this with real role-based access control.

---

## Next Steps (Sprint 3)

- **Coach initiates analysis**: API to start pose extraction job
- **Background worker**: Pose extraction job processor
- **Notification system**: Real-time updates to physiotherapists and coaches

---

## Troubleshooting

### "Unauthorized" on approval endpoints
- Check that you're using a superadmin user ID
- Verify `Authorization: Bearer {token}` format
- Update `require_superadmin()` function with real role checking

### Request not showing in pending list
- Verify protocol was submitted (check `protocols_v1` collection status = "submitted")
- Check that `protocol_requests_v1` collection has the request document
- Verify request status = "pending"

### Firestore queries failing
- Ensure composite indexes exist for:
  - `protocol_requests_v1`: where status == "pending", order_by created_at
  - `protocols_v1`: where status == "submitted"

### Frontend not loading requests
- Check browser console for API errors
- Verify CORS is enabled on Flask app
- Check `VITE_API_URL` environment variable

---

## Success Criteria for Sprint 2

- [ ] Physiotherapist can submit protocol (creates SUBMITTED protocol + PENDING request)
- [ ] Superadmin can see list of pending requests
- [ ] Superadmin can view protocol details from request
- [ ] Superadmin can approve (PENDING → APPROVED request, SUBMITTED → APPROVED protocol)
- [ ] Superadmin can reject (PENDING → REJECTED request, protocol stays SUBMITTED)
- [ ] All state transitions are logged with correlation IDs
- [ ] Dashboard UI shows list and detail views
- [ ] Success/error messages appear on UI
- [ ] Firestore documents reflect all state changes
