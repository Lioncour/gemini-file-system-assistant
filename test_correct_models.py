#!/usr/bin/env python3
"""
Test the correct model names discovered from the API
"""
import google.generativeai as genai

# Set the API key
API_KEY = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"
genai.configure(api_key=API_KEY)

print("TESTING CORRECT MODEL NAMES...")
print("=" * 50)

# Test the correct model names from the API response
test_models = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro", 
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest",
    "models/gemini-flash-latest"
]

working_models = []

for model_name in test_models:
    try:
        print(f"Testing: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, this is a test message. Please respond briefly.")
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
    print("This model will be used in the FloKroll AI app!")
else:
    print("\nNO WORKING MODELS FOUND!")

print("\n" + "=" * 50)
print("EXPERIMENT COMPLETE!")
