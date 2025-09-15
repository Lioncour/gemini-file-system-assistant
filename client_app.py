#!/usr/bin/env python3
"""
Final client application that integrates Gemini AI with local file system tools.
This script handles the complete flow: user input -> Gemini -> tool calls -> local server -> results -> Gemini -> final response.
"""

import os
import requests
import google.generativeai as genai
from tool_schemas import local_tools_schema
from typing import Dict, Any, Optional


class GeminiFileSystemClient:
    """Main client class that handles the complete AI-file system integration."""
    
    def __init__(self, api_key: str, local_server_url: str = "http://localhost:8000"):
        """
        Initialize the client with API key and local server URL.
        
        Args:
            api_key (str): Google Gemini API key
            local_server_url (str): URL of the local FastAPI server
        """
        self.api_key = api_key
        self.local_server_url = local_server_url
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the Gemini model with tools
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            tools=local_tools_schema
        )
        
        # Start a persistent chat session
        self.chat = self.model.start_chat(history=[])
        
        print("✅ Gemini File System Client initialized successfully!")
        print(f"🤖 Model: gemini-1.5-pro-latest")
        print(f"🔧 Tools: {len(local_tools_schema)} file system tools loaded")
        print(f"🌐 Local server: {local_server_url}")
    
    def execute_local_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on the local server.
        
        Args:
            tool_name (str): Name of the tool to execute
            parameters (Dict[str, Any]): Parameters for the tool
            
        Returns:
            Dict[str, Any]: Response from the local server
        """
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
    
    def process_tool_calls(self, response) -> Optional[str]:
        """
        Process tool calls from Gemini's response.
        
        Args:
            response: Gemini's response object
            
        Returns:
            Optional[str]: Final response text if no more tool calls needed, None if tool calls were processed
        """
        if not hasattr(response, 'candidates') or not response.candidates:
            return response.text
        
        candidate = response.candidates[0]
        
        # Check if the response contains function calls
        if hasattr(candidate, 'content') and candidate.content:
            parts = candidate.content.parts
            
            for part in parts:
                if hasattr(part, 'function_call') and part.function_call:
                    # Extract function call details
                    function_call = part.function_call
                    tool_name = function_call.name
                    parameters = dict(function_call.args)
                    
                    # Execute the tool on local server
                    tool_result = self.execute_local_tool(tool_name, parameters)
                    
                    # Send the tool result back to Gemini
                    function_response = genai.types.FunctionResponse(
                        name=tool_name,
                        response=tool_result
                    )
                    
                    # Send the function response back to the model
                    follow_up = self.chat.send_message(
                        genai.types.Part.from_function_response(function_response)
                    )
                    
                    # Recursively process any additional tool calls
                    return self.process_tool_calls(follow_up)
        
        # No function calls found, return the text response
        return response.text
    
    def send_message(self, user_input: str) -> str:
        """
        Send a message to Gemini and handle any tool calls.
        
        Args:
            user_input (str): The user's message
            
        Returns:
            str: Gemini's final response
        """
        try:
            print(f"👤 User: {user_input}")
            print("🤖 Gemini is thinking...")
            
            # Send the message to Gemini
            response = self.chat.send_message(user_input)
            
            # Process any tool calls
            final_response = self.process_tool_calls(response)
            
            if final_response:
                print(f"🤖 Gemini: {final_response}")
                return final_response
            else:
                return "I processed your request but didn't receive a final response."
                
        except Exception as e:
            error_msg = f"Error communicating with Gemini: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def start_conversation_loop(self):
        """Start the main conversation loop."""
        print("\n🚀 Gemini File System Assistant - Full Integration")
        print("=" * 60)
        print("This is the complete system with automatic tool calling!")
        print("You can now ask natural questions and the AI will automatically")
        print("use the file system tools to help you.")
        print("=" * 60)
        print("Examples:")
        print("- 'What files are in my directory?'")
        print("- 'Create a new file called notes.txt with some content'")
        print("- 'Read the contents of demo.txt'")
        print("- 'List all Python files in my directory'")
        print("=" * 60)
        print("Type 'exit' to quit the application.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                # Check for exit command
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye! Thanks for using the Gemini File System Assistant!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Send message and get response
                response = self.send_message(user_input)
                print()  # Add spacing between exchanges
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using the Gemini File System Assistant!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Please try again.\n")


def main():
    """Main function to run the client application."""
    print("🔑 Checking for Google API key...")
    
    # Get API key from environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not found!")
        print("Please set your API key:")
        print("Windows: set GOOGLE_API_KEY=your_api_key_here")
        print("macOS/Linux: export GOOGLE_API_KEY=your_api_key_here")
        return
    
    print("✅ API key found")
    
    # Check if local server is running
    print("🌐 Checking local server...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Local server is running")
        else:
            print("❌ Local server responded with unexpected status")
            return
    except requests.exceptions.RequestException:
        print("❌ Local server is not running!")
        print("Please start the server first by running: python main.py")
        return
    
    # Initialize and start the client
    try:
        client = GeminiFileSystemClient(api_key)
        client.start_conversation_loop()
    except Exception as e:
        print(f"❌ Failed to initialize client: {str(e)}")
        print("Please check your API key and try again.")


if __name__ == "__main__":
    main()
