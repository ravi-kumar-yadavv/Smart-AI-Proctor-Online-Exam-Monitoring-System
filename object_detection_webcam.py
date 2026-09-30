# object_detection_webcam.py

import torch
import cv2

# Load the pretrained YOLOv5 model from PyTorch Hub
# 'yolov5s' is small and fast. 's' stands for small.
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Set the confidence threshold (e.g., 0.4 means 40% confidence)
# Lower this to detect more objects, raise it for higher accuracy
model.conf = 0.40

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Run inference on the frame
    results = model(frame)

    # Get the results as a pandas DataFrame
    df = results.pandas().xyxy[0]

    # Filter for 'cell phone' detections
    phone_detections = df[df['name'] == 'cell phone']

    # Draw bounding boxes for all detected objects
    for index, row in df.iterrows():
        x1, y1, x2, y2, confidence, class_id, name = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']), row['confidence'], row['class'], row['name']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        label = f"{name}: {confidence:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # If a cell phone is detected, display a prominent warning
    if not phone_detections.empty:
        warning_text = "WARNING: Cell Phone Detected!"
        cv2.putText(frame, warning_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('AI Proctor - Object Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()