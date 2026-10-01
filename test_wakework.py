import pyaudio
import numpy as np
from openwakeword.model import Model

model = Model(wakeword_models=["hey_jarvis"])

CHUNK = 1280
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
MIC_INDEX = 11

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                     input=True, frames_per_buffer=CHUNK,
                     input_device_index=MIC_INDEX)

print("Listening... (Press Ctrl+C to stop)")

try:
    while True:
        audio_data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        
        # Print audio level to confirm mic is actually capturing sound
        volume = np.abs(audio_data).mean()
        
        prediction = model.predict(audio_data)
        
        for wake_word, score in prediction.items():
            print(f"Volume: {volume:.1f} | {wake_word}: {score:.4f}")
                
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.close()
    audio.terminate()