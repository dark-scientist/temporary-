"""
Build FAISS Index - Standalone script to index documents
Run this before starting the main application
"""

import os
import sys

# Add src to path
sys.path.insert(0, './src')


def check_documents_folder():
    """Check if documents folder exists and has files."""
    docs_path = "./data/documents"
    
    if not os.path.exists(docs_path):
        print(f"❌ Error: {docs_path} folder not found!")
        print("Please create the folder and add your documents.")
        return False
    
    # Check for .txt or .pdf files
    files = [f for f in os.listdir(docs_path) if f.endswith(('.txt', '.pdf'))]
    
    if not files:
        print("❌ Error: No .txt or .pdf files found in data/documents/")
        print("Please add .txt or .pdf files to data/documents/ before indexing")
        return False
    
    print(f"✓ Found {len(files)} document(s) in {docs_path}")
    return True


def check_existing_index():
    """Check if vector store already exists."""
    vector_store_path = "./database/vector_store"
    
    if os.path.exists(vector_store_path):
        files = os.listdir(vector_store_path)
        if files:
            print(f"\n⚠️  Vector store already exists at {vector_store_path}")
            response = input("Rebuild index? (y/n): ").strip().lower()
            
            if response != 'y':
                print("\n✓ Using existing index. Run app.py to start.")
                return False
            
            print("\n🔄 Rebuilding index...")
    
    return True


def check_ollama_service():
    """Check if Ollama is running and nomic-embed-text is available."""
    import subprocess
    from config import EMBEDDING_MODEL
    
    # Check if Ollama is running
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            print("\n❌ Error: Ollama is not running!")
            print("\nPlease start Ollama first:")
            print("  ollama serve")
            return False
        
        print("✓ Ollama service is running")
        
    except Exception as e:
        print("\n❌ Error: Cannot connect to Ollama")
        print(f"Details: {e}")
        print("\nPlease start Ollama first:")
        print("  ollama serve")
        return False
    
    # Check if nomic-embed-text is pulled
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if EMBEDDING_MODEL not in result.stdout:
            print(f"\n❌ Error: {EMBEDDING_MODEL} model not found!")
            print(f"\nPlease pull the model first:")
            print(f"  ollama pull {EMBEDDING_MODEL}")
            return False
        
        print(f"✓ Embedding model {EMBEDDING_MODEL} is available")
        
    except Exception as e:
        print(f"\n❌ Error checking Ollama models: {e}")
        return False
    
    return True


def build_index():
    """Build the FAISS index."""
    try:
        print("\n" + "="*60)
        print("[RAG] Starting document indexing...")
        print("="*60 + "\n")
        
        # Import RAG system
        from rag import RAGSystem
        
        # Initialize RAG (this will build the index)
        print("[RAG] Loading documents from data/documents/...")
        rag = RAGSystem()
        
        # Get chunk count
        if hasattr(rag, 'chunks') and rag.chunks:
            chunk_count = len(rag.chunks)
            print(f"\n✓ [RAG] Index build complete. Total chunks: {chunk_count}")
        else:
            print("\n✓ [RAG] Index build complete.")
        
        print("\n" + "="*60)
        print("✓ Success! Now run: python app.py")
        print("="*60 + "\n")
        
        return True
    
    except ImportError as e:
        print(f"\n❌ Error: Missing dependencies")
        print(f"Details: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        return False
    
    except Exception as e:
        print(f"\n❌ Error during indexing: {e}")
        return False


def main():
    """Main function."""
    print("\n" + "="*60)
    print("FAISS INDEX BUILDER")
    print("="*60 + "\n")
    
    # Step 1: Check documents folder
    if not check_documents_folder():
        sys.exit(1)
    
    # Step 2: Check if index already exists
    if not check_existing_index():
        sys.exit(0)
    
    # Step 3: Check Ollama service and embedding model
    if not check_ollama_service():
        sys.exit(1)
    
    # Step 4: Build the index
    if not build_index():
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Indexing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
