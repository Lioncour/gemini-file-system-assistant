#!/usr/bin/env python3
"""
Test the AI integration with the new API key.
"""

import os
import google.generativeai as genai

def test_ai():
    """Test the AI connection."""
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"API Key found: {api_key[:10]}..." if api_key else "No API key")
    
    if not api_key:
        print("❌ No API key")
        return
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        
        response = model.generate_content("Hello! Can you help me with file operations?")
        print("✅ AI Response:")
        print(response.text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai()

