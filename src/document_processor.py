#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
தமிழ் ஆவண செயலாக்கி
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
from docx import Document

class TamilDocumentProcessor:
    """Process Tamil documents for the knowledge base"""
    
    def __init__(self, documents_dir: str):
        """
        Initialize document processor
        
        Args:
            documents_dir: Directory containing Tamil documents
        """
        self.documents_dir = Path(documents_dir)
        self.supported_extensions = ['.txt', '.pdf', '.docx', '.md']
        
        # Tamil-specific text cleaning patterns
        self.tamil_patterns = {
            'extra_spaces': r'\s+',
            'multiple_newlines': r'\n\s*\n\s*\n+',
            'special_chars': r'[^\u0B80-\u0BFF\s\.\,\?\!\%\$\-\(\)\[\]\:;\'\"\d]'
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all available Tamil documents
        
        Returns:
            List of document information dictionaries
        """
        documents = []
        
        for ext in self.supported_extensions:
            for file_path in self.documents_dir.glob(f"*{ext}"):
                doc_info = {
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime,
                    'extension': ext
                }
                documents.append(doc_info)
        
        # Sort by modified time (newest first)
        documents.sort(key=lambda x: x['modified'], reverse=True)
        
        return documents
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from document based on file type
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted Tamil text
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        try:
            if extension == '.txt':
                return self._read_text_file(path)
            elif extension == '.pdf':
                return self._read_pdf_file(path)
            elif extension == '.docx':
                return self._read_docx_file(path)
            elif extension == '.md':
                return self._read_text_file(path)
            else:
                print(f"⚠️ ஆதரவில்லாத கோப்பு வகை: {extension}")
                return ""
                
        except Exception as e:
            print(f"❌ ஆவணத்தை படிக்க முடியவில்லை {path.name}: {e}")
            return ""
    
    def _read_text_file(self, path: Path) -> str:
        """Read text file with UTF-8 encoding"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            encodings = ['utf-8-sig', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        return f.read()
                except:
                    continue
            return ""
    
    def _read_pdf_file(self, path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"❌ PDF பிழை: {e}")
        
        return text
    
    def _read_docx_file(self, path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"❌ DOCX பிழை: {e}")
            return ""
    
    def clean_tamil_text(self, text: str) -> str:
        """
        Clean and normalize Tamil text
        
        Args:
            text: Raw Tamil text
            
        Returns:
            Cleaned Tamil text
        """
        if not text:
            return ""
        
        # Remove special characters (keep Tamil and basic punctuation)
        text = re.sub(self.tamil_patterns['special_chars'], ' ', text)
        
        # Normalize whitespace
        text = re.sub(self.tamil_patterns['extra_spaces'], ' ', text)
        
        # Normalize newlines
        text = re.sub(self.tamil_patterns['multiple_newlines'], '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, 
                         overlap: int = 200) -> List[str]:
        """
        Split Tamil text into chunks for processing
        
        Args:
            text: Tamil text to split
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Clean text first
        text = self.clean_tamil_text(text)
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + chunk_size
            
            # If we're not at the end, try to find a good breaking point
            if end < text_length:
                # Try to break at sentence end
                sentence_end = text.rfind('.', start, end)
                paragraph_end = text.rfind('\n', start, end)
                
                if sentence_end > start and (end - sentence_end) < 100:
                    end = sentence_end + 1
                elif paragraph_end > start and (end - paragraph_end) < 50:
                    end = paragraph_end + 1
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position (with overlap)
            start = end - overlap if (end - overlap) > start else end
        
        return chunks
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze Tamil document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Document analysis information
        """
        text = self.extract_text(file_path)
        cleaned_text = self.clean_tamil_text(text)
        chunks = self.split_into_chunks(cleaned_text)
        
        # Basic analysis
        analysis = {
            'file_name': Path(file_path).name,
            'original_size': len(text),
            'cleaned_size': len(cleaned_text),
            'chunk_count': len(chunks),
            'tamil_char_count': sum(1 for c in cleaned_text if '\u0B80' <= c <= '\u0BFF'),
            'word_count': len(cleaned_text.split()),
            'sample_text': cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text
        }
        
        return analysis
    
    def create_document_summary(self, file_path: str) -> str:
        """
        Create a summary of Tamil document
        
        Args:
            file_path: Path to document file
            
        Returns:
            Document summary in Tamil
        """
        analysis = self.analyze_document(file_path)
        
        summary = f"""
📄 ஆவணம்: {analysis['file_name']}
📊 புள்ளிவிவரங்கள்:
  • எழுத்துக்கள்: {analysis['cleaned_size']:,}
  • தமிழ் எழுத்துக்கள்: {analysis['tamil_char_count']:,}
  • சொற்கள்: {analysis['word_count']:,}
  • பகுதிகள்: {analysis['chunk_count']}
  
🔍 மாதிரி உரை:
{analysis['sample_text']}
        """
        
        return summary