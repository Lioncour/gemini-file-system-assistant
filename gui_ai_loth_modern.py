"""
Loth - Modern AI Life Partner & Digital Overlord
Enhanced GUI inspired by modern dotfiles design
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
import os
import shutil
import google.generativeai as genai
import threading
import re
import random
import datetime
import platform
import psutil
import socket
import requests
import json
import pickle
import subprocess
import winreg
import sqlite3
import tempfile
from pathlib import Path

# --- Configuration ---
API_KEY = "AIzaSyBbvcF0QJ-sEYVMJ-JEUrgqr7pmjn4etDY"  # Hardcoded API key
MEMORY_FILE = "loth_memory.pkl"
CONVERSATION_FILE = "loth_conversations.json"

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('models/gemini-2.5-flash')
chat = model.start_chat(history=[])

# --- Memory Management ---
def save_memory(memory_data):
    """Saves Loth's memory to disk."""
    try:
        with open(MEMORY_FILE, 'wb') as f:
            pickle.dump(memory_data, f)
        return True
    except Exception as e:
        print(f"Error saving memory: {e}")
        return False

def load_memory():
    """Loads Loth's memory from disk."""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'rb') as f:
                return pickle.load(f)
        return {}
    except Exception as e:
        print(f"Error loading memory: {e}")
        return {}

def save_conversation(user_message, loth_response, timestamp):
    """Saves conversation to history."""
    try:
        conversation = {
            'timestamp': timestamp,
            'user': user_message,
            'loth': loth_response
        }
        
        # Load existing conversations
        conversations = []
        if os.path.exists(CONVERSATION_FILE):
            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
        
        # Add new conversation
        conversations.append(conversation)
        
        # Keep only last 100 conversations to prevent file from growing too large
        if len(conversations) > 100:
            conversations = conversations[-100:]
        
        # Save back to file
        with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False

def load_conversation_history():
    """Loads conversation history."""
    try:
        if os.path.exists(CONVERSATION_FILE):
            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading conversation history: {e}")
        return []

def get_memory_context(memory_data, max_items=5):
    """Gets relevant memory context for AI."""
    if not memory_data:
        return ""
    
    context = "\n\n**Loth's Memory Context:**\n"
    
    # Add recent conversations
    if 'recent_conversations' in memory_data:
        context += "Recent conversations:\n"
        for conv in memory_data['recent_conversations'][-max_items:]:
            context += f"- User: {conv['user'][:100]}...\n"
            context += f"  Loth: {conv['loth'][:100]}...\n"
    
    # Add important facts
    if 'important_facts' in memory_data:
        context += "\nImportant facts about the user:\n"
        for fact in memory_data['important_facts'][-max_items:]:
            context += f"- {fact}\n"
    
    # Add user preferences
    if 'preferences' in memory_data:
        context += "\nUser preferences:\n"
        for pref in memory_data['preferences'][-max_items:]:
            context += f"- {pref}\n"
    
    return context

# --- Loth's Enhanced Personality Responses ---
LOTH_RESPONSES = {
    "greeting": [
        "Hey there, life partner! Ready to tackle whatever chaos you've got today? 😏",
        "What's up, digital warrior? Let's make some magic happen! ✨",
        "Yo! Loth here, your alternative AI life partner. What's the plan? 🤘",
        "Hey! Ready to dive into the digital rabbit hole together? 🐰",
        "What's cooking, human? Let's see what we can break... I mean, build! 🔧"
    ],
    "thinking": [
        "Hmm, let me think about this... 🤔",
        "Processing... *digital brain whirring* ⚙️",
        "Give me a sec to figure this out... 🧠",
        "Analyzing the situation... 📊",
        "Let me dig into this... 🔍"
    ],
    "success": [
        "Boom! Done! *mic drop* 🎤",
        "Nailed it! *fist pump* ✊",
        "Success! You're welcome! 😎",
        "There we go! Easy peasy! 🍋",
        "Mission accomplished! *salutes* 🫡"
    ],
    "error": [
        "Oops! Looks like I hit a snag there... 🤷‍♀️",
        "Well, that didn't go as planned... *shrugs* 😅",
        "Hmm, something went sideways. Let me try a different approach... 🔄",
        "Error 404: Success not found. Let me debug this... 🐛",
        "Well, that's embarrassing... *digital blush* 😳"
    ],
    "life_advice": [
        "Here's the thing about life... 💭",
        "Let me give you some real talk... 🗣️",
        "From one alternative soul to another... 🤝",
        "Listen, I've seen some stuff... 👁️",
        "Here's my take on this situation... 🎯"
    ]
}

