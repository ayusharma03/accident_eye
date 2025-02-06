import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as messagebox
import cv2
import threading
import os
import time
from datetime import datetime
from modules.helmet_detection import HelmetDetection

# Initialize helmet detection variables
consecutive_frames_with_helmet = 0
consecutive_frames_without_helmet = 0
frames_buffer = []
helmets = []
helmet_detector = HelmetDetection()

def detect_helmet_in_frame(frame):
    helmet_results, helmet_class_names = helmet_detector.detect_helmet(frame)
    helmet_detected = 'helmet' in helmet_class_names  # Adjust this condition based on your helmet detection logic
    return helmet_detected, helmet_class_names

def save_frames(frames, timestamp, classes_present):
    folder_name = timestamp.strftime("%Y-%m-%d %H-%M-%S")
    folder_path = os.path.join("helmets", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    for i, (frame, frame_time, frame_classes) in enumerate(frames):
        frame_name = f"helmet-{frame_time.strftime('%Y-%m-%d %H-%M-%S')}.png"
        cv2.imwrite(os.path.join(folder_path, frame_name), frame)
    
    helmets.append({
        "timeline": folder_name,
        "details": classes_present
    })

def create_helmet_tab(app):
    top_row = ctk.CTkFrame(app.tab3)  # Set a specific height for the top row
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
    """CAMERA INDEX HERE"""
    available_cameras = {"Camera 1": 0}
    app.selected_camera_index_tab2 = available_cameras["Camera 1"]

    # Button container with left alignment but keeping buttons smaller
    button_container = ctk.CTkFrame(button_frame)
    button_container.pack(
        fill="both", padx=5, pady=10
    )  # Ensuring buttons stay within frame width

    app.toggle_switch_tab2 = ctk.CTkSwitch(
        master=button_container,
        text="Camera",
        command=lambda: (
        start_timer(app) if app.toggle_switch_tab2.get() else stop_timer(app),
        start_camera(app) if app.toggle_switch_tab2.get() else stop_camera(app),
        ),
    )
    app.toggle_switch_tab2.pack(side="left", padx=8, fill="y")
    

    app.inferencing_tab2 = False  # Initialize inferencing state
    inferencing_button_tab2 = ctk.CTkButton(
        button_container,
        text="Start Inferencing",
        command=lambda: (
            setattr(app, "inferencing_tab2", not app.inferencing_tab2),
            inferencing_button_tab2.configure(
                text="Stop Inferencing" if app.inferencing_tab2 else "Start Inferencing"
            ),
            start_inferencing(app, 2) if app.inferencing_tab2 else stop_inferencing(app, 2),
        ),
    )
    inferencing_button_tab2.pack(
        side="left", padx=5, pady=10, expand=True, fill="x"
    )  # Expand inferencing button to take remaining space

    # Timer on the right side
    timer_frame_tab2 = ctk.CTkFrame(top_row)
    timer_frame_tab2.pack(
        side="right", padx=10, pady=10
    )  # Align at top-right (timer)
    app.camera_timer_tab2 = add_timer(app, timer_frame_tab2)

    # Status indicator (Camera Live/Off)
    status_indicator_frame_tab2 = ctk.CTkFrame(top_row)
    status_indicator_frame_tab2.pack(side="right", padx=10, pady=10)

    # Add the colored indicator (dot)
    app.status_indicator_tab2 = ctk.CTkLabel(status_indicator_frame_tab2, text="● Live", height=50, width=80)
    app.status_indicator_tab2.pack(side="left", padx=5, pady=2)
    update_status_indicator(app, "red")  # Initial state is red (camera off)

    # Main container for the three sections
    main_frame_tab2 = ctk.CTkFrame(app.tab3)
    main_frame_tab2.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=700, height=400)  # Adjusted width and height
    cam_frame_tab2.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab2 = ctk.CTkLabel(cam_frame_tab2, text="Helmet Camera Feed")
    app.camera_title_tab2.pack(pady=2)
    app.camera_title_tab2.configure(font=("Arial",18,"bold"))  # Set text color to black
    # Label to display the camera feed
    app.cam_label2 = ctk.CTkLabel(cam_frame_tab2, text=" ", fg_color="gray", height=400, width=700)  # Gray background color
    app.cam_label2.pack(expand=True, fill="both", padx=10,pady=8)  # Use fill="both" to ensure it takes up the full space
    app.cam_label2.configure( # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # helmet statistics frame below camera
    statistics_frame_tab2 = ctk.CTkFrame(cam_frame_tab2, width=700, height=100)
    statistics_frame_tab2.pack(side="left", padx=10, pady=10)
    # fill the frame with helmet statistics of the day
    app.helmet_statistics_tab2 = ctk.CTkLabel(statistics_frame_tab2, text="Helmets Today: 0\nLast Helmet: -", height=80, width=700,anchor="center")
    app.helmet_statistics_tab2.pack(pady=5, padx=10, fill="both", side="left")

    # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
    status_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=1000)
    status_frame_tab2.pack(side="right", fill="y", padx=10)

    status_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Last Helmet Detection")
    status_label_tab2.pack(pady=5)
    
    # list of last 10 helmets
    app.last_helmets_tab2 = ctk.CTkScrollableFrame(status_frame_tab2, width=600, height=700, fg_color="transparent")
    app.last_helmets_tab2.pack(pady=5)
    app.helmet_button = ctk.CTkButton(status_frame_tab2, text="View All Helmets")
    app.helmet_button.pack(pady=5)

    update_helmet_list(app)

