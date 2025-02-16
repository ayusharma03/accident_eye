import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as messagebox
import cv2
import threading
import os
import time
from datetime import datetime
from modules.accident_detection import AccidentDetection
from twilio.rest import Client  # Add this import for sending SMS and making calls
from tkinter import filedialog  # Add this import for file dialog

# Initialize accident detection variables
consecutive_frames_with_accident = 0
consecutive_frames_without_accident = 0
frames_buffer = []
accidents = []
accident_detector = AccidentDetection()

# Twilio configuration for sending SMS and making calls
# TWILIO_ACCOUNT_SID = 'ACee0adc0c7b1db4366aefc9a30dc24092'
# TWILIO_AUTH_TOKEN = '79890bf0810f43298073e50734f5d1d3'
TWILIO_PHONE_NUMBER = '+18318880932'
EMERGENCY_CONTACT_NUMBER = '+918750880297'

def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=EMERGENCY_CONTACT_NUMBER
    )

def make_call(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        from_=TWILIO_PHONE_NUMBER,
        to=EMERGENCY_CONTACT_NUMBER
    )

def contact_emergency_services(timestamp, location):
    message = f"Accident detected at {location} on {timestamp}. Immediate assistance required."
    send_sms(message)
    make_call(message)

def detect_accident_in_frame(frame):
    accident_detected, accident_class_names, accident_probabilities = accident_detector.detect_accident(frame)
    accident_detected = 'Accident' in accident_class_names  # Adjust this condition based on your accident detection logic
    return accident_detected, accident_class_names, accident_probabilities

def update_accident_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"accidents/log_{today}.txt"
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("Accidents Today: 0\nLast Accident: -\n")
    return log_file

def read_accident_log():
    log_file = update_accident_log()
    with open(log_file, "r") as f:
        lines = f.readlines()
    accidents_today = int(lines[0].split(": ")[1])
    last_accident = lines[1].split(": ")[1].strip()
    return accidents_today, last_accident

def write_accident_log(accidents_today, last_accident):
    log_file = update_accident_log()
    with open(log_file, "w") as f:
        f.write(f"Accidents Today: {accidents_today}\n")
        f.write(f"Last Accident: {last_accident}\n")

