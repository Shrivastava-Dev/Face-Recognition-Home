import cv2
import face_recognition
import pickle
import os
import speech_recognition as sr
import numpy as np
import time
import random
import uuid
from gtts import gTTS
import playsound

# ---------- CONFIGURATION ----------
CAMERA_INDEX = 0
DATABASE_PATH = "database/known_faces.pkl"
TOLERANCE = 0.6
CONFIDENCE_THRESHOLD = 0.3  # DNN detection confidence

GREETING_PHRASES = [
    "Hey {name}! Welcome back to Aditya's home!",
    "Hey hey! Welcome home, {name}!",
    "Look who's here! Welcome back, {name}!",
]

NEW_USER_PHRASES = [
    "Oh, a new friend! What's your name?",
    "Hey there! I don't think we've met. What's your name?",
]

# ---------- LOAD DNN FACE DETECTOR ----------
prototxt_path = "models/deploy.prototxt"
model_path = "models/res10_300x300_ssd_iter_140000.caffemodel"
face_detector = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

# ---------- TTS FUNCTION ----------
def speak(text):
    print(f"[SYSTEM]: {text}")
    try:
        filename = f"temp_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.in')
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"TTS Error: {e}")

# ---------- DATABASE FUNCTIONS ----------
def load_database():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'rb') as f:
            data = pickle.load(f)
        return data['encodings'], data['names']
    else:
        return [], []

def save_database(encodings, names):
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with open(DATABASE_PATH, 'wb') as f:
        pickle.dump({'encodings': encodings, 'names': names}, f)

# ---------- VOICE NAME CAPTURE ----------
def get_name_via_voice():
    recognizer = sr.Recognizer()
    
    speak("You're new here! What's your name?")
    
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... (waiting for you to speak)")
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
                print("Processing...")
                name = recognizer.recognize_google(audio)
                print(f"Heard: {name}")
                return name.strip().title()
            except sr.UnknownValueError:
                speak("Sorry, I couldn't understand. Please say your name again.")
            except Exception as e:
                print(f"Voice error: {e}")
                speak("Something went wrong. Please say your name again.")

# ---------- DNN FACE DETECTION FUNCTION ----------
def detect_faces_dnn(frame):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                   (300, 300), (104.0, 177.0, 123.0))
    face_detector.setInput(blob)
    detections = face_detector.forward()
    
    face_locations = []  # will store as (top, right, bottom, left) to match face_recognition format
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            
            # Ensure coordinates are within frame bounds
            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)
            
            face_locations.append((startY, endX, endY, startX))  # top, right, bottom, left
    
    return face_locations

# ---------- MAIN PROGRAM ----------
def main():
    known_encodings, known_names = load_database()
    
    video_capture = cv2.VideoCapture(CAMERA_INDEX)
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not video_capture.isOpened():
        print("Error: Cannot access camera")
        return
    
    speak("System started. Looking for faces.")
    
    last_greet_time = 0
    greet_cooldown = 8
    
    frame_counter = 0
    PROCESS_EVERY_N_FRAMES = 1  # Balance between speed and responsiveness
    
    face_locations = []
    face_names = []
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        frame_counter += 1
        
        if frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            # Fast DNN-based face detection (works well even at distance)
            face_locations = detect_faces_dnn(frame)
            face_names = []
            
            for (top, right, bottom, left) in face_locations:
                # Crop just the face region for encoding (much faster than full-frame encoding)
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
                    
                    current_time = time.time()
                    
                    if name != "Unknown":
                        if current_time - last_greet_time > greet_cooldown:
                            phrase = random.choice(GREETING_PHRASES).format(name=name)
                            speak(phrase)
                            last_greet_time = current_time
                    else:
                        new_name = get_name_via_voice()
                        known_encodings.append(face_encoding)
                        known_names.append(new_name)
                        save_database(known_encodings, known_names)
                        speak(f"Awesome, {new_name}! You're all set. Welcome to Aditya's home!")
                        last_greet_time = time.time()
                
                face_names.append(name)
        
        # Draw boxes (using last detection results)
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imshow('Face Recognition Home System - Press Q to quit', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()