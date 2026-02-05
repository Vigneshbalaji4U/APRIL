#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
தமிழ் குரு திட்ட உதவியாளர் - முக்கிய பயன்பாடு
Tamil Voice Plans Assistant - Main Application
"""

import os
import sys
import json
import signal
import threading
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.voice_assistant import TamilVoiceAssistant
from src.utils import setup_logging, print_tamil, play_welcome_sound

class MainApplication:
    def __init__(self):
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / "config.json"
        
        # Load configuration
        self.config = self.load_config()
        
        # Setup logging
        self.logger = setup_logging()
        
        # Initialize assistant
        self.assistant = None
        
        # Control flags
        self.is_running = False
        self.continuous_mode = False
        
    def load_config(self):
        """Load configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ கட்டமைப்பு கோப்பு கிடைக்கவில்லை. இயல்புநிலைகளைப் பயன்படுத்துகிறது.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "language": "ta",
            "models": {
                "stt_model": "openai/whisper-tiny",
                "llm_model": "llama3.2:3b"
            },
            "paths": {
                "documents": "./data/documents",
                "audio_cache": "./data/audio_cache",
                "chroma_db": "./data/chroma_db"
            }
        }
    
    def initialize_assistant(self):
        """Initialize the Tamil voice assistant"""
        print_tamil("🔧 உதவியாளரை துவக்குகிறது...")
        
        try:
            self.assistant = TamilVoiceAssistant(config=self.config)
            print_tamil("✅ உதவியாளர் தயார்!")
            return True
        except Exception as e:
            print_tamil(f"❌ உதவியாளரை துவக்க முடியவில்லை: {e}")
            return False
    
    def interactive_mode(self):
        """Run in interactive command mode"""
        print_tamil(f"\n🎯 {self.config['app_name']}")
        print_tamil("=" * 50)
        print_tamil("கட்டளைகள்:")
        print_tamil("  1. குரு பயன்முறை (Voice Mode)")
        print_tamil("  2. உரை பயன்முறை (Text Mode)")
        print_tamil("  3. ஆவணங்களை சேர்க்க (Add Documents)")
        print_tamil("  4. அமைப்புகள் (Settings)")
        print_tamil("  5. வெளியேறு (Exit)")
        print_tamil("=" * 50)
        
        while True:
            choice = input("\n👉 உங்கள் தேர்வு (1-5): ").strip()
            
            if choice == "1":
                self.run_voice_mode()
            elif choice == "2":
                self.run_text_mode()
            elif choice == "3":
                self.add_documents()
            elif choice == "4":
                self.open_settings()
            elif choice == "5":
                print_tamil("👋 நன்றி, பின்னர் சந்திப்போம்!")
                break
            else:
                print_tamil("⚠️ தவறான தேர்வு. மீண்டும் முயற்சிக்கவும்.")
    
    def run_voice_mode(self):
        """Run continuous voice listening mode"""
        if not self.assistant:
            if not self.initialize_assistant():
                return
        
        print_tamil("\n🎤 குரு பயன்முறை - இப்போது பேசுங்கள்!")
        print_tamil("💡 குறிப்புகள்:")
        print_tamil(f"  • முன்கூட்டியே சொல்ல: '{self.config['assistant']['wake_word']}'")
        print_tamil(f"  • நிறுத்த: '{self.config['assistant']['exit_word']}'")
        print_tamil("  • அமைதியாக இருந்து நிறுத்த: CTRL+C")
        print_tamil("-" * 50)
        
        # Play welcome sound
        play_welcome_sound()
        
        # Start voice assistant
        try:
            self.assistant.start_continuous_listening()
        except KeyboardInterrupt:
            print_tamil("\n⏹️ குரு பயன்முறை நிறுத்தப்பட்டது.")
    
    def run_text_mode(self):
        """Run text-based Q&A mode"""
        if not self.assistant:
            if not self.initialize_assistant():
                return
        
        print_tamil("\n⌨️ உரை பயன்முறை")
        print_tamil("தமிழில் உங்கள் கேள்விகளை தட்டச்சு செய்யவும்")
        print_tamil("வெளியேற 'வெளியேறு' அல்லது 'exit' ஐ தட்டச்சு செய்யவும்")
        print_tamil("-" * 50)
        
        while True:
            try:
                question = input("\n🙋 உங்கள் கேள்வி: ").strip()
                
                if question.lower() in ['வெளியேறு', 'exit', 'quit']:
                    break
                
                if not question:
                    continue
                
                print_tamil("🤔 சிந்திக்கிறது...")
                response = self.assistant.process_text_query(question)
                
                print_tamil(f"\n🤖 பதில்: {response}")
                
                # Ask if user wants to hear the response
                if self.config['assistant']['enable_voice']:
                    hear = input("🔊 பதிலை கேட்க விரும்புகிறீர்களா? (ஆம்/இல்லை): ").strip().lower()
                    if hear in ['ஆம்', 'yes', 'y', 'a']:
                        self.assistant.speak_response(response)
                
            except KeyboardInterrupt:
                print_tamil("\n⏹️ உரை பயன்முறை நிறுத்தப்பட்டது.")
                break
    
    def add_documents(self):
        """Add documents to the knowledge base"""
        print_tamil("\n📁 ஆவணங்களை சேர்க்க")
        
        docs_path = Path(self.config['paths']['documents'])
        docs_path.mkdir(parents=True, exist_ok=True)
        
        print_tamil(f"தற்போதைய ஆவணங்கள் பாதை: {docs_path}")
        print_tamil("\nகிடைக்கும் கோப்புகள்:")
        
        # List existing documents
        extensions = ['.txt', '.pdf', '.docx', '.md']
        files = []
        for ext in extensions:
            files.extend(list(docs_path.glob(f"*{ext}")))
        
        if files:
            for i, file in enumerate(files, 1):
                print_tamil(f"  {i}. {file.name}")
        else:
            print_tamil("  ❌ ஆவணங்கள் இல்லை")
        
        print_tamil("\nவிருப்பங்கள்:")
        print_tamil("  1. புதிய கோப்பை பதிவேற்று")
        print_tamil("  2. கோப்பை நேரடியாக உருவாக்கு")
        print_tamil("  3. முக்கிய பட்டியலுக்கு திரும்பு")
        
        choice = input("\n👉 உங்கள் தேர்வு: ").strip()
        
        if choice == "1":
            self.upload_document()
        elif choice == "2":
            self.create_document()
    
    def upload_document(self):
        """Upload a document file"""
        print_tamil("\n📤 கோப்பை பதிவேற்று")
        print_tamil("கோப்பின் முழு பாதையை உள்ளிடவும்:")
        
        file_path = input("பாதை: ").strip()
        
        if not os.path.exists(file_path):
            print_tamil("❌ கோப்பு கிடைக்கவில்லை")
            return
        
        # Copy to documents folder
        dest_path = Path(self.config['paths']['documents']) / Path(file_path).name
        try:
            import shutil
            shutil.copy2(file_path, dest_path)
            print_tamil(f"✅ கோப்பு பதிவேற்றப்பட்டது: {dest_path.name}")
            
            # Re-index if assistant is running
            if self.assistant:
                print_tamil("🔄 அறிவுத் தளத்தை புதுப்பிக்கிறது...")
                self.assistant.rebuild_knowledge_base()
                print_tamil("✅ அறிவுத் தளம் புதுப்பிக்கப்பட்டது")
                
        except Exception as e:
            print_tamil(f"❌ பதிவேற்றம் தோல்வி: {e}")
    
    def create_document(self):
        """Create a new Tamil document"""
        print_tamil("\n📝 புதிய ஆவணத்தை உருவாக்கு")
        
        filename = input("கோப்பு பெயர் (இறுதியில் .txt சேர்க்கவும்): ").strip()
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        file_path = Path(self.config['paths']['documents']) / filename
        
        print_tamil("\nதமிழில் உங்கள் திட்டங்கள்/குறிப்புகளை உள்ளிடவும்:")
        print_tamil("முடிந்ததும் 'முற்றும்' என்று தட்டச்சு செய்யவும்")
        print_tamil("-" * 40)
        
        lines = []
        while True:
            line = input()
            if line.strip() == 'முற்றும்':
                break
            lines.append(line)
        
        # Save the document
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print_tamil(f"✅ ஆவணம் சேமிக்கப்பட்டது: {filename}")
            
            # Re-index if assistant is running
            if self.assistant:
                print_tamil("🔄 அறிவுத் தளத்தை புதுப்பிக்கிறது...")
                self.assistant.rebuild_knowledge_base()
                print_tamil("✅ அறிவுத் தளம் புதுப்பிக்கப்பட்டது")
                
        except Exception as e:
            print_tamil(f"❌ ஆவணத்தை சேமிக்க முடியவில்லை: {e}")
    
    def open_settings(self):
        """Open application settings"""
        print_tamil("\n⚙️ அமைப்புகள்")
        # Settings implementation here
        print_tamil("(விரைவில் கிடைக்கும்)")
    
    def run(self):
        """Main run method"""
        print_tamil(f"\n🌟 {self.config['app_name']} v{self.config['version']} க்கு வரவேற்கிறோம்!")
        
        # Check for documents
        docs_path = Path(self.config['paths']['documents'])
        if not list(docs_path.glob("*.*")):
            print_tamil("\n⚠️ எச்சரிக்கை: ஆவணங்கள் கிடைக்கவில்லை.")
            print_tamil("முதலில் சில திட்ட ஆவணங்களை சேர்க்கவும்.")
            self.add_documents()
        
        # Run interactive mode
        self.interactive_mode()

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print_tamil("\n\n⏹️ பயன்பாடு நிறுத்தப்பட்டது.")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create Unicode-friendly environment
    if sys.platform == "win32":
        import locale
        locale.setlocale(locale.LC_ALL, 'ta_IN.UTF-8')
    
    # Run application
    app = MainApplication()
    app.run()