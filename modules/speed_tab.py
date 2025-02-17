import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import time
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading

# Define the Tracker class directly in this file to avoid import issues
class Tracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0

    def update(self, objects_rect):
        objects_bbs_ids = []
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = np.hypot(cx - pt[0], cy - pt[1])
                if dist < 35:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        self.center_points = new_center_points.copy()
        return objects_bbs_ids

model = YOLO('yolov8s.pt')
class_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

def calculate_speed(pixel_distance, frame_rate, pixels_per_meter):
    return (pixel_distance / pixels_per_meter) * frame_rate

def process_frame(video_path):
    tracker = Tracker()
    down = {}
    up = {}
    counter_down = []
    counter_up = []

    red_line_y = 198
    blue_line_y = 268
    offset = 6

    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1020, 500))

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        frame = cv2.resize(frame, (1020, 500))

        results = model.predict(frame)
        a = results[0].boxes.data
        a = a.detach().cpu().numpy()
        px = pd.DataFrame(a).astype("float")
        list = []

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            if 'car' in c:
                list.append([x1, y1, x2, y2])
        bbox_id = tracker.update(list)
        
        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox
            cx = int(x3 + x4) // 2
            cy = int(y3 + y4) // 2

            if red_line_y < (cy + offset) and red_line_y > (cy - offset):
                down[id] = time.time()
            if id in down:
                if blue_line_y < (cy + offset) and blue_line_y > (cy - offset):
                    elapsed_time = time.time() - down[id]
                    if counter_down.count(id) == 0:
                        counter_down.append(id)
                        distance = 10
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 3.6
                        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                        cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                        cv2.putText(frame, str(id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                        cv2.putText(frame, str(int(a_speed_kh)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

            if blue_line_y < (cy + offset) and blue_line_y > (cy - offset):
                up[id] = time.time()
            if id in up:
                if red_line_y < (cy + offset) and red_line_y > (cy - offset):
                    elapsed1_time = time.time() - up[id]
                    if counter_up.count(id) == 0:
                        counter_up.append(id)
                        distance1 = 10
                        a_speed_ms1 = distance1 / elapsed1_time
                        a_speed_kh1 = a_speed_ms1 * 3.6
                        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                        cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                        cv2.putText(frame, str(id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                        cv2.putText(frame, str(int(a_speed_kh1)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        text_color = (0, 0, 0)
        yellow_color = (0, 255, 255)
        red_color = (0, 0, 255)
        blue_color = (255, 0, 0)

        cv2.rectangle(frame, (0, 0), (250, 90), yellow_color, -1)
        cv2.line(frame, (172, 198), (774, 198), red_color, 2)
        cv2.putText(frame, ('Red Line'), (172, 198), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
        cv2.line(frame, (8, 268), (927, 268), blue_color, 2)
        cv2.putText(frame, ('Blue Line'), (8, 268), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
        cv2.putText(frame, ('Going Down - ' + str(len(counter_down))), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)
        cv2.putText(frame, ('Going Up - ' + str(len(counter_up))), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1, cv2.LINE_AA)

        frame_filename = f'detected_frames/frame_{count}.jpg'
        cv2.imwrite(frame_filename, frame)
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def upload_video(app):
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if video_path:
        threading.Thread(target=lambda: process_frame(video_path), daemon=True).start()

class SpeedDetection:
    def __init__(self):
        # Initialize speed detection attributes
        pass

    def process_frame(self, frame):
        # Placeholder for frame processing logic
        pass

def create_speed_tab(app):
    app.speed_detector = SpeedDetection()  # Initialize speed detector
    app.camera_running_tab4 = False  # Initialize camera state for tab 3

    top_row = ctk.CTkFrame(app.tab4)  # Set a specific height for the top row
    top_row.pack(fill="x", pady=0)  # Reduced the pady to 0 for less space

    # Logo on the left side of the top row
    logo_frame = ctk.CTkFrame(top_row)
    logo_frame.pack(
        side="left", anchor="nw", padx=10, pady=10
    )  # Align at top-left (logo) with padding
    add_logo(app, logo_frame)  # Add the logo to this frame

    button_frame = ctk.CTkFrame(top_row)
    button_frame.pack(
        side="left", padx=10, pady=10, fill="x"
    )  # Ensure it spans horizontally

    # Detect available cameras and populate the combo box with indexes
    available_cameras = {"Camera 1": 1}
    app.selected_camera_index_tab4 = available_cameras["Camera 1"]

    # Button container with left alignment but keeping buttons smaller
    button_container = ctk.CTkFrame(button_frame)
    button_container.pack(
        fill="both", padx=5, pady=10
    )  # Ensuring buttons stay within frame width

    app.toggle_switch_tab4 = ctk.CTkSwitch(
        master=button_container,
        text="Camera",
        command=lambda: (
        start_timer(app) if app.toggle_switch_tab4.get() else stop_timer(app),
        start_camera(app, 3) if app.toggle_switch_tab4.get() else stop_camera(app, 3),
        ),
    )
    app.toggle_switch_tab4.pack(side="left", padx=8, fill="y")

    app.inferencing_tab4 = False  # Initialize inferencing state
    inferencing_button_tab4 = ctk.CTkButton(
        button_container,
        text="Start Inferencing",
        command=lambda: (
            setattr(app, "inferencing_tab4", not app.inferencing_tab4),
            inferencing_button_tab4.configure(
                text="Stop Inferencing" if app.inferencing_tab4 else "Start Inferencing"
            ),
            start_inferencing(app, 3) if app.inferencing_tab4 else stop_inferencing(app, 3),
        ),
    )
    inferencing_button_tab4.pack(
        side="left", padx=5, pady=10, expand=True, fill="x"
    )  # Expand inferencing button to take remaining space

    # Add button to upload video file
    upload_button = ctk.CTkButton(
        button_container,
        text="Upload Video",
        command=lambda: upload_video(app)
    )
    upload_button.pack(side="left", padx=5, pady=10, expand=True, fill="x")

    # Timer on the right side
    timer_frame_tab4 = ctk.CTkFrame(top_row)
    timer_frame_tab4.pack(
        side="right", padx=10, pady=10
    )  # Align at top-right (timer)
    app.camera_timer_tab4 = add_timer(app, timer_frame_tab4)

    # Status indicator (Camera Live/Off)
    status_indicator_frame_tab4 = ctk.CTkFrame(top_row)
    status_indicator_frame_tab4.pack(side="right", padx=10, pady=10)

    # Add the colored indicator (dot)
    app.status_indicator_tab4 = ctk.CTkLabel(status_indicator_frame_tab4, text="● Live", height=50, width=80)
    app.status_indicator_tab4.pack(side="left", padx=5, pady=2)
    update_status_indicator(app, "red")  # Initial state is red (camera off)

    # Main container for the three sections
    main_frame_tab4 = ctk.CTkFrame(app.tab4)
    main_frame_tab4.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab4 = ctk.CTkFrame(main_frame_tab4, width=700, height=400)  # Adjusted width and height
    cam_frame_tab4.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab4 = ctk.CTkLabel(cam_frame_tab4, text="Speed Camera Feed")
    app.camera_title_tab4.pack(pady=2)
    app.camera_title_tab4.configure(font=("Arial",18,"bold"))  # Set text color to black
    # Label to display the camera feed
    app.cam_label3 = ctk.CTkLabel(cam_frame_tab4, text=" ", fg_color="gray", height=400, width=700)  # Gray background color
    app.cam_label3.pack(expand=True, fill="both", padx=10,pady=8)  # Use fill="both" to ensure it takes up the full space
    app.cam_label3.configure( # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # Speed statistics frame below camera
    statistics_frame_tab4 = ctk.CTkFrame(cam_frame_tab4, width=700, height=100)
    statistics_frame_tab4.pack(side="left", padx=10, pady=10)
    # Fill the frame with speed statistics of the day
    app.speed_statistics_tab4 = ctk.CTkLabel(statistics_frame_tab4, text="Speed Violations Today: 0\nLast Violation: -", height=80, width=700, anchor="center")
    app.speed_statistics_tab4.pack(pady=5, padx=10, fill="both", side="left")
    update_speed_statistics(app)  # Initialize speed statistics

    # Rightmost section (Detection Status, Last 10 Results)
    status_frame_tab4 = ctk.CTkFrame(main_frame_tab4, width=1000, height=500)
    status_frame_tab4.pack(side="right", fill="y", padx=10)

    status_label_tab4 = ctk.CTkLabel(status_frame_tab4, text="Last Speed Violation Detection")
    status_label_tab4.pack(pady=5)
    
    # List of last 10 speed violations
    app.last_speed_violations_tab4 = ctk.CTkScrollableFrame(status_frame_tab4, width=600, height=500, fg_color="transparent")
    app.last_speed_violations_tab4.pack(pady=5)
    app.speed_violation_button = ctk.CTkButton(status_frame_tab4, text="View All Speed Violations")
    app.speed_violation_button.pack(pady=5)

    update_speed_violation_list(app)

def add_logo(app, parent):
    logo_label = ctk.CTkLabel(parent, image=app.logo_image, text="")
    logo_label.pack(anchor="nw", padx=10, pady=10)

def detect_cars(frame):
    # Placeholder for car detection logic
    # This function should return a list of bounding boxes
    return []

def add_timer(app, parent):
    timer_label = ctk.CTkLabel(parent, text="00:00:00", font=("Arial", 20))
    timer_label.pack()
    return timer_label

def update_timer(app, timer_label):
    if app.running:
        elapsed_time = time.time() - app.start_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        timer_label.configure(text=formatted_time)
        timer_label.after(1000, lambda: update_timer(app, timer_label))

def start_timer(app):
    app.start_time = time.time()
    app.running = True
    update_timer(app, app.camera_timer_tab4)

def stop_timer(app):
    app.running = False

def update_status_indicator(app, color):
    app.status_indicator_tab4.configure(fg_color=color)

def update_speed_statistics(app):
    # Placeholder for updating speed statistics logic
    app.speed_statistics_tab4.configure(text="Speed Violations Today: 0\nLast Violation: -")

# ...existing code...
