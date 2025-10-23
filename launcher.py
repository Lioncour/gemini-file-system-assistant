#!/usr/bin/env python3
"""
Simple launcher for the Gemini File System Assistant.
This script handles everything: server startup, client launch, and error handling.
"""

import subprocess
import time
import requests
import os
import sys
from threading import Thread


def check_server_running():
    """Check if the local server is running."""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_server():
    """Start the local server in a separate process."""
    print("🚀 Starting local server...")
    try:
        # Start server in background
        subprocess.Popen([sys.executable, "main.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(10):
            if check_server_running():
                print("✅ Server started successfully!")
                return True
            time.sleep(1)
        
        print("❌ Server failed to start")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False


def main():
    """Main launcher function."""
    print("🤖 Gemini File System Assistant Launcher")
    print("=" * 50)
    
    # Set API key
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCF8rSzeF6rJjNI0pH7qUMwTw3XRvCAtvg"
    
    # Check if server is running
    if not check_server_running():
        print("🌐 Local server is not running")
        if not start_server():
            print("❌ Failed to start server. Please run 'python main.py' manually")
            input("Press Enter to exit...")
            return
    
    # Start the client
    print("🎯 Starting AI Assistant...")
    print("=" * 50)
    
    try:
        # Import and run the client
        from client_app import main as client_main
        client_main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()

