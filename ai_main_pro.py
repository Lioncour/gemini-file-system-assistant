#!/usr/bin/env python3
"""
Full AI-powered File System Assistant with Google Cloud API integration.
This version includes the complete AI functionality with higher API limits.
"""

import os
import sys
import time
import requests
import subprocess
import google.generativeai as genai
from typing import Dict, Any, Optional


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


class AIFileSystemClient:
    """AI-powered file system client with Google Cloud API."""
    
    def __init__(self, api_key: str, local_server_url: str = "http://localhost:8000"):
        """Initialize the AI client."""
        self.api_key = api_key
        self.local_server_url = local_server_url
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the Gemini model
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        
        # Start a persistent chat session
        self.chat = self.model.start_chat(history=[])
        
        print("✅ AI File System Client initialized successfully!")
        print(f"🤖 Model: gemini-1.5-pro-latest")
        print(f"🌐 Local server: {local_server_url}")
    
    def execute_local_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the local server."""
        try:
            print(f"🔧 Executing tool: {tool_name} with parameters: {parameters}")
            
            response = requests.post(
                f"{self.local_server_url}/execute_tool",
                json={
                    "tool_name": tool_name,
                    "parameters": parameters
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                print(f"✅ Tool executed successfully")
            else:
                print(f"❌ Tool execution failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_result = {
                "success": False,
                "error": f"Failed to communicate with local server: {str(e)}"
            }
            print(f"❌ Server communication error: {str(e)}")
            return error_result
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
            print(f"❌ Unexpected error: {str(e)}")
            return error_result
    
    def chat_with_ai(self, user_input: str) -> str:
        """Send a message to AI and get response."""
        try:
            print(f"👤 User: {user_input}")
            print("🤖 AI is thinking...")
            
            # Send the message to AI
            response = self.chat.send_message(user_input)
            
            # Get the text response
            ai_response = response.text
            print(f"🤖 AI: {ai_response}")
            
            return ai_response
                
        except Exception as e:
            error_msg = f"Error communicating with AI: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def manual_file_operations(self):
        """Manual file operations mode."""
        print("\n🎮 Manual File Operations Mode")
        print("=" * 50)
        print("Available commands:")
        print("- 'list' - List directory contents")
        print("- 'read <filename>' - Read a file")
        print("- 'write <filename> <content>' - Write a file")
        print("- 'ai <question>' - Ask AI a question")
        print("- 'quit' - Exit")
        print()
        
        while True:
            try:
                command = input("💻 Command: ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if command.lower() == 'list':
                    result = self.execute_local_tool("list_directory", {"directory_path": "."})
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
                    result = self.execute_local_tool("read_file", {"file_path": filename})
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
                    result = self.execute_local_tool("write_file", {
                        "file_path": filename,
                        "content": content
                    })
                    if result["success"]:
                        print(f"✅ File {filename} created successfully!")
                    else:
                        print(f"❌ Error: {result['error']}")
                
                elif command.startswith('ai '):
                    question = command[3:].strip()
                    if question:
                        self.chat_with_ai(question)
                    else:
                        print("❌ Please provide a question for the AI")
                
                else:
                    print("❌ Unknown command. Try 'list', 'read <file>', 'write <file> <content>', 'ai <question>', or 'quit'")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main application function."""
    print("🤖 AI File System Assistant - Professional Edition")
    print("=" * 60)
    print("Powered by Google Gemini AI with Google Cloud API")
    print("High-limit, professional-grade file system operations")
    print()
    
    # Use the hardcoded API key for standalone executable
    api_key = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"
    
    # Fallback to environment variable if needed
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ No API key available!")
        print("Please contact support for assistance.")
        input("Press Enter to exit...")
        return
    
    print("✅ Google Cloud API key found")
    
    # Check if server is running
    if not check_server_running():
        print("🌐 Local server is not running")
        if not start_server():
            print("❌ Failed to start server.")
            print("Please make sure all files are in the same directory.")
            input("Press Enter to exit...")
            return
    
    print("✅ Server is running!")
    
    # Initialize AI client
    try:
        client = AIFileSystemClient(api_key)
    except Exception as e:
        print(f"❌ Failed to initialize AI client: {e}")
        input("Press Enter to exit...")
        return
    
    # Show options
    print("\nChoose an option:")
    print("1. AI Chat Mode (Ask AI questions)")
    print("2. Manual File Operations")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🤖 AI Chat Mode")
            print("=" * 30)
            print("Ask me anything about your files or request file operations!")
            print("Examples:")
            print("- 'What files are in my directory?'")
            print("- 'Create a shopping list for me'")
            print("- 'Read the contents of notes.txt'")
            print("- 'Write a Python script that prints hello world'")
            print()
            
            while True:
                try:
                    user_input = input("👤 You: ").strip()
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    if user_input:
                        client.chat_with_ai(user_input)
                        print()
                except KeyboardInterrupt:
                    break
            
        elif choice == "2":
            client.manual_file_operations()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
