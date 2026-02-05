#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
தமிழ் அறிவுத் தளம் (Knowledge Base)
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document as LangchainDocument

class TamilKnowledgeBase:
    """Knowledge base for Tamil documents using vector embeddings"""
    
    def __init__(self, documents_dir: str, persist_dir: str = "./data/chroma_db"):
        """
        Initialize knowledge base
        
        Args:
            documents_dir: Directory containing Tamil documents
            persist_dir: Directory to persist vector database
        """
        self.documents_dir = Path(documents_dir)
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        
        # Metadata
        self.metadata_file = self.persist_dir / "metadata.json"
        self.metadata = self.load_metadata()
        
        # Initialize embedding model
        self._init_embeddings()
        
    def _init_embeddings(self):
        """Initialize multilingual embedding model"""
        try:
            print("🔧 பதிவிறக்கும் பதிப்பு மாதிரி...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ பதிவிறக்கும் மாதிரி தயார்")
        except Exception as e:
            print(f"❌ பதிவிறக்கும் மாதிரி பிழை: {e}")
            raise
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load knowledge base metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'created_at': datetime.now().isoformat(),
            'last_updated': None,
            'document_count': 0,
            'chunk_count': 0,
            'documents': []
        }
    
    def save_metadata(self):
        """Save knowledge base metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def create_text_splitter(self):
        """Create text splitter optimized for Tamil"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=[
                "\n\n",
                "\n",
                "।",  # Tamil full stop
                ".",
                ",",
                " ",
                ""
            ]
        )
    
    def process_documents(self) -> List[LangchainDocument]:
        """
        Process all Tamil documents into chunks
        
        Returns:
            List of document chunks
        """
        from src.document_processor import TamilDocumentProcessor
        
        processor = TamilDocumentProcessor(str(self.documents_dir))
        all_documents = processor.list_documents()
        
        if not all_documents:
            print("⚠️ செயலாக்கத்திற்கு ஆவணங்கள் இல்லை")
            return []
        
        print(f"📄 {len(all_documents)} ஆவண(ங்கள்) செயலாக்கப்படுகின்றன...")
        
        all_chunks = []
        
        for doc_info in all_documents:
            print(f"  • {doc_info['name']}...")
            
            # Extract text
            text = processor.extract_text(doc_info['path'])
            if not text:
                print(f"    ⚠️ வெற்று உரை, தவிர்க்கப்பட்டது")
                continue
            
            # Clean Tamil text
            cleaned_text = processor.clean_tamil_text(text)
            
            # Split into chunks
            if self.text_splitter is None:
                self.create_text_splitter()
            
            chunks = self.text_splitter.split_text(cleaned_text)
            
            # Create Langchain documents with metadata
            for i, chunk in enumerate(chunks):
                langchain_doc = LangchainDocument(
                    page_content=chunk,
                    metadata={
                        'source': doc_info['name'],
                        'source_path': doc_info['path'],
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'language': 'ta',
                        'processed_at': datetime.now().isoformat()
                    }
                )
                all_chunks.append(langchain_doc)
            
            print(f"    ✅ {len(chunks)} பகுதி(கள்) உருவாக்கப்பட்டது")
        
        print(f"📊 மொத்தம் {len(all_chunks)} பகுதி(கள்) உருவாக்கப்பட்டது")
        return all_chunks
    
    def build_knowledge_base(self, force_rebuild: bool = False):
        """
        Build or rebuild the knowledge base
        
        Args:
            force_rebuild: Whether to force rebuild existing knowledge base
        """
        # Check if knowledge base already exists
        if not force_rebuild and self.is_knowledge_base_exists():
            print("📚 ஏற்கனவே உள்ள அறிவுத் தளத்தை ஏற்றுகிறது...")
            self.load_existing_knowledge_base()
            return
        
        print("🏗️ புதிய அறிவுத் தளத்தை உருவாக்குகிறது...")
        
        # Process documents
        documents = self.process_documents()
        
        if not documents:
            print("❌ அறிவுத் தளத்தை உருவாக்க ஆவணங்கள் இல்லை")
            return
        
        # Create vector store
        print("🔢 திசையன் தளத்தை உருவாக்குகிறது...")
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.persist_dir)
        )
        
        # Persist the database
        self.vectorstore.persist()
        
        # Update metadata
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['document_count'] = len(set(doc.metadata['source'] for doc in documents))
        self.metadata['chunk_count'] = len(documents)
        self.metadata['documents'] = [
            {
                'name': doc.metadata['source'],
                'chunks': doc.metadata['total_chunks'],
                'added_at': doc.metadata['processed_at']
            }
            for doc in documents if doc.metadata.get('chunk_index', 0) == 0
        ]
        
        self.save_metadata()
        
        print(f"✅ அறிவுத் தளம் உருவாக்கப்பட்டது:")
        print(f"   • ஆவணங்கள்: {self.metadata['document_count']}")
        print(f"   • பகுதிகள்: {self.metadata['chunk_count']}")
        print(f"   • இடம்: {self.persist_dir}")
    
    def load_existing_knowledge_base(self):
        """Load existing knowledge base from disk"""
        try:
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_dir),
                embedding_function=self.embeddings
            )
            print("✅ அறிவுத் தளம் ஏற்றப்பட்டது")
        except Exception as e:
            print(f"❌ அறிவுத் தளத்தை ஏற்ற முடியவில்லை: {e}")
            print("🔄 மீண்டும் உருவாக்க முயற்சிக்கிறது...")
            self.build_knowledge_base(force_rebuild=True)
    
    def is_knowledge_base_exists(self) -> bool:
        """Check if knowledge base exists"""
        # Check for Chroma index files
        index_files = ['chroma.sqlite3', 'index']
        for file in index_files:
            if (self.persist_dir / file).exists():
                return True
        return False
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the knowledge base
        
        Args:
            query: Tamil search query
            k: Number of results to return
            
        Returns:
            List of search results
        """
        if self.vectorstore is None:
            print("⚠️ அறிவுத் தளம் ஏற்கனவே உள்ளது. முதலில் உருவாக்கவும்.")
            return []
        
        try:
            # Add Tamil context to query
            enhanced_query = f"தமிழ் ஆவணங்கள்: {query}"
            
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_relevance_scores(
                enhanced_query,
                k=k
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'Unknown'),
                    'chunk': doc.metadata.get('chunk_index', 0) + 1,
                    'score': float(score),
                    'language': 'ta'
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ தேடல் பிழை: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        if self.vectorstore is None:
            self.load_existing_knowledge_base()
        
        stats = self.metadata.copy()
        
        # Add vector store info if available
        if self.vectorstore:
            try:
                stats['collection_size'] = self.vectorstore._collection.count()
            except:
                stats['collection_size'] = 'Unknown'
        
        return stats
    
    def clear_knowledge_base(self):
        """Clear the knowledge base"""
        import shutil
        
        if self.persist_dir.exists():
            try:
                shutil.rmtree(self.persist_dir)
                print("🧹 அறிவுத் தளம் அழிக்கப்பட்டது")
                
                # Reset metadata
                self.metadata = {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': None,
                    'document_count': 0,
                    'chunk_count': 0,
                    'documents': []
                }
                self.save_metadata()
                
            except Exception as e:
                print(f"❌ அறிவுத் தளத்தை அழிக்க முடியவில்லை: {e}")