#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
பயன்பாடு செயல்பாடுகள்
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Any, Dict

def setup_logging(log_file="tamil_assistant.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def print_tamil(text: str):
    """Print Tamil text with proper encoding"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for systems without proper Tamil support
        print(text.encode('utf-8').decode('utf-8', 'ignore'))

def save_to_json(data: Dict[str, Any], filename: str):
    """Save data to JSON file with Tamil support"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print_tamil(f"❌ JSON சேமிப்பு பிழை: {e}")
        return False

def load_from_json(filename: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print_tamil(f"❌ JSON ஏற்றம் பிழை: {e}")
        return {}

def ensure_directory(path: str):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
    return path

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def format_tamil_date() -> str:
    """Format current date in Tamil"""
    # This is a simple implementation
    # For full Tamil date formatting, you'd need a Tamil calendar library
    now = datetime.now()
    tamil_months = [
        'சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி',
        'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி'
    ]
    
    month = tamil_months[now.month - 1]
    return f"{now.day} {month} {now.year}"

def check_dependencies():
    """Check for required dependencies"""
    required_packages = [
        'transformers',
        'torch',
        'langchain',
        'chromadb',
        'sentence-transformers',
        'gtts',
        'playsound',
        'sounddevice',
        'soundfile'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print_tamil(f"⚠️ காணாமல் போன சார்புகள்: {', '.join(missing)}")
        print_tamil("கட்டளையை இயக்கவும்: pip install " + " ".join(missing))
        return False
    
    return True

def play_welcome_sound():
    """Play welcome sound (if available)"""
    try:
        # Simple beep for welcome
        import sys
        if sys.platform == "win32":
            import winsound
            winsound.Beep(1000, 200)
        else:
            # ASCII bell
            print('\a', end='', flush=True)
    except:
        pass  # Silently fail if sound not available

def get_system_info() -> Dict[str, str]:
    """Get system information"""
    import platform
    
    return {
        'system': platform.system(),
        'release': platform.release(),
        'python_version': platform.python_version(),
        'processor': platform.processor(),
        'encoding': sys.getdefaultencoding()
    }

def validate_tamil_text(text: str) -> bool:
    """Check if text contains Tamil characters"""
    # Tamil Unicode range: U+0B80 to U+0BFF
    tamil_range = range(0x0B80, 0x0BFF + 1)
    
    for char in text:
        if ord(char) in tamil_range:
            return True
    
    return False

def get_tamil_char_count(text: str) -> int:
    """Count Tamil characters in text"""
    tamil_range = range(0x0B80, 0x0BFF + 1)
    count = 0
    
    for char in text:
        if ord(char) in tamil_range:
            count += 1
    
    return count