# Integration Testing Checklist

## Pre-Flight Checks ✓

- [ ] Python environment activated (`.venv`)
- [ ] All dependencies installed (`pip install -r api/requirements.txt`)
- [ ] Firestore credentials set (`GOOGLE_APPLICATION_CREDENTIALS` env var)
- [ ] Backend starts without errors (`python -m api.app_firestore`)
- [ ] Frontend dev server runs (`npm run dev`)
- [ ] CORS enabled on Flask backend

## Backend API Tests

### Protocol Creation
```bash
# Create a protocol
curl -X POST http://localhost:8080/api/v1/protocols \
  -H "Authorization: Bearer test-user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_name": "Football ACL Test",
    "description": "Test ACL protocol",
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
```
- [ ] Response code: 201
- [ ] Response includes `protocol_id`, `status: "draft"`, `created_by: "test-user-123"`
- [ ] Firestore document created in `protocols_v1` collection

### Protocol Listing
```bash
# List user's draft protocols
curl http://localhost:8080/api/v1/protocols/my-drafts \
  -H "Authorization: Bearer test-user-123"
```
- [ ] Response code: 200
- [ ] Response includes array of protocols where `created_by: "test-user-123"`
- [ ] Only DRAFT status protocols shown

### Protocol Retrieval
```bash
# Get protocol by ID
curl http://localhost:8080/api/v1/protocols/{protocol_id} \
  -H "Authorization: Bearer test-user-123"
```
- [ ] Response code: 200 (if creator or APPROVED)
- [ ] Response code: 403 (if not creator and not APPROVED)
- [ ] Response includes full protocol details

### Protocol Update
```bash
# Update draft protocol
curl -X PUT http://localhost:8080/api/v1/protocols/{protocol_id} \
  -H "Authorization: Bearer test-user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_name": "Football ACL Test - Updated"
  }'
```
- [ ] Response code: 200
- [ ] Firestore document updated
- [ ] Can only update own protocols (403 if not creator)
- [ ] Can only update DRAFT status (400 if already SUBMITTED)

### Protocol Submission
```bash
# Submit protocol for approval
curl -X POST http://localhost:8080/api/v1/protocols/{protocol_id}/submit \
  -H "Authorization: Bearer test-user-123"
```
- [ ] Response code: 200
- [ ] Protocol status changed from DRAFT to SUBMITTED
- [ ] Entry created in `protocol_requests_v1` with status PENDING
- [ ] Request entry has `requested_by: "test-user-123"`, `protocol_id: "{id}"`

### Approval Request Listing
```bash
# List pending approval requests
curl http://localhost:8080/api/v1/protocol-requests/pending \
  -H "Authorization: Bearer superadmin-user"
```
- [ ] Response code: 200
- [ ] Returns array of requests with status: "pending"
- [ ] Each request includes `request_id`, `protocol_id`, `requested_by`, `created_at`

### Protocol Approval
```bash
# Approve protocol
curl -X POST http://localhost:8080/api/v1/protocol-requests/{request_id}/approve \
  -H "Authorization: Bearer superadmin-user" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Looks good"}'
```
- [ ] Response code: 200
- [ ] Request status changed to APPROVED
- [ ] Associated protocol status changed to APPROVED
- [ ] Response includes decision with `decided_by`, `decided_at`

### Protocol Rejection
```bash
# Reject protocol
curl -X POST http://localhost:8080/api/v1/protocol-requests/{request_id}/reject \
  -H "Authorization: Bearer superadmin-user" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Need more baseline metrics"}'
```
- [ ] Response code: 200
- [ ] Request status changed to REJECTED
- [ ] Protocol status remains SUBMITTED (not rejected directly)
- [ ] Response includes rejection reason in decision

## Frontend UI Tests

### Physiotherapist Dashboard

#### Protocol Creation
- [ ] Navigate to "Cases" view (main dashboard)
- [ ] Click "Custom Protocols" tab
- [ ] "Your Draft Protocols" list empty initially
- [ ] Click "New Protocol" button
- [ ] Form appears with tabs: Basic, Analysis, Baseline, Report
- [ ] Fill in Basic tab:
  - [ ] Enter protocol name "Test Protocol"
  - [ ] Enter description "Test description"
  - [ ] Select sport from dropdown
