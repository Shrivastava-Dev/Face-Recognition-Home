import pyaudio
import numpy as np

CHUNK = 1280
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

audio = pyaudio.PyAudio()

try:
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                         input=True, frames_per_buffer=CHUNK)
    print("Default stream opened successfully!")
    
    for i in range(30):
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_data).mean()
        print(f"Volume: {volume:.1f}")
    
    stream.close()
    print("SUCCESS")
    
except Exception as e:
    print(f"ERROR: {e}")

audio.terminate()