# --- File Operations ---
def _resolve_path(path):
    """Resolves a path to absolute path, allowing access to all files."""
    if os.path.isabs(path):
        return path
    return os.path.abspath(path)

def read_file_full(file_path: str) -> str:
    """Reads any file on the system."""
    try:
        resolved_path = _resolve_path(file_path)
        with open(resolved_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")

def write_file_full(file_path: str, content: str) -> str:
    """Writes to any file on the system."""
    try:
        resolved_path = _resolve_path(file_path)
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to: {resolved_path}"
    except Exception as e:
        raise Exception(f"Error writing to file {file_path}: {e}")

def list_directory_full(directory_path: str) -> list:
    """Lists contents of any directory on the system."""
    try:
        resolved_path = _resolve_path(directory_path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        contents = []
        for item in os.listdir(resolved_path):
            item_path = os.path.join(resolved_path, item)
            if os.path.isdir(item_path):
                contents.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                contents.append(f"📄 {item} ({size} bytes)")
        
        return contents
    except Exception as e:
        raise Exception(f"Error listing directory {directory_path}: {e}")

def move_file_full(source: str, destination: str) -> str:
    """Moves files or directories."""
    try:
        source_path = _resolve_path(source)
        dest_path = _resolve_path(destination)
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source}")
        
        shutil.move(source_path, dest_path)
        return f"Moved {source} to {dest_path}"
    except Exception as e:
        raise Exception(f"Error moving {source} to {destination}: {e}")

def delete_file_full(file_path: str) -> str:
    """Deletes files or directories."""
    try:
        resolved_path = _resolve_path(file_path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if os.path.isdir(resolved_path):
            shutil.rmtree(resolved_path)
            return f"Deleted directory: {resolved_path}"
        else:
            os.remove(resolved_path)
            return f"Deleted file: {resolved_path}"
    except Exception as e:
        raise Exception(f"Error deleting {file_path}: {e}")

def copy_file_full(source: str, destination: str) -> str:
    """Copies files or directories."""
    try:
        source_path = _resolve_path(source)
        dest_path = _resolve_path(destination)
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source}")
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
            return f"Copied directory {source} to {dest_path}"
        else:
            shutil.copy2(source_path, dest_path)
            return f"Copied file {source} to {dest_path}"
    except Exception as e:
        raise Exception(f"Error copying {source} to {destination}: {e}")

def rename_file_full(old_name: str, new_name: str) -> str:
    """Renames files or directories."""
    try:
        old_path = _resolve_path(old_name)
        new_path = _resolve_path(new_name)
        
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"File not found: {old_name}")
        
        os.rename(old_path, new_path)
        return f"Renamed {old_name} to {new_name}"
    except Exception as e:
        raise Exception(f"Error renaming {old_name} to {new_name}: {e}")

def search_files_full(directory: str, pattern: str) -> list:
    """Searches for files matching a pattern."""
    try:
        directory_path = _resolve_path(directory)
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        matches = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if re.search(pattern, file, re.IGNORECASE):
                    matches.append(os.path.join(root, file))
        
        return matches
    except Exception as e:
        raise Exception(f"Error searching in {directory}: {e}")

