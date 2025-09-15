from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from local_tools import AVAILABLE_TOOLS, SecurityError


app = FastAPI(
    title="Local File System Tools API",
    description="A secure API for file system operations within a safe directory",
    version="1.0.0"
)


class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]


class ToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Local File System Tools API is running", "status": "healthy"}


@app.get("/tools")
async def list_available_tools():
    """List all available tools."""
    return {
        "available_tools": list(AVAILABLE_TOOLS.keys()),
        "tools_info": {
            "read_file": "Read the text content of a file",
            "write_file": "Write text content to a file", 
            "list_directory": "List the contents of a directory"
        }
    }


@app.post("/execute_tool", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """
    Execute a tool with the given parameters.
    
    Args:
        request: ToolRequest containing tool_name and parameters
        
    Returns:
        ToolResponse with the result or error information
    """
    try:
        # Check if the tool exists
        if request.tool_name not in AVAILABLE_TOOLS:
            return ToolResponse(
                success=False,
                error=f"Tool '{request.tool_name}' not found. Available tools: {list(AVAILABLE_TOOLS.keys())}"
            )
        
        # Get the tool function
        tool_function = AVAILABLE_TOOLS[request.tool_name]
        
        # Execute the tool with the provided parameters
        result = tool_function(**request.parameters)
        
        return ToolResponse(
            success=True,
            result=result
        )
        
    except SecurityError as e:
        return ToolResponse(
            success=False,
            error=f"Security violation: {str(e)}"
        )
    except FileNotFoundError as e:
        return ToolResponse(
            success=False,
            error=f"File not found: {str(e)}"
        )
    except IOError as e:
        return ToolResponse(
            success=False,
            error=f"I/O error: {str(e)}"
        )
    except TypeError as e:
        return ToolResponse(
            success=False,
            error=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )


if __name__ == "__main__":
    print("Starting Local File System Tools API server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation available at: http://localhost:8000/docs")
    print(f"Safe directory: {AVAILABLE_TOOLS['read_file'].__globals__['SAFE_DIRECTORY']}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)