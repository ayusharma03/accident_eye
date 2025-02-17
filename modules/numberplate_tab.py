import customtkinter as ctk
from PIL import Image
<<<<<<< HEAD
import tkinter.messagebox as messagebox
import cv2
import threading
import os
import time
from datetime import datetime
from modules.helmet_detection import HelmetDetection
from modules.accident_detection import AccidentDetection
from modules.numberplate_detection import NumberplateDetection

# Initialize helmet detection variables
consecutive_frames_with_helmet = 0
consecutive_frames_without_helmet = 0
frames_buffer = []
helmets = []
helmet_detector = HelmetDetection()

# Initialize accident detection variables
consecutive_frames_with_accident = 0
consecutive_frames_without_accident = 0
accidents = []
accident_detector = AccidentDetection()

# Initialize numberplate detection variables
consecutive_frames_with_numberplate = 0
consecutive_frames_without_numberplate = 0
numberplates = []
numberplate_detector = NumberplateDetection()


def detect_helmet_in_frame(frame):
    accident_results, accident_class_names = accident_detector.detect_accident(frame)
    accident_detected = (
        "Accident" in accident_class_names
    )  # Adjust this condition based on your accident detection logic
    return accident_detected, accident_class_names


def save_frames(frames, timestamp, classes_present):
    folder_name = timestamp.strftime("%Y-%m-%d %H-%M-%S")
    folder_path = os.path.join("helmets", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for i, (frame, frame_time, frame_classes) in enumerate(frames):
        frame_name = f"helmet-{frame_time.strftime('%Y-%m-%d %H-%M-%S')}.png"
        cv2.imwrite(os.path.join(folder_path, frame_name), frame)

    helmets.append({"timeline": folder_name, "details": classes_present})


def save_accident_frames(frames, timestamp, classes_present):
    folder_name = timestamp.strftime("%Y-%m-%d %H-%M-%S")
    folder_path = os.path.join("accidents", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for i, (frame, frame_time, frame_classes) in enumerate(frames):
        frame_name = f"accident-{frame_time.strftime('%Y-%m-%d %H-%M-%S')}.png"
        cv2.imwrite(os.path.join(folder_path, frame_name), frame)

    accidents.append({"timeline": folder_name, "details": classes_present})


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
    available_cameras = {"Camera 1": 1}
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
            (
                start_inferencing(app, 2)
                if app.inferencing_tab2
                else stop_inferencing(app, 2)
            ),
        ),
    )
    inferencing_button_tab2.pack(
        side="left", padx=5, pady=10, expand=True, fill="x"
    )  # Expand inferencing button to take remaining space

    # Timer on the right side
    timer_frame_tab2 = ctk.CTkFrame(top_row)
    timer_frame_tab2.pack(side="right", padx=10, pady=10)  # Align at top-right (timer)
    app.camera_timer_tab2 = add_timer(app, timer_frame_tab2)

    # Status indicator (Camera Live/Off)
    status_indicator_frame_tab2 = ctk.CTkFrame(top_row)
    status_indicator_frame_tab2.pack(side="right", padx=10, pady=10)

    # Add the colored indicator (dot)
    app.status_indicator_tab2 = ctk.CTkLabel(
        status_indicator_frame_tab2, text="● Live", height=50, width=80
    )
    app.status_indicator_tab2.pack(side="left", padx=5, pady=2)
    update_status_indicator(app, "red")  # Initial state is red (camera off)

    # Main container for the three sections
    main_frame_tab2 = ctk.CTkFrame(app.tab3)
    main_frame_tab2.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab2 = ctk.CTkFrame(
        main_frame_tab2, width=700, height=400
    )  # Adjusted width and height
    cam_frame_tab2.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab2 = ctk.CTkLabel(cam_frame_tab2, text="Helmet Camera Feed")
    app.camera_title_tab2.pack(pady=2)
    app.camera_title_tab2.configure(
        font=("Arial", 18, "bold")
    )  # Set text color to black
    # Label to display the camera feed
    app.cam_label2 = ctk.CTkLabel(
        cam_frame_tab2, text=" ", fg_color="gray", height=400, width=700
    )  # Gray background color
    app.cam_label2.pack(
        expand=True, fill="both", padx=10, pady=8
    )  # Use fill="both" to ensure it takes up the full space
    app.cam_label2.configure(  # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # helmet statistics frame below camera
    statistics_frame_tab2 = ctk.CTkFrame(cam_frame_tab2, width=700, height=100)
    statistics_frame_tab2.pack(side="left", padx=10, pady=10)
    # fill the frame with helmet statistics of the day
    app.helmet_statistics_tab2 = ctk.CTkLabel(
        statistics_frame_tab2,
        text="Helmets Today: 0\nLast Helmet: -",
        height=80,
        width=700,
        anchor="center",
    )
    app.helmet_statistics_tab2.pack(pady=5, padx=10, fill="both", side="left")

    # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
    status_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=1000)
    status_frame_tab2.pack(side="right", fill="y", padx=10)

    status_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Last Helmet Detection")
    status_label_tab2.pack(pady=5)

    # list of last 10 helmets
    app.last_helmets_tab2 = ctk.CTkScrollableFrame(
        status_frame_tab2, width=600, height=700, fg_color="transparent"
    )
    app.last_helmets_tab2.pack(pady=5)
    app.helmet_button = ctk.CTkButton(status_frame_tab2, text="View All Helmets")
    app.helmet_button.pack(pady=5)

    update_helmet_list(app)