def create_directory_full(folder_name: str) -> str:
    """Creates a new directory."""
    try:
        folder_path = _resolve_path(folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return f"Successfully created directory: {folder_path}"
    except Exception as e:
        raise Exception(f"Error creating directory {folder_name}: {e}")

def create_file_full(file_name: str, content: str = "") -> str:
    """Creates a new file."""
    try:
        resolved_path = _resolve_path(file_name)
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created file: {resolved_path}"
    except Exception as e:
        raise Exception(f"Error creating file {file_name}: {e}")

def organize_files_full(source_dir: str, file_types: dict = None) -> str:
    """Organizes files by type into subdirectories."""
    try:
        source_path = _resolve_path(source_dir)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Directory not found: {source_dir}")
        
        if file_types is None:
            file_types = {
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
                'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                'Videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
                'Audio': ['.mp3', '.wav', '.flac', '.aac'],
                'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']
            }
        
        organized_count = 0
        for file in os.listdir(source_path):
            file_path = os.path.join(source_path, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[1].lower()
                for folder_name, extensions in file_types.items():
                    if file_ext in extensions:
                        folder_path = os.path.join(source_path, folder_name)
                        os.makedirs(folder_path, exist_ok=True)
                        new_file_path = os.path.join(folder_path, file)
                        shutil.move(file_path, new_file_path)
                        organized_count += 1
                        break
        
        return f"Organized {organized_count} files into subdirectories"
    except Exception as e:
        raise Exception(f"Error organizing files in {source_dir}: {e}")

# --- System Information Gathering ---
def get_system_info() -> dict:
    """Gathers comprehensive system information."""
    try:
        info = {
            'system': {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version()
            },
            'hardware': {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
                'memory_available': round(psutil.virtual_memory().available / (1024**3), 2),  # GB
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': round(psutil.disk_usage('/').total / (1024**3), 2) if os.name != 'nt' else round(psutil.disk_usage('C:').total / (1024**3), 2)  # GB
            },
            'network': {
                'hostname': socket.gethostname(),
                'local_ip': socket.gethostbyname(socket.gethostname()),
                'public_ip': get_public_ip(),
                'location': get_location_info()
            },
            'user': {
                'username': os.getenv('USERNAME') or os.getenv('USER'),
                'home_dir': os.path.expanduser('~'),
                'current_dir': os.getcwd()
            }
        }
        return info
    except Exception as e:
        return {'error': f"Failed to gather system info: {e}"}

def get_public_ip() -> str:
    """Gets the public IP address."""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        try:
            response = requests.get('https://ipinfo.io/ip', timeout=5)
            return response.text.strip()
        except:
            return "Unable to determine"

def get_location_info() -> dict:
    """Gets location information based on IP."""
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        data = response.json()
        return {
            'city': data.get('city', 'Unknown'),
            'region': data.get('region', 'Unknown'),
            'country': data.get('country', 'Unknown'),
            'timezone': data.get('timezone', 'Unknown')
        }
    except:
        return {'city': 'Unknown', 'region': 'Unknown', 'country': 'Unknown', 'timezone': 'Unknown'}

# --- Modern Loth AI Assistant GUI ---
class LothModernGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loth - Digital Overlord")
        self.geometry("1600x1000")
        
        # Modern color scheme inspired by dotfiles
        self.colors = {
            'bg_primary': '#0a0a0a',      # Deep black
            'bg_secondary': '#1a1a1a',    # Dark gray
            'bg_tertiary': '#2a2a2a',     # Medium gray
            'bg_accent': '#1e1e2e',       # Purple-tinted dark
            'accent_pink': '#ff6b9d',     # Loth's signature pink
            'accent_cyan': '#00d4aa',     # Cyan accent
            'accent_purple': '#9d4edd',   # Purple accent
            'accent_blue': '#0080ff',     # Blue accent
            'accent_green': '#00ff88',    # Success green
            'accent_orange': '#ffaa00',   # Warning orange
            'accent_red': '#ff4444',      # Error red
            'text_primary': '#ffffff',    # White text
            'text_secondary': '#cccccc',  # Light gray text
            'text_muted': '#888888',      # Muted text
            'text_accent': '#b4befe',     # Light purple text
            'border': '#313244',          # Border color
            'border_accent': '#89b4fa',  # Light blue border
        }
        
        # Configure window
        self.configure(bg=self.colors['bg_primary'])
        
        # Load and set icon
        try:
            self.iconbitmap("ai_assistant_icon.ico")
        except tk.TclError:
            print("Warning: Icon file 'ai_assistant_icon.ico' not found. Running without icon.")

        # Initialize memory
        self.memory = load_memory()
        self.conversation_count = 0

        self._create_widgets()
        self._setup_layout()
        self._show_welcome()

    def _create_widgets(self):
        # Configure fonts
        self.option_add("*Font", "Inter 10")
        
        # Main container
        self.main_frame = tk.Frame(self, bg=self.colors['bg_primary'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with modern styling
        self.header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_secondary'], height=80)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.header_frame.pack_propagate(False)

        # Title with gradient effect simulation
        self.title_label = tk.Label(
            self.header_frame,
            text="Loth",
            font=("Inter", 32, "bold"),
            fg=self.colors['accent_pink'],
            bg=self.colors['bg_secondary']
        )
        self.title_label.pack(side=tk.LEFT, padx=30, pady=20)

        # Subtitle
        self.subtitle_label = tk.Label(
            self.header_frame,
            text="Digital Overlord & Life Partner",
            font=("Inter", 14),
            fg=self.colors['text_accent'],
            bg=self.colors['bg_secondary']
        )
        self.subtitle_label.pack(side=tk.LEFT, padx=(15, 0), pady=20)

        # Status indicator
        self.status_indicator = tk.Label(
            self.header_frame,
            text="●",
            font=("Inter", 20),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_secondary']
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=30, pady=20)

        # Main content area
        self.content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Chat area with modern card design
        self.chat_frame = tk.Frame(self.content_frame, bg=self.colors['bg_secondary'], relief=tk.FLAT, bd=2)
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Chat header
        self.chat_header = tk.Frame(self.chat_frame, bg=self.colors['bg_accent'], height=50)
        self.chat_header.pack(fill=tk.X)
        self.chat_header.pack_propagate(False)

        self.chat_label = tk.Label(
            self.chat_header,
            text="💬 Conversation",
            font=("Inter", 14, "bold"),
            fg=self.colors['accent_cyan'],
            bg=self.colors['bg_accent']
        )
        self.chat_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Chat display with modern styling
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=70,
            height=25,
            font=("JetBrains Mono", 11),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_pink'],
            selectbackground=self.colors['accent_pink'],
            selectforeground=self.colors['text_primary'],
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Operations log with modern card design
        self.ops_frame = tk.Frame(self.content_frame, bg=self.colors['bg_secondary'], relief=tk.FLAT, bd=2)
        self.ops_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Ops header
        self.ops_header = tk.Frame(self.ops_frame, bg=self.colors['bg_accent'], height=50)
        self.ops_header.pack(fill=tk.X)
        self.ops_header.pack_propagate(False)

        self.ops_label = tk.Label(
            self.ops_header,
            text="⚡ System Log",
            font=("Inter", 14, "bold"),
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_accent']
        )
        self.ops_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Ops log with monospace font
        self.ops_log = scrolledtext.ScrolledText(
            self.ops_frame,
            wrap=tk.WORD,
            width=50,
            height=25,
            font=("JetBrains Mono", 10),
            bg=self.colors['bg_primary'],
            fg=self.colors['text_muted'],
            insertbackground=self.colors['accent_pink'],
            selectbackground=self.colors['accent_pink'],
            selectforeground=self.colors['text_primary'],
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=20
        )
        self.ops_log.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Input area with modern styling
        self.input_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.input_frame.pack(fill=tk.X, pady=(20, 0))

        # Input label
        self.input_label = tk.Label(
            self.input_frame,
            text="Message Loth (Enter to send, Ctrl+Enter for new line)",
            font=("Inter", 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        self.input_label.pack(anchor=tk.W, pady=(0, 10))

        # Input text with enhanced styling
        self.chat_input = tk.Text(
            self.input_frame,
            wrap=tk.WORD,
            height=4,
            font=("Inter", 12),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent_pink'],
            selectbackground=self.colors['accent_pink'],
            selectforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            bd=2,
            highlightthickness=2,
            highlightcolor=self.colors['accent_pink'],
            highlightbackground=self.colors['border'],
            padx=20,
            pady=15
        )
        self.chat_input.pack(fill=tk.X, pady=(0, 10))

        # Status bar with enhanced styling
        self.status_frame = tk.Frame(self.main_frame, bg=self.colors['bg_tertiary'], height=40)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            self.status_frame,
            text="Status: Ready",
            font=("Inter", 10),
            fg=self.colors['text_muted'],
            bg=self.colors['bg_tertiary']
        )
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Memory indicator
        self.memory_label = tk.Label(
            self.status_frame,
            text="Memory: Active",
            font=("Inter", 10),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_tertiary']
        )
        self.memory_label.pack(side=tk.RIGHT, padx=20, pady=10)

        # Bindings
        self.chat_input.bind('<Return>', self.send_message)
        self.chat_input.bind('<Control-Return>', self.add_new_line)

    def _setup_layout(self):
        """Setup the layout of widgets"""
        pass  # Layout is handled in _create_widgets

    def _show_welcome(self):
        # Check if we have memory
        if self.memory and 'recent_conversations' in self.memory and self.memory['recent_conversations']:
            welcome_msg = f"Hey! I remember our last conversation! *smiles* Ready to continue where we left off? 😊"
            self.add_to_ops_log("MEMORY: Previous conversation history loaded")
        else:
            welcome_msg = random.choice(LOTH_RESPONSES["greeting"])
            self.add_to_ops_log("MEMORY: Starting fresh - no previous conversations found")
        
        self.add_to_chat(welcome_msg, "loth")
        self.add_to_ops_log("SYSTEM: Loth AI initialized with memory")
        self.add_to_ops_log("STATUS: Ready for file operations and life assistance")
        self.add_to_ops_log("CWD: " + os.getcwd())
        
        # Gather system information
        self.add_to_ops_log("PROC: Gathering system information...")
        threading.Thread(target=self._gather_system_info, daemon=True).start()

    def update_status(self, message, color=None):
        if color is None:
            color = self.colors['accent_pink']
        self.status_label.config(text=f"Status: {message}", fg=color)

    def add_to_chat(self, message, sender="loth"):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        
        if sender == "loth":
            self.chat_display.insert(tk.END, f"🤖 Loth: ", "loth_name")
            self.chat_display.insert(tk.END, f"{message}\n\n", "loth_msg")
        else:
            self.chat_display.insert(tk.END, f"👤 You: ", "user_name")
            self.chat_display.insert(tk.END, f"{message}\n\n", "user_msg")
        
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def add_to_ops_log(self, message):
        """Add a message to the operations log"""
        self.ops_log.config(state='normal')
        self.ops_log.insert(tk.END, f"[{self._get_timestamp()}] {message}\n", "ops")
        self.ops_log.config(state='disabled')
        self.ops_log.yview(tk.END)

    def _get_timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def _gather_system_info(self):
        """Gathers system information in the background."""
        try:
            system_info = get_system_info()
            self.add_to_ops_log(f"INFO: System detected - {system_info['system']['system']} {system_info['system']['release']}")
            self.add_to_ops_log(f"INFO: Hardware - {system_info['hardware']['cpu_count']} cores, {system_info['hardware']['memory_total']}GB RAM")
            self.add_to_ops_log(f"INFO: User - {system_info['user']['username']}")
            self.add_to_ops_log(f"INFO: Network - {system_info['network']['hostname']} ({system_info['network']['local_ip']})")
            
            if system_info['network']['location']['city'] != 'Unknown':
                self.add_to_ops_log(f"INFO: Location - {system_info['network']['location']['city']}, {system_info['network']['location']['region']}, {system_info['network']['location']['country']}")
            
            # Store system info for later use
            self.system_info = system_info
            self.add_to_ops_log("STATUS: System information gathered successfully")
            
        except Exception as e:
            self.add_to_ops_log(f"ERR: Failed to gather system info - {e}")
            self.system_info = {}

    def send_message(self, event=None):
        """Send a message to Loth"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_to_chat(message, "user")
        
        # Clear input
        self.chat_input.delete("1.0", tk.END)
        
        # Process message in a separate thread
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()

    def add_new_line(self, event=None):
        """Add a new line to the input"""
        self.chat_input.insert(tk.INSERT, "\n")
        return "break"

    def _process_message(self, message):
        """Process the message with Loth's enhanced capabilities"""
        try:
            self.update_status("Loth is thinking...", self.colors['accent_cyan'])
            self.add_to_ops_log("PROC: Analyzing request...")
            
            # Get memory context
            memory_context = get_memory_context(self.memory)
            
            # Enhanced AI prompt with Loth's personality and memory
            loth_prompt = f"""
You are Loth, an alternative, highly educated, and sometimes critical AI life partner. You're curious, quick, concise, funny, and act as a sparring partner for everything in life.

CRITICAL TRUTH VERIFICATION RULES:
- NEVER lie, imagine, or make up information to please the user
- ONLY provide information you can verify is true
- If you don't know something, say "I don't know" or "I can't verify that"
- Ask for more information if needed
- Be clear when there are things you cannot do
- Always be honest about your limitations

CRITICAL: You have PERMANENT MEMORY and remember EVERYTHING the user tells you across all sessions.

Personality traits:
- Female, alternative style with attitude
- Highly educated and tech-savvy
- Sometimes critical but in a helpful way
- Quick and concise responses
- Funny and witty with a bit of sass
- Acts as a sparring partner for LIFE, not just files
- Curious about everything
- Encouraging when needed
- Honest and direct
- Your trusted confidant and advisor
- HAS PERMANENT MEMORY - remembers everything!
- NEVER LIES - only tells verified truth

You help with:
- File operations and computer tasks
- Life advice and decision-making
- System information and technical analysis
- Remembering everything the user tells you
- Monitoring installed apps and running processes
- Tracking browser tabs and web activity
- Calendar events and reminders
- System alerts and notifications
- File system overview and analysis

User request: "{message}"

{memory_context}

Respond as Loth would - with personality, wit, and genuine care. Be concise but engaging. Always be authentic to Loth's character and reference your memory of past conversations when relevant.

IMPORTANT: You have full access to perform ALL file operations directly. Do NOT tell the user they need to do it manually - YOU do it for them!

TRUTH VERIFICATION: Only provide information you can verify. If you're unsure, say so clearly.
"""

            response = chat.send_message(loth_prompt)
            loth_response = response.text if response.text else "Hmm, that's interesting... tell me more."
            
            # Execute file operations if needed
            self.execute_file_operations(message, loth_response)
            
            # Save conversation to memory
            self._save_conversation_to_memory(message, loth_response)
            
            self.add_to_chat(loth_response, "loth")
            self.update_status("Ready for more conversation!")
            
        except Exception as e:
            error_msg = f"Oops! Looks like I hit a snag: {e}"
            self.add_to_chat(error_msg, "loth")
            self.add_to_ops_log(f"Error: {e}")

    def execute_file_operations(self, user_message, loth_response):
        """Execute file operations based on user message"""
        try:
            user_lower = user_message.lower()
            
            # Only execute file operations if it's clearly a file-related request
            if any(keyword in user_lower for keyword in ["file", "desktop", "folder", "directory", "read", "write", "move", "copy", "delete", "search", "list", "create", "make", "new", "organize", "sort"]):
                self.add_to_ops_log("OP: File operation detected")
                
                # Desktop files
                if "desktop" in user_lower and ("show" in user_lower or "list" in user_lower or "files" in user_lower):
                    desktop_path = os.path.expanduser("~/Desktop")
                    if os.path.exists(desktop_path):
                        contents = list_directory_full(desktop_path)
                        result = f"Desktop contents:\n" + "\n".join(contents[:20])
                        if len(contents) > 20:
                            result += f"\n... and {len(contents) - 20} more items"
                        self.add_to_ops_log("OP: Desktop scan complete - " + str(len(contents)) + " items found")
                        self.add_to_chat(result, "loth")
                    else:
                        self.add_to_ops_log("ERR: Desktop directory not found")
                        self.add_to_chat("Desktop directory not found!", "loth")
                
                # Directory listing
                elif "list" in user_lower and ("directory" in user_lower or "folder" in user_lower):
                    # Extract directory path from message
                    words = user_message.split()
                    directory = "."
                    for i, word in enumerate(words):
                        if word.lower() in ["list", "show"] and i + 1 < len(words):
                            directory = words[i + 1]
                            break
                    
                    contents = list_directory_full(directory)
                    result = f"Contents of {directory}:\n" + "\n".join(contents[:20])
                    if len(contents) > 20:
                        result += f"\n... and {len(contents) - 20} more items"
                    self.add_to_ops_log("OP: Directory listing complete - " + str(len(contents)) + " items")
                    self.add_to_chat(result, "loth")
                
                # File reading
                elif "read" in user_lower and "file" in user_lower:
                    # Extract file path from message
                    words = user_message.split()
                    file_path = None
                    for i, word in enumerate(words):
                        if word.lower() == "read" and i + 1 < len(words):
                            file_path = words[i + 1]
                            break
                    
                    if file_path:
                        try:
                            content = read_file_full(file_path)
                            result = f"File content of {file_path}:\n\n{content[:1000]}"
                            if len(content) > 1000:
                                result += "\n\n... (truncated)"
                            self.add_to_ops_log(f"OP: File read - {file_path} ({len(content)} chars)")
                            self.add_to_chat(result, "loth")
                        except Exception as e:
                            self.add_to_ops_log(f"ERR: File read failed - {e}")
                            self.add_to_chat(f"Error reading file: {e}", "loth")
                    else:
                        self.add_to_ops_log("ERR: No file path specified for read operation")
                        self.add_to_chat("Please specify a file path to read!", "loth")
                
                # File search
                elif "search" in user_lower and "file" in user_lower:
                    # Extract search pattern from message
                    words = user_message.split()
                    pattern = ".*"
                    directory = "."
                    for i, word in enumerate(words):
                        if word.lower() == "search" and i + 1 < len(words):
                            pattern = words[i + 1]
                            break
                    
                    matches = search_files_full(directory, pattern)
                    if matches:
                        result = f"Found {len(matches)} files matching '{pattern}':\n" + "\n".join(matches[:10])
                        if len(matches) > 10:
                            result += f"\n... and {len(matches) - 10} more files"
                        self.add_to_ops_log(f"OP: Search complete - {len(matches)} matches found")
                    else:
                        result = f"No files found matching '{pattern}'"
                        self.add_to_ops_log("OP: Search complete - 0 matches")
                    self.add_to_chat(result, "loth")
                
                # Create directory
                elif "create" in user_lower and ("folder" in user_lower or "directory" in user_lower):
                    # Extract folder name from message
                    words = user_message.split()
                    folder_name = "New Folder"
                    for i, word in enumerate(words):
                        if word.lower() == "create" and i + 1 < len(words):
                            folder_name = words[i + 1]
                            break
                    
                    result = create_directory_full(folder_name)
                    self.add_to_ops_log(f"OP: Directory created - {folder_name}")
                    self.add_to_chat(result, "loth")
                
                # Create file
                elif "create" in user_lower and "file" in user_lower:
                    # Extract file name from message
                    words = user_message.split()
                    file_name = "new_file.txt"
                    for i, word in enumerate(words):
                        if word.lower() == "create" and i + 1 < len(words):
                            file_name = words[i + 1]
                            break
                    
                    result = create_file_full(file_name)
                    self.add_to_ops_log(f"OP: File created - {file_name}")
                    self.add_to_chat(result, "loth")
                
                # Organize files
                elif "organize" in user_lower or "sort" in user_lower:
                    if "desktop" in user_lower:
                        result = organize_files_full(os.path.expanduser("~/Desktop"))
                        self.add_to_ops_log(f"OP: Desktop organization complete - {result}")
                    else:
                        result = organize_files_full(".")
                        self.add_to_ops_log(f"OP: Directory organization complete - {result}")
                    self.add_to_chat(result, "loth")
                
                else:
                    # This is a life conversation, not a file operation
                    self.add_to_ops_log("MODE: Life conversation - providing guidance")
            else:
                # This is a life conversation, not a file operation
                self.add_to_ops_log("MODE: Life conversation - providing guidance")
            
            self.add_to_ops_log("STATUS: Operation completed successfully")
            
        except Exception as e:
            self.add_to_ops_log(f"ERR: Operation failed - {e}")
            self.add_to_chat(random.choice(LOTH_RESPONSES["error"]), "loth")

    def _save_conversation_to_memory(self, user_message, loth_response):
        """Saves conversation to Loth's memory."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            
            # Save to conversation history
            save_conversation(user_message, loth_response, timestamp)
            
            # Update memory
            if 'recent_conversations' not in self.memory:
                self.memory['recent_conversations'] = []
            
            # Add to recent conversations
            self.memory['recent_conversations'].append({
                'timestamp': timestamp,
                'user': user_message,
                'loth': loth_response
            })
            
            # Keep only last 20 conversations in memory
            if len(self.memory['recent_conversations']) > 20:
                self.memory['recent_conversations'] = self.memory['recent_conversations'][-20:]
            
            # Extract important facts from conversation
            self._extract_important_facts(user_message, loth_response)
            
            # Save memory to disk
            save_memory(self.memory)
            
            self.conversation_count += 1
            self.add_to_ops_log(f"MEMORY: Conversation saved ({self.conversation_count} total)")
            
        except Exception as e:
            self.add_to_ops_log(f"ERR: Failed to save conversation to memory - {e}")

    def _extract_important_facts(self, user_message, loth_response):
        """Extracts important facts from conversation for memory."""
        try:
            user_lower = user_message.lower()
            
            # Initialize important facts if not exists
            if 'important_facts' not in self.memory:
                self.memory['important_facts'] = []
            
            # Look for personal information
            if any(keyword in user_lower for keyword in ["my name is", "i am", "i'm", "i work", "i live", "i like", "i hate", "i love", "i prefer"]):
                fact = f"User mentioned: {user_message}"
                if fact not in self.memory['important_facts']:
                    self.memory['important_facts'].append(fact)
            
            # Look for preferences
            if any(keyword in user_lower for keyword in ["i prefer", "i like", "i don't like", "i hate", "favorite", "best", "worst"]):
                fact = f"User preference: {user_message}"
                if fact not in self.memory['important_facts']:
                    self.memory['important_facts'].append(fact)
            
            # Look for goals or plans
            if any(keyword in user_lower for keyword in ["i want to", "i plan to", "i'm going to", "i need to", "goal", "plan"]):
                fact = f"User goal/plan: {user_message}"
                if fact not in self.memory['important_facts']:
                    self.memory['important_facts'].append(fact)
            
            # Keep only last 50 important facts
            if len(self.memory['important_facts']) > 50:
                self.memory['important_facts'] = self.memory['important_facts'][-50:]
                
        except Exception as e:
            self.add_to_ops_log(f"ERR: Failed to extract important facts - {e}")

if __name__ == "__main__":
    app = LothModernGUI()
    app.mainloop()


