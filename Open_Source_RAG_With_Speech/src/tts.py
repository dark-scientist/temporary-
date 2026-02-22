"""
Text-to-Speech module using Piper TTS
Converts text to speech and plays audio through speakers
"""

import subprocess
import pyaudio
from config import PIPER_EXE, PIPER_VOICE


class TextToSpeech:
    """
    Handles text-to-speech using Piper TTS via subprocess.
    Generates WAV audio and plays through speakers using PyAudio.
    """
    
    def __init__(self):
        """Initialize TTS system."""
        self.piper_exe = PIPER_EXE
        self.voice_model = PIPER_VOICE
        print("✓ Piper TTS initialized")
    
    def speak(self, text):
        """Convert text to speech and play audio."""
        if not text or text.isspace():
            print("⚠️ No text to speak")
            return False
        
        try:
            process = subprocess.Popen(
                [self.piper_exe, "--model", self.voice_model, "--output-raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate(input=text.encode('utf-8'), timeout=30)
            
            if process.returncode != 0:
                print(f"❌ Piper TTS error: {stderr.decode('utf-8')}")
                return False
            
            self._play_audio(stdout)
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ TTS timeout - text too long")
            process.kill()
            return False
        except FileNotFoundError:
            print(f"❌ Piper executable not found at {self.piper_exe}")
            return False
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return False
    
    def _play_audio(self, raw_audio):
        """Play raw audio data through speakers using PyAudio."""
        try:
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=22050,
                output=True
            )
            
            stream.write(raw_audio)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
