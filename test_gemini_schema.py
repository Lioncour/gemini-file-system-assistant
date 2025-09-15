#!/usr/bin/env python3
"""
Test script to figure out the correct schema format for Gemini API.
"""

import google.generativeai as genai
import os

def test_schema_formats():
    """Test different schema formats to find the correct one."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return
    
    genai.configure(api_key=api_key)
    
    # Test different schema formats
    test_schemas = [
        # Format 1: Simple format
        [
            {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to file"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ],
        
        # Format 2: With type field
        [
            {
                "name": "read_file", 
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to file"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ],
        
        # Format 3: Minimal format
        [
            {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file"
                    }
                }
            }
        ]
    ]
    
    for i, schema in enumerate(test_schemas, 1):
        print(f"\n🧪 Testing schema format {i}:")
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                tools=schema
            )
            print(f"   ✅ Format {i} works!")
            return schema
        except Exception as e:
            print(f"   ❌ Format {i} failed: {str(e)[:100]}...")
    
    print("\n❌ No schema format worked")
    return None

if __name__ == "__main__":
    test_schema_formats()
