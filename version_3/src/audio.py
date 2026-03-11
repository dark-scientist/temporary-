"""
Audio recording module using sounddevice
Records from microphone with automatic silence detection
"""

import sounddevice as sd
import numpy as np
from config import SAMPLE_RATE, SILENCE_THRESHOLD, SILENCE_DURATION


def record_audio():
    """
    Record audio from microphone with automatic silence detection.
    Stops recording when audio level drops below threshold for specified duration.
    
    Returns:
        numpy.ndarray: Audio data as float32 array, or None if recording failed
    """
    print("🎤 Recording... (speak now, will auto-stop on silence)")
    print("Audio level: ", end="", flush=True)
    
    try:
        audio_chunks = []
        silence_samples = int(SILENCE_DURATION * SAMPLE_RATE)
        silent_chunk_count = 0
        max_duration = 30
        max_samples = max_duration * SAMPLE_RATE
        total_samples = 0
        last_print_time = [0]
        
        def callback(indata, frames, time, status):
            nonlocal silent_chunk_count, total_samples
            
            if status:
                print(f"\nAudio status: {status}")
            
            audio_level = np.sqrt(np.mean(indata**2))
            
            current_time = time.inputBufferAdcTime if time.inputBufferAdcTime else 0
            if current_time - last_print_time[0] > 0.2:
                if audio_level > SILENCE_THRESHOLD * 3:
                    print("█", end="", flush=True)
                elif audio_level > SILENCE_THRESHOLD:
                    print("▓", end="", flush=True)
                else:
                    print("░", end="", flush=True)
                last_print_time[0] = current_time
            
            if audio_level < SILENCE_THRESHOLD:
                silent_chunk_count += frames
            else:
                silent_chunk_count = 0
            
            audio_chunks.append(indata.copy())
            total_samples += frames
            
            if silent_chunk_count >= silence_samples or total_samples >= max_samples:
                raise sd.CallbackStop()
        
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='float32',
            callback=callback
        ):
            sd.sleep(max_duration * 1000)
        
        print()
        
        if not audio_chunks:
            print("⚠️ No audio recorded")
            return None
        
        audio_data = np.concatenate(audio_chunks, axis=0)
        print(f"✓ Recording complete ({len(audio_data)/SAMPLE_RATE:.1f}s)")
        
        return audio_data.flatten()
        
    except Exception as e:
        print(f"❌ Recording error: {e}")
        return None
