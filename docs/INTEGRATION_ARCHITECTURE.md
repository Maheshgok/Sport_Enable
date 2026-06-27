# Integration Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOOVE PLATFORM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐          ┌──────────────────────┐     │
│  │   PHYSIOTHERAPIST    │          │     SUPERADMIN       │     │
│  │     FRONTEND         │          │      FRONTEND        │     │
│  ├──────────────────────┤          ├──────────────────────┤     │
│  │ ProtocolBuilderV2    │          │ ApprovalDashboard    │     │
│  │ - Create protocol    │          │ - View pending       │     │
│  │ - Save draft         │          │ - Approve/reject     │     │
│  │ - Submit for review  │          │ - See details        │     │
│  └────────┬─────────────┘          └────────┬─────────────┘     │
│           │ API calls                      │ API calls         │
│           │ (Bearer token auth)            │ (Bearer token auth)
│           │                                │                   │
│           └────────────────┬───────────────┘                   │
│                            │                                   │
│           ┌────────────────▼───────────────┐                  │
│           │      FLASK BACKEND API         │                  │
│           │   (app_firestore.py)           │                  │
│           ├───────────────────────────────┤                   │
│           │  /api/v1/protocols            │                  │
│           │  /api/v1/protocol-requests    │                  │
│           │                               │                  │
│           │ (Routes from v1_routes_flask)│                  │
│           └────────────────┬──────────────┘                  │
│                            │                                   │
│           ┌────────────────▼───────────────┐                  │
│           │   V1 MODEL LAYER              │                  │
│           │  (Repositories & Models)      │                  │
│           ├───────────────────────────────┤                  │
│           │ ProtocolRepository            │                  │
│           │ ProtocolRequestRepository     │                  │
│           │ StructuredLogger              │                  │
│           └────────────────┬──────────────┘                  │
│                            │                                   │
│           ┌────────────────▼───────────────┐                  │
│           │     FIRESTORE DATABASE        │                  │
│           │                               │                  │
│           │ Collections:                  │                  │
│           │  - protocols_v1               │                  │
│           │  - protocol_requests_v1       │                  │
│           └───────────────────────────────┘                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Protocol Creation

```
1. Physiotherapist fills form
   ↓
2. Clicks "Save Draft"
   ↓
3. Frontend POST /api/v1/protocols {protocol_name, description, sport_id, config}
   with Authorization: Bearer {user_id}
   ↓
4. Flask route handler in v1_routes_flask.py:
   - Extracts user_id from Authorization header
   - Validates required fields
   - Creates ProtocolConfig object
   ↓
5. Calls ProtocolRepository.create()
   - Generates protocol_id (UUID)
   - Sets status = DRAFT
   - Saves to protocols_v1 collection
   - Logs event with correlation_id
   ↓
6. Returns Protocol object as JSON
   ↓
7. Frontend shows success message
   Protocol appears in "Your Draft Protocols" list
```

## Data Flow: Protocol Submission

```
1. Physiotherapist clicks "Submit for Approval"
   ↓
2. Frontend POST /api/v1/protocols/{id}/submit
   with Authorization: Bearer {user_id}
   ↓
3. Flask route handler:
   - Extracts user_id
   - Checks if creator (400 if not)
   - Checks if DRAFT status (400 if not)
   ↓
4. Calls ProtocolRepository.submit()
   - Changes status to SUBMITTED
   - Updates updated_at
   - Saves to Firestore
   ↓
5. Calls ProtocolRequestRepository.create_from_submission()
   - Creates new entry in protocol_requests_v1
   - Sets status = PENDING
   - Links to protocol_id
   - Stores requested_by = user_id
   ↓
6. Both operations logged
   ↓
7. Frontend shows success
   Protocol removed from draft list
```

## Data Flow: Protocol Approval

```
1. Superadmin clicks "Approve Protocol"
   ↓
2. Frontend POST /api/v1/protocol-requests/{request_id}/approve
   with Authorization: Bearer {superadmin_id}
   ↓
3. Flask route handler:
   - Extracts superadmin_id
   - Validates request exists
   - Checks status is PENDING
   ↓
4. Calls ProtocolRequestRepository.approve()
   - Changes request status to APPROVED
   - Creates ApprovalDecision record
   - Records decided_by, decided_at, reason
   - Saves to Firestore
   ↓
5. Calls ProtocolRepository.approve()
   - Changes protocol status to APPROVED
   - Saves to Firestore (now visible to coaches)
   ↓
6. Both operations logged
   ↓
7. Frontend refreshes pending list
   Request disappears (status changed)
```

## Component Hierarchy

### Frontend (React)

```
App.jsx
├── MainApp()
│   ├── PhysiotherapistDashboard ({currentView, setCurrentView, currentUser})
│   │   ├── currentView = 'dashboard'
│   │   │   └── Dashboard overview
│   │   ├── currentView = 'cases'
│   │   │   ├── activeTab = 'protocols'
│   │   │   │   └── ProtocolBuilderV2 ({currentUser})  ← NEW
│   │   │   ├── activeTab = 'cases'
│   │   │   │   └── CaseList / CaseDetail
│   │   │   ├── activeTab = 'prompts'
│   │   │   │   └── AssessmentPrompts
│   │   │   └── activeTab = 'requests'
│   │   │       └── RequestManagement
│   │
│   └── SuperadminDashboard
│       ├── Panel: 'onboarding'
│       │   └── OnboardingPanel
│       ├── Panel: 'users'
│       │   └── UserManagement
│       ├── Panel: 'protocol-approvals'  ← NEW
│       │   └── ApprovalDashboard ({currentUser})
│       ├── Panel: 'physio-requests'
│       │   └── PhysioRequests
│       └── Panel: 'meta'
│           └── MetaAnalysis
```

