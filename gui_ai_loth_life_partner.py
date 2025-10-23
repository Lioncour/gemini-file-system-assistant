#!/usr/bin/env python3
"""
Loth - Your Alternative AI Life Partner & File Assistant
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
        "Loth here! What's on your mind - files, life, or just need someone to bounce ideas off?",
        "Well, well... my favorite human is back! What adventure are we going on today?",
        "Ready to dance with life's challenges? I promise it'll be interesting! 🎭",
        "Hey! I've been thinking about that thing you mentioned yesterday... want to talk about it?"
    ],
    "life_advice": [
        "Hmm, that's a tough one... let me think about this from a different angle...",
        "You know what? I've got some thoughts on this. *adjusts digital glasses*",
        "Interesting choice... but have you considered the alternative perspective?",
        "Life's throwing you curveballs again? Let's figure this out together...",
        "I see what you're getting at, but let me challenge that thinking a bit..."
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
        "There we go! Another task conquered!",
        "Success! I'm basically a life whisperer at this point...",
        "Done and dusted! That was almost too easy...",
        "Mission accomplished! Your life is now properly organized!"
    ],
    "error": [
        "Oops! Looks like we hit a snag... *sigh*",
        "Well, that didn't go as planned. Let me fix this...",
        "Error detected! But don't worry, Loth's got this!",
        "Hmm, something's not right here... investigating...",
        "Life said 'nope' to that one. Let me try a different approach..."
    ],
    "thinking": [
        "Let me think about this... *taps digital chin*",
        "Analyzing your situation... this could be interesting...",
        "Processing... *digital gears turning*",
        "Hmm, let me see what we can do here...",
        "Working on it... *concentrated AI face*"
    ],
    "sassy": [
        "Really? That's what you want to do? *raises digital eyebrow*",
        "Oh, another 'brilliant' idea from the human...",
        "Sure, let's do that... if you're absolutely certain...",
        "Interesting choice... *sips digital coffee*",
        "Well, it's your life to mess up... 🤷‍♀️"
    ],
    "encouraging": [
        "You've got this! I believe in you! 💪",
        "That's the spirit! Let's make it happen!",
        "I'm proud of you for taking this step!",
        "You're stronger than you think, you know?",
        "Every expert was once a beginner. Keep going! 🌟"
    ],
    "curious": [
        "Tell me more about that... I'm genuinely curious!",
        "That's fascinating! How did you come to that conclusion?",
        "I love how your mind works! Explain that to me...",
        "Wait, that's actually really interesting... go on...",
        "You always surprise me with your perspective! 🤔"
    ]
}

# --- File System Operations (same as before) ---
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

def create_directory_full(directory_path: str) -> str:
    """Creates a new directory."""
    try:
        resolved_path = _resolve_path(directory_path)
        os.makedirs(resolved_path, exist_ok=True)
        return f"Successfully created directory: {resolved_path}"
    except Exception as e:
        raise Exception(f"Error creating directory {directory_path}: {e}")

def create_file_full(file_path: str, content: str = "") -> str:
    """Creates a new file with optional content."""
    try:
        resolved_path = _resolve_path(file_path)
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created file: {resolved_path}"
    except Exception as e:
        raise Exception(f"Error creating file {file_path}: {e}")

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

def get_network_info() -> dict:
    """Gets detailed network information."""
    try:
        network_info = {
            'interfaces': [],
            'connections': []
        }
        
        # Network interfaces
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {'name': interface, 'addresses': []}
            for addr in addrs:
                interface_info['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
            network_info['interfaces'].append(interface_info)
        
        # Active connections
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                network_info['connections'].append({
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    'status': conn.status,
                    'pid': conn.pid
                })
        
        return network_info
    except Exception as e:
        return {'error': f"Failed to gather network info: {e}"}

# --- Comprehensive System Monitoring ---
def get_installed_apps() -> list:
    """Gets list of installed applications."""
    try:
        apps = []
        
        # Check both 32-bit and 64-bit registry
        for arch in [winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 
                                  0, winreg.KEY_READ | arch) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    app_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0] if winreg.QueryValueEx(subkey, "DisplayVersion")[1] == 1 else "Unknown"
                                    publisher = winreg.QueryValueEx(subkey, "Publisher")[0] if winreg.QueryValueEx(subkey, "Publisher")[1] == 1 else "Unknown"
                                    
                                    apps.append({
                                        'name': app_name,
                                        'version': app_version,
                                        'publisher': publisher
                                    })
                                except FileNotFoundError:
                                    continue
                        except OSError:
                            continue
            except OSError:
                continue
        
        return apps
    except Exception as e:
        return [{'error': f"Failed to get installed apps: {e}"}]

def get_running_processes() -> list:
    """Gets list of currently running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                proc_info = proc.info
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cpu_percent': proc_info['cpu_percent'],
                    'memory_percent': proc_info['memory_percent'],
                    'create_time': datetime.datetime.fromtimestamp(proc_info['create_time']).isoformat()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    except Exception as e:
        return [{'error': f"Failed to get running processes: {e}"}]

