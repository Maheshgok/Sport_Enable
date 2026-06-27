# Moove Implementation TODO

## Goal
Build the new architecture in parallel with the current demo application, using a modular monolith as the core application and separate background workers for pose extraction, analysis, and reporting.

---

## Phase 0 — Foundation and Planning

### 0.1 Architecture alignment
- [ ] Finalize the target architecture decision: modular monolith + background workers + queue-driven pipeline
- [ ] Document the migration boundary between current demo app and the new architecture
- [ ] Define the initial domain modules and ownership boundaries

### 0.2 Repository structure
- [ ] Create a new backend module structure under the main app for:
  - [ ] auth and access
  - [ ] protocols
  - [ ] requests and approvals
  - [ ] media
  - [ ] analysis orchestration
  - [ ] reports
  - [ ] notifications
- [ ] Create a new worker package for background jobs
- [ ] Create a shared package for common models, events, logging, and utilities

### 0.3 Observability setup
- [ ] Add structured logging format across the backend
- [ ] Add correlation ID propagation for requests and jobs
- [ ] Add request and job lifecycle logging
- [ ] Add error tracking integration for exceptions and job failures

---

## Phase 1 — Core Domain Models

### 1.1 User and access model
- [ ] Define user roles and permissions
- [ ] Define access rules for protocols, reports, and analysis results
- [ ] Build role-based authorization helpers
- [ ] Prepare tenant or clinic scoping hooks for future expansion

### 1.2 Protocol domain
- [ ] Create protocol model and schema
- [ ] Add versioning support for protocols
- [ ] Add protocol visibility and access rules
- [ ] Add schema for analysis configuration, baseline metrics, risk factors, and report template
- [ ] Add publish/archive workflow for protocols

### 1.3 Request and approval domain
- [ ] Create request model for protocol submission/approval
- [ ] Add status lifecycle states
- [ ] Add approval history and audit fields
- [ ] Add event emission for request state changes

### 1.4 Media domain
- [ ] Create media asset model
- [ ] Add upload metadata and artifact reference handling
- [ ] Add file storage location tracking
- [ ] Add signed URL generation support

### 1.5 Analysis execution domain
- [ ] Create execution model for each analysis workflow
- [ ] Add step-level status tracking for pose extraction, analysis, and reporting
- [ ] Add job metadata and retry information
- [ ] Add execution history and audit trail

---

## Phase 2 — Backend API Layer

### 2.1 API structure
- [ ] Create a new backend API router structure for:
  - [ ] protocols
  - [ ] requests
  - [ ] executions
  - [ ] reports
  - [ ] notifications
- [ ] Add versioned API routes
- [ ] Add request validation and schema enforcement

### 2.2 Protocol endpoints
- [ ] POST /api/v1/protocols
- [ ] GET /api/v1/protocols
- [ ] GET /api/v1/protocols/{id}
- [ ] PUT /api/v1/protocols/{id}
- [ ] DELETE or archive /api/v1/protocols/{id}

### 2.3 Request endpoints
- [ ] POST /api/v1/protocol-requests
- [ ] GET /api/v1/protocol-requests
- [ ] GET /api/v1/protocol-requests/{id}
- [ ] POST /api/v1/protocol-requests/{id}/approve
- [ ] POST /api/v1/protocol-requests/{id}/reject

### 2.4 Execution endpoints
- [ ] POST /api/v1/analyses
- [ ] GET /api/v1/analyses/{id}
- [ ] GET /api/v1/analyses/{id}/status
- [ ] GET /api/v1/analyses/{id}/events

### 2.5 Report endpoints
- [ ] GET /api/v1/reports/{id}
- [ ] GET /api/v1/reports/{id}/pdf
- [ ] GET /api/v1/reports/{id}/summary

### 2.6 Notification endpoints
- [ ] GET /api/v1/notifications
- [ ] POST /api/v1/notifications/{id}/read

---

## Phase 3 — Queue and Job Pipeline

### 3.1 Queue infrastructure
- [ ] Set up job queue infrastructure for background processing
- [ ] Define job message schema for each worker
- [ ] Add dead-letter handling for failed jobs
- [ ] Add retry policy with exponential backoff

### 3.2 Job orchestration
- [ ] Create orchestration logic for:
  - [ ] create execution record
  - [ ] enqueue pose extraction job
  - [ ] wait for pose extraction completion
  - [ ] enqueue analysis job
  - [ ] enqueue report generation job
- [ ] Add status updates after each stage
- [ ] Add event publication for each stage transition

### 3.3 Worker contracts
- [ ] Define input/output contract for pose extraction worker
- [ ] Define input/output contract for analysis worker
- [ ] Define input/output contract for report worker

---

## Phase 4 — Pose Extraction Worker

### 4.1 Worker skeleton
- [ ] Create a standalone pose extraction worker process
- [ ] Connect it to the queue and storage systems
- [ ] Add structured logging and job-level tracing

