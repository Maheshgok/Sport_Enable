"""
Create Super User (Admin) for Moove Platform
Run this script to create an admin user for the system
"""

import sys
import os
import getpass

# Add api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from auth import hash_password
import firestore_db as db

def create_super_user():
    """Create a super user with admin privileges"""
    
    print("=" * 60)
    print("MOOVE PLATFORM - SUPER USER CREATION")
    print("=" * 60)
    print()
    
    # User details
    email = "maheshgok@gmail.com"
    first_name = "Mahesh"
    last_name = "Gokavarapu"
    
    print(f"Creating admin user for: {email}")
    print()
    
    # Check if user already exists
    existing_user = db.get_user_by_email(email)
    if existing_user:
        print("⚠️  WARNING: User already exists!")
        print(f"   User ID: {existing_user['id']}")
        print(f"   Current roles: {existing_user['roles']}")
        print()
        
        update = input("Do you want to update this user to admin? (yes/no): ").strip().lower()
        if update == 'yes':
            # Update user roles to include admin
            try:
                doc_ref = db.db.collection('users').document(existing_user['id'])
                
                # Ensure admin role is included
                current_roles = existing_user.get('roles', [])
                if 'admin' not in current_roles:
                    current_roles.append('admin')
                
                doc_ref.update({
                    'roles': current_roles,
                    'updatedAt': db.firestore.SERVER_TIMESTAMP
                })
                
                print()
                print("✅ User updated successfully!")
                print(f"   Email: {email}")
                print(f"   Roles: {current_roles}")
                print()
                return
            except Exception as e:
                print(f"❌ Error updating user: {e}")
                return
        else:
            print("Operation cancelled.")
            return
    
    # Get password from user
    print("Set a password for the admin account:")
    while True:
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("❌ Passwords don't match. Try again.")
            print()
            continue
        
        if len(password) < 8:
            print("❌ Password must be at least 8 characters. Try again.")
            print()
            continue
        
        break
    
    # Hash password
    print()
    print("Creating user...")
    password_hash = hash_password(password)
    
    # Create user with admin role
    try:
        user = db.create_user(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            roles=['admin', 'athlete']  # Admin + Athlete role for full access
        )
        
        print()
        print("=" * 60)
        print("✅ SUPER USER CREATED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print(f"📧 Email:    {email}")
        print(f"👤 Name:     {first_name} {last_name}")
        print(f"🔑 User ID:  {user['id']}")
        print(f"⚡ Roles:    {user['roles']}")
        print()
        print("Login at: https://watch-mail-trial.web.app")
        print("API URL:  https://moove-api-812016027146.asia-south1.run.app")
        print()
        print("=" * 60)
        
    except Exception as e:
        print()
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        create_super_user()
    except KeyboardInterrupt:
        print()
        print("Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
