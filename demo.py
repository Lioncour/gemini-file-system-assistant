#!/usr/bin/env python3
"""
Demo script showing how the Gemini File System Assistant works.
This script simulates the client-server interaction without requiring a Gemini API key.
"""

import requests
import json
import time

def simulate_gemini_interaction():
    """Simulate how Gemini would interact with the local server."""
    
    print("🤖 Gemini File System Assistant - Demo")
    print("=" * 50)
    print("This demo shows how the system works by simulating")
    print("the interaction between Gemini AI and your local server.")
    print()
    
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=2)
        print("✅ Local server is running")
    except:
        print("❌ Local server is not running!")
        print("Please start it with: python main.py")
        return
    
    print("\n🎭 Simulating user request: 'What files are in my current directory?'")
    print("=" * 60)
    
    # Simulate Gemini calling list_directory
    print("🤖 Gemini: I'll check what files are in your directory...")
    print("🔧 Executing tool: list_directory")
    
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
            files = result["result"]
            print(f"✅ Tool executed successfully: Found {len(files)} items")
            
            # Simulate Gemini's response
            print("\n🤖 Gemini: Here are the files in your current directory:")
            for item in files:
                item_type = "📁 directory" if item["is_directory"] else "📄 file"
                size_info = f" ({item['size']} bytes)" if item["size"] is not None else ""
                print(f"   {item_type}: {item['name']}{size_info}")
        else:
            print(f"❌ Tool execution failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎭 Simulating user request: 'Create a new file called demo.txt with some content'")
    print("=" * 60)
    
    # Simulate Gemini calling write_file
    print("🤖 Gemini: I'll create a demo.txt file for you...")
    print("🔧 Executing tool: write_file")
    
    try:
        content = "This is a demo file created by the Gemini File System Assistant!\n\nIt shows how the system can:\n- Read files\n- Write files\n- List directories\n\nAll operations are secure and limited to the safe directory."
        
        payload = {
            "tool_name": "write_file",
            "parameters": {
                "file_path": "demo.txt",
                "content": content
            }
        }
        response = requests.post(f"{base_url}/execute_tool", json=payload, timeout=5)
        result = response.json()
        
        if result["success"]:
            print("✅ Tool executed successfully: File created")
            print(f"📄 File info: {result['result']}")
            
            # Now read the file back
            print("\n🔧 Executing tool: read_file")
            read_payload = {
                "tool_name": "read_file",
                "parameters": {
                    "file_path": "demo.txt"
                }
            }
            read_response = requests.post(f"{base_url}/execute_tool", json=read_payload, timeout=5)
            read_result = read_response.json()
            
            if read_result["success"]:
                print("✅ File read successfully")
                print("\n🤖 Gemini: Here's what I created for you:")
                print("-" * 40)
                print(read_result["result"])
                print("-" * 40)
            else:
                print(f"❌ Failed to read file: {read_result['error']}")
        else:
            print(f"❌ Tool execution failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\nTo use the full system with Gemini AI:")
    print("1. Get your API key from: https://makersuite.google.com/app/apikey")
    print("2. Set it: set GEMINI_API_KEY=your_api_key_here")
    print("3. Run: python client.py")
    print("\nThe server is already running at http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")

if __name__ == "__main__":
    simulate_gemini_interaction()
