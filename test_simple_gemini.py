#!/usr/bin/env python3
"""
Test simple Gemini API without tools first.
"""

import google.generativeai as genai
import os

def test_simple_gemini():
    """Test basic Gemini API functionality."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    try:
        genai.configure(api_key=api_key)
        
        # Test without tools first
        print("🧪 Testing basic Gemini API...")
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        response = model.generate_content("Hello! Can you help me with file operations?")
        print(f"✅ Basic API works: {response.text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic API failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_gemini()