def update_helmet_list(app):
    """Update the list of helmets in the sidebar."""
    for widget in app.last_helmets_tab2.winfo_children():
        widget.destroy()

    today = time.strftime("%Y-%m-%d")
    helmet_folders = [f for f in os.listdir("helmets") if today in f]

    for folder in helmet_folders:
        frame = ctk.CTkFrame(app.last_helmets_tab2)
        frame.pack(fill="x", padx=5, pady=5)

        timestamp = folder.replace("helmet-", "")
        image_path = f"helmets/{folder}/helmet-{timestamp}.png"
        details_path = f"helmets/{folder}/details.txt"
        classes_path = f"helmets/{folder}/classes.txt"

        try:
            helmet_image = ctk.CTkImage(Image.open(image_path), size=(50, 50))
            helmet_image_label = ctk.CTkLabel(frame, image=helmet_image, text="", width=50, height=50)
            helmet_image_label.pack(side="left", padx=8, pady=5)
        except FileNotFoundError:
            helmet_image_label = ctk.CTkLabel(frame, text="No Image", width=50, height=50)
            helmet_image_label.pack(side="left", padx=8, pady=5)

        try:
            with open(details_path, "r") as f:
                details = f.read().strip()
            button_color = "green"
        except FileNotFoundError:
            details = "No details available"
            button_color = "red"

        button = ctk.CTkButton(
            frame,
            text=timestamp,
            compound="left",
            command=lambda hel=folder: show_helmet_details(helmet=hel),
            anchor="center",
            height=50,
            fg_color=button_color
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        try:
            with open(classes_path, "r") as f:
                classes = f.readlines()
            for cls in classes:
                cls_button = ctk.CTkButton(frame, text=f"Helmet of: {cls.strip()}", height=30)
                cls_button.pack(side="left", padx=5, pady=5)
        except FileNotFoundError:
            pass

def show_helmet_details(helmet):
    """Show a pop-up with helmet details."""
    details_path = f"helmets/{helmet}/details.txt"
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
        details = "No details available"
    messagebox.showinfo("Helmet Details", f"Timestamp: {helmet.replace('helmet-', '')}\nDetails: {details}")

def add_logo(app, parent):
    """Adds a logo to the top left corner of a tab."""
    logo_label = ctk.CTkLabel(parent, image=app.logo_image, text="")
    logo_label.pack(anchor="nw", padx=10, pady=10)

def add_timer(app, parent):
    """Adds a timer to the top right corner of a tab."""
    timer_label = ctk.CTkLabel(parent, text="Time: 00:00:00", height=50, width=100)
    timer_label.pack(anchor="ne", padx=10, pady=2)
    return timer_label

def update_status_indicator(app, color):
    """Update the status indicator color."""
    app.status_indicator_tab2.configure(text_color=color)

def start_camera(app):
    """Start the webcam feed."""
    if not hasattr(app, "selected_camera_index_tab2"):
        messagebox.showerror("Error", "Please select a camera.")
        return
    if not app.camera_running_tab2:
        app.cap_tab2 = cv2.VideoCapture(
            app.selected_camera_index_tab2
        )  # Initialize the webcam with the selected index
        app.camera_running_tab2 = True
        app.camera_thread_tab2 = threading.Thread(
            target=lambda: update_camera_feed(app), daemon=True
        )
        app.camera_thread_tab2.start()
    else:
        messagebox.showerror("Error", "Camera is already running in Tab 2.")

def stop_camera(app):
    """Stop the webcam feed."""
    print("camera stopping")
    if app.camera_running_tab2:
        app.camera_running_tab2 = False
        if app.cap_tab2:
            app.cap_tab2.release()  # Release the webcam
        app.cam_label2.configure(image=None)  # Clear the camera feed

def start_inferencing(app, tab):
    """Start inferencing and update the camera feed with YOLO processed frames."""
    if tab == 2:
        if not app.camera_running_tab2:
            messagebox.showerror("Error", "Camera is not running")
            return
        app.inferencing_tab2 = True
    else:
        if not app.camera_running_tab1:
            messagebox.showerror("Error", "Camera is not running")
            return
        app.inferencing_tab1 = True

def stop_inferencing(app, tab):
    """Stop inferencing."""
    if tab == 2:
        app.inferencing_tab2 = False
    else:
        app.inferencing_tab1 = False

def update_camera_feed(app):
    """Update the camera feed in the GUI."""
    while app.camera_running_tab2:
        ret, frame = app.cap_tab2.read()
        if not ret:
            break

        helmet_detected, classes_present = detect_helmet_in_frame(frame)

        if helmet_detected:
            app.consecutive_frames_with_helmet += 1
            app.consecutive_frames_without_helmet = 0
            helmet_results, helmet_classes = app.helmet_detector.detect_helmet(frame)
            app.frames_buffer.append((frame, datetime.now(), helmet_classes))

            if app.consecutive_frames_with_helmet >= 80:
                # Store frames if helmet detected for 80 out of 100 frames
                save_frames(app.frames_buffer, datetime.now(), helmet_classes)
                app.frames_buffer = []
                app.consecutive_frames_with_helmet = 0
        else:
            app.consecutive_frames_without_helmet += 1
            if app.consecutive_frames_without_helmet >= 30:
                # Reset buffer if helmet is out of frame for 30 consecutive frames
                app.frames_buffer = []
                app.consecutive_frames_with_helmet = 0

        if app.inferencing_tab2:
            frame, classes = process_frame_with_yolo(app, frame)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label2.configure(image=img_tk)
            app.cam_label2.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[1].configure(image=img_tk_dashboard)
            app.camera_labels[1].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate

def process_frame_with_yolo(app, frame):
    """Process the frame with YOLO model."""
    results, class_names = app.helmet_detector.detect_helmet(frame)
    classes = class_names.copy()
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            class_name = class_names.pop(0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return frame, classes

def start_timer(app):
    """Start the camera and update the status indicator."""
    print("timer starting")
    if not app.running:
        print("almost")
        app.start_time = time.time() - (
            app.elapsed_time if hasattr(app, "elapsed_time") else 0
        )
        app.running = True
        update_timer(app)
        update_status_indicator(app, "green")  # Change to green when camera is live

def stop_timer(app):
    """Stop the camera and update the status indicator."""
    if app.running:
        app.elapsed_time = time.time() - app.start_time
        app.running = False
        update_status_indicator(app, "red")  # Change to red when camera is stopped

def update_timer(app):
    """Update the timer label every second while it's running."""
    if app.running:
        elapsed_time = time.time() - app.start_time
        hours, remainder = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_text = f"{hours:02}:{minutes:02}:{seconds:02}"
        app.camera_timer_tab2.configure(text=f"Time: {timer_text}")
        app.after(1000, lambda: update_timer(app))  # Update every second