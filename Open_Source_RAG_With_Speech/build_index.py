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


def check_embedding_model():
    """Check if embedding model exists."""
    from config import EMBEDDING_MODEL_PATH
    
    if not os.path.exists(EMBEDDING_MODEL_PATH):
        print(f"\n❌ Error: Embedding model not found at {EMBEDDING_MODEL_PATH}")
        print("\nPlease run the download command from the README first:")
        print('python -c "')
        print("from sentence_transformers import SentenceTransformer")
        print("model = SentenceTransformer('BAAI/bge-small-en-v1.5')")
        print("model.save('./model/models/bge-small-en-v1.5')")
        print("print('Embedding model saved successfully.')")
        print('"')
        return False
    
    print(f"✓ Embedding model found at {EMBEDDING_MODEL_PATH}")
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
    
    # Step 3: Check embedding model
    if not check_embedding_model():
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
