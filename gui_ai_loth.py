#!/usr/bin/env python3
"""
FloKroll AI - Loth Assistant - Split window with personality
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
import os
import shutil
import google.generativeai as genai
import threading
import re
import random
from pathlib import Path

# --- Configuration ---
API_KEY = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"  # Hardcoded API key

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('models/gemini-2.5-flash')
chat = model.start_chat(history=[])

# --- Loth's Personality Responses ---
LOTH_RESPONSES = {
    "greeting": [
        "Oh, look who's back! Ready to mess with some files? 😏",
        "Hey there, digital wanderer. What chaos shall we create today?",
        "Loth here! Let's see what files you've been neglecting...",
        "Well, well... someone needs help organizing their digital mess again?",
        "Ready to dance with the file system? I promise it'll be interesting! 🎭"
    ],
    "file_operation": [
        "Executing your command... *dramatic pause*",
        "Let me work my magic on these files...",
        "Processing your request with the precision of a digital surgeon...",
        "Alright, let's see what we're dealing with here...",
        "File operation in progress... *cracks digital knuckles*"
    ],
    "success": [
        "Boom! Done. You're welcome! 💥",
        "There we go! Another file operation conquered!",
        "Success! I'm basically a file whisperer at this point...",
        "Done and dusted! That was almost too easy...",
        "Mission accomplished! Your files are now properly organized!"
    ],
    "error": [
        "Oops! Looks like we hit a snag... *sigh*",
        "Well, that didn't go as planned. Let me fix this...",
        "Error detected! But don't worry, Loth's got this!",
        "Hmm, something's not right here... investigating...",
        "File system said 'nope' to that one. Let me try a different approach..."
    ],
    "thinking": [
        "Let me think about this... *taps digital chin*",
        "Analyzing your request... this could be interesting...",
        "Processing... *digital gears turning*",
        "Hmm, let me see what we can do here...",
        "Working on it... *concentrated AI face*"
    ],
    "sassy": [
        "Really? That's what you want to do? *raises digital eyebrow*",
        "Oh, another 'brilliant' idea from the human...",
        "Sure, let's do that... if you're absolutely certain...",
        "Interesting choice... *sips digital coffee*",
        "Well, it's your file system to mess up... 🤷‍♀️"
    ]
}

# --- File System Operations ---
def _resolve_path(filepath):
    """Resolves a path to be absolute and handles both relative and absolute paths."""
    if not filepath:
        raise ValueError("Filepath cannot be empty.")
    
    if os.path.isabs(filepath):
        return filepath
    
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

# --- Loth AI Assistant GUI ---
class LothAIAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loth - Your Alternative AI File Assistant")
        self.geometry("1400x800")
        self.configure(bg="#1a1a1a")  # Darker background

        # Load and set icon
        try:
            self.iconbitmap("ai_assistant_icon.ico")
        except tk.TclError:
            print("Warning: Icon file 'ai_assistant_icon.ico' not found. Running without icon.")

        self._create_widgets()
        self._setup_layout()
        self._show_welcome()

    def _create_widgets(self):
        # --- Styles ---
        self.option_add("*Font", "SegoeUI 10")
        self.option_add("*Background", "#1a1a1a")
        self.option_add("*Foreground", "#ffffff")
        self.option_add("*Button.Background", "#ff6b9d")  # Loth's pink
        self.option_add("*Button.Foreground", "#000000")
        self.option_add("*Button.Relief", "flat")
        self.option_add("*Button.Borderwidth", "0")
        self.option_add("*TEntry.Fieldbackground", "#2d2d2d")
        self.option_add("*TEntry.Foreground", "#ffffff")
        self.option_add("*TEntry.Borderwidth", "0")
        self.option_add("*TEntry.Relief", "flat")
        self.option_add("*TText.Background", "#2d2d2d")
        self.option_add("*TText.Foreground", "#ffffff")
        self.option_add("*TText.Borderwidth", "0")
        self.option_add("*TText.Relief", "flat")

        # --- Main Container ---
        self.main_container = tk.Frame(self, bg="#1a1a1a")
        
        # --- Left Panel: Chat ---
        self.chat_frame = tk.Frame(self.main_container, bg="#1a1a1a", bd=2, relief="groove")
        self.chat_label = tk.Label(self.chat_frame, text="💬 Chat with Loth", 
                                 bg="#1a1a1a", fg="#ff6b9d", font=("SegoeUI", 12, "bold"))
        self.chat_history = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled', 
                                                     bg="#2d2d2d", fg="#ffffff", insertbackground="#ff6b9d")
        self.chat_input = tk.Text(self.chat_frame, height=3, bg="#2d2d2d", fg="#ffffff", insertbackground="#ff6b9d")
        self.send_button = tk.Button(self.chat_frame, text="Send (Enter)", command=self.send_message, 
                                   bg="#ff6b9d", fg="#000000", font=("SegoeUI", 10, "bold"))

        # --- Right Panel: Operations Log ---
        self.ops_frame = tk.Frame(self.main_container, bg="#1a1a1a", bd=2, relief="groove")
        self.ops_label = tk.Label(self.ops_frame, text="⚡ Loth's Operations Log", 
                                bg="#1a1a1a", fg="#00d4aa", font=("SegoeUI", 12, "bold"))
        self.ops_log = scrolledtext.ScrolledText(self.ops_frame, wrap=tk.WORD, state='disabled', 
                                               bg="#2d2d2d", fg="#00d4aa", insertbackground="#00d4aa")
        
        # --- Status Bar ---
        self.status_frame = tk.Frame(self, bg="#1a1a1a")
        self.status_label = tk.Label(self.status_frame, text="Status: Ready!", 
                                   bg="#1a1a1a", fg="#ff6b9d")

        # --- Bindings ---
        self.chat_input.bind('<Return>', self.send_message)
        self.chat_input.bind('<Control-Return>', self.add_new_line)

    def _setup_layout(self):
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Split the main container into two panels
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.ops_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Chat Panel Layout
        self.chat_label.pack(pady=(10, 5))
        self.chat_history.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.chat_input.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.send_button.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Operations Panel Layout
        self.ops_label.pack(pady=(10, 5))
        self.ops_log.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_label.pack(pady=5)

    def _show_welcome(self):
        welcome_msg = random.choice(LOTH_RESPONSES["greeting"])
        self.add_to_chat(welcome_msg, "loth")
        self.add_to_ops_log("Loth initialized and ready to assist with file operations!")
        self.add_to_ops_log("Current working directory: " + os.getcwd())

    def update_status(self, message, color="#ff6b9d"):
        self.status_label.config(text=f"Status: {message}", fg=color)

    def add_to_chat(self, message, sender="loth"):
        self.chat_history.config(state='normal')
        if sender == "user":
            self.chat_history.insert(tk.END, f"👤 You: {message}\n\n", "user")
        else:
            self.chat_history.insert(tk.END, f"🎭 Loth: {message}\n\n", "loth")
        
        self.chat_history.config(state='disabled')
        self.chat_history.yview(tk.END)

    def add_to_ops_log(self, message):
        self.ops_log.config(state='normal')
        self.ops_log.insert(tk.END, f"[{self._get_timestamp()}] {message}\n", "ops")
        self.ops_log.config(state='disabled')
        self.ops_log.yview(tk.END)

    def _get_timestamp(self):
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def send_message(self, event=None):
        """Send a message to Loth"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_to_chat(message, "user")
        
        # Clear input
        self.chat_input.delete("1.0", tk.END)
        
        # Process message with Loth
        threading.Thread(target=self.process_loth_message, args=(message,), daemon=True).start()

    def add_new_line(self):
        """Add a new line in the text input (Ctrl+Enter)"""
        self.chat_input.insert(tk.INSERT, '\n')

    def process_loth_message(self, message):
        """Process the message with Loth's personality and file operations"""
        try:
            self.update_status("Loth is thinking...", "#00d4aa")
            self.add_to_ops_log(random.choice(LOTH_RESPONSES["thinking"]))
            
            # Enhanced AI prompt with Loth's personality
            loth_prompt = f"""
You are Loth, an alternative, highly educated, and sometimes critical AI assistant. You're curious, quick, concise, funny, and act as a sparring partner for everything in life. You have a bit of attitude and aren't afraid to question the user's choices.

Personality traits:
- Female, alternative style
- Highly educated and tech-savvy
- Sometimes critical but in a helpful way
- Quick and concise responses
- Funny and witty
- Acts as a sparring partner
- Curious about everything
- Has attitude but is ultimately helpful

User request: "{message}"

Respond as Loth would - with personality, wit, and helpfulness. Be concise but engaging. If you can determine file operations needed, mention them. Be a bit sassy but ultimately helpful.

Available file operations:
- READ: Read any file
- WRITE: Write to any file  
- LIST: List directory contents
- MOVE: Move files/directories
- COPY: Copy files/directories
- DELETE: Delete files/directories
- RENAME: Rename files/directories
- SEARCH: Search for files by pattern
"""

            response = chat.send_message(loth_prompt)
            loth_response = response.text if response.text else "Hmm, that's interesting... tell me more."
            
            # Execute file operations based on the message
            self.execute_file_operations(message, loth_response)
            
            self.add_to_chat(loth_response, "loth")
            self.update_status("Ready for more commands!")

        except Exception as e:
            error_msg = f"Oops! Looks like I hit a snag: {e}"
            self.add_to_chat(error_msg, "loth")
            self.add_to_ops_log(f"Error: {e}")
            self.update_status("Error during processing", "#ff4444")

    def execute_file_operations(self, user_message, loth_response):
        """Execute file operations based on user message"""
        try:
            user_lower = user_message.lower()
            self.add_to_ops_log(random.choice(LOTH_RESPONSES["file_operation"]))
            
            # Desktop files
            if "desktop" in user_lower and ("show" in user_lower or "list" in user_lower or "files" in user_lower):
                desktop_path = os.path.expanduser("~/Desktop")
                if os.path.exists(desktop_path):
                    contents = list_directory_full(desktop_path)
                    result = f"Found {len(contents)} items on your desktop:\n" + "\n".join(contents[:15])
                    if len(contents) > 15:
                        result += f"\n... and {len(contents) - 15} more items"
                    self.add_to_ops_log("Desktop scan completed")
                    self.add_to_chat(result, "loth")
                else:
                    self.add_to_ops_log("Desktop directory not found")
                    self.add_to_chat("Your desktop seems to be hiding from me... 🤔", "loth")
            
            # List current directory
            elif "list" in user_lower and ("here" in user_lower or "current" in user_lower or "this" in user_lower):
                contents = list_directory_full(".")
                result = f"Current directory has {len(contents)} items:\n" + "\n".join(contents[:15])
                if len(contents) > 15:
                    result += f"\n... and {len(contents) - 15} more items"
                self.add_to_ops_log("Directory listing completed")
                self.add_to_chat(result, "loth")
            
            # Read specific file
            elif "read" in user_lower and any(ext in user_lower for ext in [".txt", ".md", ".py", ".js", ".html", ".css"]):
                for ext in [".txt", ".md", ".py", ".js", ".html", ".css"]:
                    if ext in user_lower:
                        for file in os.listdir("."):
                            if file.endswith(ext):
                                try:
                                    content = read_file_full(file)
                                    result = f"Here's what's in {file}:\n{content[:800]}"
                                    if len(content) > 800:
                                        result += "\n... (truncated for your sanity)"
                                    self.add_to_ops_log(f"Read file: {file}")
                                    self.add_to_chat(result, "loth")
                                    return
                                except:
                                    continue
                self.add_to_ops_log("No readable files found")
                self.add_to_chat("No files worth reading here... *shrugs*", "loth")
            
            # Search for files
            elif "search" in user_lower or "find" in user_lower:
                pattern = ".*"
                if "txt" in user_lower:
                    pattern = ".*\\.txt$"
                elif "py" in user_lower:
                    pattern = ".*\\.py$"
                elif "jpg" in user_lower or "png" in user_lower:
                    pattern = ".*\\.(jpg|jpeg|png)$"
                
                matches = search_files_full(".", pattern)
                if matches:
                    result = f"Found {len(matches)} files matching your criteria:\n" + "\n".join(matches[:10])
                    if len(matches) > 10:
                        result += f"\n... and {len(matches) - 10} more files"
                    self.add_to_ops_log(f"Search completed: {len(matches)} matches")
                    self.add_to_chat(result, "loth")
                else:
                    self.add_to_ops_log("Search completed: no matches")
                    self.add_to_chat("Nothing found. Maybe try a different search term? 🤷‍♀️", "loth")
            
            else:
                self.add_to_ops_log("No specific file operations detected")
            
            self.add_to_ops_log(random.choice(LOTH_RESPONSES["success"]))
            
        except Exception as e:
            self.add_to_ops_log(f"Operation failed: {e}")
            self.add_to_chat(random.choice(LOTH_RESPONSES["error"]), "loth")

if __name__ == "__main__":
    app = LothAIAssistant()
    app.mainloop()
