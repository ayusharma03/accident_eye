import customtkinter as ctk
import cv2
import threading
from PIL import Image, ImageTk
import time
import tkinter.messagebox as messagebox
import webbrowser
from modules.accident_detection import AccidentDetection
ctk.set_appearance_mode("light")
class AccidentEyeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Accident Eye")
        self.geometry("1920x1080")
        
        # Load Logo
        self.logo_image = ctk.CTkImage(Image.open("assets/brand.png"), size=(200, 50))
        self.camera_running_tab1 = False  # Track if camera is running in tab 1
        self.camera_running_tab2 = False  # Track if camera is running in tab 2
        self.accident_detector = AccidentDetection()
        self.start_time = None
        self.running = False

        
        # Tab View
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill='both', expand=True)
        
        self.tab1 = self.tabview.add("Dashboard")
        self.tab2 = self.tabview.add("Accidents")
        self.tab3 = self.tabview.add("Helmet Detection")
        self.tab4 = self.tabview.add("Speed Detection")
        self.tab5 = self.tabview.add("Number Plate Detection")
        self.cameras = [0, 1, 2, 3]  # Update with actual camera indexes
        self.frames = [None] * 4
    
        # self.start_cameras()
        # Dashboard Tab Layout
        self.create_dashboard()
        
        self.create_accidents_tab()
        
    def create_dashboard(self):
        """ Creates the layout for the first dashboard tab """
        # Top analytics row
        self.analytics_frame = ctk.CTkFrame(self.tab1)
        self.analytics_frame.pack(expand=True ,padx=10, pady=5, side='top', anchor='n')
        
        # Site Selection
        self.site_frame = ctk.CTkFrame(self.analytics_frame)
        self.site_frame.pack(side='left', padx=5)
        self.site_label = ctk.CTkLabel(self.site_frame, text="Site:")
        self.site_label.pack(side='left', padx=5, pady=5)
        self.site_dropdown = ctk.CTkComboBox(self.site_frame, values=["Site A", "Site B", "Site C","Site D"])
        self.site_dropdown.pack(side='left', padx=5, pady=5)
        
        # Accident Statistics
        self.accident_frame = ctk.CTkFrame(self.analytics_frame)
        self.accident_frame.pack(side='left', padx=5)
        self.accident_label = ctk.CTkLabel(self.accident_frame, text="Accidents Today: 0")
        self.accident_label.pack(side='left', padx=10, pady=5)
        self.last_accident_label = ctk.CTkLabel(self.accident_frame, text="Last Accident: -")
        self.last_accident_label.pack(side='left', padx=10, pady=5)
        
        # Weather Info
        self.weather_frame = ctk.CTkFrame(self.analytics_frame)
        self.weather_frame.pack(side='left', padx=5)
        self.weather_label = ctk.CTkLabel(self.weather_frame, text="Weather: - | Temperature: - | Visibility: - | Fog: -")
        self.weather_label.pack(side='left', padx=10, pady=5)
        
        # Camera Feed Display
        self.camera_frame = ctk.CTkFrame(self.tab1)
        self.camera_frame.pack( expand=True, padx=10, side='top', anchor='n')
        self.camera_rows_frame = ctk.CTkFrame(self.camera_frame)
        self.camera_rows_frame.pack(padx=5, pady=5, side='top', anchor='n')
        
        self.camera_labels = []
        for i in range(4):
            label = ctk.CTkLabel(self.camera_rows_frame, text=f"Camera {i+1}", width=640, height=360)
            label.grid(row=i//2, column=i%2, padx=5, pady=5)
            self.camera_labels.append(label)

    def create_accidents_tab(self):
        top_row = ctk.CTkFrame(self.tab2)  # Set a specific height for the top row
        top_row.pack(fill="x", pady=0)  # Reduced the pady to 0 for less space

        # Logo on the left side of the top row
        logo_frame = ctk.CTkFrame(top_row)
        logo_frame.pack(
            side="left", anchor="nw", padx=10, pady=10
        )  # Align at top-left (logo) with padding
        self.add_logo(logo_frame)  # Add the logo to this frame

        button_frame = ctk.CTkFrame(top_row)
        button_frame.pack(
            side="left", padx=10, pady=10, fill="x"
        )  # Ensure it spans horizontally

        # Detect available cameras and populate the combo box with indexes
        available_cameras = {"Camera 1": 1}
        self.selected_camera_index_tab1 = available_cameras["Camera 1"]

        # Button container with left alignment but keeping buttons smaller
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(
            fill="both", padx=5, pady=10
        )  # Ensuring buttons stay within frame width

        self.toggle_switch_tab1 = ctk.CTkSwitch(
            master=button_container,
            text="Camera",
            command=lambda: (
            self.start_timer() if self.toggle_switch_tab1.get() else self.stop_timer(),
            self.start_camera() if self.toggle_switch_tab1.get() else self.stop_camera(),
            ),
        )
        self.toggle_switch_tab1.pack(side="left", padx=8, fill="y")
        

        self.inferencing_tab1 = False  # Initialize inferencing state
        inferencing_button_tab1 = ctk.CTkButton(
            button_container,
            text="Start Inferencing",
            command=lambda: (
                setattr(self, "inferencing_tab1", not self.inferencing_tab1),
                inferencing_button_tab1.configure(
                    text="Stop Inferencing" if self.inferencing_tab1 else "Start Inferencing"
                ),
                self.start_inferencing(1) if self.inferencing_tab1 else self.stop_inferencing(1),
            ),
        )
        inferencing_button_tab1.pack(
            side="left", padx=5, pady=10, expand=True, fill="x"
        )  # Expand inferencing button to take remaining space

        # Timer on the right side
        timer_frame_tab1 = ctk.CTkFrame(top_row)
        timer_frame_tab1.pack(
            side="right", padx=10, pady=10
        )  # Align at top-right (timer)
        self.camera_timer_tab1 = self.add_timer(timer_frame_tab1)

        # Status indicator (Camera Live/Off)
        status_indicator_frame_tab1 = ctk.CTkFrame(top_row)
        status_indicator_frame_tab1.pack(side="right", padx=10, pady=10)

        # Add the colored indicator (dot)
        self.status_indicator_tab1 = ctk.CTkLabel(status_indicator_frame_tab1, text="● Live", height=50, width=80)
        self.status_indicator_tab1.pack(side="left", padx=5, pady=2)
        self.update_status_indicator("red")  # Initial state is red (camera off)

    
        # Main container for the three sections
        main_frame_tab1 = ctk.CTkFrame(self.tab2)
        main_frame_tab1.pack(fill="both", expand=True, padx=5)

        # Middle section (Live Camera Feed) =======
        cam_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=700, height=400)  # Adjusted width and height
        cam_frame_tab1.pack(side="left", expand=True)  # Added pady for vertical padding
        # Camera title frame and label
        self.camera_title_tab1 = ctk.CTkLabel(cam_frame_tab1, text="Accident Camera Feed")
        self.camera_title_tab1.pack(pady=2)
        self.camera_title_tab1.configure(font=("Arial",18,"bold"))  # Set text color to black
        # Label to display the camera feed
        self.cam_label1 = ctk.CTkLabel(cam_frame_tab1, text=" ", fg_color="gray", height=400, width=700)  # Gray background color
        self.cam_label1.pack(expand=True, fill="both", padx=10,pady=8)  # Use fill="both" to ensure it takes up the full space
        self.cam_label1.configure( # Set corner radius for a rounded appearance
            corner_radius=8
        )

        # accident statistics frame below camera
        statistics_frame_tab1 = ctk.CTkFrame(cam_frame_tab1, width=700, height=100)
        statistics_frame_tab1.pack(side="left", padx=10, pady=10)
        # fill the frame with accident statistics of the day
        self.accident_statistics_tab1 = ctk.CTkLabel(statistics_frame_tab1, text="Accidents Today: 0\nLast Accident: -", height=80, width=700,anchor="center")
        self.accident_statistics_tab1.pack(pady=5, padx=10, fill="both", side="left")
        


        # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
        status_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=1000)
        status_frame_tab1.pack(side="right", fill="y", padx=10)

        status_label_tab1 = ctk.CTkLabel(status_frame_tab1, text="Last Accident Detection")
        status_label_tab1.pack(pady=5)
        
        # list of last 10 accidents
        self.last_accidents_tab1 = ctk.CTkScrollableFrame(status_frame_tab1, width=600,height=700, fg_color="transparent")
        self.last_accidents_tab1.pack(pady=5)
        self.accident_button = ctk.CTkButton(status_frame_tab1, text="View All Accidents")
        self.accident_button.pack(pady=5)

        # Example list of accidents with timestamps
        self.accidents = [
            {"timestamp": "2023-10-01 12:00:00", "details": "Accident 1 details"},
            {"timestamp": "2023-10-02 14:30:00", "details": "Accident 2 details"},
            {"timestamp": "2023-10-03 09:15:00", "details": "Accident 3 details"},
            # Add more accidents as needed
        ]

        # Display the most recent accident in a big tab
        if self.accidents:
            most_recent_accident = self.accidents[-1]
            recent_frame = ctk.CTkFrame(self.last_accidents_tab1)
            recent_frame.pack(fill="x", padx=5, pady=5)

            try:
                image_path = f"accidents/accident-{most_recent_accident['timestamp'].replace(':', '-')}.png"
                recent_accident_image = ctk.CTkImage(Image.open(image_path), size=(600, 400))
                recent_accident_image_label = ctk.CTkLabel(recent_frame, image=recent_accident_image, text="", width=600, height=400)
                recent_accident_image_label.pack(side="top", padx=8, pady=5)
            except FileNotFoundError:
                recent_accident_image_label = ctk.CTkLabel(recent_frame, text="No Image", width=600, height=400)
                recent_accident_image_label.pack(side="top", padx=8, pady=5)

            recent_details_label = ctk.CTkLabel(recent_frame, text=f"Timestamp: {most_recent_accident['timestamp']}\nDetails: {most_recent_accident['details']}")
            recent_details_label.pack(side="top", padx=5, pady=5)

        for i in range(len(self.accidents)-2,-1,-1):
            frame = ctk.CTkFrame(self.last_accidents_tab1)
            frame.pack(fill="x", padx=5, pady=5)

            try:
                image_path = f"accidents/accident-{self.accidents[i]['timestamp'].replace(':', '-')}.png"
                accident_image = ctk.CTkImage(Image.open(image_path), size=(50, 50))
                accident_image_label = ctk.CTkLabel(frame, image=accident_image, text="", width=50, height=50)
                accident_image_label.pack(side="left", padx=8, pady=5)
            except FileNotFoundError:
                accident_image_label = ctk.CTkLabel(frame, text="No Image", width=50, height=50)
                accident_image_label.pack(side="left", padx=8, pady=5)

            button = ctk.CTkButton(
            frame,
            text=self.accidents[i]["timestamp"],
            compound="left",  # Display image to the left of the text
            command=lambda acc=self.accidents[i]: show_accident_details(accident=acc),
            anchor="center",
            height=50
            )
            button.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        def show_accident_details(accident):
            """Show a pop-up with accident details."""
            messagebox.showinfo("Accident Details", f"Timestamp: {accident['timestamp']}\nDetails: {accident['details']}")

    def start_camera(self):
        """Start the webcam feed."""
        if not hasattr(self, "selected_camera_index_tab1"):
            messagebox.showerror("Error", "Please select a camera.")
            return
        if not self.camera_running_tab1:
            self.cap_tab1 = cv2.VideoCapture(
                self.selected_camera_index_tab1
            )  # Initialize the webcam with the selected index
            self.camera_running_tab1 = True
            self.camera_thread_tab1 = threading.Thread(
                target=lambda: self.update_camera_feed(), daemon=True
            )
            self.camera_thread_tab1.start()
        else:
            messagebox.showerror("Error", "Camera is already running in Tab 1.")
    
    def stop_camera(self):
        """Stop the webcam feed."""
        print("camera stoppingg")
        if self.camera_running_tab1:
            self.camera_running_tab1 = False
            if self.cap_tab1:
                self.cap_tab1.release()  # Release the webcam
            self.cam_label1.configure(image=None)  # Clear the camera feed

    def start_inferencing(self, tab):
        """Start inferencing and update the camera feed with YOLO processed frames."""
        if tab == 1:
            if not self.camera_running_tab1:
                messagebox.showerror("Error", "Camera is not running")
                return
            self.inferencing_tab1 = True
        else:
            if not self.camera_running_tab2:
                messagebox.showerror("Error", "Camera is not running")
                return
            self.inferencing_tab2 = True

    def stop_inferencing(self, tab):
        """Stop inferencing."""
        if tab == 1:
            self.inferencing_tab1 = False
        else:
            self.inferencing_tab2 = False

    def update_camera_feed(self):
        """Update the camera feed in the GUI."""
        while (self.camera_running_tab1):
            
            ret, frame = self.cap_tab1.read()  # Read a frame from the webcam
            if self.inferencing_tab1:
                frame = self.process_frame_with_yolo(frame)
                
            if ret:
                # Convert the frame to a format suitable for CTkLabel
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ctk.CTkImage(light_image=img, size=(700, 500))

                # Update the label with the new frame
                self.cam_label1.configure(image=img_tk)
                self.cam_label1.image = (
                    img_tk  # Keep a reference to avoid garbage collection
                )
            time.sleep(0.03)  # Control the frame rate

    def process_frame_with_yolo(self, frame):
        """Process the frame with YOLO model."""
        results, class_names = self.accident_detector.detect_accident(frame)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_name = class_names.pop(0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return frame

    def add_logo(self, parent):
        """Adds a logo to the top left corner of a tab."""
        logo_label = ctk.CTkLabel(parent, image=self.logo_image, text="")
        logo_label.pack(anchor="nw", padx=10, pady=10)

    def add_timer(self, parent):
        """Adds a timer to the top right corner of a tab."""
        timer_label = ctk.CTkLabel(parent, text="Time: 00:00:00", height=50, width=100)
        timer_label.pack(anchor="ne", padx=10, pady=2)
        return timer_label

    def update_status_indicator(self, color):
        """Update the status indicator color."""
        self.status_indicator_tab1.configure(text_color=color)
    def start_timer(self):
        """Start the camera and update the status indicator."""
        print("timerr starting")
        if not self.running:
            print("almsottttt")
            self.start_time = time.time() - (
                self.elapsed_time if hasattr(self, "elapsed_time") else 0
            )
            self.running = True
            self.update_timer()
            self.update_status_indicator(
                "green"
            )  # Change to green when camera is live

    def stop_timer(self):
        """Stop the camera and update the status indicator."""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False
            self.update_status_indicator(
                "red"
            )  # Change to red when camera is stopped

    def update_timer(self):
        """Update the timer label every second while it's running."""
        if self.running:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_text = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.camera_timer_tab1.configure(text=f"Time: {timer_text}")
            self.after(1000, lambda: self.update_timer())  # Update every second
    
    def on_close(self):
        """ Stops camera threads on exit """
        self.running = False
        self.destroy()
        
if __name__ == "__main__":
    app = AccidentEyeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
