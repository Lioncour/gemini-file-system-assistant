#!/usr/bin/env python3
"""
Simplified client that demonstrates the system working with manual tool calls.
This version works around the schema issues by manually handling tool calls.
"""

import google.generativeai as genai
import requests
import json
import os
from typing import Dict, Any, Optional


class SimpleGeminiClient:
    """Simplified client for demonstrating the system."""
    
    def __init__(self, api_key: str, local_server_url: str = "http://localhost:8000"):
        """Initialize the client."""
        self.api_key = api_key
        self.local_server_url = local_server_url
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model without tools for now
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Start a chat session
        self.chat = self.model.start_chat(history=[])
    
    def execute_local_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on the local server."""
        try:
            response = requests.post(
                f"{self.local_server_url}/execute_tool",
                json={
                    "tool_name": tool_name,
                    "parameters": parameters
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to communicate with local server: {str(e)}"
            }
    
    def chat_with_gemini(self, user_prompt: str) -> str:
        """Send a message to Gemini and handle responses."""
        try:
            print(f"👤 User: {user_prompt}")
            print("🤖 Gemini is thinking...")
            
            # Send the message to Gemini
            response = self.chat.send_message(user_prompt)
            
            # For now, just return the response
            print(f"🤖 Gemini: {response.text}")
            return response.text
                
        except Exception as e:
            error_msg = f"Error communicating with Gemini: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def manual_tool_demo(self):
        """Demonstrate manual tool usage."""
        print("🎭 Manual Tool Demo")
        print("=" * 50)
        
        # Demo 1: List directory
        print("\n📂 Demo 1: Listing directory contents")
        result = self.execute_local_tool("list_directory", {"directory_path": "."})
        if result["success"]:
            files = result["result"]
            print(f"✅ Found {len(files)} items:")
            for item in files[:5]:  # Show first 5
                item_type = "📁" if item["is_directory"] else "📄"
                print(f"   {item_type} {item['name']}")
        else:
            print(f"❌ Failed: {result['error']}")
        
        # Demo 2: Write a file
        print("\n✍️ Demo 2: Writing a file")
        content = "Hello from the Gemini File System Assistant!\n\nThis file was created by the AI assistant."
        result = self.execute_local_tool("write_file", {
            "file_path": "ai_demo.txt",
            "content": content
        })
        if result["success"]:
            print("✅ File created successfully!")
            print(f"📄 {result['result']['message']}")
        else:
            print(f"❌ Failed: {result['error']}")
        
        # Demo 3: Read the file
        print("\n📖 Demo 3: Reading the file")
        result = self.execute_local_tool("read_file", {"file_path": "ai_demo.txt"})
        if result["success"]:
            print("✅ File read successfully!")
            print("📄 Content:")
            print("-" * 30)
            print(result["result"])
            print("-" * 30)
        else:
            print(f"❌ Failed: {result['error']}")
    
    def start_conversation_loop(self):
        """Start an interactive conversation loop."""
        print("🚀 Simple Gemini File System Assistant")
        print("=" * 50)
        print("This is a simplified version that demonstrates the system.")
        print("The AI can chat with you, but tool calls are handled manually.")
        print("=" * 50)
        print("Type 'demo' to see manual tool demonstrations")
        print("Type 'quit' to exit")
        print()
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'demo':
                    self.manual_tool_demo()
                    continue
                
                if not user_input:
                    continue
                
                self.chat_with_gemini(user_input)
                print()  # Add spacing
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Please try again.\n")


def main():
    """Main function."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    # Check if local server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Local server is not running!")
            print("Please start it with: python main.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Local server is not running!")
        print("Please start it with: python main.py")
        return
    
    print("✅ Local server is running")
    
    # Initialize and start the client
    client = SimpleGeminiClient(api_key)
    client.start_conversation_loop()


if __name__ == "__main__":
    main()
