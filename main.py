import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"

import cv2
import face_recognition
import pickle
import speech_recognition as sr
import numpy as np
import time
import random
import uuid
import multiprocessing as mp
from gtts import gTTS
import playsound
import pyaudio
from openwakeword.model import Model as WakeWordModel

from Agent import process_command
from logger import log_event

CAMERA_INDEX = 0
DATABASE_PATH = "database/known_faces.pkl"
TOLERANCE = 0.6
CONFIDENCE_THRESHOLD = 0.5
PROCESS_EVERY_N_FRAMES = 3
MAX_COMMAND_RETRIES = 3
AUDIO_GAIN = 5

GREETING_PHRASES = [
    "Hey {name}! Welcome back to Aditya's home!",
    "Hey hey! Welcome home, {name}!",
    "Look who's here! Welcome back, {name}!",
]

NEW_USER_PHRASES = [
    "Oh, a new friend! What's your name?",
    "Hey there! I don't think we've met. What's your name?",
]

RETRY_PHRASES = [
    "Sorry, I didn't catch that. Please repeat?",
    "Hmm, could you say that again?",
]

def speak(text, audio_lock=None):
    print(f"[SYSTEM]: {text}")
    try:
        filename = f"temp_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.in')
        tts.save(filename)
        
        if audio_lock:
            with audio_lock:
                playsound.playsound(filename)
        else:
            playsound.playsound(filename)
        
        os.remove(filename)
    except Exception as e:
        print(f"TTS Error (continuing anyway): {e}")

def load_database():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'rb') as f:
            data = pickle.load(f)
        return data['encodings'], data['names']
    return [], []

def save_database(encodings, names):
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with open(DATABASE_PATH, 'wb') as f:
        pickle.dump({'encodings': encodings, 'names': names}, f)

def get_name_via_voice(audio_lock):
    recognizer = sr.Recognizer()
    speak(random.choice(NEW_USER_PHRASES), audio_lock)
    
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for name...")
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
                name = recognizer.recognize_google(audio)
                print(f"Heard: {name}")
                return name.strip().title()
            except sr.UnknownValueError:
                speak("Sorry, please say your name again.", audio_lock)
            except Exception as e:
                print(f"Voice error: {e}")

def detect_faces_dnn(frame, face_detector):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                   (300, 300), (104.0, 177.0, 123.0))
    face_detector.setInput(blob)
    detections = face_detector.forward()
    
    face_locations = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)
            face_locations.append((startY, endX, endY, startX))
    return face_locations

def face_recognition_process(pause_event, stop_event, audio_lock):
    print("[Face Recognition] Process started")
    cv2.setNumThreads(2)
    
    prototxt_path = "models/deploy.prototxt"
    model_path = "models/res10_300x300_ssd_iter_140000.caffemodel"
    face_detector = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    
    known_encodings, known_names = load_database()
    
    video_capture = cv2.VideoCapture(CAMERA_INDEX)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    greeted_names = set()
    frame_count = 0
    face_locations = []
    face_names = []
    
    try:
        while not stop_event.is_set():
            if pause_event.is_set():
                time.sleep(0.1)
                continue
            
            ret, frame = video_capture.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            
            if frame_count % PROCESS_EVERY_N_FRAMES == 0:
                face_locations = detect_faces_dnn(frame, face_detector)
                face_names = []
                
                for (top, right, bottom, left) in face_locations:
                    face_image = frame[top:bottom, left:right]
                    rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                    encodings = face_recognition.face_encodings(rgb_face)
                    
                    name = "Unknown"
                    if len(encodings) > 0:
                        face_encoding = encodings[0]
                        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
                        
                        if True in matches:
                            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = known_names[best_match_index]
                        
                        # KEY FIX: Check pause_event AGAIN right before speaking
                        # If Jarvis just became active, skip this greeting for now
                        # (name stays out of greeted_names, will be greeted next cycle)
                        if pause_event.is_set():
                            continue
                        
                        if name != "Unknown":
                            if name not in greeted_names:
                                phrase = random.choice(GREETING_PHRASES).format(name=name)
                                speak(phrase, audio_lock)
                                log_event("face_recognized", name=name)
                                greeted_names.add(name)
                        else:
                            pause_event.set()
                            new_name = get_name_via_voice(audio_lock)
                            known_encodings.append(face_encoding)
                            known_names.append(new_name)
                            save_database(known_encodings, known_names)
                            speak(f"Awesome, {new_name}! Welcome to Aditya's home!", audio_lock)
                            log_event("new_registration", name=new_name)
                            greeted_names.add(new_name)
                            pause_event.clear()
                    
                    face_names.append(name)
            
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.putText(frame, "ACTIVE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Smart Home - Face Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[Face Recognition] ERROR: {e}")
    finally:
        video_capture.release()
        cv2.destroyAllWindows()
        print("[Face Recognition] Process stopped")