### 4.2 Processing logic
- [ ] Accept video asset and execution context
- [ ] Run pose extraction pipeline
- [ ] Save intermediate artifacts to object storage
- [ ] Publish completion event with artifact references

### 4.3 Failure handling
- [ ] Handle invalid videos and processing errors
- [ ] Add retry behavior and error records
- [ ] Mark execution as failed if retries are exhausted

---

## Phase 5 — Protocol Analysis Worker

### 5.1 Worker skeleton
- [ ] Create a standalone protocol analysis worker
- [ ] Connect it to the queue and stored pose artifacts

### 5.2 Protocol-specific analysis logic
- [ ] Load the selected protocol definition
- [ ] Load baseline metrics, risk factors, and report template config
- [ ] Run protocol-specific metrics and angle calculations
- [ ] Produce structured results for downstream reporting

### 5.3 Result storage
- [ ] Save analysis result payload
- [ ] Save flagged issues and recommendations
- [ ] Link results to the execution and protocol

---

## Phase 6 — Report Generation Worker

### 6.1 Worker skeleton
- [ ] Create a standalone report generation worker
- [ ] Connect it to the queue and analysis result payloads

### 6.2 Report generation
- [ ] Generate markdown or HTML report content
- [ ] Generate PDF output
- [ ] Save report artifacts to storage
- [ ] Store report metadata in the database

### 6.3 Report access
- [ ] Add signed URL or secure access link for reports
- [ ] Link report to athlete, coach, or caretaker based on access rules

---

## Phase 7 — Frontend Architecture

### 7.1 Frontend app structure
- [ ] Create a feature-based React + TypeScript structure
- [ ] Separate authentication, dashboard, protocols, requests, analyses, and reports modules
- [ ] Add shared layout and role-aware navigation

### 7.2 Role-based views
- [ ] Superadmin dashboard for protocol requests and approvals
- [ ] Physiotherapist dashboard for protocol creation and execution
- [ ] Coach dashboard for visible protocols and athlete reports
- [ ] Athlete/caretaker dashboard for their accessible reports

### 7.3 Protocol UX
- [ ] Create protocol builder UI for custom analysis config
- [ ] Create protocol request submission flow
- [ ] Show visibility and approval state clearly

### 7.4 Execution and status UX
- [ ] Show active executions with live status
- [ ] Show stage-by-stage progress for pose extraction, analysis, and report generation
- [ ] Display errors and retry information when jobs fail

### 7.5 Report presentation
- [ ] Create report list page
- [ ] Create report detail page
- [ ] Add PDF viewer or download action
- [ ] Add summary cards for findings and recommendations

---

## Phase 8 — Notifications and Audit Trails

### 8.1 In-app notifications
- [ ] Create notification model and UI
- [ ] Send notifications for request, approval, execution, and report events

### 8.2 Audit trail
- [ ] Log significant domain events
- [ ] Expose audit history for protocols, requests, and reports

### 8.3 Error and alerting
- [ ] Add alerts for repeated worker failures
- [ ] Add operational dashboards for job health

---

## Phase 9 — Security and Compliance

### 9.1 Authentication
- [ ] Review and harden auth flow for the new backend modules
- [ ] Ensure secure storage of tokens and secrets

### 9.2 Authorization
- [ ] Enforce role-based access in API handlers
- [ ] Enforce object-level visibility for protocols and reports

### 9.3 Secrets and configuration
- [ ] Move all secrets into a secure configuration system
- [ ] Ensure no secrets are committed to the repository

---

## Phase 10 — Testing and Reliability

### 10.1 Backend tests
- [ ] Unit tests for protocol logic
- [ ] Unit tests for request/approval workflow
- [ ] Unit tests for orchestration state transitions
- [ ] Integration tests for the full pipeline

### 10.2 Frontend tests
- [ ] Component tests for protocol builder and dashboard views
- [ ] Integration tests for execution and report flow

### 10.3 Load and failure tests
- [ ] Test queue retries and recovery
- [ ] Test delayed or failed worker behavior
- [ ] Test high-volume job spikes

---

## Phase 11 — Deployment and Rollout

### 11.1 Deployment strategy
- [ ] Deploy the modular monolith backend and new worker components in parallel with the current app
- [ ] Keep the current demo flow available during migration
- [ ] Add feature flags for gradual rollout

### 11.2 Cutover plan
- [ ] Move a subset of users to the new flow
- [ ] Monitor logs, errors, and performance
- [ ] Switch traffic gradually after validation

### 11.3 Post-cutover cleanup
- [ ] Remove legacy inline flow once the new architecture is stable
- [ ] Archive or retire unused code paths

---

## Recommended Implementation Sequence

1. Build the domain models and API layer
2. Add orchestrator and queue infrastructure
3. Implement pose extraction worker
4. Implement analysis worker
5. Implement report worker
6. Add frontend views for protocol, request, execution, and report flow
7. Add notifications, audit logs, and observability
8. Harden security and testing
9. Roll out gradually in parallel with the current app
