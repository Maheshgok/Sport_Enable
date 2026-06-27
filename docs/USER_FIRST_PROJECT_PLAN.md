# Moove Project Plan: User-First Implementation

## Goal
Build the new architecture by starting with what users need to see and do, then implement the backend to support each capability. Every backend piece serves a clear frontend need.

---

## Phase 1 — Foundation and Setup

### 1.1 Project setup and team alignment
- [ ] Define the new app as a parallel branch or new folder structure
- [ ] Create a shared understanding of user roles and what each sees
- [ ] Set up logging and error tracking infrastructure from the start
- [ ] Establish a dev environment with database, storage, and queue setup

### 1.2 User roles and journeys
- [ ] Physiotherapist: create protocols, submit for approval, execute on athletes
- [ ] Superadmin: view pending protocol requests on a dashboard, approve/reject
- [ ] Coach: see approved protocols, start an analysis for an athlete, view reports
- [ ] Athlete/Caretaker: see their own accessible reports and results

---

## Phase 2 — Physiotherapist Protocol Creation (Feature 1)

### User need
A physiotherapist can design a custom analysis protocol and submit it for approval.

### Frontend
- [ ] Create protocol creation UI
  - [ ] Form for protocol name, description, sport
  - [ ] Configuration fields for angles to measure, joints to track
  - [ ] Baseline metrics and risk factor inputs
  - [ ] Report template section selection
  - [ ] Submit button that sends to backend

### Backend
- [ ] Create protocol model in database
  - [ ] protocol table with id, name, description, created_by, status
  - [ ] protocol_config table with analysis_config, baseline_metrics, risk_factors, report_template
  - [ ] protocol_status: draft, submitted, approved, archived
