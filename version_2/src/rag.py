"""
RAG (Retrieval-Augmented Generation) module
Handles document loading, chunking, embedding, and retrieval using FAISS

IMPORTANT: After this change you must:
1. Make sure nomic-embed-text is pulled: ollama pull nomic-embed-text
2. Delete database/vector_store/ folder
3. Run: python build_index.py to rebuild the index with new 768-dim vectors
"""

import os
import pickle
import numpy as np
import faiss
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
import PyPDF2
from config import (
    DOCUMENTS_PATH, VECTOR_STORE_PATH, EMBEDDING_MODEL, OLLAMA_EMBED_URL,
    CHUNK_SIZE, CHUNK_OVERLAP, TOP_K
)

_embed_session = requests.Session()


def get_embedding(text: str) -> list:
    """Get embedding vector from nomic-embed-text via Ollama"""
    try:
        response = _embed_session.post(
            OLLAMA_EMBED_URL,
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=(5, 60)
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.ConnectionError:
        print("[RAG] ERROR: Ollama must be running for embeddings. Run: ollama serve")
        raise
    except Exception as e:
        print(f"[RAG] ERROR: Failed to get embedding: {e}")
        raise


class RAGSystem:
    """
    Manages document indexing and retrieval using FAISS vector store.
    Embeds documents using nomic-embed-text via Ollama.
    """
    
    def __init__(self):
        """Initialize RAG system, build or load vector store."""
        print("Initializing RAG system...")
        
        print(f"Using embedding model: {EMBEDDING_MODEL} via Ollama...")
        # Test connection
        try:
            test_embedding = get_embedding("test")
            print(f"✓ Embedding model ready (dimension: {len(test_embedding)})")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama embedding service: {e}")
            raise
        
        index_path = os.path.join(VECTOR_STORE_PATH, "faiss.index")
        chunks_path = os.path.join(VECTOR_STORE_PATH, "chunks.pkl")
        
        if os.path.exists(index_path) and os.path.exists(chunks_path):
            print("Loading existing vector store...")
            self._load_vector_store()
        else:
            print("Building new vector store from documents...")
            self._build_vector_store()
        
        print(f"✓ RAG system ready ({len(self.chunks)} chunks indexed)")
    
    def _load_documents(self):
        """Load all .txt and .pdf files from documents folder."""
        documents = []
        
        if not os.path.exists(DOCUMENTS_PATH):
            os.makedirs(DOCUMENTS_PATH)
            print(f"⚠️ Created empty documents folder: {DOCUMENTS_PATH}")
            return documents
        
        for filename in os.listdir(DOCUMENTS_PATH):
            filepath = os.path.join(DOCUMENTS_PATH, filename)
            
            try:
                if filename.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                        documents.append(text)
                        print(f"  ✓ Loaded {filename}")
                
                elif filename.endswith('.pdf'):
                    with open(filepath, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                        documents.append(text)
                        print(f"  ✓ Loaded {filename}")
            
            except Exception as e:
                print(f"  ⚠️ Failed to load {filename}: {e}")
        
        return documents
    
    def _chunk_documents(self, documents):
        """Split documents into chunks with overlap."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len
        )
        
        all_chunks = []
        for doc in documents:
            chunks = text_splitter.split_text(doc)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def _build_vector_store(self):
        """Build FAISS index from documents in documents folder."""
        documents = self._load_documents()
        
        if not documents:
            print("⚠️ No documents found. Add .txt or .pdf files to data/documents/ folder")
            self.chunks = []
            self.index = None
            return
        
        self.chunks = self._chunk_documents(documents)
        print(f"Created {len(self.chunks)} chunks")
        
        print("Generating embeddings via Ollama...")
        embeddings = []
        from tqdm import tqdm
        for chunk in tqdm(self.chunks, desc="Embedding chunks"):
            embedding = get_embedding(chunk)
            embeddings.append(embedding)
        
        embeddings = np.array(embeddings, dtype=np.float32)
        
        # nomic-embed-text produces 768 dimensional vectors
        dimension = embeddings.shape[1]
        print(f"Embedding dimension: {dimension}")
        self.index = faiss.IndexFlatIP(dimension)
        
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        faiss.write_index(self.index, os.path.join(VECTOR_STORE_PATH, "faiss.index"))
        with open(os.path.join(VECTOR_STORE_PATH, "chunks.pkl"), 'wb') as f:
            pickle.dump(self.chunks, f)
        
        print("✓ Vector store built and saved")
    
    def _load_vector_store(self):
        """Load existing FAISS index and chunks from disk."""
        index_path = os.path.join(VECTOR_STORE_PATH, "faiss.index")
        chunks_path = os.path.join(VECTOR_STORE_PATH, "chunks.pkl")
        
        self.index = faiss.read_index(index_path)
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
        
        print("✓ Vector store loaded from disk")
    
    def retrieve(self, query, top_k=TOP_K):
        """Retrieve top-k most relevant chunks for a query."""
        if not self.chunks or self.index is None:
            return "No documents available in the knowledge base."
        
        # Get query embedding via Ollama
        query_embedding = get_embedding(query)
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        retrieved_chunks = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                retrieved_chunks.append(self.chunks[idx])
        
        return "\n\n".join(retrieved_chunks)
