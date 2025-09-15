# 🤖 Gemini File System Assistant

A secure, AI-powered file system assistant that uses Google's Gemini AI to interact with your files through a controlled, safe environment. This project demonstrates the integration of AI with local file operations through a secure API.

## ✨ Features

- **🤖 AI-Powered**: Uses Google Gemini 1.5 Pro for natural language file operations
- **🔒 Secure**: All file operations restricted to a safe directory
- **🌐 Local Server**: FastAPI-based local server for secure file access
- **🛠️ Tool Integration**: Automatic function calling between AI and file system
- **💬 Interactive**: Natural language conversation interface
- **🔧 Extensible**: Easy to add new file operations

## 🏗️ Architecture

This project consists of three main components:

1. **Local Server** (`main.py` + `local_tools.py`): FastAPI server providing secure file operations
2. **Tool Schemas** (`tool_schemas.py`): JSON schemas defining available tools for Gemini
3. **Client Applications**: Multiple client options for different use cases

## 📁 Project Structure

```
FloRobot/
├── main.py                  # FastAPI server
├── local_tools.py           # Secure file system functions
├── tool_schemas.py          # Gemini API tool definitions
├── client_app.py            # Main client with full AI integration
├── simple_client.py         # Simplified client for testing
├── demo.py                  # Interactive demonstration
├── test_api.py              # API testing script
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd FloRobot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable:

**Windows:**
```cmd
set GOOGLE_API_KEY=your_api_key_here
```

**macOS/Linux:**
```bash
export GOOGLE_API_KEY=your_api_key_here
```

### 4. Start the Local Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 5. Run the Client Application

In a new terminal window:

```bash
python client_app.py
```

## 🛠️ Available Tools

The assistant can perform these secure file operations:

### 📖 Read File
- **Tool**: `read_file`
- **Description**: Read text content from a file
- **Example**: "What's in my notes.txt file?"

### ✍️ Write File
- **Tool**: `write_file`
- **Description**: Write text content to a file
- **Example**: "Create a todo.txt file with my tasks"

### 📂 List Directory
- **Tool**: `list_directory`
- **Description**: List contents of a directory
- **Example**: "What files are in my Documents folder?"

## 💬 Example Usage

```
👤 You: What files are in my directory?
🤖 Gemini: I'll check what files are in your directory for you.
🔧 Executing tool: list_directory with parameters: {'directory_path': '.'}
✅ Tool executed successfully
🤖 Gemini: I found 15 files in your directory: client.py, demo.py, main.py, etc.

👤 You: Create a shopping list for me
🤖 Gemini: I'll create a shopping list file for you.
🔧 Executing tool: write_file with parameters: {'file_path': 'shopping_list.txt', 'content': 'Shopping List:\n- Milk\n- Bread\n- Eggs'}
✅ Tool executed successfully
🤖 Gemini: I've created a shopping list file called 'shopping_list.txt' with common grocery items.
```

## 🎯 Client Options

### 1. Full AI Integration (`client_app.py`)
- Complete AI-powered file system assistant
- Automatic tool calling
- Natural language conversation

### 2. Simplified Client (`simple_client.py`)
- Manual tool demonstrations
- Basic AI chat functionality
- Good for testing and learning

### 3. Interactive Demo (`demo.py`)
- Automated demonstrations
- Shows system capabilities
- No AI interaction required

### 4. API Testing (`test_api.py`)
- Direct API endpoint testing
- Automated test suite
- Good for debugging

## 🔧 Configuration

### Changing the Safe Directory

Edit `local_tools.py`:

```python
# Change this line in local_tools.py
SAFE_DIRECTORY = os.path.expanduser("~/Documents")  # or any other directory
```

### Server Configuration

Edit `main.py` to change port:

```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Different port
```

## 🛡️ Security Features

- **Sandboxed Access**: All file operations restricted to safe directory
- **Path Validation**: Prevents directory traversal attacks (`../` protection)
- **Local-Only**: Server only accepts localhost connections
- **Error Handling**: Comprehensive error handling without exposing sensitive info
- **API Key Security**: Environment variable storage

## 🐛 Troubleshooting

### Server Issues
- Check if port 8000 is available
- Ensure all dependencies are installed
- Verify Python version (3.8+ required)

### Client Issues
- Verify server is running on `http://localhost:8000`
- Check API key is set correctly
- Ensure environment variables are properly configured

### File Access Issues
- Check safe directory permissions
- Verify file paths are within safe directory
- Ensure files exist before reading

## 📝 API Documentation

When the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional file operations (copy, move, delete)
- File search functionality
- Batch operations
- Enhanced security features
- Better error handling
- UI improvements

## 📄 License

This project is for educational and personal use. Please ensure you comply with Google's Gemini API terms of service.

## 🙏 Acknowledgments

- Google Gemini AI for the powerful language model
- FastAPI for the excellent web framework
- The open-source community for inspiration and tools

---

**Happy coding! 🚀**