- [ ] Create protocol API endpoints
  - [ ] POST /api/v1/protocols (create or save draft)
  - [ ] GET /api/v1/protocols/my-drafts (show user's draft protocols)
  - [ ] PUT /api/v1/protocols/{id} (update draft)
  - [ ] POST /api/v1/protocols/{id}/submit (transition from draft to submitted)
- [ ] Add logging for protocol state transitions

### Testing
- [ ] Physiotherapist can create a protocol and see it in draft
- [ ] Changes to draft are saved
- [ ] Submit action triggers notification to superadmin

---

## Phase 3 — Superadmin Approval Dashboard (Feature 2)

### User need
A superadmin sees pending protocol requests on a dashboard and can approve or reject them.

### Frontend
- [ ] Create superadmin dashboard with pending requests section
  - [ ] List of submitted protocols
  - [ ] Each card shows protocol name, submitter, date submitted
  - [ ] Approve and reject buttons
  - [ ] Modal or slide-out view for detailed protocol config

### Backend
- [ ] Create request/approval tracking
  - [ ] protocol_request table with id, protocol_id, requested_by, status, created_at, decision_at, decided_by
  - [ ] Add approval event table for audit trail
- [ ] Create approval endpoints
  - [ ] GET /api/v1/protocol-requests/pending (for superadmin dashboard)
  - [ ] POST /api/v1/protocol-requests/{id}/approve
  - [ ] POST /api/v1/protocol-requests/{id}/reject
- [ ] Add notifications
  - [ ] Send notification to physiotherapist when protocol approved
  - [ ] Send notification to coaches when protocol becomes available

### Testing
- [ ] Superadmin sees pending requests
- [ ] Approval transitions protocol to published state
- [ ] Physiotherapist is notified of approval or rejection

---

## Phase 4 — Coach Initiates Analysis (Feature 3)

### User need
A coach can select an approved protocol, upload a video, and start an analysis for an athlete.

### Frontend
- [ ] Create analysis setup page
  - [ ] Dropdown to select approved protocols
  - [ ] Dropdown to select athlete
  - [ ] Video file upload (front view, optional side view)
  - [ ] Athlete metadata inputs (height, etc.)
  - [ ] Start analysis button
- [ ] Show execution status page with stages (pose extraction → analysis → report)

### Backend
- [ ] Create analysis execution model
  - [ ] analysis_execution table with id, protocol_id, athlete_id, initiated_by, status, created_at
  - [ ] analysis_step table to track pose extraction, protocol analysis, report generation steps
- [ ] Create media upload and handling
  - [ ] Accept video uploads
  - [ ] Store videos in object storage
  - [ ] Create media_asset record with signed URL for access
- [ ] Create execution start endpoint
  - [ ] POST /api/v1/analyses (create execution, enqueue pose extraction job)
- [ ] Create status endpoint
  - [ ] GET /api/v1/analyses/{id}/status (returns current step, progress)
  - [ ] GET /api/v1/analyses/{id}/events (returns list of state transitions for UI timeline)
- [ ] Add logging for every step

### Testing
- [ ] Coach can upload video and start analysis
- [ ] Status page shows pending/running state
- [ ] Events are logged for each state change

---

## Phase 5 — Pose Extraction Pipeline (Backend Worker 1)

### User need
The system processes uploaded video and extracts pose data (user does not see this, but it must work reliably).

### Worker
- [ ] Create pose extraction worker
  - [ ] Subscribes to job queue
  - [ ] Downloads video from storage
  - [ ] Runs pose extraction algorithm
  - [ ] Saves pose frames to storage
  - [ ] Publishes completion event with artifact references
- [ ] Add retry logic
  - [ ] Retries up to 3 times on failure
  - [ ] Dead-letter handling if all retries fail
- [ ] Add logging
  - [ ] Log job start, progress checkpoints, completion
  - [ ] Log errors and retry attempts

### Backend support
- [ ] Create job message schema for pose extraction job
- [ ] Create job queue infrastructure (Pub/Sub or similar)
- [ ] Add pose_artifact table to track intermediate outputs
- [ ] Add execution step update logic to transition analysis_step.status from pose_extraction_pending → pose_extraction_running → pose_extraction_completed
- [ ] Add error handling to transition to failed state if worker fails

### Frontend observability
- [ ] Status page shows "pose extraction in progress" with start time
- [ ] If pose extraction fails, show user-friendly error message

### Testing
- [ ] Upload a test video and verify pose extraction completes
- [ ] Verify pose artifacts are stored and retrievable
- [ ] Simulate worker failure and verify retry and dead-letter behavior

---

## Phase 6 — Protocol-Specific Analysis (Backend Worker 2)

### User need
The system performs custom calculations based on the chosen protocol (user does not see this, but it must produce correct results).

### Worker
- [ ] Create protocol analysis worker
  - [ ] Subscribes to job queue
  - [ ] Downloads pose artifacts from pose extraction stage
  - [ ] Loads protocol definition with baseline metrics and risk factors
  - [ ] Runs protocol-specific calculations
  - [ ] Saves analysis results to storage
  - [ ] Publishes completion event with result references
- [ ] Add retry and error handling like pose extraction worker

### Backend support
- [ ] Create job message schema for analysis job
- [ ] Add analysis_result table to store computed metrics, flagged issues, recommendations
- [ ] Add execution step update logic to transition from analysis_pending → analysis_running → analysis_completed
- [ ] Ensure protocol config is accessible to worker

### Frontend observability
- [ ] Status page transitions to "analysis in progress"
- [ ] Show elapsed time

### Testing
- [ ] Verify protocol configuration is loaded correctly
- [ ] Verify results are stored and match expected calculations
- [ ] Test different protocols produce different results

---

## Phase 7 — Report Generation (Backend Worker 3)

### User need
The system generates a PDF report that the user can download and view.

### Worker
- [ ] Create report generation worker
  - [ ] Subscribes to job queue
  - [ ] Loads analysis results
  - [ ] Generates report content using report template from protocol
  - [ ] Renders PDF
  - [ ] Saves PDF and summary to storage
  - [ ] Publishes completion event with report URL
- [ ] Add retry and error handling

### Backend support
- [ ] Create job message schema for report job
- [ ] Add report table to store report metadata, URL, summary text, access rules
- [ ] Add execution step update logic to transition from report_pending → report_running → report_completed
- [ ] Ensure report is linked to correct user/athlete with proper access rules

### Frontend
- [ ] Status page transitions to "report ready"
- [ ] Show download button for PDF
- [ ] Show summary text on page

### Testing
- [ ] Verify PDF is generated and downloadable
- [ ] Verify access rules are enforced (athlete sees their own, coach sees their athletes', etc.)

---

## Phase 8 — Report Viewing (Feature 4)

### User need
Athletes, coaches, and parents can view reports for their accessible analyses.

### Frontend
- [ ] Create reports list page
  - [ ] Show all accessible reports with protocol name, athlete, date, status
  - [ ] Filter by athlete or protocol
- [ ] Create report detail page
  - [ ] Show summary text extracted from report
  - [ ] Show key findings and recommendations
  - [ ] Show download button for PDF
  - [ ] Optional: show PDF inline viewer
- [ ] Create athlete profile or summary page
  - [ ] Show athlete's recent reports
  - [ ] Show analysis timeline

### Backend
- [ ] Create report visibility and access endpoint
  - [ ] GET /api/v1/reports (returns reports accessible to current user)
  - [ ] GET /api/v1/reports/{id} (returns report data, enforces access)
  - [ ] GET /api/v1/reports/{id}/pdf (returns signed URL or streams PDF)
- [ ] Add role-based filtering:
  - [ ] Athletes/caretakers see only their own reports
  - [ ] Coaches see reports for their assigned athletes
  - [ ] Superadmin sees all reports

### Testing
- [ ] Athlete can see their own report
- [ ] Coach can see assigned athlete's reports
- [ ] Coach cannot see other coach's athletes' reports
- [ ] PDF is accessible for download

---

## Phase 9 — Real-Time Status Updates (Feature 5)

### User need
Coach sees analysis progress update in real time without refreshing the page.

### Frontend
- [ ] Add WebSocket or SSE subscription on execution detail page
  - [ ] Subscribe to execution events on page load
  - [ ] Update status and timeline when events arrive
  - [ ] Show "pose extraction complete" → "analysis running" → "report ready" in real time

### Backend
- [ ] Add WebSocket or SSE endpoint
  - [ ] GET /api/v1/analyses/{id}/subscribe (opens persistent connection)
  - [ ] Broadcast execution_step.status changes to connected clients
  - [ ] Enforce authorization (only allowed users receive updates)
- [ ] Publish events to WebSocket when jobs complete
  - [ ] Pose extraction completion → emit event
  - [ ] Analysis completion → emit event
  - [ ] Report completion → emit event

### Testing
- [ ] Submit an analysis and watch status update live
- [ ] Verify unauthorized users do not receive updates

---

## Phase 10 — Notifications (Feature 6)

### User need
Users are notified of important events without checking the dashboard.

### Frontend
- [ ] Create notification center UI
  - [ ] Show in-app notification list
  - [ ] Show notification badge with count
  - [ ] Mark as read/dismissed

### Backend
- [ ] Create notification model
  - [ ] notification table with id, user_id, event_type, related_entity_id, message, read_at
- [ ] Emit notifications for key events
  - [ ] Protocol submitted → notify superadmin
  - [ ] Protocol approved → notify physiotherapist
  - [ ] Analysis completed → notify coach
  - [ ] Report ready → notify athlete/caretaker
- [ ] Create notification endpoints
  - [ ] GET /api/v1/notifications (list for current user)
  - [ ] POST /api/v1/notifications/{id}/read
- [ ] Optional: add email notifications for critical events

### Testing
- [ ] Physiotherapist submits protocol, superadmin receives notification
- [ ] Coach starts analysis, receives notification when report is ready

---

## Phase 11 — Error Handling and User Feedback (Feature 7)

### User need
If something goes wrong, the user knows why and can take action.

### Frontend
- [ ] Add error messages to execution detail page
  - [ ] Show error reason if job fails
  - [ ] Show retry button if applicable
  - [ ] Show contact support link

### Backend
- [ ] Store failure details in execution record
  - [ ] failure_reason, failure_timestamp, last_retry_at, retry_count
- [ ] Add error tracking (Sentry or similar)
  - [ ] Capture all exceptions
  - [ ] Alert ops team on repeated failures
- [ ] Add detailed logging
  - [ ] Every job logs start, progress, completion, or failure
  - [ ] Include correlation IDs for tracing

### Testing
- [ ] Simulate pose extraction failure and verify error is shown to user
- [ ] Verify retry button retriggers the job
- [ ] Verify ops team receives alert on repeated failures

---

## Phase 12 — Protocol Visibility (Feature 8)

### User need
Coaches and athletes see only protocols that have been approved and made visible to them.

### Frontend
- [ ] Protocol selection dropdown shows only visible protocols
- [ ] Physiotherapist dashboard shows draft and submitted protocols they created

### Backend
- [ ] Add protocol visibility control
  - [ ] protocol_visibility table with protocol_id, role, visible (true/false)
  - [ ] When protocol is approved, set visible=true for coach and athlete roles
- [ ] Update protocol list endpoints
  - [ ] GET /api/v1/protocols?visible=true (for coaches/athletes)
  - [ ] GET /api/v1/protocols/all (for superadmin, unfiltered)
  - [ ] GET /api/v1/protocols/mine (for physiotherapist, shows own)
- [ ] Enforce visibility at query time

### Testing
- [ ] Physiotherapist sees their own protocols
- [ ] Coach sees only approved protocols
- [ ] Superadmin sees all protocols

---

## Phase 13 — Audit Trail and Compliance (Feature 9)

### User need
Organization can audit who did what and when (compliance requirement).

### Backend
- [ ] Add audit_event table
  - [ ] event_type, actor_id, entity_type, entity_id, action, timestamp, changes (JSON)
- [ ] Log all important actions
  - [ ] Protocol created/edited/published
  - [ ] Request approved/rejected
  - [ ] Analysis started/completed
  - [ ] Report viewed/downloaded
- [ ] Create audit endpoint
  - [ ] GET /api/v1/audit?entity_id={id}&event_type={type} (for superadmin)

### Frontend
- [ ] Optional: show audit timeline on protocol or report detail pages

### Testing
- [ ] Verify protocol creation is logged
- [ ] Verify approval is logged with decision_by
- [ ] Verify audit can be queried

---

## Phase 14 — Testing and Quality (Feature 10)

### Backend tests
- [ ] Unit tests for protocol creation and state transitions
- [ ] Unit tests for execution orchestration
- [ ] Integration tests for the full flow: protocol submit → approve → start analysis → report generation
- [ ] Worker tests: pose extraction, analysis, report generation
- [ ] Queue retry and dead-letter tests

### Frontend tests
- [ ] Component tests for protocol form, execution status page, report viewer
- [ ] Integration tests for user flows (select protocol → upload → see status → download report)
- [ ] Permission tests (verify users see only their data)

### Load tests
- [ ] Test queue under high volume
- [ ] Test worker scaling

---

## Phase 15 — Deployment and Cutover (Feature 11)

### Pre-production
- [ ] Deploy new backend and workers in parallel with existing app
- [ ] Add feature flags to routing
  - [ ] Route new users to new flow gradually
  - [ ] Keep old flow available for fallback

### Production
- [ ] Monitor logs, errors, performance on new flow
- [ ] Switch new users to new flow
- [ ] Once stable, retire old flow code

### Post-production
- [ ] Document new architecture and operations
- [ ] Set up runbooks for common issues
- [ ] Decommission old code and dependencies

---

## Sprint-by-Sprint Breakdown

### Sprint 1: Physiotherapist Protocol Creation
- Phase 1.1, 1.2
- Phase 2 (frontend + backend)

### Sprint 2: Superadmin Dashboard
- Phase 3

### Sprint 3: Coach Analysis Setup
- Phase 4

### Sprint 4: Pose Extraction Pipeline
- Phase 5

### Sprint 5: Protocol Analysis Pipeline
- Phase 6

### Sprint 6: Report Generation
- Phase 7

### Sprint 7: Report Viewing
- Phase 8

### Sprint 8: Real-Time Updates + Notifications
- Phase 9
- Phase 10

### Sprint 9: Error Handling + Visibility + Audit
- Phase 11
- Phase 12
- Phase 13

### Sprint 10: Testing + Deployment
- Phase 14
- Phase 15

---

## Key Principles Throughout

1. **Every backend feature serves a frontend need**: do not build backend capability that is not used by the UI
2. **Frontend-first design**: sketch the user experience first, then determine backend requirements
3. **Early integration**: integrate frontend and backend early; do not wait until each is "done"
4. **Logging from day one**: structured logs, correlation IDs, and tracing are not afterthoughts
5. **User feedback**: show users what is happening; no silent failures
6. **Easy rollback**: keep old flow available until new flow is proven
7. **Role-based throughout**: every query and action respects user roles and permissions

---

## Success Criteria

- Physiotherapist can create and submit a protocol
- Superadmin can approve and reject protocols
- Coach can start an analysis on a video
- Analysis completes with pose extraction → protocol analysis → report generation
- Report is downloadable and viewable
- All users see their accessible data
- Errors are shown to users and logged for debugging
- No user can access data they should not see
- New architecture is production-ready and can coexist with the current app
