import speech_recognition as sr

mic_list = sr.Microphone.list_microphone_names()
for index, name in enumerate(mic_list):
    print(f"Index {index}: {name}")