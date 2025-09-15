#!/usr/bin/env python3
"""
Simple test script to verify the API is working.
"""

import requests
import json

def test_api():
    """Test the API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Gemini File System Assistant API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test 2: Write file
    print("\n2. Testing write_file...")
    try:
        payload = {
            "tool_name": "write_file",
            "parameters": {
                "file_path": "test.txt",
                "content": "Hello from the API test!"
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=payload, timeout=5)
        result = response.json()
        
        if result["success"]:
            print("   ✅ write_file succeeded")
            print(f"   📄 Response: {result}")
        else:
            print(f"   ❌ write_file failed: {result['error']}")
    except Exception as e:
        print(f"   ❌ write_file error: {e}")
    
    # Test 3: Read file
    print("\n3. Testing read_file...")
    try:
        payload = {
            "tool_name": "read_file",
            "parameters": {
                "file_path": "test.txt"
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=payload, timeout=5)
        result = response.json()
        
        if result["success"]:
            print("   ✅ read_file succeeded")
            print(f"   📄 Content: {result['result']}")
        else:
            print(f"   ❌ read_file failed: {result['error']}")
    except Exception as e:
        print(f"   ❌ read_file error: {e}")
    
    # Test 4: List directory
    print("\n4. Testing list_directory...")
    try:
        payload = {
            "tool_name": "list_directory",
            "parameters": {
                "directory_path": "."
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=payload, timeout=5)
        result = response.json()
        
        if result["success"]:
            print("   ✅ list_directory succeeded")
            files = result["result"]
            print(f"   📄 Found {len(files)} items:")
            for item in files[:5]:  # Show first 5 items
                print(f"      - {item['name']} ({'dir' if item['is_directory'] else 'file'})")
        else:
            print(f"   ❌ list_directory failed: {result['error']}")
    except Exception as e:
        print(f"   ❌ list_directory error: {e}")
    
    print("\n🎉 API test completed!")

if __name__ == "__main__":
    test_api()
