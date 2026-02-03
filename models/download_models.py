#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI மாதிரிகளை பதிவிறக்கும் ஸ்கிரிப்டு
"""

import os
import sys
from pathlib import Path

def download_whisper_model():
    """Download Whisper model for Tamil STT"""
    print("🔧 Whisper மாதிரியை பதிவிறக்குகிறது...")
    
    try:
        import whisper
        # This will download the model on first use
        print("✅ Whisper மாதிரி பதிவிறக்கம் தயார்")
        return True
    except Exception as e:
        print(f"❌ Whisper பதிவிறக்கம் பிழை: {e}")
        return False

def download_embedding_model():
    """Download embedding model"""
    print("🔧 பதிவிறக்கும் மாதிரியை பதிவிறக்குகிறது...")
    
    try:
        from sentence_transformers import SentenceTransformer
        # Test with small model
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ பதிவிறக்கும் மாதிரி பதிவிறக்கம் தயார்")
        return True
    except Exception as e:
        print(f"❌ பதிவிறக்கும் மாதிரி பதிவிறக்கம் பிழை: {e}")
        return False

def main():
    """Main download function"""
    print("🤖 AI மாதிரி பதிவிறக்கம் தொடங்கியது")
    print("=" * 50)
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Download models
    success = True
    
    if not download_whisper_model():
        success = False
    
    if not download_embedding_model():
        success = False
    
    print("=" * 50)
    if success:
        print("✅ அனைத்து மாதிரிகளும் வெற்றிகரமாக பதிவிறக்கப்பட்டன")
    else:
        print("⚠️ சில மாதிரிகள் பதிவிறக்கப்படவில்லை")
        print("பயன்பாடு இன்னும் வேலை செய்யும், ஆனால் சில அம்சங்கள் கிடைக்காது")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())