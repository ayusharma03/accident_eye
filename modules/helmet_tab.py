import customtkinter as ctk
from PIL import Image
import cv2
import threading
import time
from datetime import datetime
import os
from tkinter import filedialog  # Add this import for file dialog
from modules.helmet_detection import HelmetDetection

def detect_helmet_in_frame(app, frame):
    helmet_results = app.helmet_detector.detect_helmet(frame)
    return helmet_results

def create_helmet_tab(app):
    app.helmet_detector = HelmetDetection()  # Initialize helmet detector
    app.camera_running_tab3 = False  # Initialize camera state for tab 3


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
<<<<<<< HEAD
    """CAMERA INDEX HERE"""
    available_cameras = {"Camera 1": 1}
    app.selected_camera_index_tab2 = available_cameras["Camera 1"]
=======
    available_cameras = {"Camera 1": 1}
    app.selected_camera_index_tab3 = available_cameras["Camera 1"]
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38

    # Button container with left alignment but keeping buttons smaller
    button_container = ctk.CTkFrame(button_frame)
    button_container.pack(
        fill="both", padx=5, pady=10
    )  # Ensuring buttons stay within frame width

    app.toggle_switch_tab3 = ctk.CTkSwitch(
        master=button_container,
        text="Camera",
        command=lambda: (
        start_timer(app) if app.toggle_switch_tab3.get() else stop_timer(app),
        start_camera(app, 3) if app.toggle_switch_tab3.get() else stop_camera(app, 3),
        ),
    )
    app.toggle_switch_tab3.pack(side="left", padx=8, fill="y")

    app.inferencing_tab3 = False  # Initialize inferencing state
    inferencing_button_tab3 = ctk.CTkButton(
        button_container,
        text="Start Inferencing",
        command=lambda: (
            setattr(app, "inferencing_tab3", not app.inferencing_tab3),
            inferencing_button_tab3.configure(
                text="Stop Inferencing" if app.inferencing_tab3 else "Start Inferencing"
            ),
            start_inferencing(app, 3) if app.inferencing_tab3 else stop_inferencing(app, 3),
        ),
    )
    inferencing_button_tab3.pack(
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
    timer_frame_tab3 = ctk.CTkFrame(top_row)
    timer_frame_tab3.pack(
        side="right", padx=10, pady=10
    )  # Align at top-right (timer)
    app.camera_timer_tab3 = add_timer(app, timer_frame_tab3)

    # Status indicator (Camera Live/Off)
    status_indicator_frame_tab3 = ctk.CTkFrame(top_row)
    status_indicator_frame_tab3.pack(side="right", padx=10, pady=10)

    # Add the colored indicator (dot)
    app.status_indicator_tab3 = ctk.CTkLabel(status_indicator_frame_tab3, text="● Live", height=50, width=80)
    app.status_indicator_tab3.pack(side="left", padx=5, pady=2)
    update_status_indicator(app, "red")  # Initial state is red (camera off)

    # Main container for the three sections
    main_frame_tab3 = ctk.CTkFrame(app.tab3)
    main_frame_tab3.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab3 = ctk.CTkFrame(main_frame_tab3, width=700, height=400)  # Adjusted width and height
    cam_frame_tab3.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab3 = ctk.CTkLabel(cam_frame_tab3, text="Helmet Camera Feed")
    app.camera_title_tab3.pack(pady=2)
    app.camera_title_tab3.configure(font=("Arial",18,"bold"))  # Set text color to black
    # Label to display the camera feed
    app.cam_label3 = ctk.CTkLabel(cam_frame_tab3, text=" ", fg_color="gray", height=400, width=700)  # Gray background color
    app.cam_label3.pack(expand=True, fill="both", padx=10,pady=8)  # Use fill="both" to ensure it takes up the full space
    app.cam_label3.configure( # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # Helmet statistics frame below camera
    statistics_frame_tab3 = ctk.CTkFrame(cam_frame_tab3, width=700, height=100)
    statistics_frame_tab3.pack(side="left", padx=10, pady=10)
    # Fill the frame with helmet statistics of the day
    app.helmet_statistics_tab3 = ctk.CTkLabel(statistics_frame_tab3, text="Helmets Detected Today: 0\nLast Helmet: -", height=80, width=700, anchor="center")
    app.helmet_statistics_tab3.pack(pady=5, padx=10, fill="both", side="left")
    update_helmet_statistics(app)  # Initialize helmet statistics

    # Rightmost section (Detection Status, Last 10 Results)
    status_frame_tab3 = ctk.CTkFrame(main_frame_tab3, width=1000, height=500)
    status_frame_tab3.pack(side="right", fill="y", padx=10)

    status_label_tab3 = ctk.CTkLabel(status_frame_tab3, text="Last Helmet Detection")
    status_label_tab3.pack(pady=5)
    
    # List of last 10 helmets
    app.last_helmets_tab3 = ctk.CTkScrollableFrame(status_frame_tab3, width=600, height=500, fg_color="transparent")
    app.last_helmets_tab3.pack(pady=5)
    app.helmet_button = ctk.CTkButton(status_frame_tab3, text="View All Helmets")
    app.helmet_button.pack(pady=5)

    update_helmet_list(app)

    # List of bikes without helmets
    no_helmet_label_tab3 = ctk.CTkLabel(status_frame_tab3, text="Bikes Without Helmets")
    no_helmet_label_tab3.pack(pady=5)
    
    app.no_helmet_tab3 = ctk.CTkScrollableFrame(status_frame_tab3, width=600, height=500, fg_color="transparent")
    app.no_helmet_tab3.pack(pady=5)
    app.no_helmet_button = ctk.CTkButton(status_frame_tab3, text="View All No Helmets")
    app.no_helmet_button.pack(pady=5)

    update_no_helmet_list(app)

def upload_video(app):
    """Upload a video file and run the model on it."""
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if video_path:
        threading.Thread(target=lambda: process_video(app, video_path), daemon=True).start()

def process_video(app, video_path):
    """Process the uploaded video file."""
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        helmet_results = detect_helmet_in_frame(app, frame)
        frame = process_frame_with_yolo(app, frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
        app.cam_label3.configure(image=img_tk)
        app.cam_label3.image = img_tk

        # Resize the image to fit the dashboard frame
        img_dashboard = img.resize((560, 360), Image.LANCZOS)
        img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
        app.camera_labels[1].configure(image=img_tk_dashboard)
        app.camera_labels[1].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate

    cap.release()

def update_helmet_statistics(app, last_helmet=""):
    """Update the helmet statistics."""
    detected_today = int(app.helmet_statistics_tab3.cget("text").split(":")[1].split("\n")[0].strip()) + 1
    app.helmet_statistics_tab3.configure(
        text=f"Helmets Detected Today: {detected_today}\nLast Helmet: {last_helmet}"
    )

def update_helmet_list(app):
    """Update the list of helmets in the sidebar."""
    for widget in app.last_helmets_tab3.winfo_children():
        widget.destroy()

    # Placeholder for helmet folders
    helmet_folders = []

    for i, folder in enumerate(helmet_folders):
        frame = ctk.CTkFrame(app.last_helmets_tab3)
        frame.pack(fill="x", padx=5, pady=5)

        timestamp = datetime.strptime(folder, "%Y-%m-%d %H-%M-%S").strftime("%d-%m-%Y %H:%M:%S")
        image_path = f"helmets/{folder}/helmet-{folder}.png"
        details_path = f"helmets/{folder}/details.txt"

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
            details = "No details found"
            button_color = "red"

        button = ctk.CTkButton(
            frame,
            text=timestamp,
            compound="left",
            command=lambda hl=folder: show_helmet_details(app, helmet=hl, editable=(button_color == "red")),
            anchor="center",
            height=50,
            fg_color=button_color
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

def show_helmet_details(app, helmet, editable=False, large=False):
    """Show a pop-up with helmet details."""
    details_path = f"helmets/{helmet}/details.txt"
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
        details = "No data found, add data"

    popup = ctk.CTkToplevel(app)
    popup.title("Helmet Details")
    popup.geometry("800x800" if large else "600x600")
    popup.attributes("-topmost", True)  # Keep the pop-up on top

    scrollable_frame = ctk.CTkScrollableFrame(popup)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    details_label = ctk.CTkLabel(scrollable_frame, text=f"TIMESTAMP: {helmet.replace('helmet-', '')}", font=("Arial", 16, "bold"))
    details_label.pack(pady=10)

    if editable:
        helmet_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Enter helmet details")
        helmet_entry.pack(pady=5)

        def save_details():
            with open(details_path, "w") as f:
                f.write(helmet_entry.get())
            popup.destroy()
            update_helmet_list(app)

        save_button = ctk.CTkButton(scrollable_frame, text="Save", command=save_details)
        save_button.pack(pady=10)

    else:
        details_label = ctk.CTkLabel(scrollable_frame, text=details, font=("Arial", 14))
        details_label.pack(pady=10)

        edit_button = ctk.CTkButton(scrollable_frame, text="Edit", command=lambda: show_helmet_details(app, helmet, editable=True))
        edit_button.pack(pady=10)

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
    app.status_indicator_tab3.configure(text_color=color)

def start_camera(app, tab):
    """Start the webcam feed."""
    if tab == 3:
        if not hasattr(app, "selected_camera_index_tab3"):
            messagebox.showerror("Error", "Please select a camera.")
            return
        if not app.camera_running_tab3:
            app.cap_tab3 = cv2.VideoCapture(
                app.selected_camera_index_tab3
            )  # Initialize the webcam with the selected index
            app.camera_running_tab3 = True
            app.camera_thread_tab3 = threading.Thread(
                target=lambda: update_camera_feed_tab3(app), daemon=True
            )
            app.camera_thread_tab3.start()
        else:
            messagebox.showerror("Error", "Camera is already running in Tab 3.")

def stop_camera(app, tab):
    """Stop the webcam feed."""
    if tab == 3:
        if app.camera_running_tab3:
            app.camera_running_tab3 = False
            if app.cap_tab3:
                app.cap_tab3.release()  # Release the webcam
            app.cam_label3.configure(image=None)  # Clear the camera feed

def start_inferencing(app, tab):
    """Start inferencing and update the camera feed with YOLO processed frames."""
    if tab == 3:
        if not app.camera_running_tab3:
            messagebox.showerror("Error", "Camera is not running")
            return
        app.inferencing_tab3 = True

def stop_inferencing(app, tab):
    """Stop inferencing."""
    if tab == 3:
        app.inferencing_tab3 = False

def process_frame_with_yolo(app, frame):
    """Process the frame with YOLO model."""
    results = app.helmet_detector.detect_helmet(frame)
    if isinstance(results, str):
        return frame  # Return the frame if a string is returned (e.g., "Helmet detected")
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            if box.conf[0] > 0.5:  # Only show the box if probability is higher than 0.5
                if "no helmet" in result.names:
                    no_helmet_text = mark_and_ocr_no_helmet(app, frame, (x1, y1, x2, y2))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{no_helmet_text}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                else:
                    helmet_text = mark_and_ocr_helmet(app, frame, (x1, y1, x2, y2))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{helmet_text}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return frame

def mark_and_ocr_helmet(app, frame, bbox):
    """Mark the helmet and run OCR to extract the number."""
    x1, y1, x2, y2 = bbox
    helmet_image = frame[y1:y2, x1:x2]
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    folder_path = f"helmets/{timestamp}"
    os.makedirs(folder_path, exist_ok=True)
    image_path = f"{folder_path}/helmet-{timestamp}.png"
    cv2.imwrite(image_path, cv2.cvtColor(helmet_image, cv2.COLOR_RGB2BGR))
    
    # Run OCR on the cropped helmet image using EasyOCR
    result = app.helmet_detector.ocr_reader.readtext(helmet_image)
    helmet_text = result[0][-2] if result else "Unknown"
    
    with open(f"{folder_path}/details.txt", "w") as f:
        f.write(f"Helmet: {helmet_text}")
    
    update_helmet_list(app)
    update_helmet_statistics(app, helmet_text)
    
    return helmet_text

def mark_and_ocr_no_helmet(app, frame, bbox):
    """Mark the bike without helmet and run OCR to extract the number plate."""
    x1, y1, x2, y2 = bbox
    no_helmet_image = frame[y1:y2, x1:x2]
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    folder_path = f"no_helmets/{timestamp}"
    os.makedirs(folder_path, exist_ok=True)
    image_path = f"{folder_path}/no_helmet-{timestamp}.png"
    cv2.imwrite(image_path, cv2.cvtColor(no_helmet_image, cv2.COLOR_RGB2BGR))
    
    # Run OCR on the cropped no helmet image using EasyOCR
    result = app.helmet_detector.ocr_reader.readtext(no_helmet_image)
    no_helmet_text = result[0][-2] if result else "Unknown"
    
    with open(f"{folder_path}/details.txt", "w") as f:
        f.write(f"No Helmet: {no_helmet_text}")
    
    update_no_helmet_list(app)
    
    return no_helmet_text

def update_no_helmet_list(app):
    """Update the list of bikes without helmets in the sidebar."""
    for widget in app.no_helmet_tab3.winfo_children():
        widget.destroy()

    # Placeholder for no helmet folders
    no_helmet_folders = []

    for i, folder in enumerate(no_helmet_folders):
        frame = ctk.CTkFrame(app.no_helmet_tab3)
        frame.pack(fill="x", padx=5, pady=5)

        timestamp = datetime.strptime(folder, "%Y-%m-%d %H-%M-%S").strftime("%d-%m-%Y %H-%M-%S")
        image_path = f"no_helmets/{folder}/no_helmet-{folder}.png"
        details_path = f"no_helmets/{folder}/details.txt"

        try:
            no_helmet_image = ctk.CTkImage(Image.open(image_path), size=(50, 50))
            no_helmet_image_label = ctk.CTkLabel(frame, image=no_helmet_image, text="", width=50, height=50)
            no_helmet_image_label.pack(side="left", padx=8, pady=5)
        except FileNotFoundError:
            no_helmet_image_label = ctk.CTkLabel(frame, text="No Image", width=50, height=50)
            no_helmet_image_label.pack(side="left", padx=8, pady=5)

        try:
            with open(details_path, "r") as f:
                details = f.read().strip()
            button_color = "green"
        except FileNotFoundError:
            details = "No details found"
            button_color = "red"

        button = ctk.CTkButton(
            frame,
            text=timestamp,
            compound="left",
            command=lambda nh=folder: show_no_helmet_details(app, no_helmet=nh, editable=(button_color == "red")),
            anchor="center",
            height=50,
            fg_color=button_color
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

def show_no_helmet_details(app, no_helmet, editable=False, large=False):
    """Show a pop-up with no helmet details."""
    details_path = f"no_helmets/{no_helmet}/details.txt"
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
        details = "No data found, add data"

    popup = ctk.CTkToplevel(app)
    popup.title("No Helmet Details")
    popup.geometry("800x800" if large else "600x600")
    popup.attributes("-topmost", True)  # Keep the pop-up on top

    scrollable_frame = ctk.CTkScrollableFrame(popup)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    details_label = ctk.CTkLabel(scrollable_frame, text=f"TIMESTAMP: {no_helmet.replace('no_helmet-', '')}", font=("Arial", 16, "bold"))
    details_label.pack(pady=10)

    if editable:
        no_helmet_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Enter no helmet details")
        no_helmet_entry.pack(pady=5)

        def save_details():
            with open(details_path, "w") as f:
                f.write(no_helmet_entry.get())
            popup.destroy()
            update_no_helmet_list(app)

        save_button = ctk.CTkButton(scrollable_frame, text="Save", command=save_details)
        save_button.pack(pady=10)

    else:
        details_label = ctk.CTkLabel(scrollable_frame, text=details, font=("Arial", 14))
        details_label.pack(pady=10)

        edit_button = ctk.CTkButton(scrollable_frame, text="Edit", command=lambda: show_no_helmet_details(app, no_helmet, editable=True))
        edit_button.pack(pady=10)

def update_camera_feed_tab3(app):
    """Update the camera feed in the GUI for tab 3."""
    while app.camera_running_tab3:
        ret, frame = app.cap_tab3.read()
        if not ret:
            break

        helmet_results = detect_helmet_in_frame(app, frame)

        if app.inferencing_tab3:
            frame = process_frame_with_yolo(app, frame)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label3.configure(image=img_tk)
            app.cam_label3.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[1].configure(image=img_tk_dashboard)
            app.camera_labels[1].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate

def start_timer(app):
    """Start the timer."""
    app.timer_running_tab3 = True
    app.timer_thread_tab3 = threading.Thread(target=lambda: update_timer(app), daemon=True)
    app.timer_thread_tab3.start()

def stop_timer(app):
    """Stop the timer."""
    app.timer_running_tab3 = False

def update_timer(app):
    """Update the timer display."""
    start_time = time.time()
    while app.timer_running_tab3:
        elapsed_time = time.time() - start_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        app.camera_timer_tab3.configure(text=f"Time: {formatted_time}")
        time.sleep(1)
