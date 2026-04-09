"""
Test Authentication API
Quick test script for the authentication endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8080"

def test_register():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "john.athlete@example.com",
        "password": "secure123",
        "first_name": "John",
        "last_name": "Athlete",
        "roles": ["athlete"],
        "phone": "+1234567890",
        "date_of_birth": "1995-06-15",
        "gender": "male"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()['token']
    return None

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "email": "john.athlete@example.com",
        "password": "secure123"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()['token']
    return None

def test_get_current_user(token):
    """Test getting current user info"""
    print("\n=== Testing Get Current User ===")
    
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_update_user(token, user_id):
    """Test updating user profile"""
    print("\n=== Testing Update User ===")
    
    url = f"{BASE_URL}/api/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "phone": "+1987654321",
        "avatar": "https://example.com/avatar.jpg"
    }
    
    response = requests.patch(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_change_password(token):
    """Test changing password"""
    print("\n=== Testing Change Password ===")
    
    url = f"{BASE_URL}/api/auth/change-password"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "current_password": "secure123",
        "new_password": "newsecure456"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_admin_list_users(admin_token):
    """Test listing all users (admin only)"""
    print("\n=== Testing List Users (Admin) ===")
    
    url = f"{BASE_URL}/api/users?limit=10"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Authentication API Test Suite")
    print("=" * 60)
    print("\nMake sure:")
    print("1. Database is running and schema is initialized")
    print("2. API server is running (python api/app.py)")
    print("3. Environment variables are configured")
    print("=" * 60)
    
    input("\nPress Enter to start tests...")
    
    # Test registration
    token = test_register()
    
    if not token:
        print("\n⚠ Registration failed. Trying login instead...")
        token = test_login()
    
    if not token:
        print("\n✗ Could not get authentication token. Tests aborted.")
        return
    
    print(f"\n✓ Authentication successful!")
    print(f"Token: {token[:30]}...")
    
    # Test authenticated endpoints
    test_get_current_user(token)
    
    # For these tests, you'll need the user_id from the registration response
    # test_update_user(token, "user-id-here")
    # test_change_password(token)
    
    # For admin tests, you need an admin token
    # admin_token = "your-admin-token-here"
    # test_admin_list_users(admin_token)
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("Make sure the API is running on http://localhost:8080")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
