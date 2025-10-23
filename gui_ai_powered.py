import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import time
import sys
from PIL import Image, ImageTk
import io
import base64
import google.generativeai as genai
import json

class FloKrollAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FloKroll AI Assistant - Professional Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # API Configuration
        self.api_key = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"
        self.model = None
        self.chat_session = None
        
        # Initialize Gemini AI
        self.initialize_ai()
        
        # Show startup message
        self.show_startup_message()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def initialize_ai(self):
        """Initialize the Gemini AI model"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            print(f"AI initialization error: {e}")
            self.model = None
    
    def show_startup_message(self):
        """Show startup message while initializing"""
        startup_window = tk.Toplevel(self.root)
        startup_window.title("FloKroll AI Assistant - Starting...")
        startup_window.geometry("400x200")
        startup_window.configure(bg='#1a1a1a')
        startup_window.transient(self.root)
        startup_window.grab_set()
        
        # Center the window
        startup_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 300,
            self.root.winfo_rooty() + 200
        ))
        
        # Startup message
        tk.Label(startup_window, 
                text="🤖 FloKroll AI Assistant", 
                bg='#1a1a1a', 
                fg='#00ff88', 
                font=('Segoe UI', 16, 'bold')).pack(pady=20)
        
        tk.Label(startup_window, 
                text="Initializing AI...", 
                bg='#1a1a1a', 
                fg='#ffffff', 
                font=('Segoe UI', 12)).pack(pady=10)
        
        tk.Label(startup_window, 
                text="Ready to help with your files!", 
                bg='#1a1a1a', 
                fg='#cccccc', 
                font=('Segoe UI', 10)).pack(pady=5)
        
        # Progress bar
        progress = ttk.Progressbar(startup_window, mode='indeterminate')
        progress.pack(pady=20, padx=20, fill=tk.X)
        progress.start()
        
        # Close startup window after 2 seconds
        self.root.after(2000, startup_window.destroy)
    
    def setup_styles(self):
        """Configure the modern dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#1a1a1a', 
                       foreground='#00ff88', 
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Subtitle.TLabel', 
                       background='#1a1a1a', 
                       foreground='#ffffff', 
                       font=('Segoe UI', 10))
        
        style.configure('Status.TLabel', 
                       background='#1a1a1a', 
                       foreground='#00ff88', 
                       font=('Segoe UI', 9, 'bold'))
        
        style.configure('Custom.TButton',
                       background='#00ff88',
                       foreground='#1a1a1a',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Custom.TButton',
                 background=[('active', '#00cc6a')])
        
        style.configure('File.TButton',
                       background='#2d2d2d',
                       foreground='#ffffff',
                       font=('Segoe UI', 9),
                       borderwidth=1)
        
        style.map('File.TButton',
                 background=[('active', '#404040')])
    
    def create_widgets(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#1a1a1a')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🤖 FloKroll AI Assistant", 
                               style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                  text="AI-Powered File System Operations with Google Gemini", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, 
                                     text="✅ AI Ready - Just talk to me!", 
                                     style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # AI Chat section (full width)
        chat_frame = tk.LabelFrame(content_frame, 
                                  text="💬 Talk to FloKroll AI", 
                                  bg='#1a1a1a', 
                                  fg='#ffffff',
                                  font=('Segoe UI', 11, 'bold'),
                                  relief=tk.RAISED,
                                  bd=2)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, 
                                                     bg='#2d2d2d', 
                                                     fg='#ffffff',
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD,
                                                     state=tk.DISABLED,
                                                     height=20)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat input
        input_frame = tk.Frame(chat_frame, bg='#1a1a1a')
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.chat_input = tk.Text(input_frame, 
                                 bg='#2d2d2d', 
                                 fg='#ffffff',
                                 font=('Segoe UI', 10),
                                 height=3,
                                 wrap=tk.WORD)
        self.chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.send_button = ttk.Button(input_frame, 
                                     text="Send", 
                                     command=self.send_message,
                                     style='Custom.TButton')
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.chat_input.bind('<Return>', lambda e: self.send_message())
        self.chat_input.bind('<Control-Return>', lambda e: self.add_new_line())
        
        # Add welcome message
        self.add_to_chat("🤖 Hello! I'm FloKroll AI Assistant!", "ai")
        self.add_to_chat("I can help you with file operations using natural language.", "ai")
        self.add_to_chat("Just tell me what you want to do with your files!", "ai")
        self.add_to_chat("Examples:", "ai")
        self.add_to_chat("• 'Read the README file'", "ai")
        self.add_to_chat("• 'List all files in this directory'", "ai")
        self.add_to_chat("• 'Create a new file called notes.txt with some content'", "ai")
        self.add_to_chat("• 'Show me what's in the src folder'", "ai")
    
    def add_to_chat(self, message, sender="user"):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "ai":
            self.chat_display.insert(tk.END, f"🤖 FloKroll AI: {message}\n\n", "ai")
        else:
            self.chat_display.insert(tk.END, f"👤 You: {message}\n\n", "user")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
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
        """Process the AI message with actual Gemini AI"""
        try:
            if not self.model:
                self.add_to_chat("❌ AI is not initialized. Please restart the application.", "ai")
                return
            
            # Create a system prompt for file operations
            system_prompt = f"""You are FloKroll AI Assistant, a helpful AI that can perform file operations. 
            You can read files, write files, and list directories. 
            Current working directory: {os.getcwd()}
            
            When the user asks you to do file operations, you should:
            1. Understand what they want to do
            2. Perform the actual file operation
            3. Report back the results
            
            Available operations:
            - Read files: I can read any file in the current directory or subdirectories
            - Write files: I can create or modify files
            - List directories: I can show contents of directories
            
            Always be helpful and explain what you're doing. If you need to perform a file operation, 
            tell the user what you're going to do first, then do it."""
            
            # Send message to Gemini
            full_message = f"{system_prompt}\n\nUser request: {message}"
            response = self.chat_session.send_message(full_message)
            
            # Get AI response
            ai_response = response.text
            
            # Check if the AI wants to perform file operations
            if any(keyword in message.lower() for keyword in ['read', 'write', 'create', 'list', 'show', 'file', 'directory', 'folder']):
                # Perform the actual file operation
                result = self.perform_file_operation(message)
                if result:
                    ai_response += f"\n\n{result}"
            
            self.add_to_chat(ai_response, "ai")
                
        except Exception as e:
            self.add_to_chat(f"Sorry, I encountered an error: {str(e)}", "ai")
    
    def perform_file_operation(self, message):
        """Perform actual file operations based on the message"""
        try:
            message_lower = message.lower()
            
            # Read file operations
            if any(word in message_lower for word in ['read', 'show', 'display', 'open']):
                if 'readme' in message_lower:
                    return self.read_file('README.md')
                elif 'file' in message_lower:
                    # Try to extract filename from message
                    words = message.split()
                    for i, word in enumerate(words):
                        if word.lower() in ['read', 'show', 'display', 'open'] and i + 1 < len(words):
                            filename = words[i + 1]
                            if '.' in filename:  # Likely a filename
                                return self.read_file(filename)
                else:
                    # List current directory
                    return self.list_directory('.')
            
            # List directory operations
            elif any(word in message_lower for word in ['list', 'show', 'what', 'files', 'directory', 'folder']):
                if 'current' in message_lower or 'this' in message_lower:
                    return self.list_directory('.')
                else:
                    # Try to extract directory name
                    words = message.split()
                    for i, word in enumerate(words):
                        if word.lower() in ['list', 'show', 'what'] and i + 1 < len(words):
                            dirname = words[i + 1]
                            return self.list_directory(dirname)
                    return self.list_directory('.')
            
            # Write file operations
            elif any(word in message_lower for word in ['write', 'create', 'make', 'save']):
                if 'file' in message_lower:
                    # This is a simplified version - in a real implementation,
                    # you'd want to extract filename and content from the message
                    return "I can help you create files! Please be more specific about the filename and content you want to write."
            
            return None
            
        except Exception as e:
            return f"Error performing file operation: {str(e)}"
    
    def read_file(self, filename):
        """Read a file and return its content"""
        try:
            if not os.path.exists(filename):
                return f"❌ File '{filename}' not found."
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"📖 Content of '{filename}':\n\n{content}"
            
        except Exception as e:
            return f"❌ Error reading file '{filename}': {str(e)}"
    
    def list_directory(self, directory):
        """List directory contents"""
        try:
            if not os.path.exists(directory):
                return f"❌ Directory '{directory}' not found."
            
            files = os.listdir(directory)
            if not files:
                return f"📁 Directory '{directory}' is empty."
            
            file_list = "\n".join(f"📄 {f}" for f in files)
            return f"📁 Contents of '{directory}':\n\n{file_list}"
            
        except Exception as e:
            return f"❌ Error listing directory '{directory}': {str(e)}"
    
    def on_closing(self):
        """Handle window closing"""
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FloKrollAIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
