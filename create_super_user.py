"""
Create Super User Script
Creates an admin/super user with full access to the system
"""

import sys
import os
import getpass

# Add api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from auth import hash_password
from db import get_db_cursor, execute_query

def create_super_user():
    """Interactive script to create a super user"""
    
    print("=" * 50)
    print("Create Super User / Admin Account")
    print("=" * 50)
    print()
    
    # Get user input
    email = input("Email: ").strip().lower()
    if '@' not in email:
        print("Error: Invalid email format")
        return False
    
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    
    # Get password securely
    while True:
        password = getpass.getpass("Password (min 8 characters): ")
        if len(password) < 8:
            print("Error: Password must be at least 8 characters")
            continue
        
        password_confirm = getpass.getpass("Confirm Password: ")
        if password != password_confirm:
            print("Error: Passwords do not match")
            continue
        
        break
    
    print()
    print("Creating super user...")
    
    try:
        # Check if user already exists
        existing = execute_query(
            "SELECT user_id FROM physio_app.users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        
        if existing:
            print(f"Error: User with email '{email}' already exists")
            return False
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create super user
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO physio_app.users 
                (email, password_hash, roles, first_name, last_name, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING user_id, email, roles, created_at
            """, (
                email,
                password_hash,
                ['admin', 'super_user'],
                first_name,
                last_name,
                'active'
            ))
            
            user = cur.fetchone()
        
        print()
        print("=" * 50)
        print("✓ Super User Created Successfully!")
        print("=" * 50)
        print(f"User ID: {user['user_id']}")
        print(f"Email: {user['email']}")
        print(f"Roles: {', '.join(user['roles'])}")
        print(f"Created: {user['created_at']}")
        print()
        print("You can now login with these credentials.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"Error creating super user: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_super_users():
    """List all existing super users"""
    try:
        users = execute_query("""
            SELECT user_id, email, first_name, last_name, roles, status, created_at, last_login_at
            FROM physio_app.users
            WHERE 'admin' = ANY(roles) OR 'super_user' = ANY(roles)
            ORDER BY created_at
        """, fetch_all=True)
        
        if not users:
            print("No super users found in the database.")
            return
        
        print()
        print("=" * 80)
        print("Existing Super Users / Admins")
        print("=" * 80)
        print()
        
        for user in users:
            print(f"User ID: {user['user_id']}")
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Roles: {', '.join(user['roles'])}")
            print(f"  Status: {user['status']}")
            print(f"  Created: {user['created_at']}")
            if user['last_login_at']:
                print(f"  Last Login: {user['last_login_at']}")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Error listing super users: {e}")

if __name__ == '__main__':
    print()
    
    # Check database connection
    from db import test_connection
    if not test_connection():
        print("Error: Cannot connect to database")
        print("Please check your database configuration in environment variables:")
        print("  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        sys.exit(1)
    
    # Menu
    print()
    print("1. Create new super user")
    print("2. List existing super users")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        create_super_user()
    elif choice == '2':
        list_super_users()
    else:
        print("Invalid choice")
