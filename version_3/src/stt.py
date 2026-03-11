"""
Speech-to-Text module using faster-whisper
Transcribes audio to text using CPU-optimized Whisper model
"""

from faster_whisper import WhisperModel
import numpy as np
from config import WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE, SAMPLE_RATE


class SpeechToText:
    """
    Handles speech-to-text transcription using faster-whisper.
    Optimized for CPU with int8 quantization.
    """
    
    def __init__(self):
        """Initialize the Whisper model with CPU optimization."""
        print(f"Loading Whisper model ({WHISPER_MODEL_SIZE})...")
        self.model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE
        )
        print("✓ Whisper model loaded")
    
    def transcribe(self, audio_data):
        """
        Transcribe audio data to text.
        
        Args:
            audio_data (numpy.ndarray): Audio data as float32 array
            
        Returns:
            str: Transcribed text, or None if no speech was detected

        Raises:
            RuntimeError: If the transcription engine fails to decode/process audio
        """
        if audio_data is None or len(audio_data) == 0:
            return None
        
        try:
            segments, info = self.model.transcribe(
                audio_data,
                beam_size=1,
                language="en"
            )
            
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            
            full_text = " ".join(text_parts).strip()
            
            if not full_text or full_text.isspace():
                return None
            
            return full_text
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def transcribe_file(self, audio_file_path):
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            str: Transcribed text, or None if transcription failed/empty
        """
        try:
            segments, info = self.model.transcribe(
                audio_file_path,
                beam_size=1,
                language="en"
            )
            
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            
            full_text = " ".join(text_parts).strip()
            
            if not full_text or full_text.isspace():
                return None
            
            return full_text
            
        except Exception as e:
            raise RuntimeError(f"Transcription engine failed: {e}") from e
