import google.generativeai as genai
import requests
import json
import os
from typing import Dict, Any, Optional
from tool_schemas import local_tools_schema


class GeminiClient:
    """Client for communicating with Gemini API and local file system tools."""
    
    def __init__(self, api_key: str, local_server_url: str = "http://localhost:8000"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key (str): Your Google Gemini API key
            local_server_url (str): URL of the local FastAPI server
        """
        self.api_key = api_key
        self.local_server_url = local_server_url
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize the model with tools
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=local_tools_schema
        )
        
        # Start a chat session
        self.chat = self.model.start_chat(history=[])
    
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
                    
                    print(f"🔧 Executing tool: {tool_name} with parameters: {parameters}")
                    
                    # Execute the tool on local server
                    tool_result = self.execute_local_tool(tool_name, parameters)
                    
                    if tool_result.get("success"):
                        print(f"✅ Tool executed successfully: {tool_result.get('result', 'No result')}")
                    else:
                        print(f"❌ Tool execution failed: {tool_result.get('error', 'Unknown error')}")
                    
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
    
    def chat_with_gemini(self, user_prompt: str) -> str:
        """
        Send a message to Gemini and handle any tool calls.
        
        Args:
            user_prompt (str): The user's message/prompt
            
        Returns:
            str: Gemini's final response
        """
        try:
            print(f"👤 User: {user_prompt}")
            print("🤖 Gemini is thinking...")
            
            # Send the message to Gemini
            response = self.chat.send_message(user_prompt)
            
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
        """Start an interactive conversation loop."""
        print("🚀 Gemini File System Assistant Started!")
        print("=" * 50)
        print("You can ask me to:")
        print("- Read files: 'What's in my notes.txt file?'")
        print("- Write files: 'Create a new file called todo.txt with my tasks'")
        print("- List directories: 'What files are in my Documents folder?'")
        print("- Or any combination of these operations!")
        print("=" * 50)
        print("Type 'quit' or 'exit' to stop the conversation.\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                response = self.chat_with_gemini(user_input)
                print()  # Add spacing between exchanges
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Please try again.\n")


def main():
    """Main function to run the client."""
    # Get API key from environment variable or prompt user
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("🔑 Please set your Gemini API key:")
        print("Option 1: Set environment variable: set GEMINI_API_KEY=your_api_key_here")
        print("Option 2: Enter it now (it won't be saved):")
        api_key = input("API Key: ").strip()
        
        if not api_key:
            print("❌ No API key provided. Exiting.")
            return
    
    # Check if local server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Local server is running")
        else:
            print("⚠️  Local server responded with unexpected status")
    except requests.exceptions.RequestException:
        print("❌ Local server is not running!")
        print("Please start the server first by running: python main.py")
        return
    
    # Initialize and start the client
    client = GeminiClient(api_key)
    client.start_conversation_loop()


if __name__ == "__main__":
    main()