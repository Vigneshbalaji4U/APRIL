#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
தமிழ் பேச்சு-உரை மாற்றி (Speech-to-Text Engine)
"""

import os
import tempfile
import numpy as np
from datetime import datetime
from typing import Optional, Tuple
import sounddevice as sd
import soundfile as sf

class TamilSTTEngine:
    """Tamil Speech-to-Text Engine using Whisper"""
    
    def __init__(self, model_name="base", device=None):
        """
        Initialize Tamil STT Engine
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium)
            device: Computation device (cpu/cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.sample_rate = 16000
        self.audio_cache = {}
        
    def load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            try:
                import whisper
                print(f"🔧 தமிழ் STT மாதிரியை ஏற்றுகிறது: {self.model_name}")
                self.model = whisper.load_model(self.model_name, device=self.device)
                print("✅ STT மாதிரி ஏற்றப்பட்டது")
            except ImportError:
                print("❌ whisper நூலகம் தேவை: pip install openai-whisper")
                raise
        return self.model
    
    def record_audio(self, duration: float = 7.0) -> np.ndarray:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            NumPy array of audio data
        """
        print(f"🔴 பதிவு தொடங்குகிறது ({duration} வினாடிகள்)...")
        
        try:
            # Record audio
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()  # Wait for recording to complete
            
            print("✅ பதிவு முடிந்தது")
            return audio.flatten()
            
        except Exception as e:
            print(f"❌ பதிவில் பிழை: {e}")
            raise
    
    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribe Tamil audio to text
        
        Args:
            audio_data: Audio data as NumPy array
            
        Returns:
            Transcribed Tamil text
        """
        if self.model is None:
            self.load_model()
        
        try:
            # Save to temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, audio_data, self.sample_rate)
            
            # Transcribe with Tamil language specified
            result = self.model.transcribe(
                tmp_path,
                language="ta",  # Tamil language code
                task="transcribe",
                temperature=0.0,
                best_of=1
            )
            
            # Clean up
            os.unlink(tmp_path)
            
            tamil_text = result["text"].strip()
            
            if tamil_text:
                print(f"🎤 கேட்டது: {tamil_text}")
            else:
                print("🎤 கேட்கப்படவில்லை (வெற்று உரை)")
            
            return tamil_text
            
        except Exception as e:
            print(f"❌ படியெடுப்பில் பிழை: {e}")
            return ""
    
    def listen_and_transcribe(self, duration: float = 7.0) -> Tuple[str, np.ndarray]:
        """
        Record and transcribe in one step
        
        Returns:
            Tuple of (transcribed_text, audio_data)
        """
        # Record audio
        audio_data = self.record_audio(duration)
        
        # Transcribe
        text = self.transcribe_audio(audio_data)
        
        return text, audio_data
    
    def realtime_listening(self, callback, stop_event):
        """
        Real-time listening with callback
        
        Args:
            callback: Function to call with transcribed text
            stop_event: Threading event to stop listening
        """
        print("👂 உணர்திறன் கேட்டல் தொடங்கியது...")
        
        chunk_duration = 0.5  # Process in 500ms chunks
        chunk_size = int(self.sample_rate * chunk_duration)
        
        audio_buffer = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"🔊 நிலை: {status}")
            
            # Add to buffer
            audio_buffer.extend(indata[:, 0])
            
            # Process if buffer has enough data
            if len(audio_buffer) >= chunk_size:
                # Extract chunk
                chunk = np.array(audio_buffer[:chunk_size])
                audio_buffer[:] = audio_buffer[chunk_size:]
                
                # Transcribe chunk
                text = self.transcribe_audio(chunk)
                if text:
                    callback(text)
        
        try:
            # Start stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=audio_callback,
                blocksize=chunk_size
            ):
                print("🎧 குரு ஓட்டம் தொடங்கியது...")
                # Wait for stop event
                while not stop_event.is_set():
                    sd.sleep(100)
                    
        except Exception as e:
            print(f"❌ உணர்திறன் கேட்டல் பிழை: {e}")
    
    def save_audio(self, audio_data: np.ndarray, filename: Optional[str] = None):
        """
        Save audio data to file
        
        Args:
            audio_data: Audio data to save
            filename: Output filename (optional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"
        
        sf.write(filename, audio_data, self.sample_rate)
        print(f"💾 குரு சேமிக்கப்பட்டது: {filename}")
        
        return filename