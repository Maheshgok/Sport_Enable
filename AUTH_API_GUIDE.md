# Authentication & User Management API

This document describes the authentication and user management features added to the Moove API.

## Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [User Roles](#user-roles)
4. [API Endpoints](#api-endpoints)
5. [Authentication](#authentication)
6. [Super User Creation](#super-user-creation)

## Overview

The Moove API now includes comprehensive authentication and user management:

- **JWT-based authentication** - Secure token-based authentication
- **Multiple user roles** - Support for athletes, physiotherapists, coaches, caretakers, and admins
- **Super user access** - Admin accounts with full system access
- **Profile management** - User profile creation and updates
- **Password security** - Bcrypt password hashing

## Setup

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `JWT_SECRET` - Secret key for JWT tokens (change in production!)

### 3. Initialize Database

Ensure your PostgreSQL database is running and the schema is created:

```bash
cd database
psql -U postgres -d moove_db -f run_all.sql
```

### 4. Create Super User

Create your first admin account:

```bash
python create_super_user.py
```

Follow the prompts to create an admin account with full access.

## User Roles

The system supports the following user roles:

1. **athlete** - Athletes receiving treatment
2. **physiotherapist** - Healthcare providers
3. **coach** - Athletic coaches
4. **caretaker** - Support staff (nurses, trainers, family)
5. **admin** / **super_user** - System administrators with full access

Users can have multiple roles assigned.

## API Endpoints

### Authentication Endpoints

#### Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["athlete"],
  "phone": "+1234567890",
  "date_of_birth": "1995-06-15",
  "gender": "male"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "roles": ["athlete"],
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "roles": ["athlete"],
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "roles": ["athlete"],
    "first_name": "John",
    "last_name": "Doe",
    "status": "active"
  }
}
```

#### Change Password
```http
POST /api/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### User Management Endpoints (Admin Only)

#### List All Users
```http
GET /api/users?role=athlete&status=active&limit=50&offset=0
Authorization: Bearer <admin-token>
```

**Query Parameters:**
- `role` - Filter by role (athlete, physiotherapist, coach, caretaker)
- `status` - Filter by status (active, inactive, suspended)
- `limit` - Results per page (default: 100)
- `offset` - Pagination offset (default: 0)

#### Get User by ID
```http
GET /api/users/{user_id}
Authorization: Bearer <token>
```

Users can view their own profile, admins can view any user.

#### Update User
```http
PATCH /api/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Jane",
  "phone": "+1987654321"
}
```

**Admin-only fields:**
- `roles` - Update user roles
- `status` - Change account status
- `organization_id` - Assign to organization

#### Delete User
```http
DELETE /api/users/{user_id}
Authorization: Bearer <admin-token>
```

Permanently deletes a user. Admins cannot delete themselves.

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Expiration

Tokens expire after 24 hours. Users must login again to get a new token.

### Role-Based Access Control

Some endpoints require specific roles:

- **Admin-only endpoints:**
  - `GET /api/users` - List all users
  - `DELETE /api/users/{id}` - Delete users
  - Update user roles and status

- **User or Admin:**
  - `GET /api/users/{id}` - View user (own profile or admin)
  - `PATCH /api/users/{id}` - Update user (own profile or admin)

## Super User Creation

### Create First Admin

Use the interactive script:

```bash
python create_super_user.py
```

Select option 1 and provide:
- Email address
- First name
- Last name
- Password (min 8 characters)

### List Existing Admins

```bash
python create_super_user.py
```

Select option 2 to view all super users in the system.

### Super User Capabilities

Super users can:
- View all users in the system
- Update any user's profile
- Change user roles and status
- Delete users (except themselves)
- Access all API endpoints
- Manage system-wide data

## Security Best Practices

1. **Change JWT_SECRET** - Use a strong, random secret in production
2. **Use HTTPS** - Always use encrypted connections in production
3. **Strong Passwords** - Enforce minimum 8 characters (consider stronger requirements)
4. **Secure Storage** - Never commit `.env` file to version control
5. **Token Storage** - Store tokens securely on the client side
6. **Regular Rotation** - Consider implementing token refresh mechanism

## Error Codes

- `400` - Bad Request (missing/invalid fields)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (user/resource doesn't exist)
- `409` - Conflict (email already registered)
- `500` - Internal Server Error

## Example Usage

### Complete Registration Flow

```javascript
// 1. Register new athlete
const registerResponse = await fetch('http://localhost:8080/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'athlete@example.com',
    password: 'secure123',
    first_name: 'John',
    last_name: 'Athlete',
    roles: ['athlete']
  })
});

const { token, user } = await registerResponse.json();

// 2. Use token for authenticated requests
const userProfile = await fetch('http://localhost:8080/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// 3. Update profile
await fetch(`http://localhost:8080/api/users/${user.user_id}`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    phone: '+1234567890'
  })
});
```

## Database Schema

The authentication system uses the following tables:

- `physio_app.users` - Base user accounts
- `physio_app.athlete_profiles` - Athlete-specific data
- `physio_app.physiotherapist_profiles` - Physiotherapist credentials
- `physio_app.coach_profiles` - Coach information
- `physio_app.caretaker_profiles` - Caretaker details

See `database/schema/01_users_and_profiles.sql` for complete schema.