- [ ] Click Analysis tab
- [ ] Add joints:
  - [ ] Enter "knee_right" in joint field
  - [ ] Click "Add Joint"
  - [ ] Joint appears in list
  - [ ] Can remove joint with X button
- [ ] Add angles:
  - [ ] Enter "flexion" in angle field
  - [ ] Click "Add Angle"
  - [ ] Angle appears in list
- [ ] Add metrics:
  - [ ] Enter "range_of_motion" in metric field
  - [ ] Click "Add Metric"
  - [ ] Metric appears in list
- [ ] Click "Save Draft" button
- [ ] Success message appears: "Protocol saved as draft"
- [ ] Protocol appears in "Your Draft Protocols" list

#### Protocol Submission
- [ ] From draft protocols list, click on a protocol
- [ ] "Edit" button appears
- [ ] Click "Edit" to load protocol
- [ ] Form populates with existing data
- [ ] Make a small change (e.g., add another joint)
- [ ] Click "Save Draft"
- [ ] Success message appears
- [ ] Click "Submit for Approval"
- [ ] Success message appears: "Submitted for approval"
- [ ] Protocol disappears from "Your Draft Protocols"
- [ ] Tab automatically switches to draft list

### Superadmin Dashboard

#### Approval Dashboard View
- [ ] Log in as superadmin user
- [ ] Navigate to "Protocol Approvals" panel
- [ ] Initial list empty or shows pending protocols
- [ ] Each protocol request shows:
  - [ ] Protocol name
  - [ ] Physiotherapist who submitted
  - [ ] Submission date/time

#### Approve Protocol
- [ ] Click on a protocol request in the pending list
- [ ] Request details appear:
  - [ ] Protocol name, sport, description
  - [ ] Analysis configuration (joints, angles, metrics)
- [ ] Click "Approve Protocol"
- [ ] Success message appears
- [ ] Protocol disappears from pending list
- [ ] List count decreases

#### Reject Protocol
- [ ] Click on another protocol request
- [ ] Click "Reject Protocol"
- [ ] Rejection form appears with reason text area
- [ ] Enter rejection reason (e.g., "Need baseline metrics")
- [ ] Click "Confirm Reject"
- [ ] Success message appears
- [ ] Protocol disappears from pending list
- [ ] Physiotherapist can re-edit and resubmit

## Error Handling Tests

### Authorization Errors
- [ ] API call without Authorization header → 401
- [ ] API call with invalid token → 401
- [ ] Non-creator trying to edit protocol → 403
- [ ] Non-superadmin trying to approve → 401/403

### Validation Errors
- [ ] Submit protocol with missing fields → 400 with error message
- [ ] Try to submit non-DRAFT protocol → 400 with error message
- [ ] Try to approve non-PENDING request → 400 with error message

### Network Errors
- [ ] Frontend gracefully handles API timeouts
- [ ] Frontend shows error message if backend unreachable
- [ ] Frontend retries failed requests (if applicable)

## Logging Tests

### Check Logs
- [ ] Backend logs appear in console or Cloud Logging
- [ ] Each action logged with correlation ID
- [ ] Logs include `event`, `user_id`, `entity_type`, `entity_id`, `message`
- [ ] Error logs include `error_code`
- [ ] Log severity levels correct (info/error)

## Performance Tests

- [ ] Protocol creation < 2s
- [ ] List protocols < 1s
- [ ] Approve/reject < 2s
- [ ] Frontend form responsive (no lag on add/remove fields)
- [ ] No console errors

## Success Criteria

- [ ] All API tests pass (backend)
- [ ] All UI tests pass (frontend)
- [ ] All error handling works
- [ ] Logs contain all expected information
- [ ] Performance acceptable

## Sign-Off

Date tested: _____________
Tester: _____________
Result: [ ] PASS  [ ] FAIL

Notes:
________________________________
________________________________
