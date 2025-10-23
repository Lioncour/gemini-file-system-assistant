import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import time
import sys
from PIL import Image, ImageTk
import io
import base64

class FloKrollAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FloKroll AI Assistant - Professional Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # API Configuration
        self.api_key = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"
        self.server_running = True  # Always true since we use direct operations
        
        # Show startup message
        self.show_startup_message()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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
                text="Initializing file operations...", 
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
                                  text="Professional File System Operations with Google Gemini AI", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=1)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, 
                                     text="✅ Ready for file operations", 
                                     style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - AI Chat
        left_panel = tk.Frame(content_frame, bg='#1a1a1a')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # AI Chat section
        chat_frame = tk.LabelFrame(left_panel, 
                                  text="💬 AI Chat", 
                                  bg='#1a1a1a', 
                                  fg='#ffffff',
                                  font=('Segoe UI', 11, 'bold'),
                                  relief=tk.RAISED,
                                  bd=2)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, 
                                                     bg='#2d2d2d', 
                                                     fg='#ffffff',
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD,
                                                     state=tk.DISABLED,
                                                     height=15)
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
        self.chat_input.bind('<Control-Return>', lambda e: self.send_message())
        
        # Right panel - File Operations
        right_panel = tk.Frame(content_frame, bg='#1a1a1a')
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # File Operations section
        file_frame = tk.LabelFrame(right_panel, 
                                  text="📁 File Operations", 
                                  bg='#1a1a1a', 
                                  fg='#ffffff',
                                  font=('Segoe UI', 11, 'bold'),
                                  relief=tk.RAISED,
                                  bd=2)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File operation buttons
        self.read_button = ttk.Button(file_frame, 
                                     text="📖 Read File", 
                                     command=self.read_file_dialog,
                                     style='File.TButton')
        self.read_button.pack(fill=tk.X, padx=10, pady=5)
        
        self.write_button = ttk.Button(file_frame, 
                                      text="✏️ Write File", 
                                      command=self.write_file_dialog,
                                      style='File.TButton')
        self.write_button.pack(fill=tk.X, padx=10, pady=5)
        
        self.list_button = ttk.Button(file_frame, 
                                     text="📋 List Directory", 
                                     command=self.list_directory_dialog,
                                     style='File.TButton')
        self.list_button.pack(fill=tk.X, padx=10, pady=5)
        
        # Quick Actions section
        quick_frame = tk.LabelFrame(right_panel, 
                                   text="⚡ Quick Actions", 
                                   bg='#1a1a1a', 
                                   fg='#ffffff',
                                   font=('Segoe UI', 11, 'bold'),
                                   relief=tk.RAISED,
                                   bd=2)
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.quick_read_button = ttk.Button(quick_frame, 
                                           text="📄 Read README", 
                                           command=self.quick_read_readme,
                                           style='File.TButton')
        self.quick_read_button.pack(fill=tk.X, padx=10, pady=5)
        
        self.quick_list_button = ttk.Button(quick_frame, 
                                           text="📂 List Current Dir", 
                                           command=self.quick_list_current,
                                           style='File.TButton')
        self.quick_list_button.pack(fill=tk.X, padx=10, pady=5)
        
        # Add welcome message
        self.add_to_chat("🤖 Welcome to FloKroll AI Assistant!", "system")
        self.add_to_chat("I can help you with file operations directly!", "system")
        self.add_to_chat("Use the buttons on the right or ask me to help with files.", "system")
    
    def add_to_chat(self, message, sender="user"):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "system":
            self.chat_display.insert(tk.END, f"🤖 {message}\n\n", "system")
        elif sender == "ai":
            self.chat_display.insert(tk.END, f"🤖 AI: {message}\n\n", "ai")
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
        
        # Process message in a separate thread
        threading.Thread(target=self.process_ai_message, args=(message,), daemon=True).start()
    
    def process_ai_message(self, message):
        """Process the AI message (simplified for demo)"""
        try:
            # For now, we'll do a simple keyword-based response
            # In a full implementation, this would call the Gemini API
            
            if "read" in message.lower() and "file" in message.lower():
                self.add_to_chat("I can help you read files! Use the 'Read File' button on the right, or tell me the specific file path.", "ai")
            elif "write" in message.lower() and "file" in message.lower():
                self.add_to_chat("I can help you write files! Use the 'Write File' button on the right, or tell me what you want to write and where.", "ai")
            elif "list" in message.lower() and "directory" in message.lower():
                self.add_to_chat("I can help you list directory contents! Use the 'List Directory' button on the right, or tell me which directory to list.", "ai")
            else:
                self.add_to_chat("I understand you want help with file operations. You can use the buttons on the right for specific operations, or describe what you need in more detail!", "ai")
                
        except Exception as e:
            self.add_to_chat(f"Sorry, I encountered an error: {str(e)}", "ai")
    
    def read_file_dialog(self):
        """Open file dialog to read a file"""
        file_path = filedialog.askopenfilename(
            title="Select file to read",
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.read_file(file_path)
    
    def read_file(self, file_path):
        """Read a file directly"""
        try:
            # Make relative to current directory
            rel_path = os.path.relpath(file_path, os.getcwd())
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.add_to_chat(f"📖 File content from {rel_path}:\n\n{content}", "ai")
                
        except Exception as e:
            self.add_to_chat(f"❌ Error reading file: {str(e)}", "ai")
    
    def write_file_dialog(self):
        """Open dialog to write a file"""
        # Simple dialog for file writing
        dialog = tk.Toplevel(self.root)
        dialog.title("Write File")
        dialog.geometry("500x400")
        dialog.configure(bg='#1a1a1a')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # File path input
        tk.Label(dialog, text="File path:", bg='#1a1a1a', fg='#ffffff').pack(anchor=tk.W, padx=10, pady=(10, 5))
        path_entry = tk.Entry(dialog, width=50, bg='#2d2d2d', fg='#ffffff')
        path_entry.pack(padx=10, pady=(0, 10))
        
        # Content input
        tk.Label(dialog, text="File content:", bg='#1a1a1a', fg='#ffffff').pack(anchor=tk.W, padx=10, pady=(0, 5))
        content_text = scrolledtext.ScrolledText(dialog, height=15, bg='#2d2d2d', fg='#ffffff')
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def write_file():
            file_path = path_entry.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not file_path or not content:
                messagebox.showerror("Error", "Please provide both file path and content.")
                return
            
            self.write_file(file_path, content)
            dialog.destroy()
        
        ttk.Button(button_frame, text="Write File", command=write_file, style='Custom.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, style='File.TButton').pack(side=tk.RIGHT)
    
    def write_file(self, file_path, content):
        """Write a file directly"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.add_to_chat(f"✅ Successfully wrote to {file_path}", "ai")
                
        except Exception as e:
            self.add_to_chat(f"❌ Error writing file: {str(e)}", "ai")
    
    def list_directory_dialog(self):
        """Open dialog to list directory contents"""
        directory = filedialog.askdirectory(
            title="Select directory to list",
            initialdir=os.getcwd()
        )
        
        if directory:
            self.list_directory(directory)
    
    def list_directory(self, directory):
        """List directory contents directly"""
        try:
            # Make relative to current directory
            rel_path = os.path.relpath(directory, os.getcwd())
            
            files = os.listdir(directory)
            file_list = "\n".join(f"📄 {f}" for f in files)
            self.add_to_chat(f"📁 Directory contents of {rel_path}:\n\n{file_list}", "ai")
                
        except Exception as e:
            self.add_to_chat(f"❌ Error listing directory: {str(e)}", "ai")
    
    def quick_read_readme(self):
        """Quick action to read README file"""
        readme_files = ['README.md', 'readme.txt', 'README.txt', 'readme.md']
        
        for readme in readme_files:
            if os.path.exists(readme):
                self.read_file(readme)
                return
        
        self.add_to_chat("❌ No README file found in current directory", "ai")
    
    def quick_list_current(self):
        """Quick action to list current directory"""
        self.list_directory(os.getcwd())
    
    def on_closing(self):
        """Handle window closing"""
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FloKrollAIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

