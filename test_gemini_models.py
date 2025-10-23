#!/usr/bin/env python3
"""
Experimental script to discover the correct Gemini model names
"""
import google.generativeai as genai
import os

# Set the API key
API_KEY = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"
genai.configure(api_key=API_KEY)

print("DISCOVERING GEMINI MODELS...")
print("=" * 50)

try:
    # List all available models
    print("Available models:")
    models = genai.list_models()
    
    for model in models:
        print(f"  - {model.name}")
        print(f"    Display Name: {model.display_name}")
        print(f"    Supported Methods: {model.supported_generation_methods}")
        print()
    
    print("=" * 50)
    print("TESTING DIFFERENT MODEL NAMES...")
    
    # Test different model name variations
    test_models = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-1.0-pro",
        "gemini-1.5-pro-001",
        "gemini-1.5-flash-001",
        "models/gemini-pro",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash"
    ]
    
    working_models = []
    
    for model_name in test_models:
        try:
            print(f"Testing: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, test message")
            print(f"SUCCESS: {model_name} works!")
            working_models.append(model_name)
            print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"FAILED: {model_name} - {str(e)[:100]}...")
        print()
    
    print("=" * 50)
    print("WORKING MODELS:")
    for model in working_models:
        print(f"  SUCCESS: {model}")
    
    if working_models:
        print(f"\nRECOMMENDED MODEL: {working_models[0]}")
    else:
        print("\nNO WORKING MODELS FOUND!")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 50)
print("EXPERIMENT COMPLETE!")
