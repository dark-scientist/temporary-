"""
Voice RAG Pipeline - Main application loop
Orchestrates STT, RAG, LLM, and TTS in a continuous loop
"""

import sys
import time
from stt import SpeechToText
from rag import RAGSystem
from llm import OllamaLLM
from tts import TextToSpeech
from audio import record_audio
from config import OLLAMA_MODEL
from logger import RAGLogger


def check_ollama():
    """Check if Ollama server is running."""
    llm = OllamaLLM()
    if not llm.check_ollama_running():
        print("\n" + "="*60)
        print("❌ ERROR: Ollama is not running!")
        print("="*60)
        print("Please start Ollama in a separate terminal:")
        print("  > ollama serve")
        print("\nThen run this script again.")
        print("="*60 + "\n")
        return False
    return True


def main():
    """Main application loop."""
    print("\n" + "="*60)
    print("VOICE RAG PIPELINE - Fully Offline")
    print("="*60)
    print(f"Model: {OLLAMA_MODEL}")
    print("="*60 + "\n")
    
    if not check_ollama():
        sys.exit(1)
    
    try:
        print("[INIT] Loading components...\n")
        logger = RAGLogger()
        stt = SpeechToText()
        rag = RAGSystem()
        llm = OllamaLLM()
        tts = TextToSpeech()
        print("\n✓ All components loaded successfully\n")
        logger.log_event("INIT", f"All components loaded. Model: {OLLAMA_MODEL}")
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)
    
    print("="*60)
    print("Ready! Press Ctrl+C to exit")
    print("="*60 + "\n")
    
    try:
        while True:
            input("Press Enter to speak... ")
            
            audio_data = record_audio()
            if audio_data is None:
                print("⚠️ Recording failed, try again\n")
                logger.log_error("AUDIO", "Recording failed")
                continue
            
            print("\n[STT] Transcribing...")
            text = stt.transcribe(audio_data)
            
            if text is None:
                print("⚠️ Didn't catch that, try again\n")
                logger.log_error("STT", "Transcription failed")
                continue
            
            print(f"You said: \"{text}\"\n")
            
            print("[RAG] Retrieving relevant context...")
            context = rag.retrieve(text)
            print(f"Retrieved {len(context)} characters of context\n")
            
            print("[LLM] Generating response...")
            start_time = time.time()
            response = llm.generate(text, context)
            duration = time.time() - start_time
            print(f"Response: {response}\n")
            
            # Log the search
            logger.log_search(
                question=text,
                context=context,
                response=response,
                model=OLLAMA_MODEL,
                duration=duration
            )
            
            print("[TTS] Speaking response...")
            tts.speak(response)
            print("✓ Done\n")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("Goodbye!")
        print("="*60)
        logger.log_event("EXIT", "User terminated session")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.log_error("SYSTEM", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
