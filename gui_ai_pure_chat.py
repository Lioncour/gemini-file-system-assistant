#!/usr/bin/env python3
"""
FloKroll AI Pure Chat Assistant - Everything through natural language chat
"""
import tkinter as tk
from tkinter import scrolledtext
import os
import shutil
import google.generativeai as genai
import threading
import re
from pathlib import Path

# --- Configuration ---
API_KEY = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"  # Hardcoded API key

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('models/gemini-2.5-flash')
chat = model.start_chat(history=[])

# --- File System Operations ---
def _resolve_path(filepath):
    """Resolves a path to be absolute and handles both relative and absolute paths."""
    if not filepath:
        raise ValueError("Filepath cannot be empty.")
    
    # If it's already absolute, use it as is
    if os.path.isabs(filepath):
        return filepath
    
    # Otherwise, make it absolute from current directory
    return os.path.abspath(filepath)

def read_file_full(filepath: str) -> str:
    """Reads the content of any file on the system."""
    try:
        resolved_path = _resolve_path(filepath)
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {filepath}")
    except Exception as e:
        raise Exception(f"Error reading file {filepath}: {e}")

def write_file_full(filepath: str, content: str) -> str:
    """Writes content to any file on the system."""
    try:
        resolved_path = _resolve_path(filepath)
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {resolved_path}"
    except PermissionError:
        raise PermissionError(f"Permission denied: {filepath}")
    except Exception as e:
        raise Exception(f"Error writing to file {filepath}: {e}")

def list_directory_full(path: str = ".") -> list:
    """Lists the contents of any directory on the system."""
    try:
        resolved_path = _resolve_path(path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Directory not found: {path}")
        if not os.path.isdir(resolved_path):
            raise NotADirectoryError(f"Path is not a directory: {path}")
        
        contents = []
        for item in os.listdir(resolved_path):
            item_path = os.path.join(resolved_path, item)
            if os.path.isdir(item_path):
                contents.append(f"[DIR] {item}")
            else:
                size = os.path.getsize(item_path)
                contents.append(f"[FILE] {item} ({size} bytes)")
        return contents
    except Exception as e:
        raise Exception(f"Error listing directory {path}: {e}")

def move_file_full(source: str, destination: str) -> str:
    """Moves a file or directory to a new location."""
    try:
        source_path = _resolve_path(source)
        dest_path = _resolve_path(destination)
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source}")
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        shutil.move(source_path, dest_path)
        return f"Successfully moved {source} to {dest_path}"
    except Exception as e:
        raise Exception(f"Error moving {source} to {destination}: {e}")

def copy_file_full(source: str, destination: str) -> str:
    """Copies a file or directory to a new location."""
    try:
        source_path = _resolve_path(source)
        dest_path = _resolve_path(destination)
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source}")
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)
        
        return f"Successfully copied {source} to {dest_path}"
    except Exception as e:
        raise Exception(f"Error copying {source} to {destination}: {e}")

def delete_file_full(filepath: str) -> str:
    """Deletes a file or directory."""
    try:
        resolved_path = _resolve_path(filepath)
        
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if os.path.isdir(resolved_path):
            shutil.rmtree(resolved_path)
            return f"Successfully deleted directory: {resolved_path}"
        else:
            os.remove(resolved_path)
            return f"Successfully deleted file: {resolved_path}"
    except Exception as e:
        raise Exception(f"Error deleting {filepath}: {e}")

def rename_file_full(old_path: str, new_path: str) -> str:
    """Renames a file or directory."""
    try:
        old_resolved = _resolve_path(old_path)
        new_resolved = _resolve_path(new_path)
        
        if not os.path.exists(old_resolved):
            raise FileNotFoundError(f"File not found: {old_path}")
        
        os.rename(old_resolved, new_resolved)
        return f"Successfully renamed {old_path} to {new_resolved}"
    except Exception as e:
        raise Exception(f"Error renaming {old_path} to {new_path}: {e}")

