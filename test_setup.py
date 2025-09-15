#!/usr/bin/env python3
"""
Test script to verify the Gemini File System Assistant setup.
This script tests the local server functionality without requiring the Gemini API.
"""

import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread


def test_local_tools():
    """Test the local tools directly."""
    print("🧪 Testing local tools directly...")
    
    try:
        from local_tools import read_file, write_file, list_directory, SecurityError
        
        # Test write_file
        print("  📝 Testing write_file...")
        result = write_file("test_file.txt", "Hello, World!")
        assert result["success"] == True
        print("    ✅ write_file works")
        
        # Test read_file
        print("  📖 Testing read_file...")
        content = read_file("test_file.txt")
        assert content == "Hello, World!"
        print("    ✅ read_file works")
        
        # Test list_directory
        print("  📂 Testing list_directory...")
        files = list_directory(".")
        assert isinstance(files, list)
        print(f"    ✅ list_directory works (found {len(files)} items)")
        
        # Test security
        print("  🔒 Testing security...")
        try:
            read_file("../../../etc/passwd")  # This should fail
            print("    ❌ Security test failed - should have been blocked")
        except SecurityError:
            print("    ✅ Security test passed - blocked unauthorized access")
        
        # Cleanup
        os.remove("test_file.txt")
        print("  🧹 Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Local tools test failed: {e}")
        return False


def test_server_api():
    """Test the FastAPI server endpoints."""
    print("🌐 Testing server API...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health check
        print("  ❤️  Testing health check...")
        response = requests.get(f"{base_url}/", timeout=5)
        assert response.status_code == 200
        print("    ✅ Health check works")
        
        # Test tools list
        print("  🛠️  Testing tools list...")
        response = requests.get(f"{base_url}/tools", timeout=5)
        assert response.status_code == 200
        tools_data = response.json()
        assert "read_file" in tools_data["available_tools"]
        print("    ✅ Tools list works")
        
        # Test tool execution
        print("  ⚡ Testing tool execution...")
        
        # Test write_file
        write_payload = {
            "tool_name": "write_file",
            "parameters": {
                "file_path": "api_test.txt",
                "content": "API test content"
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=write_payload, timeout=5)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print("    ✅ write_file via API works")
        
        # Test read_file
        read_payload = {
            "tool_name": "read_file",
            "parameters": {
                "file_path": "api_test.txt"
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=read_payload, timeout=5)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert result["result"] == "API test content"
        print("    ✅ read_file via API works")
        
        # Test list_directory
        list_payload = {
            "tool_name": "list_directory",
            "parameters": {
                "directory_path": "."
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=list_payload, timeout=5)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert isinstance(result["result"], list)
        print("    ✅ list_directory via API works")
        
        # Test security
        print("  🔒 Testing API security...")
        security_payload = {
            "tool_name": "read_file",
            "parameters": {
                "file_path": "../../../etc/passwd"
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=security_payload, timeout=5)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == False
        assert "Security violation" in result["error"]
        print("    ✅ API security works")
        
        # Cleanup
        os.remove("api_test.txt")
        print("  🧹 Cleaned up API test file")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("    ❌ Server not running - start it with: python main.py")
        return False
    except Exception as e:
        print(f"    ❌ API test failed: {e}")
        return False


def start_server_background():
    """Start the server in the background for testing."""
    print("🚀 Starting server in background...")
    
    def run_server():
        try:
            import uvicorn
            from main import app
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
        except Exception as e:
            print(f"Server error: {e}")
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/", timeout=1)
            if response.status_code == 200:
                print("  ✅ Server started successfully")
                return True
        except:
            time.sleep(1)
    
    print("  ❌ Server failed to start")
    return False


def main():
    """Run all tests."""
    print("🧪 Gemini File System Assistant - Setup Test")
    print("=" * 50)
    
    # Test 1: Local tools
    local_test_passed = test_local_tools()
    print()
    
    # Test 2: Server API (try to connect first)
    print("🌐 Testing server connection...")
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        server_running = True
        print("  ✅ Server is already running")
    except:
        server_running = False
        print("  ⚠️  Server not running, starting it...")
        if not start_server_background():
            print("❌ Could not start server for testing")
            return
    
    api_test_passed = test_server_api()
    print()
    
    # Summary
    print("📊 Test Results:")
    print("=" * 30)
    print(f"Local Tools: {'✅ PASS' if local_test_passed else '❌ FAIL'}")
    print(f"Server API:  {'✅ PASS' if api_test_passed else '❌ FAIL'}")
    
    if local_test_passed and api_test_passed:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set your GEMINI_API_KEY environment variable")
        print("2. Run: python client.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()