"""
Tool schema definitions for Google Gemini API.
These schemas define the available tools that can be called by the Gemini model.
"""

# Local tools schema for Google Gemini API
local_tools_schema = [
    {
        "name": "read_file",
        "description": "Read the text content of a file from the local file system. This tool can only access files within the safe directory (typically the user's Desktop).",
        "parameters": {
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read, relative to the safe directory"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file", 
        "description": "Write text content to a file on the local file system. This tool can only write files within the safe directory (typically the user's Desktop). If the directory doesn't exist, it will be created.",
        "parameters": {
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write, relative to the safe directory"
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List the contents of a directory on the local file system. This tool can only access directories within the safe directory (typically the user's Desktop).",
        "parameters": {
            "properties": {
                "directory_path": {
                    "type": "string", 
                    "description": "The path to the directory to list, relative to the safe directory"
                }
            },
            "required": ["directory_path"]
        }
    }
]

# Alternative format for function calling (if needed)
FUNCTION_DEFINITIONS = {
    "read_file": {
        "name": "read_file",
        "description": "Read the text content of a file from the local file system within the safe directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read, relative to the safe directory"
                }
            },
            "required": ["file_path"]
        }
    },
    "write_file": {
        "name": "write_file",
        "description": "Write text content to a file on the local file system within the safe directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write, relative to the safe directory"
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    "list_directory": {
        "name": "list_directory",
        "description": "List the contents of a directory on the local file system within the safe directory",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "The path to the directory to list, relative to the safe directory"
                }
            },
            "required": ["directory_path"]
        }
    }
}