def save_frames(app, frames, timestamp, classes_present, confirmed=True):
    folder_name = timestamp.strftime("%Y-%m-%d %H-%M-%S")
    folder_path = os.path.join("accidents", folder_name)
    if not confirmed:
        folder_path = os.path.join("accidents/reject_accidents", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    for i, (frame, frame_time, frame_classes) in enumerate(frames):
        frame_name = f"accident-{frame_time.strftime('%Y-%m-%d %H-%M-%S')}.png"
        cv2.imwrite(os.path.join(folder_path, frame_name), frame)
    
    if confirmed:
        accidents.append({
            "timeline": folder_name,
            "details": classes_present
        })
        accidents_today, _ = read_accident_log()
        accidents_today += 1
        write_accident_log(accidents_today, folder_name)
        update_accident_list(app)  # Update the accident list in real-time
        update_accident_statistics(app)  # Update the accident statistics in real-time

def confirm_accident(app, frames_buffer, timestamp, accident_classes):
    def on_confirm():
        save_frames(app, frames_buffer, timestamp, accident_classes, confirmed=True)
        stop_inferencing(app, 1)  # Stop inferencing when an accident is confirmed
        stop_backend_detection(app)  # Stop backend accident detection
        contact_emergency_services(timestamp, "Coimbatore")  # Contact emergency services
        popup.destroy()
        confirm_clearance(app)  # Confirm clearance before starting next inference

    def on_reject():
        save_frames(app, frames_buffer, timestamp, accident_classes, confirmed=False)
        popup.destroy()

    popup = ctk.CTkToplevel(app)
    popup.title("Confirm Accident")
    popup.geometry("300x150")
    popup.attributes("-topmost", True)  # Keep the pop-up on top
    label = ctk.CTkLabel(popup, text="Is this an accident?")
    label.pack(pady=10)
    confirm_button = ctk.CTkButton(popup, text="Yes", command=on_confirm)
    confirm_button.pack(side="left", padx=20, pady=20)
    reject_button = ctk.CTkButton(popup, text="No", command=on_reject)
    reject_button.pack(side="right", padx=20, pady=20)
    
    popup.after(20000, on_confirm)  # Automatically confirm after 20 seconds

def confirm_clearance(app):
    def on_clear():
        start_inferencing(app, 1)  # Start inferencing after clearance is confirmed
        start_backend_detection(app)  # Start backend accident detection
        popup.destroy()

    popup = ctk.CTkToplevel(app)
    popup.title("Confirm Clearance")
    popup.geometry("300x150")
    popup.attributes("-topmost", True)  # Keep the pop-up on top
    label = ctk.CTkLabel(popup, text="Is the accident site cleared?")
    label.pack(pady=10)
    clear_button = ctk.CTkButton(popup, text="Yes", command=on_clear)
    clear_button.pack(pady=20)

def create_accidents_tab(app):
    app.backend_detection_running = True  # Initialize backend detection state
    top_row = ctk.CTkFrame(app.tab2)  # Set a specific height for the top row
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
    app.selected_camera_index_tab1 = available_cameras["Camera 1"]

    # Button container with left alignment but keeping buttons smaller
    button_container = ctk.CTkFrame(button_frame)
    button_container.pack(
        fill="both", padx=5, pady=10
    )  # Ensuring buttons stay within frame width

    app.toggle_switch_tab1 = ctk.CTkSwitch(
        master=button_container,
        text="Camera",
        command=lambda: (
        start_timer(app) if app.toggle_switch_tab1.get() else stop_timer(app),
        start_camera(app) if app.toggle_switch_tab1.get() else stop_camera(app),
        ),
    )
    app.toggle_switch_tab1.pack(side="left", padx=8, fill="y")
    

    app.inferencing_tab1 = False  # Initialize inferencing state
    inferencing_button_tab1 = ctk.CTkButton(
        button_container,
        text="Start Inferencing",
        command=lambda: (
            setattr(app, "inferencing_tab1", not app.inferencing_tab1),
            inferencing_button_tab1.configure(
                text="Stop Inferencing" if app.inferencing_tab1 else "Start Inferencing"
            ),
            start_inferencing(app, 1) if app.inferencing_tab1 else stop_inferencing(app, 1),
        ),
    )
    inferencing_button_tab1.pack(
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
    timer_frame_tab1 = ctk.CTkFrame(top_row)
    timer_frame_tab1.pack(
        side="right", padx=10, pady=10
    )  # Align at top-right (timer)
    app.camera_timer_tab1 = add_timer(app, timer_frame_tab1)

    # Status indicator (Camera Live/Off)
    status_indicator_frame_tab1 = ctk.CTkFrame(top_row)
    status_indicator_frame_tab1.pack(side="right", padx=10, pady=10)

    # Add the colored indicator (dot)
    app.status_indicator_tab1 = ctk.CTkLabel(status_indicator_frame_tab1, text="● Live", height=50, width=80)
    app.status_indicator_tab1.pack(side="left", padx=5, pady=2)
    update_status_indicator(app, "red")  # Initial state is red (camera off)

    # Main container for the three sections
    main_frame_tab1 = ctk.CTkFrame(app.tab2)
    main_frame_tab1.pack(fill="both", expand=True, padx=5)

    # Middle section (Live Camera Feed) =======
    cam_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=700, height=400)  # Adjusted width and height
    cam_frame_tab1.pack(side="left", expand=True)  # Added pady for vertical padding
    # Camera title frame and label
    app.camera_title_tab1 = ctk.CTkLabel(cam_frame_tab1, text="Accident Camera Feed")
    app.camera_title_tab1.pack(pady=2)
    app.camera_title_tab1.configure(font=("Arial",18,"bold"))  # Set text color to black
    # Label to display the camera feed
    app.cam_label1 = ctk.CTkLabel(cam_frame_tab1, text=" ", fg_color="gray", height=400, width=700)  # Gray background color
    app.cam_label1.pack(expand=True, fill="both", padx=10,pady=8)  # Use fill="both" to ensure it takes up the full space
    app.cam_label1.configure( # Set corner radius for a rounded appearance
        corner_radius=8
    )

    # accident statistics frame below camera
    statistics_frame_tab1 = ctk.CTkFrame(cam_frame_tab1, width=700, height=100)
    statistics_frame_tab1.pack(side="left", padx=10, pady=10)
    # fill the frame with accident statistics of the day
    app.accident_statistics_tab1 = ctk.CTkLabel(statistics_frame_tab1, text="Accidents Today: 0\nLast Accident: -", height=80, width=700,anchor="center")
    app.accident_statistics_tab1.pack(pady=5, padx=10, fill="both", side="left")
    update_accident_statistics(app)  # Initialize accident statistics

    # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
    status_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=1000, height=500)
    status_frame_tab1.pack(side="right", fill="y", padx=10)

    status_label_tab1 = ctk.CTkLabel(status_frame_tab1, text="Last Accident Detection")
    status_label_tab1.pack(pady=5)
    
    # list of last 10 accidents
    app.last_accidents_tab1 = ctk.CTkScrollableFrame(status_frame_tab1, width=600, height=500, fg_color="transparent")
    app.last_accidents_tab1.pack(pady=5)
    app.accident_button = ctk.CTkButton(status_frame_tab1, text="View All Accidents")
    app.accident_button.pack(pady=5)

    update_accident_list(app)

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

            accident_detected, classes_present, probabilities = detect_accident_in_frame(frame)
            probabilities = [float(prob) for prob in probabilities]  # Convert probabilities to float

            if accident_detected and max(probabilities) > 0.5:
                app.consecutive_frames_with_accident += 1
                app.consecutive_frames_without_accident = 0
                accident_results, accident_classes, accident_probabilities = app.accident_detector.detect_accident(frame)
                app.frames_buffer.append((frame, datetime.now(), accident_classes))

                if app.consecutive_frames_with_accident >= 80:
                    # Store frames if accident detected for 80 out of 100 frames
                    confirm_accident(app, app.frames_buffer, datetime.now(), accident_classes)
                    app.frames_buffer = []
                    app.consecutive_frames_with_accident = 0
            else:
                app.consecutive_frames_without_accident += 1
                if app.consecutive_frames_without_accident >= 30:
                    # Reset buffer if accident is out of frame for 30 consecutive frames
                    app.frames_buffer = []
                    app.consecutive_frames_with_accident = 0

            frame, classes = process_frame_with_yolo(app, frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label1.configure(image=img_tk)
            app.cam_label1.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[0].configure(image=img_tk_dashboard)
            app.camera_labels[0].image = img_tk_dashboard

            time.sleep(0.03)  # Control the frame rate

        cap.release()

def update_accident_statistics(app):
    accidents_today, last_accident = read_accident_log()
    app.accident_statistics_tab1.configure(
        text=f"Accidents Today: {accidents_today}\nLast Accident: {last_accident}"
    )

def update_accident_list(app):
    """Update the list of accidents in the sidebar."""
    for widget in app.last_accidents_tab1.winfo_children():
        widget.destroy()

    accident_folders = sorted(
        [f for f in os.listdir("accidents") if os.path.isdir(os.path.join("accidents", f)) and "reject_accidents" not in f],
        key=lambda x: datetime.strptime(x, "%Y-%m-%d %H-%M-%S"),
        reverse=True
    )

    for i, folder in enumerate(accident_folders):
        frame = ctk.CTkFrame(app.last_accidents_tab1)
        frame.pack(fill="x", padx=5, pady=5)

        timestamp = datetime.strptime(folder, "%Y-%m-%d %H-%M-%S").strftime("%d-%m-%Y %H:%M:%S")
        image_path = f"accidents/{folder}/accident-{folder}.png"
        details_path = f"accidents/{folder}/details.txt"
        classes_path = f"accidents/{folder}/classes.txt"

        try:
            accident_image = ctk.CTkImage(Image.open(image_path), size=(50, 50))
            accident_image_label = ctk.CTkLabel(frame, image=accident_image, text="", width=50, height=50)
            accident_image_label.pack(side="left", padx=8, pady=5)
        except FileNotFoundError:
            accident_image_label = ctk.CTkLabel(frame, text="No Image", width=50, height=50)
            accident_image_label.pack(side="left", padx=8, pady=5)

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
            command=lambda acc=folder: show_accident_details(app, accident=acc, editable=(button_color == "red")),
            anchor="center",
            height=50,
            fg_color=button_color
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        try:
            with open(classes_path, "r") as f:
                classes = f.readlines()
            for cls in classes:
                cls_button = ctk.CTkButton(frame, text=f"Collision of: {cls.strip()}", height=30)
                cls_button.pack(side="left", padx=5, pady=5)
        except FileNotFoundError:
            pass

def show_accident_details(app, accident, editable=False, large=False):
    """Show a pop-up with accident details."""
    details_path = f"accidents/{accident}/details.txt"
    video_path = f"accidents/{accident}/accident_video.mp4"
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
        details = "No data found, add data"

    popup = ctk.CTkToplevel(app)
    popup.title("Accident Details")
    popup.geometry("800x800" if large else "600x600")
    popup.attributes("-topmost", True)  # Keep the pop-up on top

    scrollable_frame = ctk.CTkScrollableFrame(popup)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    details_label = ctk.CTkLabel(scrollable_frame, text=f"TIMESTAMP: {accident.replace('accident-', '')}", font=("Arial", 16, "bold"))
    details_label.pack(pady=10)

    if editable:
        vehicle_classes_label = ctk.CTkLabel(scrollable_frame, text="VEHICLE CLASSES INVOLVED:", font=("Arial", 14, "bold"))
        vehicle_classes_label.pack(pady=5)
        
        vehicle_classes = ["Car", "Truck", "Bike", "Bus", "Van"]
        vehicle_class_buttons = []
        vehicle_class_frame = ctk.CTkFrame(scrollable_frame)
        vehicle_class_frame.pack(pady=5)
        for i, vehicle_class in enumerate(vehicle_classes):
            var = ctk.BooleanVar()
            button = ctk.CTkCheckBox(vehicle_class_frame, text=vehicle_class, variable=var)
            button.grid(row=i//2, column=i%2, padx=5, pady=5)
            vehicle_class_buttons.append((vehicle_class, var))

        reason_frame = ctk.CTkFrame(scrollable_frame)
        reason_frame.pack(pady=5, fill="x")
        reason_label = ctk.CTkLabel(reason_frame, text="REASON OF ACCIDENT:", font=("Arial", 14, "bold"))
        reason_label.pack(pady=5)
        reason_entry = ctk.CTkEntry(reason_frame, placeholder_text="Enter reason of accident")
        reason_entry.pack(pady=5)

        casualties_frame = ctk.CTkFrame(scrollable_frame)
        casualties_frame.pack(pady=5, fill="x")
        casualties_label = ctk.CTkLabel(casualties_frame, text="CASUALTIES:", font=("Arial", 14, "bold"))
        casualties_label.pack(pady=5)
        casualties_entry = ctk.CTkEntry(casualties_frame, placeholder_text="Enter number of casualties")
        casualties_entry.pack(pady=5)

        injured_frame = ctk.CTkFrame(scrollable_frame)
        injured_frame.pack(pady=5, fill="x")
        injured_label = ctk.CTkLabel(injured_frame, text="INJURED PEOPLE:", font=("Arial", 14, "bold"))
        injured_label.pack(pady=5)
        injured_entry = ctk.CTkEntry(injured_frame, placeholder_text="Enter number of injured people")
        injured_entry.pack(pady=5)

        accident_type_frame = ctk.CTkFrame(scrollable_frame)
        accident_type_frame.pack(pady=5, fill="x")
        accident_type_label = ctk.CTkLabel(accident_type_frame, text="TYPE OF ACCIDENT:", font=("Arial", 14, "bold"))
        accident_type_label.pack(pady=5)
        accident_type_var = ctk.StringVar()
        minor_radio = ctk.CTkRadioButton(accident_type_frame, text="Minor", variable=accident_type_var, value="Minor")
        minor_radio.pack(pady=5)
        major_radio = ctk.CTkRadioButton(accident_type_frame, text="Major", variable=accident_type_var, value="Major")
        major_radio.pack(pady=5)

        def save_details():
            selected_classes = [vc for vc, var in vehicle_class_buttons if var.get()]
            with open(details_path, "w") as f:
                f.write(f"Vehicle Classes: {', '.join(selected_classes)}\n")
                f.write(f"Reason: {reason_entry.get()}\n")
                f.write(f"Casualties: {casualties_entry.get()}\n")
                f.write(f"Injured: {injured_entry.get()}\n")
                f.write(f"Type: {accident_type_var.get()}\n")
            popup.destroy()
            update_accident_list(app)

        save_button = ctk.CTkButton(scrollable_frame, text="Save", command=save_details)
        save_button.pack(pady=10)

    else:
        details_lines = details.split('\n')
        for line in details_lines:
            if line.startswith("Vehicle Classes:"):
                vehicle_classes_frame = ctk.CTkFrame(scrollable_frame, fg_color="lightgray")
                vehicle_classes_frame.pack(pady=5, fill="x")
                vehicle_classes_label = ctk.CTkLabel(vehicle_classes_frame, text=line, font=("Arial", 14))
                vehicle_classes_label.pack(pady=5)
            elif line.startswith("Reason:"):
                reason_frame = ctk.CTkFrame(scrollable_frame, fg_color="lightgray")
                reason_frame.pack(pady=5, fill="x")
                reason_label = ctk.CTkLabel(reason_frame, text=line, font=("Arial", 14))
                reason_label.pack(pady=5)
            elif line.startswith("Casualties:"):
                casualties_frame = ctk.CTkFrame(scrollable_frame, fg_color="lightgray")
                casualties_frame.pack(pady=5, fill="x")
                casualties_label = ctk.CTkLabel(casualties_frame, text=line, font=("Arial", 14))
                casualties_label.pack(pady=5)
            elif line.startswith("Injured:"):
                injured_frame = ctk.CTkFrame(scrollable_frame, fg_color="lightgray")
                injured_frame.pack(pady=5, fill="x")
                injured_label = ctk.CTkLabel(injured_frame, text=line, font=("Arial", 14))
                injured_label.pack(pady=5)
            elif line.startswith("Type:"):
                accident_type_frame = ctk.CTkFrame(scrollable_frame, fg_color="lightgray")
                accident_type_frame.pack(pady=5, fill="x")
                accident_type_label = ctk.CTkLabel(accident_type_frame, text=line, font=("Arial", 14))
                accident_type_label.pack(pady=5)

        if details == "No data found, add data":
            no_data_label = ctk.CTkLabel(scrollable_frame, text=details, font=("Arial", 14, "bold"))
            no_data_label.pack(pady=10)

        edit_button = ctk.CTkButton(scrollable_frame, text="Edit", command=lambda: show_accident_details(app, accident, editable=True))
        edit_button.pack(pady=10)

    # Add video player frame at the bottom
    video_frame = ctk.CTkFrame(scrollable_frame)
    video_frame.pack(pady=10, fill="x")

    if os.path.exists(video_path):
        video_label = ctk.CTkLabel(video_frame, text="Accident Video:", font=("Arial", 14, "bold"))
        video_label.pack(pady=5)
        
        video_player = ctk.CTkLabel(video_frame)
        video_player.pack(pady=5)

        def play_video():
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                video_player.configure(image=img_tk)
                video_player.image = img_tk
                video_player.update()
                time.sleep(0.03)
            cap.release()

        threading.Thread(target=play_video, daemon=True).start()

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
    app.status_indicator_tab1.configure(text_color=color)

def start_camera(app):
    """Start the webcam feed."""
    if not hasattr(app, "selected_camera_index_tab1"):
        messagebox.showerror("Error", "Please select a camera.")
        return
    if not app.camera_running_tab1:
        app.cap_tab1 = cv2.VideoCapture(
            app.selected_camera_index_tab1
        )  # Initialize the webcam with the selected index
        app.camera_running_tab1 = True
        app.camera_thread_tab1 = threading.Thread(
            target=lambda: update_camera_feed(app), daemon=True
        )
        app.camera_thread_tab1.start()
    else:
        messagebox.showerror("Error", "Camera is already running in Tab 1.")

def stop_camera(app):
    """Stop the webcam feed."""
    print("camera stoppingg")
    if app.camera_running_tab1:
        app.camera_running_tab1 = False
        if app.cap_tab1:
            app.cap_tab1.release()  # Release the webcam
        app.cam_label1.configure(image=None)  # Clear the camera feed

def start_inferencing(app, tab):
    """Start inferencing and update the camera feed with YOLO processed frames."""
    if tab == 1:
        if not app.camera_running_tab1:
            messagebox.showerror("Error", "Camera is not running")
            return
        app.inferencing_tab1 = True
    else:
        if not app.camera_running_tab2:
            messagebox.showerror("Error", "Camera is not running")
            return
        app.inferencing_tab2 = True

def stop_inferencing(app, tab):
    """Stop inferencing."""
    if tab == 1:
        app.inferencing_tab1 = False
    else:
        app.inferencing_tab2 = False

def update_camera_feed(app):
    """Update the camera feed in the GUI."""
    while app.camera_running_tab1:
        ret, frame = app.cap_tab1.read()
        if not ret:
            break

        if not app.backend_detection_running:
            time.sleep(0.03)  # Control the frame rate
            continue

        accident_detected, classes_present, probabilities = detect_accident_in_frame(frame)
        probabilities = [float(prob) for prob in probabilities]  # Convert probabilities to float

        if accident_detected and max(probabilities) > 0.2:
            app.consecutive_frames_with_accident += 1
            app.consecutive_frames_without_accident = 0
            accident_results, accident_classes, accident_probabilities = app.accident_detector.detect_accident(frame)
            app.frames_buffer.append((frame, datetime.now(), accident_classes))

            if app.consecutive_frames_with_accident >= 40:
                # Store frames if accident detected for 80 out of 100 frames
                confirm_accident(app, app.frames_buffer, datetime.now(), accident_classes)
                app.frames_buffer = []
                app.consecutive_frames_with_accident = 0
        else:
            app.consecutive_frames_without_accident += 1
            if app.consecutive_frames_without_accident >= 30:
                # Reset buffer if accident is out of frame for 30 consecutive frames
                app.frames_buffer = []
                app.consecutive_frames_with_accident = 0

        if app.inferencing_tab1:
            frame, classes = process_frame_with_yolo(app, frame)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label1.configure(image=img_tk)
            app.cam_label1.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[0].configure(image=img_tk_dashboard)
            app.camera_labels[0].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate

def process_frame_with_yolo(app, frame):
    """Process the frame with YOLO model."""
    results, class_names, probabilities = app.accident_detector.detect_accident(frame)
    probabilities = [float(prob) for prob in probabilities]  # Convert probabilities to float
    classes = class_names.copy()
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            class_name = class_names.pop(0)
            probability = probabilities.pop(0)
            color = (0, 255, 0) if probability < 0.7 else (0, 0, 255)  # Green if probability < 70%, else Red
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{class_name} ({probability:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return frame, classes

def start_timer(app):
    """Start the camera and update the status indicator."""
    print("timerr starting")
    if not app.running:
        print("almsottttt")
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
        app.camera_timer_tab1.configure(text=f"Time: {timer_text}")
        app.after(1000, lambda: update_timer(app))  # Update every second

def stop_backend_detection(app):
    """Stop backend accident detection."""
    app.backend_detection_running = False

def start_backend_detection(app):
    """Start backend accident detection."""
    if not hasattr(app, 'backend_detection_running') or not app.backend_detection_running:
        app.backend_detection_running = True
        threading.Thread(target=backend_detection_loop, args=(app,), daemon=True).start()

def backend_detection_loop(app):
    """Backend loop for accident detection."""
    while app.backend_detection_running:
        # Implement backend detection logic here
        time.sleep(1)  # Adjust the sleep time as needed

# ...existing code...

def update_camera_feed(app):
    """Update the camera feed in the GUI."""
    while app.camera_running_tab1:
        ret, frame = app.cap_tab1.read()
        if not ret:
            break

        if not app.backend_detection_running:
            time.sleep(0.03)  # Control the frame rate
            continue

        accident_detected, classes_present, probabilities = detect_accident_in_frame(frame)
        probabilities = [float(prob) for prob in probabilities]  # Convert probabilities to float

        if accident_detected and max(probabilities) > 0.2:
            app.consecutive_frames_with_accident += 1
            app.consecutive_frames_without_accident = 0
            accident_results, accident_classes, accident_probabilities = app.accident_detector.detect_accident(frame)
            app.frames_buffer.append((frame, datetime.now(), accident_classes))

            if app.consecutive_frames_with_accident >= 40:
                # Store frames if accident detected for 80 out of 100 frames
                confirm_accident(app, app.frames_buffer, datetime.now(), accident_classes)
                app.frames_buffer = []
                app.consecutive_frames_with_accident = 0
        else:
            app.consecutive_frames_without_accident += 1
            if app.consecutive_frames_without_accident >= 30:
                # Reset buffer if accident is out of frame for 30 consecutive frames
                app.frames_buffer = []
                app.consecutive_frames_with_accident = 0

        if app.inferencing_tab1:
            frame, classes = process_frame_with_yolo(app, frame)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
            app.cam_label1.configure(image=img_tk)
            app.cam_label1.image = img_tk

            # Resize the image to fit the dashboard frame
            img_dashboard = img.resize((560, 360), Image.LANCZOS)
            img_tk_dashboard = ctk.CTkImage(light_image=img_dashboard, size=(540, 320))
            app.camera_labels[0].configure(image=img_tk_dashboard)
            app.camera_labels[0].image = img_tk_dashboard

        time.sleep(0.03)  # Control the frame rate

# ...existing code...
