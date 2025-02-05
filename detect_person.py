import cv2
import os
from datetime import datetime
from modules.accident_detection import AccidentDetection

# ...existing code...

consecutive_frames_with_accident = 0
consecutive_frames_without_accident = 0
frames_buffer = []
accidents = []
accident_detector = AccidentDetection()

def detect_accident_in_frame(frame):
    accident_results, accident_class_names = accident_detector.detect_accident(frame)
    accident_detected = 'accident' in accident_class_names  # Adjust this condition based on your accident detection logic
    return accident_detected, accident_class_names

def save_frames(frames, timestamp, classes_present):
    folder_name = timestamp.strftime("%Y-%m-%d %H-%M-%S")
    folder_path = os.path.join("accidents", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    for i, (frame, frame_time, frame_classes) in enumerate(frames):
        frame_name = f"accident-{frame_time.strftime('%Y-%m-%d %H-%M-%S')}.png"
        cv2.imwrite(os.path.join(folder_path, frame_name), frame)
    
    accidents.append({
        "timeline": folder_name,
        "details": classes_present
    })

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    accident_detected, classes_present = detect_accident_in_frame(frame)
    
    if accident_detected:
        consecutive_frames_with_accident += 1
        consecutive_frames_without_accident = 0
        accident_results, accident_classes = accident_detector.detect_accident(frame)
        frames_buffer.append((frame, datetime.now(), accident_classes))
        
        if consecutive_frames_with_accident >= 80:
            # Store frames if accident detected for 80 out of 100 frames
            save_frames(frames_buffer, datetime.now(), accident_classes)
            frames_buffer = []
            consecutive_frames_with_accident = 0
    else:
        consecutive_frames_without_accident += 1
        if consecutive_frames_without_accident >= 30:
            # Reset buffer if accident is out of frame for 30 consecutive frames
            frames_buffer = []
            consecutive_frames_with_accident = 0
    
    # ...existing code for displaying frame...

cap.release()
cv2.destroyAllWindows()