def search_files_full(directory: str, pattern: str) -> list:
    """Searches for files matching a pattern in a directory."""
    try:
        search_path = _resolve_path(directory)
        if not os.path.exists(search_path):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        matches = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if re.search(pattern, file, re.IGNORECASE):
                    matches.append(os.path.join(root, file))
        return matches
    except Exception as e:
        raise Exception(f"Error searching in {directory}: {e}")

# --- Pure Chat GUI Application ---
class FloKrollAIPureChat(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FloKroll AI Pure Chat Assistant")
        self.geometry("1000x700")
        self.configure(bg="#2e2e2e")  # Dark background

        # Load and set icon
        try:
            self.iconbitmap("ai_assistant_icon.ico")
        except tk.TclError:
            print("Warning: Icon file 'ai_assistant_icon.ico' not found. Running without icon.")

        self._create_widgets()
        self._setup_layout()
        self.add_to_chat("🤖 Hello! I'm FloKroll AI Assistant!", "ai")
        self.add_to_chat("I can help you with ALL file operations on your computer using natural language.", "ai")
        self.add_to_chat("Just tell me what you want to do with your files!", "ai")
        self.add_to_chat("Examples: 'show me desktop files', 'move file.txt to downloads', 'delete old files'", "ai")

    def _create_widgets(self):
        # --- Styles ---
        self.option_add("*Font", "SegoeUI 10")
        self.option_add("*Background", "#2e2e2e")
        self.option_add("*Foreground", "#ffffff")
        self.option_add("*Button.Background", "#00ff88")
        self.option_add("*Button.Foreground", "#2e2e2e")
        self.option_add("*Button.Relief", "flat")
        self.option_add("*Button.Borderwidth", "0")
        self.option_add("*TEntry.Fieldbackground", "#4a4a4a")
        self.option_add("*TEntry.Foreground", "#ffffff")
        self.option_add("*TEntry.Borderwidth", "0")
        self.option_add("*TEntry.Relief", "flat")
        self.option_add("*TText.Background", "#4a4a4a")
        self.option_add("*TText.Foreground", "#ffffff")
        self.option_add("*TText.Borderwidth", "0")
        self.option_add("*TText.Relief", "flat")

        # --- Main Frame ---
        self.main_frame = tk.Frame(self, bg="#2e2e2e")

        # --- Chat Panel ---
        self.chat_history = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, state='disabled', 
                                                     bg="#4a4a4a", fg="#ffffff", insertbackground="#00ff88")
        self.chat_input = tk.Text(self.main_frame, height=3, bg="#4a4a4a", fg="#ffffff", insertbackground="#00ff88")
        self.send_button = tk.Button(self.main_frame, text="Send (Enter)", command=self.send_message, 
                                   bg="#00ff88", fg="#2e2e2e")

        # --- Status ---
        self.status_label = tk.Label(self.main_frame, text="Status: Ready!", 
                                   bg="#2e2e2e", fg="#00ff88")

        # --- Bindings ---
        self.chat_input.bind('<Return>', self.send_message)
        self.chat_input.bind('<Control-Return>', self.add_new_line)

    def _setup_layout(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Chat Panel Layout
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_input.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.send_button.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.status_label.pack(pady=5)

    def update_status(self, message, color="#00ff88"):
        self.status_label.config(text=f"Status: {message}", fg=color)

    def add_to_chat(self, message, sender="ai"):
        self.chat_history.config(state='normal')
        if sender == "user":
            self.chat_history.insert(tk.END, f"👤 You: {message}\n\n", "user")
        else:
            self.chat_history.insert(tk.END, f"🤖 FloKroll AI: {message}\n\n", "ai")
        
        self.chat_history.config(state='disabled')
        self.chat_history.yview(tk.END)

    def send_message(self, event=None):
        """Send a message to the AI"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_to_chat(message, "user")
        
        # Clear input
        self.chat_input.delete("1.0", tk.END)
        
        # Process message with AI
        threading.Thread(target=self.process_ai_message, args=(message,), daemon=True).start()

    def add_new_line(self):
        """Add a new line in the text input (Ctrl+Enter)"""
        self.chat_input.insert(tk.INSERT, '\n')

    def process_ai_message(self, message):
        """Process the AI message with full system capabilities"""
        try:
            self.update_status("AI is thinking...", "#FFA500")
            
            # Enhanced AI prompt with full system capabilities
            enhanced_prompt = f"""
You are FloKroll AI, a powerful file system assistant with FULL access to the user's computer.

Available operations:
- READ: Read any file on the system
- WRITE: Write to any file on the system  
- LIST: List contents of any directory
- MOVE: Move files or directories
- COPY: Copy files or directories
- DELETE: Delete files or directories
- RENAME: Rename files or directories
- SEARCH: Search for files by pattern

User request: "{message}"

Analyze the request and determine what file operations are needed. Be specific about file paths.
If the user asks about "desktop files", they likely mean files in their Desktop directory.
If they ask about "all files", help them navigate to specific directories.

Respond with helpful guidance and suggest specific file operations. If you can determine the exact operation needed, provide the specific file paths and operation.
"""

            response = chat.send_message(enhanced_prompt)
            ai_response = response.text if response.text else "I'm here to help with your files!"
            
            # Try to execute file operations based on the AI response
            self.execute_file_operations(message, ai_response)
            
            self.add_to_chat(ai_response, "ai")
            self.update_status("Ready for more commands!")

        except Exception as e:
            self.add_to_chat(f"Sorry, I encountered an error: {e}", "ai")
            self.update_status("Error during AI processing", "#FF6347")

    def execute_file_operations(self, user_message, ai_response):
        """Try to execute file operations based on user message"""
        try:
            user_lower = user_message.lower()
            
            # Desktop files
            if "desktop" in user_lower and ("show" in user_lower or "list" in user_lower or "files" in user_lower):
                desktop_path = os.path.expanduser("~/Desktop")
                if os.path.exists(desktop_path):
                    contents = list_directory_full(desktop_path)
                    result = f"Desktop contents:\n" + "\n".join(contents[:20])  # Limit to first 20 items
                    if len(contents) > 20:
                        result += f"\n... and {len(contents) - 20} more items"
                    self.add_to_chat(result, "ai")
                else:
                    self.add_to_chat("Desktop directory not found.", "ai")
            
            # List current directory
            elif "list" in user_lower and ("here" in user_lower or "current" in user_lower or "this" in user_lower):
                contents = list_directory_full(".")
                result = f"Current directory contents:\n" + "\n".join(contents[:20])
                if len(contents) > 20:
                    result += f"\n... and {len(contents) - 20} more items"
                self.add_to_chat(result, "ai")
            
            # Read specific file
            elif "read" in user_lower and any(ext in user_lower for ext in [".txt", ".md", ".py", ".js", ".html", ".css"]):
                # Try to find a file to read
                for ext in [".txt", ".md", ".py", ".js", ".html", ".css"]:
                    if ext in user_lower:
                        # Look for files with this extension
                        for file in os.listdir("."):
                            if file.endswith(ext):
                                try:
                                    content = read_file_full(file)
                                    result = f"Content of {file}:\n{content[:1000]}"
                                    if len(content) > 1000:
                                        result += "\n... (truncated)"
                                    self.add_to_chat(result, "ai")
                                    return
                                except:
                                    continue
                self.add_to_chat("No readable files found in current directory.", "ai")
            
            # Search for files
            elif "search" in user_lower or "find" in user_lower:
                # Extract search pattern from message
                pattern = ".*"  # Default pattern
                if "txt" in user_lower:
                    pattern = ".*\\.txt$"
                elif "py" in user_lower:
                    pattern = ".*\\.py$"
                elif "jpg" in user_lower or "png" in user_lower:
                    pattern = ".*\\.(jpg|jpeg|png)$"
                
                matches = search_files_full(".", pattern)
                if matches:
                    result = f"Found {len(matches)} files:\n" + "\n".join(matches[:10])
                    if len(matches) > 10:
                        result += f"\n... and {len(matches) - 10} more files"
                    self.add_to_chat(result, "ai")
                else:
                    self.add_to_chat(f"No files found matching pattern: {pattern}", "ai")
            
        except Exception as e:
            self.add_to_chat(f"Error executing file operation: {e}", "ai")

if __name__ == "__main__":
    app = FloKrollAIPureChat()
    app.mainloop()
