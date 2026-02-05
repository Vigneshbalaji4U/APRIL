#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
முக்கிய தமிழ் குரு உதவியாளர் வகுப்பு
Main Tamil Voice Assistant Class
"""

import os
import time
import threading
import queue
from typing import Optional, Dict, Any
from datetime import datetime

# Import local modules
from .stt_engine import TamilSTTEngine
from .tts_engine import TamilTTSEngine
from .knowledge_base import TamilKnowledgeBase
from .document_processor import TamilDocumentProcessor

class TamilVoiceAssistant:
    """Main Tamil Voice Assistant class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Tamil Voice Assistant
        
        Args:
            config: Configuration dictionary
        """
        # Load configuration
        self.config = config or self._load_default_config()
        
        # Initialize paths
        self._setup_paths()
        
        # Initialize components
        self.stt_engine = None
        self.tts_engine = None
        self.knowledge_base = None
        self.document_processor = None
        
        # Conversation state
        self.conversation_history = []
        self.is_listening = False
        self.stop_event = threading.Event()
        self.command_queue = queue.Queue()
        
        # Wake word detection
        self.wake_word = self.config.get('assistant', {}).get('wake_word', 'உதவி')
        self.exit_word = self.config.get('assistant', {}).get('exit_word', 'நிறுத்து')
        
        # Initialize engines
        self._initialize_engines()
        
        # Greeting messages
        self.greetings = [
            "வணக்கம்! நான் உங்கள் தமிழ் திட்ட உதவியாளர்.",
            "உங்கள் திட்டங்களைப் பற்றி கேளுங்கள்.",
            "நான் உங்கள் குறிப்புகளிலிருந்து பதிலளிப்பேன்."
        ]
        
        print("🤖 தமிழ் குரு உதவியாளர் துவக்கப்பட்டது")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "language": "ta",
            "models": {
                "stt_model": "base",
                "llm_model": "llama3.2:3b"
            },
            "paths": {
                "documents": "./data/documents",
                "audio_cache": "./data/audio_cache",
                "chroma_db": "./data/chroma_db"
            },
            "assistant": {
                "wake_word": "உதவி",
                "exit_word": "நிறுத்து",
                "enable_voice": True,
                "enable_history": True,
                "max_history": 10
            }
        }
    
    def _setup_paths(self):
        """Create necessary directories"""
        paths = self.config['paths']
        
        for path_key in ['documents', 'audio_cache', 'chroma_db']:
            path = paths.get(path_key)
            if path:
                os.makedirs(path, exist_ok=True)
    
    def _initialize_engines(self):
        """Initialize all AI engines"""
        print("🔧 உதவியாளர் பொறிகளை துவக்குகிறது...")
        
        # Initialize STT
        try:
            self.stt_engine = TamilSTTEngine(
                model_name=self.config['models'].get('stt_model', 'base')
            )
            print("✅ STT பொறி தயார்")
        except Exception as e:
            print(f"❌ STT பொறி பிழை: {e}")
        
        # Initialize TTS
        try:
            cache_dir = self.config['paths'].get('audio_cache', './data/audio_cache')
            self.tts_engine = TamilTTSEngine(cache_dir=cache_dir)
            print("✅ TTS பொறி தயார்")
        except Exception as e:
            print(f"❌ TTS பொறி பிழை: {e}")
        
        # Initialize Document Processor
        try:
            docs_dir = self.config['paths'].get('documents', './data/documents')
            self.document_processor = TamilDocumentProcessor(docs_dir)
            print("✅ ஆவண செயலாக்கி தயார்")
        except Exception as e:
            print(f"❌ ஆவண செயலாக்கி பிழை: {e}")
        
        # Initialize Knowledge Base
        try:
            docs_dir = self.config['paths'].get('documents', './data/documents')
            chroma_dir = self.config['paths'].get('chroma_db', './data/chroma_db')
            self.knowledge_base = TamilKnowledgeBase(docs_dir, chroma_dir)
            print("✅ அறிவுத் தளம் தயார்")
        except Exception as e:
            print(f"❌ அறிவுத் தளம் பிழை: {e}")
        
        # Build knowledge base if needed
        if self.knowledge_base:
            self.knowledge_base.build_knowledge_base()
    
    def speak_response(self, text: str):
        """Speak response using TTS"""
        if self.tts_engine and text.strip():
            self.tts_engine.speak_gtts(text)
    
    def process_text_query(self, query: str) -> str:
        """
        Process text query and return response
        
        Args:
            query: Tamil text query
            
        Returns:
            Response in Tamil
        """
        print(f"🧠 கேள்வி செயலாக்கம்: {query}")
        
        # Add to conversation history
        self._add_to_history("user", query)
        
        # Check for special commands
        response = self._handle_special_commands(query)
        if response:
            self._add_to_history("assistant", response)
            return response
        
        # Search knowledge base
        if self.knowledge_base:
            try:
                # Search for relevant information
                search_results = self.knowledge_base.search(query, k=3)
                
                if search_results:
                    # Extract relevant context
                    context = "\n\n".join([r['content'] for r in search_results[:2]])
                    
                    # Generate response based on context
                    response = self._generate_response(query, context)
                else:
                    response = "மன்னிக்கவும், உங்கள் கேள்விக்கான தகவல் எனது ஆவணங்களில் கிடைக்கவில்லை."
                    
            except Exception as e:
                print(f"❌ அறிவுத் தள தேடல் பிழை: {e}")
                response = "மன்னிக்கவும், தேடலில் பிழை ஏற்பட்டுள்ளது."
        else:
            response = "அறிவுத் தளம் தயார் நிலையில் இல்லை."
        
        # Add to conversation history
        self._add_to_history("assistant", response)
        
        return response
    
    def _generate_response(self, query: str, context: str) -> str:
        """
        Generate response based on query and context
        
        Args:
            query: User query
            context: Retrieved context from knowledge base
            
        Returns:
            Generated response
        """
        # Simple rule-based response generation
        # In production, you would use an LLM here
        
        response_templates = [
            "எனது குறிப்புகளின்படி: {context}\n\nஇது உங்கள் கேள்விக்கான பதில்: இதில் இருந்து, {query} பற்றி மேலே கொடுக்கப்பட்ட தகவல்கள் உள்ளன.",
            "ஆவணங்களிலிருந்து கிடைத்த தகவல்:\n{context}\n\n{query} - இது பற்றி மேலே உள்ள தகவல்களைப் பார்க்கவும்.",
            "எனது தரவுகளின்படி:\n{context}\n\nஇந்தத் தகவல்களின் அடிப்படையில், உங்கள் கேள்விக்கான பதில் காணப்படுகிறது."
        ]
        
        import random
        template = random.choice(response_templates)
        
        # Truncate context if too long
        if len(context) > 500:
            context = context[:497] + "..."
        
        response = template.format(context=context, query=query)
        return response
    
    def _handle_special_commands(self, query: str) -> Optional[str]:
        """
        Handle special commands
        
        Args:
            query: User query
            
        Returns:
            Response if it's a special command, None otherwise
        """
        query_lower = query.lower()
        
        # Greetings
        greetings = ['வணக்கம்', 'ஹலோ', 'hello', 'hi', 'ஹாய்']
        if any(greet in query_lower for greet in greetings):
            import random
            return random.choice(self.greetings)
        
        # Help
        if 'உதவி' in query or 'help' in query_lower:
            return self._get_help_response()
        
        # About
        if 'உனக்கு பற்றி' in query or 'about' in query_lower:
            return self._get_about_response()
        
        # Stats
        if 'புள்ளிவிவரம்' in query or 'stats' in query_lower:
            return self._get_stats_response()
        
        # Exit/Stop
        if self.exit_word in query or 'exit' in query_lower or 'stop' in query_lower:
            return "நன்றி! பின்னர் சந்திப்போம். நிறுத்த கட்டளையை அனுப்பவும்."
        
        return None
    
    def _get_help_response(self) -> str:
        """Get help response"""
        return """உதவி விருப்பங்கள்:

