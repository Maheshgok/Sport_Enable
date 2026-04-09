"""
Register Admin User via API
Uses the deployed Cloud Run API to create an admin user
"""

import requests
import json

API_URL = "https://moove-api-812016027146.asia-south1.run.app"

def register_admin():
    """Register admin user via API"""
    
    print("=" * 60)
    print("MOOVE PLATFORM - ADMIN REGISTRATION VIA API")
    print("=" * 60)
    print()
    
    # Admin user details
    email = "maheshgok@gmail.com"
    password = input("Enter password for admin account: ")
    
    registration_data = {
        "email": email,
        "password": password,
        "firstName": "Mahesh",
        "lastName": "Gokavarapu",
        "role": "admin"  # This will register as admin
    }
    
    print()
    print(f"Registering admin user: {email}")
    print(f"API URL: {API_URL}/api/auth/register")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            print("=" * 60)
            print("✅ ADMIN USER REGISTERED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print(f"📧 Email:    {email}")
            print(f"👤 Name:     {data['user']['firstName']} {data['user']['lastName']}")
            print(f"🔑 User ID:  {data['user']['id']}")
            print(f"⚡ Roles:    {data['user']['roles']}")
            print()
            print("🔐 JWT Token (save this for testing):")
            print(data['token'][:50] + "...")
            print()
            print("Login at: https://watch-mail-trial.web.app")
            print()
            print("=" * 60)
            
        elif response.status_code == 400:
            error_data = response.json()
            print(f"❌ Registration failed: {error_data.get('error', 'Unknown error')}")
            
            if 'already exists' in error_data.get('error', '').lower():
                print()
                print("💡 User already exists. Try logging in instead:")
                print()
                
                # Try to login
                login_data = {
                    "email": email,
                    "password": password
                }
                
                login_response = requests.post(
                    f"{API_URL}/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print("✅ Login successful!")
                    print(f"👤 User: {login_result['user']['firstName']} {login_result['user']['lastName']}")
                    print(f"⚡ Roles: {login_result['user']['roles']}")
                    print()
                else:
                    print(f"❌ Login failed: {login_response.json().get('error', 'Unknown error')}")
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it deployed?")
        print(f"   URL: {API_URL}")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        register_admin()
    except KeyboardInterrupt:
        print()
        print("Operation cancelled.")