def create_numberplate_tab(app):
=======
import cv2
import threading
import time
from datetime import datetime
import os
from tkinter import filedialog  # Add this import for file dialog
from modules.numberplate_detection import NumberplateDetection
import easyocr  # Add this import for EasyOCR

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def detect_numberplate_in_frame(app, frame):
    numberplate_results = app.numberplate_detector.detect_numberplate(frame)
    return numberplate_results

def create_numberplate_tab(app):
    app.numberplate_detector = NumberplateDetection()  # Initialize numberplate detector
    app.camera_running_tab2 = False  # Initialize camera state for tab 2

>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
    top_row = ctk.CTkFrame(app.tab5)  # Set a specific height for the top row
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
    app.selected_camera_index_tab5 = available_cameras["Camera 1"]
=======
    available_cameras = {"Camera 1": 1}
    app.selected_camera_index_tab2 = available_cameras["Camera 1"]
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38

    # Button container with left alignment but keeping buttons smaller
    button_container = ctk.CTkFrame(button_frame)
    button_container.pack(
        fill="both", padx=5, pady=10
    )  # Ensuring buttons stay within frame width

<<<<<<< HEAD
    app.toggle_switch_tab5 = ctk.CTkSwitch(
        master=button_container,
        text="Camera",
        command=lambda: (
            start_timer(app) if app.toggle_switch_tab5.get() else stop_timer(app),
            start_camera(app) if app.toggle_switch_tab5.get() else stop_camera(app),
        ),
    )
    app.toggle_switch_tab5.pack(side="left", padx=8, fill="y")

    app.inferencing_tab5 = False  # Initialize inferencing state
    inferencing_button_tab5 = ctk.CTkButton(
        button_container,
        text="Start Inferencing",
        command=lambda: (
            setattr(app, "inferencing_tab5", not app.inferencing_tab5),
            inferencing_button_tab5.configure(
                text="Stop Inferencing" if app.inferencing_tab5 else "Start Inferencing"
            ),
            (
                start_inferencing(app, 5)
                if app.inferencing_tab5
                else stop_inferencing(app, 5)
            ),
        ),
    )
    inferencing_button_tab5.pack(
        side="left", padx=5, pady=10, expand=True, fill="x"
    )  # Expand inferencing button to take remaining space

    # Timer on the right side
    timer_frame_tab5 = ctk.CTkFrame(top_row)
    timer_frame_tab5.pack(side="right", padx=10, pady=10)  # Align at top-right (timer)
    app.camera_timer_tab5 = add_timer(app, timer_frame_tab5)

    # Status indicator (Camera Live/Off)
    status_indicator_frame_tab5 = ctk.CTkFrame(top_row)
    status_indicator_frame_tab5.pack(side="right", padx=10, pady=10)

    # Add the colored indicator (dot)
    app.status_indicator_tab5 = ctk.CTkLabel(
        status_indicator_frame_tab5, text="● Live", height=50, width=80
    )
    app.status_indicator_tab5.pack(side="left", padx=5, pady=2)
    update_status_indicator(app, "red")  # Initial state is red (camera off)

    # Main container for the three sections
    main_frame_tab5 = ctk.CTkFrame(app.tab5)
    main_frame_tab5.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab5 = ctk.CTkFrame(
        main_frame_tab5, width=700, height=400
    )  # Adjusted width and height
    cam_frame_tab5.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab5 = ctk.CTkLabel(
        cam_frame_tab5, text="Number Plate Camera Feed"
    )
    app.camera_title_tab5.pack(pady=2)
    app.camera_title_tab5.configure(
        font=("Arial", 18, "bold")
    )  # Set text color to black
    # Label to display the camera feed
    app.cam_label5 = ctk.CTkLabel(
        cam_frame_tab5, text=" ", fg_color="gray", height=400, width=700
    )  # Gray background color
    app.cam_label5.pack(
        expand=True, fill="both", padx=10, pady=8
    )  # Use fill="both" to ensure it takes up the full space
    app.cam_label5.configure(  # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # accident statistics frame below camera
    statistics_frame_tab5 = ctk.CTkFrame(cam_frame_tab5, width=700, height=100)
    statistics_frame_tab5.pack(side="left", padx=10, pady=10)
    # fill the frame with accident statistics of the day
    app.accident_statistics_tab5 = ctk.CTkLabel(
        statistics_frame_tab5,
        text="Accidents Today: 0\nLast Accident: -",
        height=80,
        width=700,
        anchor="center",
    )
    app.accident_statistics_tab5.pack(pady=5, padx=10, fill="both", side="left")

    # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
    status_frame_tab5 = ctk.CTkFrame(main_frame_tab5, width=1000)
    status_frame_tab5.pack(side="right", fill="y", padx=10)

    status_label_tab5 = ctk.CTkLabel(status_frame_tab5, text="Last Accident Detection")
    status_label_tab5.pack(pady=5)

    # list of last 10 accidents
    app.last_accidents_tab5 = ctk.CTkScrollableFrame(
        status_frame_tab5, width=600, height=700, fg_color="transparent"
    )
    app.last_accidents_tab5.pack(pady=5)
    app.accident_button = ctk.CTkButton(status_frame_tab5, text="View All Accidents")
    app.accident_button.pack(pady=5)

    update_accident_list(app)


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
            helmet_image_label = ctk.CTkLabel(
                frame, image=helmet_image, text="", width=50, height=50
            )
            helmet_image_label.pack(side="left", padx=8, pady=5)
        except FileNotFoundError:
            helmet_image_label = ctk.CTkLabel(
                frame, text="No Image", width=50, height=50
            )
            helmet_image_label.pack(side="left", padx=8, pady=5)
=======
    app.toggle_switch_tab2 = ctk.CTkSwitch(
        master=button_container,
        text="Camera",
        command=lambda: (
        start_timer(app) if app.toggle_switch_tab2.get() else stop_timer(app),
        start_camera(app, 2) if app.toggle_switch_tab2.get() else stop_camera(app, 2),
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

    # Add button to upload video file
    upload_button = ctk.CTkButton(
        button_container,
        text="Upload Video",
        command=lambda: upload_video(app)
    )
    upload_button.pack(side="left", padx=5, pady=10, expand=True, fill="x")

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
    main_frame_tab2 = ctk.CTkFrame(app.tab5)
    main_frame_tab2.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=700, height=400)  # Adjusted width and height
    cam_frame_tab2.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab2 = ctk.CTkLabel(cam_frame_tab2, text="Numberplate Camera Feed")
    app.camera_title_tab2.pack(pady=2)
    app.camera_title_tab2.configure(font=("Arial",18,"bold"))  # Set text color to black
    # Label to display the camera feed
    app.cam_label2 = ctk.CTkLabel(cam_frame_tab2, text=" ", fg_color="gray", height=400, width=700)  # Gray background color
    app.cam_label2.pack(expand=True, fill="both", padx=10,pady=8)  # Use fill="both" to ensure it takes up the full space
    app.cam_label2.configure( # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # Numberplate statistics frame below camera
    statistics_frame_tab2 = ctk.CTkFrame(cam_frame_tab2, width=700, height=100)
    statistics_frame_tab2.pack(side="left", padx=10, pady=10)
    # Fill the frame with numberplate statistics of the day
    app.numberplate_statistics_tab2 = ctk.CTkLabel(statistics_frame_tab2, text="Numberplates Detected Today: 0\nLast Numberplate: -", height=80, width=700, anchor="center")
    app.numberplate_statistics_tab2.pack(pady=5, padx=10, fill="both", side="left")
    update_numberplate_statistics(app)  # Initialize numberplate statistics

    # Rightmost section (Detection Status, Last 10 Results)
    status_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=1000, height=500)
    status_frame_tab2.pack(side="right", fill="y", padx=10)

    status_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Last Numberplate Detection")
    status_label_tab2.pack(pady=5)
    
    # List of last 10 numberplates
    app.last_numberplates_tab2 = ctk.CTkScrollableFrame(status_frame_tab2, width=600, height=500, fg_color="transparent")
    app.last_numberplates_tab2.pack(pady=5)
    app.numberplate_button = ctk.CTkButton(status_frame_tab2, text="View All Numberplates")
    app.numberplate_button.pack(pady=5)

    update_numberplate_list(app)

def upload_video(app):
    """Upload a video file and run the model on it."""
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if video_path:
        threading.Thread(target=lambda: process_video(app, video_path), daemon=True).start()

def process_video(app, video_path):
    """Process the uploaded video file."""
    while True:  # Loop the video
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            numberplate_results = detect_numberplate_in_frame(app, frame)
            frame, classes = process_frame_with_yolo(app, frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label2.configure(image=img_tk)
            app.cam_label2.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[2].configure(image=img_tk_dashboard)
            app.camera_labels[2].image = img_tk_dashboard

            time.sleep(0.03)  # Control the frame rate

        cap.release()

def update_numberplate_statistics(app, last_numberplate=""):
    """Update the numberplate statistics."""
    detected_today = int(app.numberplate_statistics_tab2.cget("text").split(":")[1].split("\n")[0].strip()) + 1
    app.numberplate_statistics_tab2.configure(
        text=f"Numberplates Detected Today: {detected_today}\nLast Numberplate: {last_numberplate}"
    )

def update_numberplate_list(app):
    """Update the list of numberplates in the sidebar."""
    for widget in app.last_numberplates_tab2.winfo_children():
        widget.destroy()

    # Placeholder for numberplate folders
    numberplate_folders = []

    for i, folder in enumerate(numberplate_folders):
        frame = ctk.CTkFrame(app.last_numberplates_tab2)
        frame.pack(fill="x", padx=5, pady=5)

        timestamp = datetime.strptime(folder, "%Y-%m-%d %H-%M-%S").strftime("%d-%m-%Y %H:%M:%S")
        image_path = f"numberplates/{folder}/numberplate-{folder}.png"
        details_path = f"numberplates/{folder}/details.txt"

        try:
            numberplate_image = ctk.CTkImage(Image.open(image_path), size=(50, 50))
            numberplate_image_label = ctk.CTkLabel(frame, image=numberplate_image, text="", width=50, height=50)
            numberplate_image_label.pack(side="left", padx=8, pady=5)
        except FileNotFoundError:
            numberplate_image_label = ctk.CTkLabel(frame, text="No Image", width=50, height=50)
            numberplate_image_label.pack(side="left", padx=8, pady=5)
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38

        try:
            with open(details_path, "r") as f:
                details = f.read().strip()
            button_color = "green"
        except FileNotFoundError:
<<<<<<< HEAD
            details = "No details available"
=======
            details = "No details found"
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
            button_color = "red"

        button = ctk.CTkButton(
            frame,
            text=timestamp,
            compound="left",
<<<<<<< HEAD
            command=lambda hel=folder: show_helmet_details(helmet=hel),
            anchor="center",
            height=50,
            fg_color=button_color,
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        try:
            with open(classes_path, "r") as f:
                classes = f.readlines()
            for cls in classes:
                cls_button = ctk.CTkButton(
                    frame, text=f"Helmet of: {cls.strip()}", height=30
                )
                cls_button.pack(side="left", padx=5, pady=5)
        except FileNotFoundError:
            pass


def update_accident_list(app):
    """Update the list of accidents in the sidebar."""
    for widget in app.last_accidents_tab5.winfo_children():
        widget.destroy()

    today = time.strftime("%Y-%m-%d")
    accident_folders = [f for f in os.listdir("accidents") if today in f]

    for folder in accident_folders:
        frame = ctk.CTkFrame(app.last_accidents_tab5)
        frame.pack(fill="x", padx=5, pady=5)

        timestamp = folder.replace("accident-", "")
        image_path = f"accidents/{folder}/accident-{timestamp}.png"
        details_path = f"accidents/{folder}/details.txt"
        classes_path = f"accidents/{folder}/classes.txt"

        try:
            accident_image = ctk.CTkImage(Image.open(image_path), size=(50, 50))
            accident_image_label = ctk.CTkLabel(
                frame, image=accident_image, text="", width=50, height=50
            )
            accident_image_label.pack(side="left", padx=8, pady=5)
        except FileNotFoundError:
            accident_image_label = ctk.CTkLabel(
                frame, text="No Image", width=50, height=50
            )
            accident_image_label.pack(side="left", padx=8, pady=5)

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
            command=lambda acc=folder: show_accident_details(accident=acc),
            anchor="center",
            height=50,
            fg_color=button_color,
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        try:
            with open(classes_path, "r") as f:
                classes = f.readlines()
            for cls in classes:
                cls_button = ctk.CTkButton(
                    frame, text=f"Collision of: {cls.strip()}", height=30
                )
                cls_button.pack(side="left", padx=5, pady=5)
        except FileNotFoundError:
            pass


def show_helmet_details(helmet):
    """Show a pop-up with helmet details."""
    details_path = f"helmets/{helmet}/details.txt"
=======
            command=lambda np=folder: show_numberplate_details(app, numberplate=np, editable=(button_color == "red")),
            anchor="center",
            height=50,
            fg_color=button_color
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

def show_numberplate_details(app, numberplate, editable=False, large=False):
    """Show a pop-up with numberplate details."""
    details_path = f"numberplates/{numberplate}/details.txt"
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
<<<<<<< HEAD
        details = "No details available"
    messagebox.showinfo(
        "Helmet Details",
        f"Timestamp: {helmet.replace('helmet-', '')}\nDetails: {details}",
    )


def show_accident_details(accident):
    """Show a pop-up with accident details."""
    details_path = f"accidents/{accident}/details.txt"
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
        details = "No details available"
    messagebox.showinfo(
        "Accident Details",
        f"Timestamp: {accident.replace('accident-', '')}\nDetails: {details}",
    )

=======
        details = "No data found, add data"

    popup = ctk.CTkToplevel(app)
    popup.title("Numberplate Details")
    popup.geometry("800x800" if large else "600x600")
    popup.attributes("-topmost", True)  # Keep the pop-up on top

    scrollable_frame = ctk.CTkScrollableFrame(popup)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    details_label = ctk.CTkLabel(scrollable_frame, text=f"TIMESTAMP: {numberplate.replace('numberplate-', '')}", font=("Arial", 16, "bold"))
    details_label.pack(pady=10)

    if editable:
        numberplate_entry = ctk.CTkEntry(scrollable_frame, placeholder_text="Enter numberplate details")
        numberplate_entry.pack(pady=5)

        def save_details():
            with open(details_path, "w") as f:
                f.write(numberplate_entry.get())
            popup.destroy()
            update_numberplate_list(app)

        save_button = ctk.CTkButton(scrollable_frame, text="Save", command=save_details)
        save_button.pack(pady=10)

    else:
        details_label = ctk.CTkLabel(scrollable_frame, text=details, font=("Arial", 14))
        details_label.pack(pady=10)

        edit_button = ctk.CTkButton(scrollable_frame, text="Edit", command=lambda: show_numberplate_details(app, numberplate, editable=True))
        edit_button.pack(pady=10)
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38

def add_logo(app, parent):
    """Adds a logo to the top left corner of a tab."""
    logo_label = ctk.CTkLabel(parent, image=app.logo_image, text="")
    logo_label.pack(anchor="nw", padx=10, pady=10)

<<<<<<< HEAD

=======
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
def add_timer(app, parent):
    """Adds a timer to the top right corner of a tab."""
    timer_label = ctk.CTkLabel(parent, text="Time: 00:00:00", height=50, width=100)
    timer_label.pack(anchor="ne", padx=10, pady=2)
    return timer_label

<<<<<<< HEAD

=======
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
def update_status_indicator(app, color):
    """Update the status indicator color."""
    app.status_indicator_tab2.configure(text_color=color)

<<<<<<< HEAD

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
=======
def start_camera(app, tab):
    """Start the webcam feed."""
    if tab == 2:
        if not hasattr(app, "selected_camera_index_tab2"):
            messagebox.showerror("Error", "Please select a camera.")
            return
        if not app.camera_running_tab2:
            app.cap_tab2 = cv2.VideoCapture(
                app.selected_camera_index_tab2
            )  # Initialize the webcam with the selected index
            app.camera_running_tab2 = True
            app.camera_thread_tab2 = threading.Thread(
                target=lambda: update_camera_feed_tab2(app), daemon=True
            )
            app.camera_thread_tab2.start()
        else:
            messagebox.showerror("Error", "Camera is already running in Tab 2.")

def stop_camera(app, tab):
    """Stop the webcam feed."""
    if tab == 2:
        if app.camera_running_tab2:
            app.camera_running_tab2 = False
            if app.cap_tab2:
                app.cap_tab2.release()  # Release the webcam
            app.cam_label2.configure(image=None)  # Clear the camera feed

def process_frame_with_yolo(app, frame):
    """Process the frame with YOLO model."""
    results, class_names = app.numberplate_detector.detect_numberplate(frame)
    classes = class_names.copy()
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            if class_names:
                class_name = class_names.pop(0)
                numberplate_text = mark_and_ocr_numberplate(app, frame, (x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{numberplate_text}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return frame, classes

def mark_and_ocr_numberplate(app, frame, bbox):
    """Mark the numberplate and run OCR to extract the number."""
    x1, y1, x2, y2 = bbox
    numberplate_image = frame[y1:y2, x1:x2]
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    folder_path = f"numberplates/{timestamp}"
    os.makedirs(folder_path, exist_ok=True)
    image_path = f"{folder_path}/numberplate-{timestamp}.png"
    cv2.imwrite(image_path, cv2.cvtColor(numberplate_image, cv2.COLOR_RGB2BGR))
    
    # Run OCR on the cropped numberplate image using EasyOCR
    result = reader.readtext(numberplate_image)
    numberplate_text = result[0][-2] if result else "Unknown"
    
    with open(f"{folder_path}/details.txt", "w") as f:
        f.write(f"Numberplate: {numberplate_text}")
    
    update_numberplate_list(app)
    update_numberplate_statistics(app, numberplate_text)
    
    return numberplate_text

def update_camera_feed_tab2(app):
    """Update the camera feed in the GUI for tab 2."""
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
    while app.camera_running_tab2:
        ret, frame = app.cap_tab2.read()
        if not ret:
            break

<<<<<<< HEAD
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
=======
        numberplate_results = detect_numberplate_in_frame(app, frame)
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38

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
<<<<<<< HEAD
            app.camera_labels[1].configure(image=img_tk_dashboard)
            app.camera_labels[1].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate


def update_accident_camera_feed(app):
    """Update the camera feed in the GUI."""
    while app.camera_running_tab5:
        ret, frame = app.cap_tab5.read()
        if not ret:
            break

        accident_detected, classes_present = detect_helmet_in_frame(frame)

        if accident_detected:
            app.consecutive_frames_with_accident += 1
            app.consecutive_frames_without_accident = 0
            accident_results, accident_classes = app.accident_detector.detect_accident(
                frame
            )
            app.frames_buffer.append((frame, datetime.now(), accident_classes))

            if app.consecutive_frames_with_accident >= 80:
                # Store frames if accident detected for 80 out of 100 frames
                save_accident_frames(
                    app.frames_buffer, datetime.now(), accident_classes
                )
                app.frames_buffer = []
                app.consecutive_frames_with_accident = 0
        else:
            app.consecutive_frames_without_accident += 1
            if app.consecutive_frames_without_accident >= 30:
                # Reset buffer if accident is out of frame for 30 consecutive frames
                app.frames_buffer = []
                app.consecutive_frames_with_accident = 0

        if app.inferencing_tab5:
            frame, classes = process_accident_frame_with_yolo(app, frame)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label5.configure(image=img_tk)
            app.cam_label5.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[3].configure(image=img_tk_dashboard)
            app.camera_labels[3].image = img_tk_dashboard

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
            cv2.putText(
                frame,
                class_name,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )
    return frame, classes


def process_accident_frame_with_yolo(app, frame):
    """Process the frame with YOLO model."""
    results, class_names = app.accident_detector.detect_accident(frame)
    classes = class_names.copy()
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            class_name = class_names.pop(0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                class_name,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )
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
=======
            app.camera_labels[2].configure(image=img_tk_dashboard)
            app.camera_labels[2].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate

def start_timer(app):
    """Start the timer."""
    app.timer_running_tab2 = True
    app.timer_thread_tab2 = threading.Thread(target=lambda: update_timer(app), daemon=True)
    app.timer_thread_tab2.start()

def stop_timer(app):
    """Stop the timer."""
    app.timer_running_tab2 = False

def update_timer(app):
    """Update the timer display."""
    start_time = time.time()
    while app.timer_running_tab2:
        elapsed_time = time.time() - start_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        app.camera_timer_tab2.configure(text=f"Time: {formatted_time}")
        time.sleep(1)

# ...existing code...
>>>>>>> 2189b8e6d7ca1b1bfa3ec1e6f7c4647de71e0e38
