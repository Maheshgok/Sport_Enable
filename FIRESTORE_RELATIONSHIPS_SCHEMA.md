# Firestore Schema - Relationship Management System

## Overview
This document describes the Firestore collections for the invite-based relationship management system, adapted from the PostgreSQL schema.

---

## Collection Structure

```
firestore/
├── users/                          # User accounts (already exists)
├── athleteProfiles/                # Extended athlete data
├── coachProfiles/                  # Extended coach data
├── physiotherapistProfiles/        # Extended physio data
├── parentGuardianProfiles/         # Extended parent/guardian data
├── relationshipInvitations/        # Pending invitations
├── relationships/                  # Active relationships
├── relationshipChangeRequests/     # Admin approval queue
└── relationshipAuditLog/           # Complete audit trail
```

---

## Collections

### 1. `users/` (Enhanced)
**Purpose:** Core user accounts with authentication

```javascript
{
  "users/{userId}": {
    // Core fields
    "id": "user_001",
    "email": "athlete@example.com",
    "passwordHash": "bcrypt_hash_here",
    "firstName": "John",
    "lastName": "Doe",
    "roles": ["athlete"],  // Array: athlete, coach, physiotherapist, parent, admin
    "status": "active",    // active | suspended | deleted
    
    // Timestamps
    "createdAt": Timestamp(2026-04-08T10:00:00Z),
    "updatedAt": Timestamp(2026-04-08T10:00:00Z),
    "lastLoginAt": Timestamp(2026-04-08T10:00:00Z),
    
    // Optional
    "phoneNumber": "+1234567890",
    "profilePicture": "https://storage.googleapis.com/...",
    "timezone": "Asia/Kolkata"
  }
}
```

**Indexes:**
- `email` (unique)
- `roles` (array-contains)
- `status`

---

### 2. `athleteProfiles/`
**Purpose:** Extended profile for athletes

