#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
தமிழ் உரை-பேச்சு மாற்றி (Text-to-Speech Engine)
"""

import os
import tempfile
import hashlib
from pathlib import Path
from gtts import gTTS
import playsound

class TamilTTSEngine:
    """Tamil Text-to-Speech Engine using multiple backends"""
    
    def __init__(self, cache_dir="./data/audio_cache", use_cache=True):
        """
        Initialize Tamil TTS Engine
        
        Args:
            cache_dir: Directory to cache audio files
            use_cache: Whether to use audio caching
        """
        self.cache_dir = Path(cache_dir)
        self.use_cache = use_cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Tamil voice configuration
        self.language = "ta"
        self.tld = "co.in"  # Indian domain for better Tamil pronunciation
        
    def text_to_hash(self, text: str) -> str:
        """
        Generate hash for Tamil text
        
        Args:
            text: Tamil text
            
        Returns:
            MD5 hash of text
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_cached_audio(self, text: str) -> Optional[str]:
        """
        Get cached audio file path for text
        
        Args:
            text: Tamil text
            
        Returns:
            Path to cached audio file or None
        """
        if not self.use_cache:
            return None
            
        text_hash = self.text_to_hash(text)
        audio_file = self.cache_dir / f"{text_hash}.mp3"
        
        if audio_file.exists():
            return str(audio_file)
        
        return None
    
    def cache_audio(self, text: str, audio_file: str):
        """
        Cache audio file for text
        
        Args:
            text: Tamil text
            audio_file: Path to audio file
        """
        if not self.use_cache:
            return
            
        text_hash = self.text_to_hash(text)
        dest_file = self.cache_dir / f"{text_hash}.mp3"
        
        try:
            import shutil
            shutil.copy2(audio_file, dest_file)
        except Exception as e:
            print(f"⚠️ கேச் செய்ய முடியவில்லை: {e}")
    
    def speak_gtts(self, text: str, slow: bool = False, wait: bool = True) -> str:
        """
        Convert Tamil text to speech using gTTS (Google)
        
        Args:
            text: Tamil text to speak
            slow: Whether to speak slowly
            wait: Whether to wait for playback to finish
            
        Returns:
            Path to audio file
        """
        print(f"🔊 பேசுகிறது: {text[:50]}..." if len(text) > 50 else f"🔊 பேசுகிறது: {text}")
        
        # Check cache first
        cached_file = self.get_cached_audio(text)
        if cached_file:
            print("💾 கேச் செய்யப்பட்ட குரு பயன்படுத்தப்படுகிறது")
            if wait:
                playsound.playsound(cached_file)
            return cached_file
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                temp_audio = tmp.name
            
            # Generate Tamil speech with Indian domain
            tts = gTTS(
                text=text,
                lang=self.language,
                tld=self.tld,
                slow=slow
            )
            
            # Save to file
            tts.save(temp_audio)
            
            # Cache the audio
            self.cache_audio(text, temp_audio)
            
            # Play the audio
            if wait:
                playsound.playsound(temp_audio)
            
            # Clean up temp file after playing
            if wait:
                os.unlink(temp_audio)
                return cached_file if cached_file else temp_audio
            else:
                return temp_audio
                
        except Exception as e:
            print(f"❌ TTS பிழை: {e}")
            # Fallback to English
            try:
                tts = gTTS(text="Sorry, I cannot speak Tamil right now.", lang='en')
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    temp_audio = tmp.name
                tts.save(temp_audio)
                playsound.playsound(temp_audio)
                os.unlink(temp_audio)
            except:
                print("❌ விபத்து தவிர்ப்பு TTS தோல்வி")
            
            return ""
    
    def speak_multiple(self, texts: list, pause_duration: float = 0.5):
        """
        Speak multiple texts with pauses
        
        Args:
            texts: List of Tamil texts to speak
            pause_duration: Pause between texts in seconds
        """
        import time
        
        for i, text in enumerate(texts):
            if text.strip():  # Skip empty texts
                self.speak_gtts(text, wait=True)
                if i < len(texts) - 1:  # Pause except after last text
                    time.sleep(pause_duration)
    
    def get_available_voices(self):
        """
        List available TTS voices/systems
        """
        voices = {
            "gtts": "Google Text-to-Speech (இணையம் தேவை)",
            "pyttsx3": "System TTS (வரையறுக்கப்பட்ட தமிழ் ஆதரவு)",
            "coqui": "Coqui TTS (அதிநவீன, ஆனால் நிறுவுதல் தேவை)"
        }
        
        return voices
    
    def set_voice_speed(self, speed: float):
        """
        Set voice speed (not supported by gTTS)
        
        Note: gTTS only supports slow/normal
        """
        print("ℹ️ gTTS வேக அமைப்புகளை ஆதரிக்கவில்லை. மெதுவாக/இயல்பானது மட்டுமே.")
    
    def test_tamil_pronunciation(self):
        """
        Test Tamil pronunciation with common phrases
        """
        test_phrases = [
            "வணக்கம், நான் உங்கள் தமிழ் உதவியாளர்.",
            "உங்கள் திட்டங்களைப் பற்றி கேளுங்கள்.",
            "நான் உங்கள் குறிப்புகளிலிருந்து பதிலளிப்பேன்.",
            "நன்றி, நல்ல நாள்!"
        ]
        
        print("🎵 தமிழ் உச்சரிப்பு சோதனை...")
        for phrase in test_phrases:
            print(f"  பேசும்: {phrase}")
            self.speak_gtts(phrase, wait=True)
            input("  அடுத்ததற்கு Enter அழுத்தவும்...")