### Backend (Flask/Python)

```
app_firestore.py (Flask app)
├── Registers protocol routes from v1_routes_flask.py
└── Initializes Firestore client
    
v1_routes_flask.py (Flask route handlers)
├── POST /api/v1/protocols (create)
├── GET /api/v1/protocols/my-drafts (list user drafts)
├── GET /api/v1/protocols/{id} (get)
├── PUT /api/v1/protocols/{id} (update)
├── POST /api/v1/protocols/{id}/submit (submit)
├── GET /api/v1/protocol-requests/pending (list pending)
├── GET /api/v1/protocol-requests/{id} (get request)
├── POST /api/v1/protocol-requests/{id}/approve (approve)
└── POST /api/v1/protocol-requests/{id}/reject (reject)

v1/models/protocol.py
├── Protocol (dataclass)
├── ProtocolStatus (enum)
├── ProtocolConfig (dataclass)
└── ProtocolRepository (Firestore persistence)

v1/models/protocol_request.py
├── ProtocolRequest (dataclass)
├── RequestStatus (enum)
├── ApprovalDecision (dataclass)
└── ProtocolRequestRepository (Firestore persistence)

v1/schemas/protocol.py
├── ProtocolConfigSchema (Pydantic)
├── ProtocolCreateRequest
├── ProtocolUpdateRequest
└── ProtocolResponse

v1/schemas/protocol_request.py
├── ProtocolRequestResponse
├── ApprovalDecisionSchema
├── ApproveRequest
└── RejectRequest

v1/core/logging.py
└── StructuredLogger (JSON logging with correlation IDs)
```

## Authorization Model

### API Level
```
All endpoints require Authorization header:
Authorization: Bearer {user_id}

User ID extracted from header and passed to business logic
```

### Business Logic Level
```
Physiotherapist endpoints:
- Can only CRUD own protocols (created_by == user_id)
- Can only edit DRAFT protocols
- Can only submit to SUBMITTED status

Superadmin endpoints:
- Can view all pending requests
- Can approve/reject any pending request (no creator check)
```

### Firestore Level
Security rules can enforce:
- Authenticated users only
- Can read own user docs
- Can read shared/public data
- Admins can read all
```

## Error Handling

### API Level
- 401: Missing/invalid Authorization header
- 403: Not authorized to access/modify resource
- 404: Resource not found
- 400: Invalid request (validation errors, wrong state transition)
- 500: Server error (try/except catches and logs)

### Frontend Level
- Network errors caught and displayed as toast/message
- Form validation before API call
- Disabled buttons during loading
- Error messages persist until dismissed

### Logging Level
- All errors logged with correlation_id
- Include error_code for categorization
- Include user_id for audit trail
- Full stack trace in server logs (not returned to client)

## State Management

### Frontend (React)
- Component state for form data, loading, errors, success
- currentUser passed via props (from AuthContext)
- currentView controls major sections
- activeTab controls tabs within sections

### Backend (Firestore)
- Protocol documents in protocols_v1 collection
- Request documents in protocol_requests_v1 collection
- Timestamps (created_at, updated_at) for audit trail
- Status fields (enum) for state transitions

## Deployment Considerations

### Local Development
```bash
# Python backend
python -m api.app_firestore

# React frontend  
npm run dev

# Both need:
- Firestore credentials (GOOGLE_APPLICATION_CREDENTIALS)
- Environment variables (VITE_API_URL)
```

### Cloud Deployment (Cloud Run)
```
- Flask app containerized (Dockerfile exists)
- Firestore used directly (no local fallback needed)
- Cloud Logging captures all logs
- IAM roles ensure access to Firestore, Storage
```

## Performance Characteristics

### API Response Times
- Create protocol: 100-200ms (Firestore write)
- List protocols: 50-100ms (Firestore query)
- Approve/reject: 200-300ms (update + request creation)

### Database Load
- Reads: Simple direct lookups or where clause filters
- Writes: Sequential (protocol update, then request creation)
- Indexes: Auto-created for status queries

### Frontend Performance
- Form fields add/remove: <50ms (local state)
- API calls: Async, non-blocking
- Re-renders: Minimal (state updates only)

## Security

### Authentication
- User ID extracted from Bearer token (frontend responsible for issuing)
- No password/session management at API level
- TODO: Implement proper JWT validation

### Authorization
- Business logic checks creator/role before operations
- TODO: Implement proper role-based access control (RBAC)

### Data Protection
- Firestore collections are authenticated (users must be logged in)
- TODO: Add field-level encryption for sensitive data
- TODO: Add audit logging for compliance

### Validation
- Pydantic schemas validate all inputs
- Required fields checked
- Enums prevent invalid state transitions

## Scalability

### Current Architecture
- Stateless Flask backend (can scale horizontally)
- Firestore handles database scaling
- Frontend is SPA (browser-based scaling)

### Bottlenecks (if any)
- Firestore queries could slow down with large datasets (>1M protocols)
- Real-time notifications not yet implemented (polling alternative slower)
- Logging to Cloud Logging has rate limits

### Future Improvements
- Add caching layer (Redis) for frequently accessed protocols
- Implement batch operations for bulk approvals
- Add CDN for static assets (frontend)
- Implement event sourcing for audit trail