1. உங்கள் திட்டங்களைப் பற்றி கேளுங்கள்
   எ.கா: "வார இறுதி திட்டங்கள் என்ன?"
   
2. ஆவணங்களை சேர்க்க
   "ஆவணம் சேர்" என்று சொல்லவும்
   
3. புள்ளிவிவரங்களைப் பார்க்க
   "புள்ளிவிவரம்" என்று சொல்லவும்
   
4. நிறுத்த
   "நிறுத்து" என்று சொல்லவும்

நான் உங்கள் தமிழ் ஆவணங்களிலிருந்து பதிலளிப்பேன்."""
    
    def _get_about_response(self) -> str:
        """Get about response"""
        doc_count = len(self.document_processor.list_documents()) if self.document_processor else 0
        return f"""நான் உங்கள் தமிழ் திட்ட உதவியாளர்.

• மொழி: தமிழ்
• ஆவணங்கள்: {doc_count}
• செயல்பாடு: உங்கள் திட்ட ஆவணங்களிலிருந்து பதிலளித்தல்
• பதிப்பு: 1.0

நீங்கள் சேமித்த திட்டங்கள் மற்றும் குறிப்புகளின் அடிப்படையில் நான் பதிலளிப்பேன்."""
    
    def _get_stats_response(self) -> str:
        """Get statistics response"""
        if not self.knowledge_base:
            return "அறிவுத் தளம் தயார் நிலையில் இல்லை."
        
        stats = self.knowledge_base.get_stats()
        
        return f"""அறிவுத் தள புள்ளிவிவரங்கள்:

• ஆவணங்கள்: {stats.get('document_count', 0)}
• பகுதிகள்: {stats.get('chunk_count', 0)}
• கடைசி புதுப்பிப்பு: {stats.get('last_updated', 'இல்லை')}
• உரையாடல் வரலாறு: {len(self.conversation_history)}"""
    
    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        if self.config.get('assistant', {}).get('enable_history', True):
            max_history = self.config.get('assistant', {}).get('max_history', 10)
            
            self.conversation_history.append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last N messages
            if len(self.conversation_history) > max_history:
                self.conversation_history = self.conversation_history[-max_history:]
    
    def start_continuous_listening(self):
        """Start continuous voice listening"""
        if not self.stt_engine:
            print("❌ STT பொறி தயார் நிலையில் இல்லை")
            return
        
        print("🎤 தொடர்ச்சியான கேட்டல் தொடங்கியது...")
        print(f"💡 முன்கூட்டியே சொல்ல: '{self.wake_word}'")
        print(f"💡 நிறுத்த: '{self.exit_word}' அல்லது CTRL+C")
        print("-" * 50)
        
        self.is_listening = True
        self.stop_event.clear()
        
        # Speak welcome message
        self.speak_response("தமிழ் குரு உதவியாளர் தயார். உதவி என்று சொல்லுங்கள்.")
        
        try:
            while not self.stop_event.is_set():
                # Listen for audio
                print("\n🔴 கேட்கிறது... (பேசுங்கள்)")
                transcribed_text, audio_data = self.stt_engine.listen_and_transcribe(duration=5)
                
                if transcribed_text:
                    # Check for wake word
                    if self.wake_word in transcribed_text or self.is_listening:
                        # Remove wake word from query
                        query = transcribed_text.replace(self.wake_word, "").strip()
                        
                        if query:
                            # Process the query
                            response = self.process_text_query(query)
                            
                            # Speak the response
                            self.speak_response(response)
                    
                    # Check for exit word
                    if self.exit_word in transcribed_text:
                        self.speak_response("நன்றி, பயன்பாட்டை மூடுகிறது.")
                        break
                
                # Small delay between listening cycles
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n⏹️ கேட்டல் நிறுத்தப்பட்டது")
        finally:
            self.is_listening = False
    
    def rebuild_knowledge_base(self):
        """Rebuild the knowledge base with current documents"""
        if self.knowledge_base:
            print("🔄 அறிவுத் தளத்தை மீண்டும் உருவாக்குகிறது...")
            self.knowledge_base.build_knowledge_base(force_rebuild=True)
            print("✅ அறிவுத் தளம் மீண்டும் உருவாக்கப்பட்டது")
    
    def get_conversation_history(self):
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ உரையாடல் வரலாறு அழிக்கப்பட்டது")