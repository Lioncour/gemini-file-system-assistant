#!/usr/bin/env python3
"""
Main application entry point for the Gemini File System Assistant.
This is the single file that will be compiled into an executable.
"""

import os
import sys
import time
import requests
import subprocess
import threading
from pathlib import Path


def check_server_running():
    """Check if the local server is running."""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_server():
    """Start the local server in background."""
    print("🚀 Starting local server...")
    try:
        # Start server in background
        subprocess.Popen([sys.executable, "main.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(15):
            if check_server_running():
                print("✅ Server started successfully!")
                return True
            time.sleep(1)
        
        print("❌ Server failed to start after 15 seconds")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False


def demo_file_operations():
    """Demonstrate file operations."""
    print("\n🎭 File System Operations Demo")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Demo 1: List directory
    print("📂 Listing directory contents...")
    try:
        response = requests.post(f"{base_url}/execute_tool", json={
            "tool_name": "list_directory",
            "parameters": {"directory_path": "."}
        })
        result = response.json()
        
        if result["success"]:
            files = result["result"]
            print(f"✅ Found {len(files)} items:")
            for item in files[:10]:  # Show first 10
                item_type = "📁" if item["is_directory"] else "📄"
                size_info = f" ({item['size']} bytes)" if item["size"] else ""
                print(f"   {item_type} {item['name']}{size_info}")
        else:
            print(f"❌ Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Demo 2: Create a file
    print("\n✍️ Creating a demo file...")
    try:
        content = """Hello from the File System Assistant!

This file was created by the demo system.
The file operations are working perfectly!

Features:
- Read files
- Write files  
- List directories
- Secure access control

All operations are restricted to the safe directory.

Created on: """ + time.strftime("%Y-%m-%d %H:%M:%S")
        
        response = requests.post(f"{base_url}/execute_tool", json={
            "tool_name": "write_file",
            "parameters": {
                "file_path": "ai_assistant_demo.txt",
                "content": content
            }
        })
        result = response.json()
        
        if result["success"]:
            print("✅ File created successfully!")
            print(f"📄 {result['result']['message']}")
        else:
            print(f"❌ Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Demo 3: Read the file
    print("\n📖 Reading the demo file...")
    try:
        response = requests.post(f"{base_url}/execute_tool", json={
            "tool_name": "read_file",
            "parameters": {"file_path": "ai_assistant_demo.txt"}
        })
        result = response.json()
        
        if result["success"]:
            print("✅ File read successfully!")
            print("📄 Content:")
            print("-" * 40)
            print(result["result"])
            print("-" * 40)
        else:
            print(f"❌ Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_mode():
    """Interactive mode for manual commands."""
    print("\n🎮 Interactive Mode")
    print("=" * 50)
    print("Type commands like:")
    print("- 'list' to list directory")
    print("- 'read <filename>' to read a file")
    print("- 'write <filename> <content>' to write a file")
    print("- 'quit' to exit")
    print()
    
    base_url = "http://localhost:8000"
    
    while True:
        try:
            command = input("💻 Command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if command.lower() == 'list':
                response = requests.post(f"{base_url}/execute_tool", json={
                    "tool_name": "list_directory",
                    "parameters": {"directory_path": "."}
                })
                result = response.json()
                
                if result["success"]:
                    files = result["result"]
                    print(f"📂 Found {len(files)} items:")
                    for item in files:
                        item_type = "📁" if item["is_directory"] else "📄"
                        size_info = f" ({item['size']} bytes)" if item["size"] else ""
                        print(f"   {item_type} {item['name']}{size_info}")
                else:
                    print(f"❌ Error: {result['error']}")
            
            elif command.startswith('read '):
                filename = command[5:].strip()
                response = requests.post(f"{base_url}/execute_tool", json={
                    "tool_name": "read_file",
                    "parameters": {"file_path": filename}
                })
                result = response.json()
                
                if result["success"]:
                    print(f"📄 Content of {filename}:")
                    print("-" * 40)
                    print(result["result"])
                    print("-" * 40)
                else:
                    print(f"❌ Error: {result['error']}")
            
            elif command.startswith('write '):
                parts = command[6:].strip().split(' ', 1)
                if len(parts) < 2:
                    print("❌ Usage: write <filename> <content>")
                    continue
                
                filename, content = parts
                response = requests.post(f"{base_url}/execute_tool", json={
                    "tool_name": "write_file",
                    "parameters": {
                        "file_path": filename,
                        "content": content
                    }
                })
                result = response.json()
                
                if result["success"]:
                    print(f"✅ File {filename} created successfully!")
                else:
                    print(f"❌ Error: {result['error']}")
            
            else:
                print("❌ Unknown command. Try 'list', 'read <file>', 'write <file> <content>', or 'quit'")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main application function."""
    print("🤖 Gemini File System Assistant")
    print("=" * 50)
    print("AI-powered file system operations")
    print("Secure, local, and easy to use!")
    print()
    
    # Check if server is running
    if not check_server_running():
        print("🌐 Local server is not running")
        if not start_server():
            print("❌ Failed to start server.")
            print("Please make sure all files are in the same directory.")
            input("\nPress Enter to exit...")
            return
    
    print("✅ Server is running!")
    
    # Show options
    print("\nChoose an option:")
    print("1. Run demo (automatic file operations)")
    print("2. Interactive mode (manual commands)")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            demo_file_operations()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()

