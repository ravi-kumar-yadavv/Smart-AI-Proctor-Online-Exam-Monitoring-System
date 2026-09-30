import csv
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import torch
import threading
import time
import os
import speech_recognition as sr # <--- NEW: Google Speech Recognition

# --- 1. Safe Import for MediaPipe ---
USE_MEDIAPIPE = False
try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    USE_MEDIAPIPE = True
    print("✅ MediaPipe Loaded Successfully (Gaze & Head Tracking Active)")
except Exception as e:
    print(f"⚠️ Warning: MediaPipe Error ({e}). Only YOLO & Audio will work.")
    USE_MEDIAPIPE = False

app = Flask(__name__)
CORS(app)

# --- 2. Load YOLO Model ---
print("Loading AI Models...")
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
yolo_model.conf = 0.40
print("✅ System Ready!")

# --- 3. SPEECH TO TEXT MONITORING (Jasoos Mode) 🕵️‍♂️ ---
speech_warning = False
detected_text = ""

def monitor_speech():
    global speech_warning, detected_text
    recognizer = sr.Recognizer()
    
    # Check Microphone
    try:
        with sr.Microphone() as source:
            print("🎤 Jasoos Mode ON: Listening for whispers...")
            recognizer.adjust_for_ambient_noise(source) # Shor kam karne ke liye
            
            while True:
                try:
                    # Listen for audio (Time limit ensures it doesn't get stuck)
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    
                    # Convert Voice to Text (Google API)
                    text = recognizer.recognize_google(audio)
                    text = text.lower()
                    
                    print(f"🗣️ Heard: {text}") # Console me dikhega
                    
                    # Evidence save karein
                    with open("speech_evidence.txt", "a") as f:
                        t = datetime.now().strftime("%H:%M:%S")
                        f.write(f"[{t}] {text}\n")

                    # Cheating Keywords Check
                    suspicious_words = ['answer', 'bata', 'hello', 'question', 'copy', 'bhai', 'what', 'bol']
                    
                    if any(word in text for word in suspicious_words):
                        print(f"🚨 CAUGHT! Suspicious word detected: {text}")
                        speech_warning = True
                        detected_text = f"Talking: '{text}'"
                        time.sleep(2) # Warning hold karein
                        speech_warning = False
                        
                except sr.WaitTimeoutError:
                    pass # Koi nahi bola, continue karo
                except sr.UnknownValueError:
                    pass # Shor tha, samajh nahi aaya
                except Exception as e:
                    print("Speech Error:", e)
                    
    except Exception as e:
        print("❌ Mic Error: Microphone not found or blocked.")

# Start Jasoos Thread
t = threading.Thread(target=monitor_speech, daemon=True)
t.start()

# --- 4. Helper Functions (Gaze/Head) ---
def get_gaze_direction(face_landmarks, w, h):
    try:
        mesh_points = np.array([np.multiply([p.x, p.y], [w, h]).astype(int) for p in face_landmarks.landmark])
        p1, p2, iris = mesh_points[33], mesh_points[133], mesh_points[468]
        ratio = np.linalg.norm(iris - p1) / np.linalg.norm(p1 - p2)
        if ratio < 0.35: return "Looking Left"
        if ratio > 0.65: return "Looking Right"
        return "Center"
    except: return "Center"

def get_head_pose(face_landmarks, w, h):
    try:
        face_3d, face_2d = [], []
        for idx, lm in enumerate(face_landmarks.landmark):
            if idx in [33, 263, 1, 61, 291, 199]:
                x, y = int(lm.x * w), int(lm.y * h)
                face_2d.append([x, y]); face_3d.append([x, y, lm.z])
        
        face_2d, face_3d = np.array(face_2d, dtype=np.float64), np.array(face_3d, dtype=np.float64)
        focal_length = 1 * w
        cam_matrix = np.array([[focal_length, 0, h/2], [0, focal_length, w/2], [0, 0, 1]])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        rmat, jac = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        
        y_angle, x_angle = angles[1] * 360, angles[0] * 360
        if y_angle < -10: return "Head Left"
        if y_angle > 10: return "Head Right"
        if x_angle < -10: return "Head Down"
        return "Center"
    except: return "Center"

# --- 5. Main Analysis ---
def analyze_advanced(frame):
    warnings = []
    h, w, c = frame.shape
    
    # A. Check Speech Warning (From Jasoos Thread)
    global speech_warning, detected_text
    if speech_warning:
        warnings.append(detected_text)

    # B. MediaPipe (Gaze/Head)
    if USE_MEDIAPIPE:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        if results.multi_face_landmarks:
            for lm in results.multi_face_landmarks:
                gaze = get_gaze_direction(lm, w, h)
                if gaze != "Center": warnings.append(gaze)
                head = get_head_pose(lm, w, h)
                if head != "Center": warnings.append(head)
        else: warnings.append("No Face")
    else:
        # Fallback
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if len(face_cascade.detectMultiScale(gray, 1.1, 5)) == 0: warnings.append("No Face")

    # C. YOLO (Object)
    df = yolo_model(frame).pandas().xyxy[0]
    for _, row in df.iterrows():
        if row['name'] in ['cell phone', 'book']: warnings.append(f"{row['name']} Found")

    return list(set(warnings))

# --- API Endpoint ---
@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.json
        img_data = data.get('image') or data.get('image_data')
        if not img_data: return jsonify({"error": "No image"})
        
        img = cv2.imdecode(np.frombuffer(base64.b64decode(img_data.split(',')[1]), np.uint8), cv2.IMREAD_COLOR)
        warnings = analyze_advanced(img)

        # Save Evidence (CSV + Photo)
        if warnings:
            t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            t_file = datetime.now().strftime("%H-%M-%S")
            
            # CSV Log
            with open('exam_logs.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                for w in warnings: writer.writerow([t_str, w])
            
            # Photo Evidence
            if not os.path.exists('evidence'): os.makedirs('evidence')
            tag = warnings[0].replace(" ", "")[:10]
            cv2.imwrite(f"evidence/CHEAT_{t_file}_{tag}.jpg", img)

        return jsonify({"status": "WARNING" if warnings else "OK", "warnings": warnings})

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "ERROR"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