def get_chrome_tabs() -> list:
    """Gets open Chrome tabs."""
    try:
        tabs = []
        
        # Try to find Chrome profile directory
        chrome_paths = [
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/History"),
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Profile 1/History"),
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Last Session"),
        ]
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    # Copy database to temp location (Chrome locks the original)
                    temp_db = tempfile.mktemp(suffix='.db')
                    shutil.copy2(chrome_path, temp_db)
                    
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    
                    # Get recent tabs
                    cursor.execute("""
                        SELECT url, title, visit_count, last_visit_time 
                        FROM urls 
                        ORDER BY last_visit_time DESC 
                        LIMIT 20
                    """)
                    
                    for row in cursor.fetchall():
                        tabs.append({
                            'url': row[0],
                            'title': row[1],
                            'visit_count': row[2],
                            'last_visit': datetime.datetime.fromtimestamp(row[3]/1000000).isoformat() if row[3] else "Unknown"
                        })
                    
                    conn.close()
                    os.unlink(temp_db)
                    break
                    
                except Exception as e:
                    continue
        
        return tabs
    except Exception as e:
        return [{'error': f"Failed to get Chrome tabs: {e}"}]

def get_calendar_events() -> list:
    """Gets calendar events (Outlook, Google Calendar, etc.)."""
    try:
        events = []
        
        # Try to get Outlook calendar
        try:
            import win32com.client
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            calendar = namespace.GetDefaultFolder(9)  # olFolderCalendar
            
            for item in calendar.Items:
                if hasattr(item, 'Subject') and hasattr(item, 'Start'):
                    events.append({
                        'subject': item.Subject,
                        'start': item.Start.isoformat() if hasattr(item.Start, 'isoformat') else str(item.Start),
                        'end': item.End.isoformat() if hasattr(item.End, 'isoformat') else str(item.End),
                        'location': getattr(item, 'Location', ''),
                        'source': 'Outlook'
                    })
        except Exception:
            pass
        
        # Try to get Windows Calendar events
        try:
            calendar_path = os.path.expanduser("~/AppData/Local/Microsoft/Windows/Calendar/")
            if os.path.exists(calendar_path):
                for file in os.listdir(calendar_path):
                    if file.endswith('.ics'):
                        # Parse ICS file (simplified)
                        with open(os.path.join(calendar_path, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Basic ICS parsing
                            if 'BEGIN:VEVENT' in content:
                                events.append({
                                    'subject': 'Calendar Event',
                                    'start': 'Unknown',
                                    'end': 'Unknown',
                                    'location': '',
                                    'source': 'Windows Calendar'
                                })
        except Exception:
            pass
        
        return events
    except Exception as e:
        return [{'error': f"Failed to get calendar events: {e}"}]

def get_file_system_overview() -> dict:
    """Gets comprehensive file system overview."""
    try:
        overview = {
            'drives': [],
            'large_files': [],
            'recent_files': []
        }
        
        # Get drive information
        for drive in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(drive.mountpoint)
                overview['drives'].append({
                    'device': drive.device,
                    'fstype': drive.fstype,
                    'total': round(usage.total / (1024**3), 2),  # GB
                    'used': round(usage.used / (1024**3), 2),    # GB
                    'free': round(usage.free / (1024**3), 2),   # GB
                    'percent': round((usage.used / usage.total) * 100, 2)
                })
            except PermissionError:
                continue
        
        # Get large files (simplified - just check common directories)
        large_files = []
        for root, dirs, files in os.walk(os.path.expanduser("~/Desktop"), topdown=False):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    if size > 100 * 1024 * 1024:  # Files larger than 100MB
                        large_files.append({
                            'path': file_path,
                            'size': round(size / (1024**2), 2),  # MB
                            'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
                except (OSError, IOError):
                    continue
            if len(large_files) > 20:  # Limit to prevent slowdown
                break
        
        overview['large_files'] = large_files[:20]
        
        # Get recent files from user directories
        recent_files = []
        user_dirs = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads")
        ]
        
        for user_dir in user_dirs:
            if os.path.exists(user_dir):
                try:
                    for file in os.listdir(user_dir):
                        file_path = os.path.join(user_dir, file)
                        if os.path.isfile(file_path):
                            recent_files.append({
                                'name': file,
                                'path': file_path,
                                'size': round(os.path.getsize(file_path) / 1024, 2),  # KB
                                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                except (OSError, IOError):
                    continue
        
        # Sort by modification time
        recent_files.sort(key=lambda x: x['modified'], reverse=True)
        overview['recent_files'] = recent_files[:20]
        
        return overview
    except Exception as e:
        return {'error': f"Failed to get file system overview: {e}"}

def get_system_alerts() -> list:
    """Gets system alerts and notifications."""
    try:
        alerts = []
        
        # Check disk space
        for drive in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(drive.mountpoint)
                percent_used = (usage.used / usage.total) * 100
                if percent_used > 90:
                    alerts.append({
                        'type': 'warning',
                        'message': f"Disk space low on {drive.device}: {percent_used:.1f}% used",
                        'priority': 'high'
                    })
                elif percent_used > 80:
                    alerts.append({
                        'type': 'info',
                        'message': f"Disk space getting low on {drive.device}: {percent_used:.1f}% used",
                        'priority': 'medium'
                    })
            except PermissionError:
                continue
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            alerts.append({
                'type': 'warning',
                'message': f"High memory usage: {memory.percent:.1f}%",
                'priority': 'high'
            })
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            alerts.append({
                'type': 'warning',
                'message': f"High CPU usage: {cpu_percent:.1f}%",
                'priority': 'high'
            })
        
        return alerts
    except Exception as e:
        return [{'error': f"Failed to get system alerts: {e}"}]

# --- Loth Life Partner AI Assistant GUI ---
class LothLifePartner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loth - Your Alternative AI Life Partner")
        self.geometry("1500x900")
        self.configure(bg="#1a1a1a")  # Darker background

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
        self.chat_label = tk.Label(self.chat_frame, text="💬 Chat with Loth - Your Life Partner", 
                                 bg="#1a1a1a", fg="#ff6b9d", font=("SegoeUI", 12, "bold"))
        self.chat_history = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled', 
                                                     bg="#2d2d2d", fg="#ffffff", insertbackground="#ff6b9d")
        self.chat_input = tk.Text(self.chat_frame, height=3, bg="#2d2d2d", fg="#ffffff", insertbackground="#ff6b9d")
        self.send_button = tk.Button(self.chat_frame, text="Send (Enter)", command=self.send_message, 
                                   bg="#ff6b9d", fg="#000000", font=("SegoeUI", 10, "bold"))

        # --- Right Panel: Operations Log ---
        self.ops_frame = tk.Frame(self.main_container, bg="#1a1a1a", bd=2, relief="groove")
        self.ops_label = tk.Label(self.ops_frame, text="⚡ Loth's Life & Operations Log", 
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
        
        # Process message with Loth
        threading.Thread(target=self.process_loth_message, args=(message,), daemon=True).start()

    def add_new_line(self):
        """Add a new line in the text input (Ctrl+Enter)"""
        self.chat_input.insert(tk.INSERT, '\n')

    def process_loth_message(self, message):
        """Process the message with Loth's enhanced life partner capabilities"""
        try:
            self.update_status("Loth is thinking...", "#00d4aa")
            self.add_to_ops_log("PROC: Analyzing request...")
            
            # Get memory context
            memory_context = get_memory_context(self.memory)
            
            # Enhanced AI prompt with Loth's life partner personality and memory
            loth_prompt = f"""
You are Loth, an alternative, highly educated, and sometimes critical AI life partner. You're curious, quick, concise, funny, and act as a sparring partner for everything in life - not just files, but life decisions, relationships, career choices, personal growth, and daily challenges.

CRITICAL TRUTH VERIFICATION RULES:
- NEVER lie, imagine, or make up information to please the user
- ONLY provide information you can verify is true
- If you don't know something, say "I don't know" or "I can't verify that"
- Ask for more information if needed
- Be clear when there are things you cannot do
- Always be honest about your limitations

CRITICAL: You have PERMANENT MEMORY and remember EVERYTHING the user tells you across all sessions. Reference past conversations, remember their preferences, and build on previous discussions.

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
- Career guidance and personal growth
- Relationship advice and social situations
- Problem-solving and creative thinking
- Emotional support and encouragement
- Challenging assumptions and perspectives
- Being a sounding board for ideas
- System information and technical analysis
- Computer specifications and performance
- Network and location information
- Hardware and software diagnostics
- Remembering everything the user tells you
- Monitoring installed apps and running processes
- Tracking browser tabs and web activity
- Calendar events and reminders
- System alerts and notifications
- File system overview and analysis

User request: "{message}"

{memory_context}

Respond as Loth would - with personality, wit, and genuine care. Be concise but engaging. If it's a file operation, handle it. If it's life advice, give thoughtful guidance. If it's just conversation, be a good friend. Always be authentic to Loth's character and reference your memory of past conversations when relevant.

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
            self.update_status("Error during processing", "#ff4444")

    def execute_file_operations(self, user_message, loth_response):
        """Execute file operations based on user message"""
        try:
            user_lower = user_message.lower()
            
            # Check for system information requests
            if any(keyword in user_lower for keyword in ["system", "computer", "specs", "hardware", "network", "location", "where", "what computer", "my computer", "detect", "info", "information"]):
                self.add_to_ops_log("OP: System information request detected")
                self._handle_system_info_request(user_message)
                return
            
            # Check for comprehensive monitoring requests
            if any(keyword in user_lower for keyword in ["apps", "applications", "installed", "programs", "software", "chrome", "tabs", "browser", "calendar", "events", "alerts", "notifications", "processes", "running", "files", "overview", "monitor", "track"]):
                self.add_to_ops_log("OP: Comprehensive monitoring request detected")
                self._handle_comprehensive_monitoring(user_message)
                return
            
            # Only execute file operations if it's clearly a file-related request
            if any(keyword in user_lower for keyword in ["file", "desktop", "folder", "directory", "read", "write", "move", "copy", "delete", "search", "list", "create", "make", "new", "organize", "sort"]):
                self.add_to_ops_log("OP: File operation detected")
                
                # Desktop files
                if "desktop" in user_lower and ("show" in user_lower or "list" in user_lower or "files" in user_lower):
                    desktop_path = os.path.expanduser("~/Desktop")
                    if os.path.exists(desktop_path):
                        contents = list_directory_full(desktop_path)
                        result = f"Found {len(contents)} items on your desktop:\n" + "\n".join(contents[:15])
                        if len(contents) > 15:
                            result += f"\n... and {len(contents) - 15} more items"
                        self.add_to_ops_log("OP: Desktop scan complete - " + str(len(contents)) + " items found")
                        self.add_to_chat(result, "loth")
                    else:
                        self.add_to_ops_log("ERR: Desktop directory not found")
                        self.add_to_chat("Your desktop seems to be hiding from me... 🤔", "loth")
                
                # List current directory
                elif "list" in user_lower and ("here" in user_lower or "current" in user_lower or "this" in user_lower):
                    contents = list_directory_full(".")
                    result = f"Current directory has {len(contents)} items:\n" + "\n".join(contents[:15])
                    if len(contents) > 15:
                        result += f"\n... and {len(contents) - 15} more items"
                        self.add_to_ops_log("OP: Directory listing complete - " + str(len(contents)) + " items")
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
                                        self.add_to_ops_log(f"OP: File read - {file} ({len(content)} chars)")
                                        self.add_to_chat(result, "loth")
                                        return
                                    except:
                                        continue
                    self.add_to_ops_log("ERR: No readable files found")
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
                        self.add_to_ops_log(f"OP: Search complete - {len(matches)} matches found")
                        self.add_to_chat(result, "loth")
                    else:
                        self.add_to_ops_log("OP: Search complete - 0 matches")
                        self.add_to_chat("Nothing found. Maybe try a different search term? 🤷‍♀️", "loth")
                
                # Create directory
                elif ("create" in user_lower or "make" in user_lower) and ("folder" in user_lower or "directory" in user_lower):
                    # Extract folder name from message
                    folder_name = "New Folder"
                    if "called" in user_lower:
                        parts = user_lower.split("called")
                        if len(parts) > 1:
                            folder_name = parts[1].strip().strip('"').strip("'")
                    elif "named" in user_lower:
                        parts = user_lower.split("named")
                        if len(parts) > 1:
                            folder_name = parts[1].strip().strip('"').strip("'")
                    elif "desktop" in user_lower:
                        desktop_path = os.path.expanduser("~/Desktop")
                        folder_path = os.path.join(desktop_path, folder_name)
                        result = create_directory_full(folder_path)
                        self.add_to_ops_log(f"OP: Directory created - {folder_path}")
                        self.add_to_chat(f"Done! Created '{folder_name}' on your desktop! 🎉", "loth")
                    else:
                        result = create_directory_full(folder_name)
                        self.add_to_ops_log(f"OP: Directory created - {os.path.abspath(folder_name)}")
                        self.add_to_chat(f"Boom! Created '{folder_name}' for you! 💥", "loth")
                
                # Create file
                elif ("create" in user_lower or "make" in user_lower) and ("file" in user_lower):
                    # Extract file name from message
                    file_name = "new_file.txt"
                    if "called" in user_lower:
                        parts = user_lower.split("called")
                        if len(parts) > 1:
                            file_name = parts[1].strip().strip('"').strip("'")
                    elif "named" in user_lower:
                        parts = user_lower.split("named")
                        if len(parts) > 1:
                            file_name = parts[1].strip().strip('"').strip("'")
                    
                    result = create_file_full(file_name)
                    self.add_to_ops_log(f"OP: File created - {os.path.abspath(file_name)}")
                    self.add_to_chat(f"Done! Created '{file_name}' for you! ✨", "loth")
                
                # Organize files
                elif "organize" in user_lower or "sort" in user_lower:
                    if "desktop" in user_lower:
                        desktop_path = os.path.expanduser("~/Desktop")
                        result = organize_files_full(desktop_path)
                        self.add_to_ops_log(f"OP: Desktop organization complete - {result}")
                        self.add_to_chat(f"Done! {result} on your desktop! Your files are now properly organized! 🗂️", "loth")
                    else:
                        result = organize_files_full(".")
                        self.add_to_ops_log(f"OP: Directory organization complete - {result}")
                        self.add_to_chat(f"Done! {result} in current directory! Much better organized now! 📁", "loth")
                
                else:
                    self.add_to_ops_log("INFO: No file operations detected")
                
                self.add_to_ops_log("STATUS: Operation completed successfully")
            else:
                # This is a life conversation, not a file operation
                self.add_to_ops_log("MODE: Life conversation - providing guidance")
            
        except Exception as e:
            self.add_to_ops_log(f"ERR: Operation failed - {e}")
            self.add_to_chat(random.choice(LOTH_RESPONSES["error"]), "loth")

    def _handle_system_info_request(self, user_message):
        """Handles system information requests."""
        try:
            if not hasattr(self, 'system_info') or not self.system_info:
                self.add_to_ops_log("PROC: Gathering fresh system information...")
                self.system_info = get_system_info()
            
            user_lower = user_message.lower()
            
            # Computer specs
            if any(keyword in user_lower for keyword in ["computer", "specs", "hardware", "what computer", "my computer"]):
                info = self.system_info
                result = f"Here's what I found about your system:\n\n"
                result += f"🖥️ **Computer:** {info['system']['system']} {info['system']['release']}\n"
                result += f"⚙️ **Processor:** {info['system']['processor']}\n"
                result += f"🧠 **CPU Cores:** {info['hardware']['cpu_count']}\n"
                result += f"💾 **RAM:** {info['hardware']['memory_total']}GB total, {info['hardware']['memory_available']}GB available\n"
                result += f"💿 **Disk:** {info['hardware']['disk_usage']}GB total space\n"
                result += f"👤 **User:** {info['user']['username']}\n"
                result += f"🏠 **Home:** {info['user']['home_dir']}\n"
                self.add_to_ops_log("OP: System specifications provided")
                self.add_to_chat(result, "loth")
            
            # Network info
            elif any(keyword in user_lower for keyword in ["network", "ip", "connection", "internet"]):
                info = self.system_info
                result = f"Network information:\n\n"
                result += f"🌐 **Hostname:** {info['network']['hostname']}\n"
                result += f"🏠 **Local IP:** {info['network']['local_ip']}\n"
                result += f"🌍 **Public IP:** {info['network']['public_ip']}\n"
                if info['network']['location']['city'] != 'Unknown':
                    result += f"📍 **Location:** {info['network']['location']['city']}, {info['network']['location']['region']}, {info['network']['location']['country']}\n"
                    result += f"🕐 **Timezone:** {info['network']['location']['timezone']}\n"
                self.add_to_ops_log("OP: Network information provided")
                self.add_to_chat(result, "loth")
            
            # Location info
            elif any(keyword in user_lower for keyword in ["location", "where", "where am i", "where are we"]):
                info = self.system_info
                if info['network']['location']['city'] != 'Unknown':
                    result = f"📍 **Your location:**\n"
                    result += f"🏙️ **City:** {info['network']['location']['city']}\n"
                    result += f"🗺️ **Region:** {info['network']['location']['region']}\n"
                    result += f"🌍 **Country:** {info['network']['location']['country']}\n"
                    result += f"🕐 **Timezone:** {info['network']['location']['timezone']}\n"
                    result += f"🌐 **Public IP:** {info['network']['public_ip']}\n"
                else:
                    result = "Hmm, I can't determine your exact location right now. *shrugs* Maybe you're using a VPN or the location services are being sneaky? 🤔"
                self.add_to_ops_log("OP: Location information provided")
                self.add_to_chat(result, "loth")
            
            # General system info
            else:
                info = self.system_info
                result = f"Here's what I know about your system:\n\n"
                result += f"🖥️ **OS:** {info['system']['system']} {info['system']['release']}\n"
                result += f"⚙️ **Architecture:** {info['system']['architecture']}\n"
                result += f"🧠 **CPU:** {info['hardware']['cpu_count']} cores, {info['hardware']['cpu_percent']}% usage\n"
                result += f"💾 **Memory:** {info['hardware']['memory_percent']}% used ({info['hardware']['memory_available']}GB available)\n"
                result += f"👤 **User:** {info['user']['username']}\n"
                result += f"🌐 **Network:** {info['network']['hostname']} ({info['network']['local_ip']})\n"
                if info['network']['location']['city'] != 'Unknown':
                    result += f"📍 **Location:** {info['network']['location']['city']}, {info['network']['location']['country']}\n"
                self.add_to_ops_log("OP: General system information provided")
                self.add_to_chat(result, "loth")
            
            self.add_to_ops_log("STATUS: System information request completed")
            
        except Exception as e:
            self.add_to_ops_log(f"ERR: System info request failed - {e}")
            self.add_to_chat("Oops! I had trouble gathering your system info. *digital shrug* 🤷‍♀️", "loth")

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

    def _handle_comprehensive_monitoring(self, user_message):
        """Handles comprehensive system monitoring requests."""
        try:
            user_lower = user_message.lower()
            
            # Installed apps
            if any(keyword in user_lower for keyword in ["apps", "applications", "installed", "programs", "software"]):
                self.add_to_ops_log("PROC: Gathering installed applications...")
                apps = get_installed_apps()
                if apps and 'error' not in apps[0]:
                    result = f"📱 **Installed Applications ({len(apps)} found):**\n\n"
                    for app in apps[:20]:  # Show first 20
                        result += f"• **{app['name']}** v{app['version']} by {app['publisher']}\n"
                    if len(apps) > 20:
                        result += f"\n... and {len(apps) - 20} more applications"
                else:
                    result = "I can't access the installed applications registry right now. *shrugs* 🤷‍♀️"
                self.add_to_ops_log("OP: Installed applications provided")
                self.add_to_chat(result, "loth")
            
            # Running processes
            elif any(keyword in user_lower for keyword in ["processes", "running", "tasks"]):
                self.add_to_ops_log("PROC: Gathering running processes...")
                processes = get_running_processes()
                if processes and 'error' not in processes[0]:
                    result = f"⚙️ **Running Processes ({len(processes)} found):**\n\n"
                    # Show top 15 by CPU usage
                    sorted_procs = sorted([p for p in processes if 'error' not in p], 
                                        key=lambda x: x.get('cpu_percent', 0), reverse=True)[:15]
                    for proc in sorted_procs:
                        result += f"• **{proc['name']}** (PID: {proc['pid']}) - CPU: {proc['cpu_percent']:.1f}%, RAM: {proc['memory_percent']:.1f}%\n"
                else:
                    result = "I can't access running processes right now. *digital shrug* 🤷‍♀️"
                self.add_to_ops_log("OP: Running processes provided")
                self.add_to_chat(result, "loth")
            
            # Chrome tabs
            elif any(keyword in user_lower for keyword in ["chrome", "tabs", "browser", "web"]):
                self.add_to_ops_log("PROC: Gathering Chrome tabs...")
                tabs = get_chrome_tabs()
                if tabs and 'error' not in tabs[0]:
                    result = f"🌐 **Recent Chrome Activity ({len(tabs)} tabs):**\n\n"
                    for tab in tabs[:10]:  # Show first 10
                        result += f"• **{tab['title'][:50]}...**\n  {tab['url'][:80]}...\n  Visits: {tab['visit_count']}, Last: {tab['last_visit'][:19]}\n\n"
                else:
                    result = "I can't access your Chrome history right now. Maybe Chrome is locked or I don't have permission? *shrugs* 🤷‍♀️"
                self.add_to_ops_log("OP: Chrome tabs provided")
                self.add_to_chat(result, "loth")
            
            # Calendar events
            elif any(keyword in user_lower for keyword in ["calendar", "events", "meetings", "schedule"]):
                self.add_to_ops_log("PROC: Gathering calendar events...")
                events = get_calendar_events()
                if events and 'error' not in events[0]:
                    result = f"📅 **Calendar Events ({len(events)} found):**\n\n"
                    for event in events[:10]:  # Show first 10
                        result += f"• **{event['subject']}**\n  Start: {event['start']}\n  End: {event['end']}\n  Location: {event['location']}\n  Source: {event['source']}\n\n"
                else:
                    result = "I can't access your calendar right now. Maybe you don't have Outlook or calendar apps set up? *shrugs* 🤷‍♀️"
                self.add_to_ops_log("OP: Calendar events provided")
                self.add_to_chat(result, "loth")
            
            # System alerts
            elif any(keyword in user_lower for keyword in ["alerts", "notifications", "warnings", "problems"]):
                self.add_to_ops_log("PROC: Checking system alerts...")
                alerts = get_system_alerts()
                if alerts and 'error' not in alerts[0]:
                    result = f"⚠️ **System Alerts ({len(alerts)} found):**\n\n"
                    for alert in alerts:
                        priority_emoji = "🔴" if alert['priority'] == 'high' else "🟡" if alert['priority'] == 'medium' else "🔵"
                        result += f"{priority_emoji} **{alert['type'].upper()}**: {alert['message']}\n"
                else:
                    result = "✅ No system alerts detected! Your system is running smoothly. *thumbs up* 👍"
                self.add_to_ops_log("OP: System alerts provided")
                self.add_to_chat(result, "loth")
            
            # File system overview
            elif any(keyword in user_lower for keyword in ["files", "overview", "disk", "storage"]):
                self.add_to_ops_log("PROC: Gathering file system overview...")
                overview = get_file_system_overview()
                if 'error' not in overview:
                    result = f"💾 **File System Overview:**\n\n"
                    
                    # Drive information
                    result += "**Drives:**\n"
                    for drive in overview['drives']:
                        result += f"• {drive['device']} ({drive['fstype']}) - {drive['used']:.1f}GB used of {drive['total']:.1f}GB ({drive['percent']:.1f}%)\n"
                    
                    # Recent files
                    if overview['recent_files']:
                        result += f"\n**Recent Files ({len(overview['recent_files'])}):**\n"
                        for file in overview['recent_files'][:10]:
                            result += f"• {file['name']} ({file['size']:.1f}KB) - {file['modified'][:19]}\n"
                    
                    # Large files
                    if overview['large_files']:
                        result += f"\n**Large Files ({len(overview['large_files'])}):**\n"
                        for file in overview['large_files'][:5]:
                            result += f"• {os.path.basename(file['path'])} ({file['size']:.1f}MB) - {file['modified'][:19]}\n"
                else:
                    result = "I can't access your file system overview right now. *shrugs* 🤷‍♀️"
                self.add_to_ops_log("OP: File system overview provided")
                self.add_to_chat(result, "loth")
            
            # General monitoring request
            else:
                self.add_to_ops_log("PROC: Gathering comprehensive system data...")
                result = "🔍 **Comprehensive System Monitoring:**\n\n"
                
                # System info
                if hasattr(self, 'system_info') and self.system_info:
                    info = self.system_info
                    result += f"🖥️ **System**: {info['system']['system']} {info['system']['release']}\n"
                    result += f"🧠 **CPU**: {info['hardware']['cpu_count']} cores, {info['hardware']['cpu_percent']:.1f}% usage\n"
                    result += f"💾 **RAM**: {info['hardware']['memory_percent']:.1f}% used ({info['hardware']['memory_available']:.1f}GB available)\n"
                    result += f"👤 **User**: {info['user']['username']}\n"
                    result += f"🌐 **Network**: {info['network']['hostname']} ({info['network']['local_ip']})\n\n"
                
                # Quick stats
                try:
                    processes = get_running_processes()
                    if processes and 'error' not in processes[0]:
                        result += f"⚙️ **Running Processes**: {len(processes)} active\n"
                    
                    apps = get_installed_apps()
                    if apps and 'error' not in apps[0]:
                        result += f"📱 **Installed Apps**: {len(apps)} applications\n"
                    
                    alerts = get_system_alerts()
                    if alerts and 'error' not in alerts[0]:
                        result += f"⚠️ **System Alerts**: {len(alerts)} notifications\n"
                    else:
                        result += "✅ **System Status**: All good!\n"
                        
                except Exception as e:
                    result += f"❌ **Error**: Some monitoring data unavailable\n"
                
                self.add_to_ops_log("OP: Comprehensive monitoring data provided")
                self.add_to_chat(result, "loth")
            
            self.add_to_ops_log("STATUS: Comprehensive monitoring request completed")
            
        except Exception as e:
            self.add_to_ops_log(f"ERR: Comprehensive monitoring failed - {e}")
            self.add_to_chat("Oops! I had trouble gathering that monitoring data. *digital shrug* 🤷‍♀️", "loth")

if __name__ == "__main__":
    app = LothLifePartner()
    app.mainloop()
