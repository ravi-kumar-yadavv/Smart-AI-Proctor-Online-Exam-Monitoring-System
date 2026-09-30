# main_proctor.py

import torch
import cv2

# ---- MODEL LOADING ----
# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Load YOLOv5 for object detection
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
yolo_model.conf = 0.40 # Set confidence threshold

# ---- WEBCAM SETUP ----
cap = cv2.VideoCapture(0)

# ---- MAIN PROCESSING LOOP ----
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    
    # Create a list to hold all warning messages for the current frame
    warnings = []

    # ---- 1. FACE DETECTION ANALYSIS ----
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    if len(faces) == 0:
        warnings.append("No Face Detected!")
    elif len(faces) > 1:
        warnings.append(f"{len(faces)} Faces Detected!")
    
    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # ---- 2. OBJECT DETECTION ANALYSIS ----
    results = yolo_model(frame)
    df = results.pandas().xyxy[0]
    
    # Look for specific objects we want to flag
    prohibited_items = ['cell phone', 'book']
    for index, row in df.iterrows():
        item_name = row['name']
        if item_name in prohibited_items:
            warnings.append(f"{item_name.title()} Detected!")
            # Draw a red box around prohibited items
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, item_name.upper(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # ---- 3. DISPLAY WARNINGS ----
    # Display all collected warnings on the screen
    y_offset = 30
    for warning in warnings:
        cv2.putText(frame, f"WARNING: {warning}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y_offset += 30 # Move next warning down
    
    # If no warnings, show OK status
    if not warnings:
        cv2.putText(frame, "Status: OK", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # ---- DISPLAY FRAME ----
    cv2.imshow('AI Proctoring System', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()