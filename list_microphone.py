import sounddevice as sd
import numpy as np

print("Available devices:")
print(sd.query_devices())

print("\n--- Testing default input device ---")
print("Speak now for 5 seconds...")

duration = 5  # seconds
sample_rate = 16000

recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
sd.wait()

volume = np.abs(recording).mean()
max_vol = np.abs(recording).max()

print(f"\nAverage volume: {volume}")
print(f"Max volume: {max_vol}")

if max_vol > 100:
    print("✅ Microphone IS capturing audio!")
else:
    print("❌ Microphone is NOT capturing audio (silence detected)")