```javascript
{
  "athleteProfiles/{userId}": {
    "userId": "user_001",              // Reference to users collection
    "sportId": "cricket",              // REQUIRED for athletes
    "sportName": "Cricket",
    "position": "Fast Bowler",
    "team": "Mumbai Indians",
    "level": "professional",           // amateur | semi-pro | professional | elite
    
    // Custom baselines (sport-specific metrics)
    "customBaselines": {
      "vo2Max": 55.2,
      "maxStrength": {
        "bench": 80,
        "squat": 120
      },
      "flexibility": {
        "shoulderROM": 175
      }
    },
    
    // Metadata
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes:**
- `userId` (unique)
- `sportId`

---

### 3. `coachProfiles/`
**Purpose:** Extended profile for coaches

```javascript
{
  "coachProfiles/{userId}": {
    "userId": "coach_001",
    "specialization": "Strength & Conditioning",  // Optional
    "yearsOfExperience": 10,
    "certifications": [
      "NSCA-CSCS",
      "UKSCA"
    ],
    "sportsSpecialty": ["Cricket", "Football"],
    
    // Stats
    "athletesCoached": 0,               // Auto-incremented
    "activePlayers": 0,
    
    // Metadata
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes:**
- `userId` (unique)
- `specialization`

---

### 4. `physiotherapistProfiles/`
**Purpose:** Extended profile for physiotherapists

```javascript
{
  "physiotherapistProfiles/{userId}": {
    "userId": "physio_001",
    "specialization": "Sports Medicine",  // Optional
    "licenseNumber": "PT-12345",          // Optional but recommended
    "certifications": [
      "DPT",
      "OCS"
    ],
    "sportsSpecialty": ["Cricket", "Tennis"],
    
    // Stats
    "activePatients": 0,
    
    // Metadata
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes:**
- `userId` (unique)
- `licenseNumber`

---

### 5. `parentGuardianProfiles/`
**Purpose:** Extended profile for parents/guardians/managers

```javascript
{
  "parentGuardianProfiles/{userId}": {
    "userId": "parent_001",
    "guardianType": "parent",          // REQUIRED: parent | legal_guardian | manager | agent | family_member
    "relationshipToAthlete": "Mother",  // Optional: e.g., "Mother", "Legal Guardian", "Sports Manager"
    
    // Permissions (what they can access)
    "permissions": {
      "canViewMedical": false,         // Default: false (sensitive data)
      "canViewVideos": true,           // Default: true
      "canViewReports": true,          // Default: true
      "canUploadVideos": false,        // Default: false
      "canScheduleSessions": false     // Default: false
    },
    
    // Capacity limits
    "maxAthletes": 3,                   // How many athletes they can be guardian of
    "currentAthletes": 0,               // Auto-incremented
    
    // Metadata
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes:**
- `userId` (unique)
- `guardianType`

---

### 6. `relationshipInvitations/`
**Purpose:** Pending invitations (invite-accept mechanism)

```javascript
{
  "relationshipInvitations/{invitationId}": {
    "id": "inv_001",
    
    // Parties involved
    "inviterId": "coach_001",           // User who sent the invitation
    "inviterEmail": "coach@example.com",
    "inviterName": "Coach Smith",
    "inviterRoles": ["coach"],
    
    "inviteeEmail": "athlete@example.com",  // Email to send invitation to
    "inviteeId": "user_001",            // Set when user accepts (if registered)
    "inviteeName": "John Doe",          // Set when accepted
    
    // Invitation details
    "relationshipType": "coach_athlete",  // One of 9 types (see below)
    "invitationToken": "secure_random_token_here",  // Unique secure token
    "message": "I'd like to work with you on improving your bowling technique",  // Optional
    
    // Status tracking
    "status": "pending",                // pending | accepted | rejected | expired | revoked | cancelled
    "createdAt": Timestamp(2026-04-08T10:00:00Z),
    "expiresAt": Timestamp(2026-04-15T10:00:00Z),  // 7 days from creation
    "respondedAt": null,                // Set when accepted/rejected
    "rejectionReason": null,            // Optional reason for rejection
    
    // Audit
    "updatedAt": Timestamp
  }
}
```

**Valid Relationship Types:**
1. `coach_athlete` - Coach training athlete
2. `coach_parent` - Coach connected to parent
3. `coach_physiotherapist` - Coach-physio coordination
4. `coach_coach` - Coach collaboration
5. `parent_athlete` - Parent of athlete
6. `guardian_athlete` - Guardian of athlete
7. `manager_athlete` - Manager of athlete
8. `physiotherapist_athlete` - Physio treating athlete
9. `physiotherapist_coach` - Physio-coach coordination

**Indexes:**
- `invitationToken` (unique)
- `inviterId`
- `inviteeEmail`
- `inviteeId`
- `status`
- `expiresAt`
- Composite: `inviteeEmail + status`

**Firestore Rules:**
```javascript
// Only allow reading own invitations
match /relationshipInvitations/{invitationId} {
  allow read: if isAuthenticated() && 
    (resource.data.inviterId == request.auth.uid || 
     resource.data.inviteeId == request.auth.uid ||
     resource.data.inviteeEmail == request.auth.token.email);
  allow create: if isAuthenticated();
  allow update: if isAuthenticated() && 
    (resource.data.inviterId == request.auth.uid || 
     resource.data.inviteeId == request.auth.uid);
}
```

---

### 7. `relationships/`
**Purpose:** Active established relationships

```javascript
{
  "relationships/{relationshipId}": {
    "id": "rel_001",
    
    // Parties
    "user1Id": "coach_001",
    "user1Name": "Coach Smith",
    "user1Roles": ["coach"],
    
    "user2Id": "athlete_001",
    "user2Name": "John Doe",
    "user2Roles": ["athlete"],
    
    // Relationship info
    "relationshipType": "coach_athlete",
    "status": "active",                 // active | suspended | terminated | on_hold
    
    // Permissions (can be customized per relationship)
    "permissions": {
      "canViewMedical": true,
      "canViewVideos": true,
      "canEditPrescriptions": true,
      "customPermissions": {}
    },
    
    // Establishment tracking
    "establishedVia": "inv_001",        // Reference to invitation
    "invitationId": "inv_001",
    "acceptedAt": Timestamp,
    "approvedBy": "admin_001",          // Admin who approved
    "approvedAt": Timestamp,
    
    // Termination tracking
    "terminatedAt": null,
    "terminatedBy": null,
    "terminationReason": null,
    
    // Notes
    "notes": "Working on bowling technique recovery",
    
    // Metadata
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes:**
- `user1Id`
- `user2Id`
- `relationshipType`
- `status`
- Composite: `user1Id + status`
- Composite: `user2Id + status`

**Firestore Rules:**
```javascript
match /relationships/{relationshipId} {
  allow read: if isAuthenticated() && 
    (resource.data.user1Id == request.auth.uid || 
     resource.data.user2Id == request.auth.uid || 
     isAdmin());
  allow write: if isAdmin();  // Only admins can modify active relationships
}
```

---

### 8. `relationshipChangeRequests/`
**Purpose:** Admin approval queue for relationship changes

```javascript
{
  "relationshipChangeRequests/{requestId}": {
    "id": "req_001",
    
    // Request details
    "requestType": "add_relationship",  // add_relationship | remove_relationship | modify_permissions
    "requestedBy": "athlete_001",
    "requestedByName": "John Doe",
    
    // What's being requested
    "invitationId": "inv_001",          // If adding new relationship
    "relationshipId": "rel_001",        // If modifying existing
    "user1Id": "coach_001",
    "user2Id": "athlete_001",
    "relationshipType": "coach_athlete",
    
    // Requested changes (for modify_permissions)
    "requestedChanges": {
      "permissions": {
        "canViewMedical": false
      }
    },
    
    // Status tracking
    "status": "pending_admin",          // pending_admin | approved | rejected | cancelled | superseded
    "priority": "normal",               // low | normal | high | urgent
    
    // Admin review
    "reviewedBy": null,
    "reviewedByName": null,
    "reviewedAt": null,
    "approvalNotes": null,
    "rejectionReason": null,
    
    // Metadata
    "createdAt": Timestamp,
    "updatedAt": Timestamp
  }
}
```

**Indexes:**
- `requestedBy`
- `status`
- `priority`
- `relationshipId`
- Composite: `status + createdAt`

**Firestore Rules:**
```javascript
match /relationshipChangeRequests/{requestId} {
  allow read: if isAuthenticated();
  allow create: if isAuthenticated();
  allow update: if isAdmin();  // Only admins can approve/reject
}
```

---

### 9. `relationshipAuditLog/`
**Purpose:** Complete audit trail of all relationship actions

```javascript
{
  "relationshipAuditLog/{logId}": {
    "id": "log_001",
    
    // Action details
    "action": "invitation_sent",        // invitation_sent | invitation_accepted | invitation_rejected
                                        // | relationship_approved | relationship_terminated
                                        // | permissions_modified
    
    // Actors
    "actorId": "coach_001",
    "actorName": "Coach Smith",
    "actorRoles": ["coach"],
    
    "targetUserId": "athlete_001",      // User affected by action
    "targetUserName": "John Doe",
    
    // Context
    "invitationId": "inv_001",          // If applicable
    "relationshipId": "rel_001",        // If applicable
    "relationshipType": "coach_athlete",
    
    // Changes (what was modified)
    "changeDetails": {
      "oldValue": {"status": "pending"},
      "newValue": {"status": "accepted"}
    },
    
    // Metadata
    "ipAddress": "192.168.1.1",         // For security
    "userAgent": "Mozilla/5.0...",
    "timestamp": Timestamp,
    
    // Admin actions (if manually intervened)
    "adminOverride": false,
    "adminNotes": null
  }
}
```

**Indexes:**
- `actorId`
- `targetUserId`
- `action`
- `timestamp` (descending)
- `relationshipId`

**Firestore Rules:**
```javascript
match /relationshipAuditLog/{logId} {
  allow read: if isAdmin();  // Only admins can read audit logs
  allow write: if false;     // Never allow direct writes (use Cloud Functions)
}
```

---

## Permission Matrix

| User Type | Can Send Invitations? | Can Invite Athletes | Can Invite Coaches | Can Invite Parents | Can Invite Physios |
|-----------|----------------------|--------------------|--------------------|--------------------|--------------------|
| **Admin** | ✅ Yes | ✅ | ✅ | ✅ | ✅ |
| **Coach** | ✅ Yes | ✅ | ✅ | ✅ | ✅ |
| **Athlete** | ✅ Yes | ❌ | ✅ | ✅ | ✅ |
| **Physiotherapist** | ✅ Yes | ✅ | ✅ | ❌ | ❌ |
| **Parent/Guardian** | ❌ **NO** | ❌ | ❌ | ❌ | ❌ |

---

## Cloud Functions Recommendations

For better security and data consistency, use Cloud Functions for:

### 1. Auto-Expire Invitations
```javascript
// Run daily at midnight
exports.expireOldInvitations = functions.pubsub
  .schedule('0 0 * * *')
  .onRun(async (context) => {
    const now = admin.firestore.Timestamp.now();
    const expiredInvitations = db.collection('relationshipInvitations')
      .where('status', '==', 'pending')
      .where('expiresAt', '<', now);
    
    // Update to expired status
  });
```

### 2. Create Audit Log Entries
```javascript
// Triggered when invitation is created/updated
exports.logInvitationAction = functions.firestore
  .document('relationshipInvitations/{invitationId}')
  .onWrite(async (change, context) => {
    // Create audit log entry
  });
```

### 3. Send Email Notifications
```javascript
exports.sendInvitationEmail = functions.firestore
  .document('relationshipInvitations/{invitationId}')
  .onCreate(async (snap, context) => {
    const invitation = snap.data();
    // Send email via SendGrid/Firebase Email Extension
  });
```

---

## Migration from PostgreSQL

If you have existing data in PostgreSQL:

1. **Export PostgreSQL data** using `pg_dump`
2. **Transform to JSON** using Python script
3. **Import to Firestore** using Firebase Admin SDK

Example migration script: `migrate-to-firestore.js`

---

## Advantages Over PostgreSQL

✅ **No database server costs** - Pay only for reads/writes/storage
✅ **Real-time updates** - UI automatically updates when data changes
✅ **Offline support** - Firestore caches data locally
✅ **Automatic backups** - Built into Firebase
✅ **Scales to zero** - Perfect for MVP/low traffic
✅ **Easy authentication integration** - Firebase Auth works seamlessly
✅ **Global CDN** - Data replicated across regions

---

## Cost Estimation

**Free Tier (Spark Plan):**
- 50K reads/day
- 20K writes/day
- 1GB storage
- Perfect for MVP!

**Paid (Blaze Plan):**
- $0.06 per 100K document reads
- $0.18 per 100K document writes
- $0.18/GB storage

**Estimated monthly cost for 100 active users:**
- ~$5-10/month (vs $10-15 for Cloud SQL db-f1-micro)

---

## Next Steps

1. ✅ Schema designed
2. ⏭️ Update API to use Firestore (Python Admin SDK)
3. ⏭️ Update firestore.rules with relationship rules
4. ⏭️ Deploy updated system
5. ⏭️ Test invite flow end-to-end
