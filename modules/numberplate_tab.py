import customtkinter as ctk
from PIL import Image
import cv2
import threading
import time
from datetime import datetime
import os
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
            command=lambda np=folder: show_numberplate_details(app, numberplate=np, editable=(button_color == "red")),
            anchor="center",
            height=50,
            fg_color=button_color
        )
        button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

def show_numberplate_details(app, numberplate, editable=False, large=False):
    """Show a pop-up with numberplate details."""
    details_path = f"numberplates/{numberplate}/details.txt"
    try:
        with open(details_path, "r") as f:
            details = f.read().strip()
    except FileNotFoundError:
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
    while app.camera_running_tab2:
        ret, frame = app.cap_tab2.read()
        if not ret:
            break

        numberplate_results = detect_numberplate_in_frame(app, frame)

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
