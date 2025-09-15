import os
import pathlib
from typing import List, Dict, Any


class SecurityError(Exception):
    """Raised when a file operation attempts to access files outside the safe directory."""
    pass


# Define the safe directory - change this to your desired safe directory
# Using current directory for testing, change to Desktop for production
SAFE_DIRECTORY = os.getcwd()


def _validate_path(file_path: str) -> str:
    """
    Validate that the given path is within the safe directory.
    Raises SecurityError if the path is outside the safe directory.
    """
    # Convert to absolute path
    abs_path = os.path.abspath(file_path)
    safe_abs_path = os.path.abspath(SAFE_DIRECTORY)
    
    # Check if the path is within the safe directory
    if not abs_path.startswith(safe_abs_path):
        raise SecurityError(f"Access denied: Path '{file_path}' is outside the safe directory '{SAFE_DIRECTORY}'")
    
    return abs_path


def read_file(file_path: str) -> str:
    """
    Read the text content of a file.
    
    Args:
        file_path (str): Path to the file to read (relative to safe directory)
    
    Returns:
        str: The content of the file
        
    Raises:
        SecurityError: If the file path is outside the safe directory
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    validated_path = _validate_path(file_path)
    
    try:
        with open(validated_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise IOError(f"Error reading file '{file_path}': {str(e)}")


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Write text content to a file.
    
    Args:
        file_path (str): Path to the file to write (relative to safe directory)
        content (str): The content to write to the file
    
    Returns:
        Dict[str, Any]: Success message and file info
        
    Raises:
        SecurityError: If the file path is outside the safe directory
        IOError: If there's an error writing the file
    """
    validated_path = _validate_path(file_path)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(validated_path), exist_ok=True)
        
        with open(validated_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return {
            "success": True,
            "message": f"Successfully wrote to file: {file_path}",
            "file_path": file_path,
            "bytes_written": len(content.encode('utf-8'))
        }
    except Exception as e:
        raise IOError(f"Error writing to file '{file_path}': {str(e)}")


def list_directory(directory_path: str) -> List[Dict[str, Any]]:
    """
    List the contents of a directory.
    
    Args:
        directory_path (str): Path to the directory to list (relative to safe directory)
    
    Returns:
        List[Dict[str, Any]]: List of files and directories with their info
        
    Raises:
        SecurityError: If the directory path is outside the safe directory
        FileNotFoundError: If the directory doesn't exist
        IOError: If there's an error reading the directory
    """
    validated_path = _validate_path(directory_path)
    
    try:
        if not os.path.exists(validated_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not os.path.isdir(validated_path):
            raise IOError(f"Path is not a directory: {directory_path}")
        
        items = []
        for item in os.listdir(validated_path):
            item_path = os.path.join(validated_path, item)
            item_info = {
                "name": item,
                "is_directory": os.path.isdir(item_path),
                "is_file": os.path.isfile(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None
            }
            items.append(item_info)
        
        return items
    except FileNotFoundError:
        raise
    except Exception as e:
        raise IOError(f"Error listing directory '{directory_path}': {str(e)}")


# Available tools mapping for the API
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory
}