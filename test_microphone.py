import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Adjusting for ambient noise... please wait")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listening... (waiting as long as needed for you to speak)")
    try:
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
        print("Processing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except Exception as e:
        print(f"Error: {e}")