// content.js - With Stop Button

(function() {
    // Check if already running to prevent duplicates
    if (document.getElementById('ai-proctor-video')) return;

    console.log("AI Proctoring Script Injected!");

    let mediaStream = null;
    let proctorInterval = null;

    // 1. Create UI Elements (Video, Alert Box, Stop Button)
    
    // Video Element
    const video = document.createElement('video');
    video.id = 'ai-proctor-video';
    video.setAttribute('autoplay', 'true');
    video.style.position = 'fixed';
    video.style.bottom = '10px';
    video.style.right = '10px';
    video.style.width = '200px';
    video.style.border = '3px solid red';
    video.style.borderRadius = '8px';
    video.style.zIndex = '9999';
    document.body.appendChild(video);

    // Canvas (Hidden)
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    // Alert Box
    const alertBox = document.createElement('div');
    alertBox.id = 'ai-proctor-alert';
    alertBox.style.position = 'fixed';
    alertBox.style.bottom = '10px';
    alertBox.style.left = '10px';
    alertBox.style.padding = '15px';
    alertBox.style.backgroundColor = 'white';
    alertBox.style.border = '2px solid black';
    alertBox.style.borderRadius = '8px';
    alertBox.style.zIndex = '9999';
    alertBox.style.fontFamily = 'Arial, sans-serif';
    alertBox.style.fontSize = '14px';
    alertBox.innerHTML = '<strong>🔴 AI Proctor Active</strong><br><span id="status-text">Starting...</span>';
    document.body.appendChild(alertBox);
    const statusText = document.getElementById('status-text');

    // --- NEW: STOP BUTTON ---
    const stopBtn = document.createElement('button');
    stopBtn.innerText = "Finish Exam";
    stopBtn.style.position = 'fixed';
    stopBtn.style.top = '10px';     // Top Right Corner
    stopBtn.style.right = '10px';
    stopBtn.style.padding = '10px 20px';
    stopBtn.style.backgroundColor = '#dc3545'; // Red Color
    stopBtn.style.color = 'white';
    stopBtn.style.border = 'none';
    stopBtn.style.borderRadius = '5px';
    stopBtn.style.cursor = 'pointer';
    stopBtn.style.zIndex = '10000';
    stopBtn.style.fontSize = '16px';
    stopBtn.style.fontWeight = 'bold';
    document.body.appendChild(stopBtn);

    // 2. Start Webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            mediaStream = stream; // Stream ko save karein taaki baad me rok sakein
            video.srcObject = stream;
        })
        .catch(err => {
            console.error("Webcam Error:", err);
            statusText.innerText = "Camera Access Denied!";
            statusText.style.color = "red";
        });

    // 3. Send Frame Loop
    proctorInterval = setInterval(() => {
        if (!video.videoWidth) return; 

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        let imageData = canvas.toDataURL('image/jpeg', 0.7);

        const SERVER_URL = 'http://127.0.0.1:5001/process_frame';

        fetch(SERVER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "WARNING" && data.warnings.length > 0) {
                statusText.style.color = 'red';
                statusText.innerHTML = "⚠️ " + data.warnings.join(', ');
                alertBox.style.backgroundColor = '#ffe6e6';
                video.style.borderColor = 'red';
            } else {
                statusText.style.color = 'green';
                statusText.innerText = '✅ System Check: OK';
                alertBox.style.backgroundColor = 'white';
                video.style.borderColor = 'green';
            }
        })
        .catch(error => {
            // console.error(error);
            statusText.innerText = 'Connecting...';
            statusText.style.color = 'orange';
        });

    }, 2000); 

    // 4. Stop Function 
        // 4. Stop Function (With Confirmation Check)
        stopBtn.addEventListener('click', function() {
            
            // STEP 1: Confirmation Box
            let isSure = confirm("⚠️ Are you sure you want to SUBMIT and FINISH the exam?\n\nClick OK to Submit.\nClick Cancel to Continue Exam.");
    
            // STEP 2: If student press ok than close
            if (isSure) {
                
                // A. Stop Loop
                if (proctorInterval) clearInterval(proctorInterval);
    
                // B. Stop Camera Light
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                }
    
                // C. Remove UI Elements
                video.remove();
                alertBox.remove();
                stopBtn.remove();
    
                alert("Exam Submitted Successfully! ✅\nProctoring Stopped.");
                console.log("AI Proctor Stopped by Student.");
                
            } else {
                
                console.log("Submission Cancelled by Student.");
            }
        });
    
    })();
