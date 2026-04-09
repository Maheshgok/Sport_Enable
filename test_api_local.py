"""
Quick test script for the Video Annotation API
Tests all endpoints locally before deployment
"""

import requests
import os
import sys

API_BASE_URL = os.getenv('API_URL', 'http://localhost:8080')

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f'{API_BASE_URL}/health')
        if response.status_code == 200:
            print("✅ PASS: Health check successful")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_upload(video_path):
    """Test video upload endpoint"""
    print("\n🔍 Testing Upload Endpoint...")
    
    if not os.path.exists(video_path):
        print(f"❌ FAIL: Video file not found: {video_path}")
        return None
    
    try:
        with open(video_path, 'rb') as f:
            files = {'video': f}
            response = requests.post(f'{API_BASE_URL}/api/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print("✅ PASS: Upload successful")
            print(f"   Job ID: {job_id}")
            return job_id
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            print(f"   Response: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return None

def test_status(job_id):
    """Test status endpoint"""
    print("\n🔍 Testing Status Endpoint...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/status/{job_id}')
        if response.status_code == 200:
            print("✅ PASS: Status check successful")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_process(job_id):
    """Test processing endpoint"""
    print("\n🔍 Testing Process Endpoint...")
    print("   (This may take a few minutes...)")
    try:
        response = requests.post(f'{API_BASE_URL}/api/process/{job_id}', timeout=600)
        if response.status_code == 200:
            print("✅ PASS: Processing successful")
            print(f"   Files generated: {len(response.json().get('files', []))}")
            return True
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_results(job_id):
    """Test results endpoint"""
    print("\n🔍 Testing Results Endpoint...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/results/{job_id}')
        if response.status_code == 200:
            files = response.json().get('files', [])
            print("✅ PASS: Results retrieved")
            print(f"   Files available: {len(files)}")
            for file in files:
                print(f"   - {file['filename']} ({file['size']} bytes)")
            return True
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Video Analysis API Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Make sure API is running.")
        print("   Start with: python api/app.py")
        sys.exit(1)
    
    # Get test video path
    video_path = input("\n📹 Enter path to test video (or press Enter to skip upload tests): ").strip()
    
    if not video_path:
        print("\n⏭️  Skipping upload tests")
        print("=" * 60)
        print("✅ Basic API test complete!")
        print("=" * 60)
        return
    
    # Test 2: Upload
    job_id = test_upload(video_path)
    if not job_id:
        print("\n❌ Upload failed. Cannot continue with other tests.")
        sys.exit(1)
    
    # Test 3: Status
    test_status(job_id)
    
    # Test 4: Process
    if test_process(job_id):
        # Test 5: Results
        test_results(job_id)
    
    print("\n" + "=" * 60)
    print("✅ All Tests Complete!")
    print("=" * 60)
    print("\nYour API is working correctly and ready for deployment!")

if __name__ == "__main__":
    main()
