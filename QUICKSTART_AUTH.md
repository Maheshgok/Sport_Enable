# Quick Start: Authentication Setup

## 🚀 Getting Started with Login Features

### Step 1: Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### Step 2: Configure Environment

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and set your database credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=moove_db
DB_USER=postgres
DB_PASSWORD=your_password

JWT_SECRET=change-this-to-a-random-secret-key
```

### Step 3: Initialize Database

Make sure PostgreSQL is running, then:

```bash
cd database
psql -U postgres -d moove_db -f run_all.sql
```

### Step 4: Create Super User (Admin)

```bash
python create_super_user.py
```

Follow the prompts:
- Enter email (e.g., admin@moove.com)
- Enter first name and last name
- Create a strong password
- This user will have full admin access

### Step 5: Start the API

```bash
cd api
python app.py
```

The API will run on `http://localhost:8080`

### Step 6: Test the API (Optional)

```bash
# In a new terminal
python test_auth_api.py
```

## 📋 What's Included

### ✅ Authentication Features
- **User Registration** - Create new user accounts
- **Login** - JWT token-based authentication
- **Password Management** - Secure bcrypt hashing
- **Profile Management** - View and update user profiles

### ✅ User Roles
- **athlete** - Athletes receiving treatment
- **physiotherapist** - Healthcare providers
- **coach** - Athletic coaches
- **caretaker** - Support staff
- **admin / super_user** - System administrators

### ✅ Super User Access
- View all users
- Update any user profile
- Change user roles and status
- Delete users
- Full system access

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

### User Management (Admin)
- `GET /api/users` - List all users
- `GET /api/users/{id}` - Get user by ID
- `PATCH /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

## 📖 Documentation

- **Complete API Guide**: See [AUTH_API_GUIDE.md](AUTH_API_GUIDE.md)
- **Database Schema**: See [database/schema/01_users_and_profiles.sql](database/schema/01_users_and_profiles.sql)

## 🧪 Quick Test

Using curl:

```bash
# Register a new user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "secure123",
    "first_name": "Test",
    "last_name": "User",
    "roles": ["athlete"]
  }'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "secure123"
  }'

# Get current user (replace TOKEN with your JWT token)
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## 🔒 Security Notes

1. **Change JWT_SECRET** in production to a secure random string
2. **Use HTTPS** in production environments
3. **Never commit** `.env` file to git
4. Tokens expire after 24 hours
5. Passwords are hashed with bcrypt

## 📁 New Files Created

```
api/
  ├── app.py (updated with auth endpoints)
  ├── auth.py (authentication utilities)
  ├── db.py (database connection)
  └── requirements.txt (updated dependencies)

create_super_user.py (admin creation script)
test_auth_api.py (API test script)
.env.example (environment template)
AUTH_API_GUIDE.md (complete documentation)
QUICKSTART_AUTH.md (this file)
```

## ❓ Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify credentials in `.env`
- Ensure database exists: `CREATE DATABASE moove_db;`

### Token Invalid/Expired
- Tokens expire after 24 hours
- Login again to get a new token
- Check JWT_SECRET is set correctly

### Permission Denied
- Regular users can only edit their own profiles
- Admin features require admin/super_user role
- Use `create_super_user.py` to create admin account

## 🎯 Next Steps

1. Integrate with your frontend application
2. Add profile-specific endpoints (athlete profiles, etc.)
3. Implement password reset functionality
4. Add email verification
5. Set up token refresh mechanism

---

**Need Help?** Check the complete guide in [AUTH_API_GUIDE.md](AUTH_API_GUIDE.md)
