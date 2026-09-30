# 🛡️ AI-Powered Automated Proctoring System

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-green?style=for-the-badge&logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-red?style=for-the-badge&logo=opencv)
![YOLOv5](https://img.shields.io/badge/YOLOv5-Object_Detection-orange?style=for-the-badge)

## 📌 Overview
This is a **Commercial-Grade AI Proctoring System** designed to monitor online examinations automatically. It uses **Computer Vision (OpenCV, MediaPipe, YOLO)** and **Audio Analysis (Speech Recognition)** to detect suspicious activities in real-time.

Unlike basic proctoring tools, this system features **"Jasoos Mode" (Spy Mode)** which records whispered conversations, tracks eye gaze, and logs evidence with screenshots.

---

## 🚀 Key Features

### 👁️ Visual AI Monitoring
- **Face Detection:** Detects if the student is present or if multiple people are in the frame.
- **Object Detection (YOLOv5):** Automatically flags prohibited items like **Cell Phones, Books, and Laptops**.
- **Gaze Tracking:** Alerts if the student looks away from the screen (Left/Right).
- **Head Pose Estimation:** Detects if the student is looking down or turning their head.

### 🎤 Audio Intelligence ("Jasoos Mode")
- **Speech-to-Text:** Converts audio to text in real-time to detect conversations.
- **Keyword Trigger:** Automatically flags suspicious words like *"Answer", "Bata de", "Hello", "Copy"* etc.
- **Volume Monitor:** Detects high background noise.

### 🔒 Browser Security (Extension)
- **Tab Switching Lock:** Alerts if the student switches tabs.
- **Anti-Copy/Paste:** Blocks Right-Click, `Ctrl+C`, `Ctrl+V`, and `Alt+Tab`.
- **Full-Screen Enforcement:** Monitors window focus.

### 📂 Automated Evidence Logging
- **CSV Logs:** Timestamps every warning in `exam_logs.csv`.
- **Photo Proof:** Automatically captures screenshots of the student when cheating is detected (`evidence/` folder).
- **Speech Logs:** Saves transcripts of conversations in `speech_evidence.txt`.

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **AI/ML Models:** - `YOLOv5` (Object Detection)
  - `MediaPipe` (Face Mesh & Pose)
  - `Haar Cascades` (Face Count)
  - `Google Speech API` (Audio Analysis)
- **Frontend:** HTML, JavaScript (Chrome Extension)
- **Database/Storage:** CSV & File System (Local Logging)

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Chrome Browser
- A Webcam & Microphone

### Step 1: Clone the Repository
```bash
git clone [https://github.com/your-username/AI-Proctor-System.git](https://github.com/your-username/AI-Proctor-System.git)
cd AI-Proctor-System
