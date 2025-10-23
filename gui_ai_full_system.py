#!/usr/bin/env python3
"""
FloKroll AI Full System Assistant - Complete file system access with AI
"""
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, simpledialog
import os
import shutil
import google.generativeai as genai
import threading
import time
import re
from pathlib import Path

# --- Configuration ---
API_KEY = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"  # Hardcoded API key

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Initialize the Gemini model with tools
model = genai.GenerativeModel('models/gemini-2.5-flash')
chat = model.start_chat(history=[])

# --- Enhanced File System Operations ---
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

# --- GUI Application ---
class FloKrollAIFullSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FloKroll AI Full System Assistant")
        self.geometry("1200x800")
        self.configure(bg="#2e2e2e")  # Dark background

        # Load and set icon
        try:
            self.iconbitmap("ai_assistant_icon.ico")
        except tk.TclError:
            print("Warning: Icon file 'ai_assistant_icon.ico' not found. Running without icon.")

        self._create_widgets()
        self._setup_layout()
        self.update_status("Ready! I can now access ALL files on your computer!")

    def _create_widgets(self):
        # --- Styles ---
        self.option_add("*Font", "SegoeUI 10")
        self.option_add("*Background", "#2e2e2e")
        self.option_add("*Foreground", "#ffffff")
        self.option_add("*Button.Background", "#005f5f")
        self.option_add("*Button.Foreground", "#ffffff")
        self.option_add("*Button.Relief", "flat")
        self.option_add("*Button.Borderwidth", "0")
        self.option_add("*Button.HighlightBackground", "#00ff88")  # FloKroll green
        self.option_add("*Button.HighlightColor", "#00ff88")
        self.option_add("*TEntry.Fieldbackground", "#4a4a4a")
        self.option_add("*TEntry.Foreground", "#ffffff")
        self.option_add("*TEntry.Borderwidth", "0")
        self.option_add("*TEntry.Relief", "flat")
        self.option_add("*TText.Background", "#4a4a4a")
        self.option_add("*TText.Foreground", "#ffffff")
        self.option_add("*TText.Borderwidth", "0")
        self.option_add("*TText.Relief", "flat")

        # --- Main Frames ---
        self.main_frame = tk.Frame(self, bg="#2e2e2e")
        self.chat_frame = tk.Frame(self.main_frame, bg="#2e2e2e", bd=2, relief="groove")
        self.controls_frame = tk.Frame(self.main_frame, bg="#2e2e2e", bd=2, relief="groove")

        # --- Chat Panel ---
        self.chat_history = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled', 
                                                     bg="#4a4a4a", fg="#ffffff", insertbackground="#00ff88")
        self.chat_input = tk.Text(self.chat_frame, height=3, bg="#4a4a4a", fg="#ffffff", insertbackground="#00ff88")
        self.send_button = tk.Button(self.chat_frame, text="Send (Enter)", command=self.send_message, 
                                   bg="#00ff88", fg="#2e2e2e")

        # --- Controls Panel ---
        self.status_label = tk.Label(self.controls_frame, text="Status: Initializing...", 
                                   bg="#2e2e2e", fg="#00ff88")
        self.current_dir_label = tk.Label(self.controls_frame, text=f"Current Directory: {os.getcwd()}", 
                                        bg="#2e2e2e", fg="#ffffff", wraplength=300)

        # File Operations Buttons
        self.read_button = tk.Button(self.controls_frame, text="📖 Read File", command=self.open_read_dialog, bg="#005f5f")
        self.write_button = tk.Button(self.controls_frame, text="✏️ Write File", command=self.open_write_dialog, bg="#005f5f")
        self.list_button = tk.Button(self.controls_frame, text="📋 List Directory", command=self.open_list_dialog, bg="#005f5f")
        self.move_button = tk.Button(self.controls_frame, text="📁 Move File", command=self.open_move_dialog, bg="#005f5f")
        self.copy_button = tk.Button(self.controls_frame, text="📋 Copy File", command=self.open_copy_dialog, bg="#005f5f")
        self.delete_button = tk.Button(self.controls_frame, text="🗑️ Delete File", command=self.open_delete_dialog, bg="#FF4444")
        self.rename_button = tk.Button(self.controls_frame, text="✏️ Rename File", command=self.open_rename_dialog, bg="#005f5f")
        self.search_button = tk.Button(self.controls_frame, text="🔍 Search Files", command=self.open_search_dialog, bg="#005f5f")

        # --- Bindings ---
        self.chat_input.bind('<Return>', self.send_message)
        self.chat_input.bind('<Control-Return>', self.add_new_line)

    def _setup_layout(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Chat Panel Layout
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_input.pack(padx=10, pady=(0, 5), fill=tk.X)
        self.send_button.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Controls Panel Layout
        self.status_label.pack(pady=(10, 5))
        self.current_dir_label.pack(pady=(0, 10))
        tk.Label(self.controls_frame, text="File Operations:", bg="#2e2e2e", fg="#00ff88").pack(pady=(10, 5))
        self.read_button.pack(fill=tk.X, padx=10, pady=2)
        self.write_button.pack(fill=tk.X, padx=10, pady=2)
        self.list_button.pack(fill=tk.X, padx=10, pady=2)
        self.move_button.pack(fill=tk.X, padx=10, pady=2)
        self.copy_button.pack(fill=tk.X, padx=10, pady=2)
        self.rename_button.pack(fill=tk.X, padx=10, pady=2)
        self.search_button.pack(fill=tk.X, padx=10, pady=2)
        self.delete_button.pack(fill=tk.X, padx=10, pady=2)

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
            if not model:
                self.add_to_chat("AI model not initialized. Please restart the application.")
                return

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

Respond with helpful guidance and suggest specific file operations.
"""

            response = chat.send_message(enhanced_prompt)
            ai_response = response.text if response.text else "I'm here to help with your files!"
            
            self.add_to_chat(ai_response, "ai")
            self.update_status("Ready for more commands!")

        except Exception as e:
            self.add_to_chat(f"Sorry, I encountered an error: {e}", "ai")
            self.update_status("Error during AI processing", "#FF6347")

    # --- Enhanced File Operation Dialogs ---
    def open_read_dialog(self):
        filepath = filedialog.askopenfilename(title="Select file to read")
        if filepath:
            self.read_file_gui(filepath)

    def read_file_gui(self, filepath):
        threading.Thread(target=self._read_file_thread, args=(filepath,)).start()

    def _read_file_thread(self, filepath):
        try:
            content = read_file_full(filepath)
            self.after(0, lambda: self._show_file_content_dialog(filepath, content))
            self.update_status(f"Successfully read {filepath}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Reading File", str(e)))
            self.update_status(f"Error reading {filepath}", "#FF6347")

    def _show_file_content_dialog(self, filepath, content):
        dialog = tk.Toplevel(self)
        dialog.title(f"Content of {os.path.basename(filepath)}")
        dialog.geometry("800x600")
        dialog.configure(bg="#2e2e2e")

        text_area = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, bg="#4a4a4a", fg="#ffffff", insertbackground="#00ff88")
        text_area.insert(tk.END, content)
        text_area.config(state='disabled')
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        close_button = tk.Button(dialog, text="Close", command=dialog.destroy, bg="#005f5f", fg="#ffffff")
        close_button.pack(pady=5)

    def open_write_dialog(self):
        filepath = filedialog.asksaveasfilename(title="Save file as")
        if filepath:
            self._show_write_dialog(filepath)

    def _show_write_dialog(self, filepath):
        dialog = tk.Toplevel(self)
        dialog.title(f"Write to {os.path.basename(filepath)}")
        dialog.geometry("800x600")
        dialog.configure(bg="#2e2e2e")

        content_label = tk.Label(dialog, text="Enter content:", bg="#2e2e2e", fg="#ffffff")
        content_label.pack(pady=(10, 0))

        text_area = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, bg="#4a4a4a", fg="#ffffff", insertbackground="#00ff88")
        text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        def save_content():
            content = text_area.get(1.0, tk.END).strip()
            threading.Thread(target=self._write_file_thread, args=(filepath, content, dialog)).start()

        save_button = tk.Button(dialog, text="Save", command=save_content, bg="#00ff88", fg="#2e2e2e")
        save_button.pack(side=tk.LEFT, padx=10, pady=5)
        cancel_button = tk.Button(dialog, text="Cancel", command=dialog.destroy, bg="#005f5f", fg="#ffffff")
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=5)

    def _write_file_thread(self, filepath, content, dialog):
        try:
            result = write_file_full(filepath, content)
            self.after(0, lambda: messagebox.showinfo("Success", result))
            self.after(0, dialog.destroy)
            self.update_status(f"Successfully wrote to {filepath}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Writing File", str(e)))
            self.update_status(f"Error writing to {filepath}", "#FF6347")

    def open_list_dialog(self):
        dirpath = filedialog.askdirectory(title="Select directory to list")
        if dirpath:
            self.list_directory_gui(dirpath)

    def list_directory_gui(self, dirpath):
        threading.Thread(target=self._list_directory_thread, args=(dirpath,)).start()

    def _list_directory_thread(self, dirpath):
        try:
            contents = list_directory_full(dirpath)
            self.after(0, lambda: self._show_directory_contents_dialog(dirpath, contents))
            self.update_status(f"Successfully listed {dirpath}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Listing Directory", str(e)))
            self.update_status(f"Error listing {dirpath}", "#FF6347")

    def _show_directory_contents_dialog(self, dirpath, contents):
        dialog = tk.Toplevel(self)
        dialog.title(f"Contents of {os.path.basename(dirpath)}")
        dialog.geometry("800x600")
        dialog.configure(bg="#2e2e2e")

        list_box = tk.Listbox(dialog, bg="#4a4a4a", fg="#ffffff", selectbackground="#00ff88", selectforeground="#2e2e2e")
        for item in contents:
            list_box.insert(tk.END, item)
        list_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        close_button = tk.Button(dialog, text="Close", command=dialog.destroy, bg="#005f5f", fg="#ffffff")
        close_button.pack(pady=5)

    def open_move_dialog(self):
        source = filedialog.askopenfilename(title="Select file to move")
        if source:
            destination = filedialog.asksaveasfilename(title="Select destination", initialvalue=os.path.basename(source))
            if destination:
                self.move_file_gui(source, destination)

    def move_file_gui(self, source, destination):
        threading.Thread(target=self._move_file_thread, args=(source, destination,)).start()

    def _move_file_thread(self, source, destination):
        try:
            result = move_file_full(source, destination)
            self.after(0, lambda: messagebox.showinfo("Success", result))
            self.update_status(f"Successfully moved {source}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Moving File", str(e)))
            self.update_status(f"Error moving {source}", "#FF6347")

    def open_copy_dialog(self):
        source = filedialog.askopenfilename(title="Select file to copy")
        if source:
            destination = filedialog.asksaveasfilename(title="Select destination", initialvalue=os.path.basename(source))
            if destination:
                self.copy_file_gui(source, destination)

    def copy_file_gui(self, source, destination):
        threading.Thread(target=self._copy_file_thread, args=(source, destination,)).start()

    def _copy_file_thread(self, source, destination):
        try:
            result = copy_file_full(source, destination)
            self.after(0, lambda: messagebox.showinfo("Success", result))
            self.update_status(f"Successfully copied {source}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Copying File", str(e)))
            self.update_status(f"Error copying {source}", "#FF6347")

    def open_delete_dialog(self):
        filepath = filedialog.askopenfilename(title="Select file to delete")
        if filepath:
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{filepath}\n\nThis action cannot be undone!"):
                self.delete_file_gui(filepath)

    def delete_file_gui(self, filepath):
        threading.Thread(target=self._delete_file_thread, args=(filepath,)).start()

    def _delete_file_thread(self, filepath):
        try:
            result = delete_file_full(filepath)
            self.after(0, lambda: messagebox.showinfo("Success", result))
            self.update_status(f"Successfully deleted {filepath}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Deleting File", str(e)))
            self.update_status(f"Error deleting {filepath}", "#FF6347")

    def open_rename_dialog(self):
        old_path = filedialog.askopenfilename(title="Select file to rename")
        if old_path:
            new_name = tk.simpledialog.askstring("Rename File", f"Enter new name for {os.path.basename(old_path)}:", initialvalue=os.path.basename(old_path))
            if new_name:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                self.rename_file_gui(old_path, new_path)

    def rename_file_gui(self, old_path, new_path):
        threading.Thread(target=self._rename_file_thread, args=(old_path, new_path,)).start()

    def _rename_file_thread(self, old_path, new_path):
        try:
            result = rename_file_full(old_path, new_path)
            self.after(0, lambda: messagebox.showinfo("Success", result))
            self.update_status(f"Successfully renamed {old_path}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Renaming File", str(e)))
            self.update_status(f"Error renaming {old_path}", "#FF6347")

    def open_search_dialog(self):
        directory = filedialog.askdirectory(title="Select directory to search in")
        if directory:
            pattern = tk.simpledialog.askstring("Search Files", "Enter search pattern (e.g., *.txt, test*):")
            if pattern:
                self.search_files_gui(directory, pattern)

    def search_files_gui(self, directory, pattern):
        threading.Thread(target=self._search_files_thread, args=(directory, pattern,)).start()

    def _search_files_thread(self, directory, pattern):
        try:
            matches = search_files_full(directory, pattern)
            self.after(0, lambda: self._show_search_results_dialog(directory, pattern, matches))
            self.update_status(f"Found {len(matches)} matches in {directory}", "#00ff88")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Searching Files", str(e)))
            self.update_status(f"Error searching in {directory}", "#FF6347")

    def _show_search_results_dialog(self, directory, pattern, matches):
        dialog = tk.Toplevel(self)
        dialog.title(f"Search Results for '{pattern}' in {os.path.basename(directory)}")
        dialog.geometry("800x600")
        dialog.configure(bg="#2e2e2e")

        if matches:
            list_box = tk.Listbox(dialog, bg="#4a4a4a", fg="#ffffff", selectbackground="#00ff88", selectforeground="#2e2e2e")
            for match in matches:
                list_box.insert(tk.END, match)
            list_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        else:
            no_results = tk.Label(dialog, text=f"No files found matching '{pattern}'", bg="#2e2e2e", fg="#ffffff")
            no_results.pack(padx=10, pady=10)

        close_button = tk.Button(dialog, text="Close", command=dialog.destroy, bg="#005f5f", fg="#ffffff")
        close_button.pack(pady=5)

if __name__ == "__main__":
    app = FloKrollAIFullSystem()
    app.mainloop()
