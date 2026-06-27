# Sprint 1 Implementation — Integration Guide

## What was built

### Backend (Flask)
- **Logging**: `api/v1/core/logging.py` — Structured JSON logging with correlation IDs
- **Protocol Model**: `api/v1/models/protocol.py` — Domain model, repository, and Firestore persistence
- **Schemas**: `api/v1/schemas/protocol.py` — Pydantic request/response validation
- **Routes**: `api/v1/routes/protocols.py` — FastAPI endpoints for protocol CRUD and submission

### Frontend (React)
- **ProtocolBuilderV2**: `src/pages/physiotherapist/v2/ProtocolBuilderV2.jsx` — UI for creating and managing protocols

---

## Integration Steps

### 1. Add the v1 API routes to Flask app

Open `api/app_firestore.py` and add the new router:

```python
from api.v1.routes.protocols import router as protocols_router

# In the FastAPI app setup:
app.include_router(protocols_router)
```

### 2. Update App.jsx to add the new protocol builder route

```jsx
import ProtocolBuilderV2 from './pages/physiotherapist/v2/ProtocolBuilderV2';

// In your route configuration:
<Route path="/physiotherapist/protocols/v2" element={<ProtocolBuilderV2 currentUser={currentUser} />} />
<Route path="/physiotherapist/protocols/v2/:protocolId" element={<ProtocolBuilderV2 currentUser={currentUser} />} />
```

### 3. Add navigation link in the sidebar

Add a link to the new protocol builder in your physiotherapist dashboard:

```jsx
<Link to="/physiotherapist/protocols/v2" className="...">
  <FileText className="w-5 h-5" />
  <span>Create Protocol (v2)</span>
</Link>
```

### 4. Fix the database access in routes

Update `api/v1/routes/protocols.py` to properly initialize the Firestore client:

```python
from api.firestore_db import get_db

def get_protocol_repository() -> ProtocolRepository:
    """Get protocol repository with database client"""
    db = get_db()  # Use your existing Firestore setup
    return ProtocolRepository(db)
```

---

## Testing

### 1. Backend API

Test the new endpoints with curl or Postman:

```bash
# Create a protocol
curl -X POST http://localhost:8080/api/v1/protocols \
  -H "Authorization: Bearer user_123" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_name": "Football ACL Baseline",
    "description": "Baseline assessment for ACL injury risk",
    "sport_id": "football",
    "config": {
      "joints_to_track": ["left_knee", "right_knee"],
      "angles_to_measure": ["knee_flexion"],
      "metrics_to_calculate": ["range_of_motion"],
      "baseline_metrics": {"knee_flexion": {"min": 0, "max": 120}},
      "risk_factors": {},
      "report_template": {"sections": ["summary"]},
      "required_views": ["front"],
      "expected_duration_seconds": 30
    }
  }'

# List draft protocols
curl http://localhost:8080/api/v1/protocols/my-drafts \
  -H "Authorization: Bearer user_123"

# Submit a protocol
curl -X POST http://localhost:8080/api/v1/protocols/{protocol_id}/submit \
  -H "Authorization: Bearer user_123"
```

### 2. Frontend

1. Log in as a physiotherapist
2. Navigate to `/physiotherapist/protocols/v2`
3. Click "New Protocol"
4. Fill in the basic info:
   - Name: "Test ACL Protocol"
   - Description: "Test protocol"
   - Sport: "football"
5. Click "Analysis" tab
6. Add joints, angles, and metrics
7. Click "Save Draft"
8. Verify the protocol appears in "Your Draft Protocols"
9. Click "Edit" to load it back
10. Click "Submit for Approval"

---

## Database Schema (Firestore)

The new protocols are stored in the `protocols_v1` collection:

```json
{
  "protocol_id": "uuid",
  "protocol_name": "Football ACL Baseline",
  "description": "...",
  "sport_id": "football",
  "created_by": "user_123",
  "status": "draft|submitted|approved|archived",
  "config": {
    "joints_to_track": [...],
    "angles_to_measure": [...],
    "metrics_to_calculate": [...],
    "baseline_metrics": {...},
    "risk_factors": {...},
    "report_template": {...},
    "required_views": ["front", "side"],
    "expected_duration_seconds": 30
  },
  "created_at": "2026-06-26T12:00:00Z",
  "updated_at": "2026-06-26T12:00:00Z",
  "version": 1
}
```

---

## Logging Output

The system logs all protocol actions as structured JSON. Example:

```json
{
  "timestamp": "2026-06-26T12:41:00Z",
  "service": "moove-backend",
  "event": "protocol.created",
  "severity": "info",
  "correlation_id": "c-789",
  "user_id": "user_123",
  "entity_type": "protocol",
  "entity_id": "proto_abc",
  "message": "Protocol created successfully"
}
```

These logs help with debugging, auditing, and monitoring.

---

## Next Steps (Sprint 2)

- Build the **Superadmin Approval Dashboard** to:
  - Show pending protocol requests
  - Allow approval/rejection
  - Send notifications to physiotherapists

---

## Troubleshooting

### "Module not found: api.v1.core.logging"
- Ensure the `api/v1/` folder structure is created with `__init__.py` files

### "Unauthorized" errors
- Check the `Authorization: Bearer {token}` header format
- The token should match the `user_id`

### Firestore document not saved
- Check that Firestore credentials are properly configured
- Verify that `protocols_v1` collection exists in Firestore

### Frontend not calling backend
- Check `VITE_API_URL` environment variable
- Verify CORS is enabled on the backend Flask app

---

## Success Criteria for Sprint 1

- [ ] Physiotherapist can create a protocol with basic info
- [ ] Physiotherapist can add joints, angles, and metrics
- [ ] Protocol is saved as draft in Firestore
- [ ] Physiotherapist can see their draft protocols
- [ ] Physiotherapist can edit draft protocols
- [ ] Physiotherapist can submit protocol for approval
- [ ] Submission transitions protocol from DRAFT to SUBMITTED state
- [ ] All actions are logged with correlation IDs
- [ ] Backend validates authorization (creator can only edit own protocols)