def run_command_listening(audio_lock):
    print("\n=== WAKE WORD DETECTED - PAUSING FACE RECOGNITION ===")
    speak("Yes, I am listening", audio_lock)
    
    recognizer = sr.Recognizer()
    attempt = 0
    
    while attempt < MAX_COMMAND_RETRIES:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=13, phrase_time_limit=10)
                command = recognizer.recognize_google(audio)
                print(f"Command heard: {command}")
                
                response_text = process_command(command)
                speak(response_text, audio_lock)
                break
                
            except sr.WaitTimeoutError:
                print("[No speech detected within 13 seconds - silently returning]")
                print("=== RESUMING FACE RECOGNITION ===\n")
                return
                
            except sr.UnknownValueError:
                attempt += 1
                print(f"[Retry {attempt}/{MAX_COMMAND_RETRIES}] Could not understand")
                if attempt < MAX_COMMAND_RETRIES:
                    speak(random.choice(RETRY_PHRASES), audio_lock)
                else:
                    speak("I'm still having trouble understanding. Let's try again later.", audio_lock)
    
    print("=== RESUMING FACE RECOGNITION ===\n")

def wake_word_process(pause_event, stop_event, audio_lock):
    print("[Wake Word] Initializing...")
    
    CHUNK = 1280
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    audio = pyaudio.PyAudio()
    
    def open_fresh_stream():
        return audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                           input=True, frames_per_buffer=CHUNK)
    
    def read_amplified_chunk(stream):
        raw_data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        
        peak = np.abs(raw_data).max()
        
        if peak > 0:
            target_peak = 32767 * 0.7
            gain = min(target_peak / peak, AUDIO_GAIN)
        else:
            gain = 1
        
        amplified = np.clip(raw_data.astype(np.float32) * gain, -32768, 32767).astype(np.int16)
        return amplified
    
    try:
        wake_model = WakeWordModel(wakeword_models=["hey_jarvis"])
        stream = open_fresh_stream()
        
        WARMUP_CHUNKS = 15
        print("[Wake Word] Warming up...")
        for _ in range(WARMUP_CHUNKS):
            audio_data = read_amplified_chunk(stream)
            wake_model.predict(audio_data)
        
        print(f"[Wake Word] READY - You can now say 'Hey Jarvis'")
        
        consecutive_high_scores = 0
        
        while not stop_event.is_set():
            audio_data = read_amplified_chunk(stream)
            prediction = wake_model.predict(audio_data)
            
            max_score = max(prediction.values()) if prediction else 0
            
            if max_score > 0.2:
                print(f"[DEBUG] hey_jarvis: {max_score:.3f}")
            
            if max_score > 0.2:
                consecutive_high_scores += 1
            else:
                consecutive_high_scores = 0
            
            if max_score > 0.3 or consecutive_high_scores >= 2:
                print(">>> WAKE WORD TRIGGERED <<<")
                consecutive_high_scores = 0
                
                # Set pause IMMEDIATELY, before anything else
                pause_event.set()
                
                stream.close()
                run_command_listening(audio_lock)
                
                stream = open_fresh_stream()
                wake_model = WakeWordModel(wakeword_models=["hey_jarvis"])
                
                for _ in range(WARMUP_CHUNKS):
                    audio_data = read_amplified_chunk(stream)
                    wake_model.predict(audio_data)
                
                print("[Wake Word] READY again")
                pause_event.clear()
        
        stream.close()
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[Wake Word] ERROR: {e}")
    finally:
        audio.terminate()
        print("[Wake Word] Process stopped")

def main():
    print("=== SMART HOME SYSTEM STARTED ===")
    speak("System started")
    
    pause_face_recognition = mp.Event()
    stop_all = mp.Event()
    audio_lock = mp.Lock()
    
    p_wake = mp.Process(target=wake_word_process, args=(pause_face_recognition, stop_all, audio_lock))
    p_face = mp.Process(target=face_recognition_process, args=(pause_face_recognition, stop_all, audio_lock))
    
    p_wake.start()
    time.sleep(3)
    p_face.start()
    
    try:
        while not stop_all.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Shutting down...")
        stop_all.set()
    
    p_face.join(timeout=5)
    p_wake.join(timeout=5)
    
    if p_face.is_alive():
        p_face.terminate()
    if p_wake.is_alive():
        p_wake.terminate()

if __name__ == "__main__":
    mp.freeze_support()
    main()