#!/usr/bin/env python3
"""
FloKroll AI Assistant Launcher
Sets the API key and launches the main application.
"""

import os
import sys
import subprocess
import time

def main():
    """Launch the FloKroll AI Assistant with proper API key."""
    
    # Set the API key
    api_key = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"
    os.environ["GOOGLE_API_KEY"] = api_key
    
    print("🤖 FloKroll AI Assistant Launcher")
    print("=" * 50)
    print("✅ API Key configured")
    print("🚀 Starting AI Assistant...")
    print()
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(script_dir, "dist", "FloKroll_AI_Assistant.exe")
        
        if not os.path.exists(exe_path):
            print(f"❌ Executable not found at: {exe_path}")
            print("Please make sure the executable is in the dist folder.")
            input("Press Enter to exit...")
            return
        
        # Launch the executable
        subprocess.run([exe_path], cwd=script_dir)
        
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

