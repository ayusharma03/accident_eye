import customtkinter as ctk
from PIL import Image, ImageTk
import time
import cv2
import threading


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class CameraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Camera Application Prototype")
        self.geometry("1200x700")
        
        # Initialize timer variables
        self.start_time = None
        self.running = False
        self.camera_running = False  # Initialize camera_running

        # Load Logo
        self.logo_image = ctk.CTkImage(Image.open("assets/logo.png"), size=(100, 50))

        # Create tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.overview_tab = self.tab_view.add("Overview")
        self.camera_tab = self.tab_view.add("Camera 1")
        self.camera_tab2 = self.tab_view.add("Camera 2")
        
        self.setup_overview_tab()
        self.setup_camera_tab()
        self.setup_camera_tab2()

    def add_logo(self, parent):
        """Adds a logo to the top left corner of a tab."""
        logo_label = ctk.CTkLabel(parent, image=self.logo_image, text="")
        logo_label.pack(anchor="nw", padx=10, pady=10)
        
    def add_timer(self, parent):
        """Adds a timer to the top right corner of a tab."""
        timer_label = ctk.CTkLabel(parent, text="Time: 00:00:00")
        timer_label.pack(anchor="ne", padx=10, pady=10)
        return timer_label
    
    def update_status_indicator(self, color):
        """Update the status indicator color."""
        self.status_indicator.configure(text_color=color)

    def start_timer(self):
        """Start the camera and update the status indicator."""
        if not self.running:
            self.start_time = time.time() - (self.elapsed_time if hasattr(self, 'elapsed_time') else 0)
            self.running = True
            self.update_timer()
            self.update_status_indicator("green")  # Change to green when camera is live

    def stop_timer(self):
        """Stop the camera and update the status indicator."""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False
            self.update_status_indicator("red")  # Change to red when camera is stopped

    def update_timer(self):
        """Update the timer label every second while it's running."""
        if self.running:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_text = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.camera_timer.configure(text=f"Time: {timer_text}")
            self.after(1000, self.update_timer)  # Update every second
    
    def start_camera(self):
        """Start the webcam feed."""
        if not self.camera_running:
            self.cap = cv2.VideoCapture(2)  # Initialize the webcam
            self.camera_running = True
            self.camera_thread = threading.Thread(target=self.update_camera_feed, daemon=True)
            self.camera_thread.start()

    def stop_camera(self):
        """Stop the webcam feed."""
        if self.camera_running:
            self.camera_running = False
            if self.cap:
                self.cap.release()  # Release the webcam
            self.cam_label1.configure(image="")  # Clear the camera feed
            self.cam_label2.configure(image="")  # Clear the camera feed

    def update_camera_feed(self):
        """Update the camera feed in the GUI."""
        while self.camera_running:
            ret, frame = self.cap.read()  # Read a frame from the webcam
            if ret:
                # Convert the frame to a format suitable for CTkLabel
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ctk.CTkImage(light_image=img, size=(660, 500))
                # img_tk = ImageTk.PhotoImage(image=img)

                # Update the label with the new frame
                self.cam_label1.configure(image=img_tk)
                self.cam_label1.image = img_tk  # Keep a reference to avoid garbage collection
                self.cam_label2.configure(image=img_tk)
                self.cam_label2.image = img_tk  # Keep a reference to avoid garbage collection
            time.sleep(0.03)  # Control the frame rate
            
    def update_result_circles(self, results):
        """Update the color of the result circles based on the last 10 results."""
        for i, result in enumerate(results):
            color = "green" if result else "red"
            self.result_circles[i].configure(text_color=color)

    def setup_overview_tab(self):
        """Set up the overview tab."""
        logo_frame = ctk.CTkFrame(self.overview_tab)
        logo_frame.place(relx=0.08, rely=0.05, anchor="center")  # Align more to the left (logo)
        self.add_logo(logo_frame)
        intro_label = ctk.CTkLabel(self.overview_tab, text="Welcome to the Camera Application!")
        intro_label.pack(pady=10)

        cam_frame1 = ctk.CTkFrame(self.overview_tab, width=350, height=250)
        cam_frame1.pack(side="left", padx=10, pady=10)
        cam_label1 = ctk.CTkLabel(cam_frame1, text="Camera Feed 1 (Running)")
        cam_label1.pack(expand=True)

        cam_frame2 = ctk.CTkFrame(self.overview_tab, width=350, height=250)
        cam_frame2.pack(side="right", padx=10, pady=10)
        cam_label2 = ctk.CTkLabel(cam_frame2, text="Camera Feed 2 (Running)")
        cam_label2.pack(expand=True)

    def setup_camera_tab(self):
        """Set up the camera feed tab for Camera 1."""
        # Create main container for top row
        top_row = ctk.CTkFrame(self.camera_tab)  # Set a specific height for the top row
        top_row.pack(fill="x", pady=0)  # Reduced the pady to 0 for less space

        # Logo on the left side of the top row
        logo_frame = ctk.CTkFrame(top_row)
        logo_frame.pack(side="left", anchor="nw", padx=10, pady=10)  # Align at top-left (logo) with padding
        self.add_logo(logo_frame)  # Add the logo to this frame

        button_frame = ctk.CTkFrame(top_row)
        button_frame.pack(side="left", padx=10, pady=10, fill="x")  # Ensure it spans horizontally

        # Make the combo box span the full width and set it to non-editable
        self.camera_list = ctk.CTkComboBox(button_frame, values=["Camera 1", "Camera 2", "Camera 3"], state="readonly")
        self.camera_list.set("Select Camera")
        self.camera_list.pack(fill="x", padx=5, pady=5)

        # Button container with left alignment but keeping buttons smaller
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(fill="x", padx=5, pady=5)  # Ensuring buttons stay within frame width

        self.toggle_button = ctk.CTkButton(button_container, text="On", width=50, command=lambda: (
            self.toggle_button.configure(text="Off" if self.toggle_button.cget("text") == "On" else "On"),
            self.start_timer() if self.toggle_button.cget("text") == "Off" else self.stop_timer(),
            self.start_camera() if self.toggle_button.cget("text") == "Off" else self.stop_camera()
        ))
        self.toggle_button.pack(side="left", padx=5, pady=5)  # Small width for text fitting

        self.trigger_mode = False  # Initialize trigger mode state
        trigger_button = ctk.CTkButton(button_container, text="Trigger Mode", command=lambda: (
            setattr(self, 'trigger_mode', not self.trigger_mode),
            trigger_button.configure(text="Continuous Mode" if self.trigger_mode else "Trigger Mode")
        ))
        trigger_button.pack(side="left", padx=5, pady=5, expand=True, fill="x")  # Expand trigger button to take remaining space

        # Timer on the right side
        timer_frame = ctk.CTkFrame(top_row)
        timer_frame.pack(side="right", padx=10, pady=10)  # Align at top-right (timer)
        self.camera_timer = self.add_timer(timer_frame)

        # Status indicator (Camera Live/Off)
        status_indicator_frame = ctk.CTkFrame(top_row)
        status_indicator_frame.pack(side="right", padx=10, pady=10)

        # Add the colored indicator (dot)
        self.status_indicator = ctk.CTkLabel(status_indicator_frame, text="●")
        self.status_indicator.pack(side="left", padx=5, pady=2)
        self.update_status_indicator("red")  # Initial state is red (camera off)

        # Add the "Live" label next to the indicator
        self.live_label = ctk.CTkLabel(status_indicator_frame, text="Live")
        self.live_label.pack(side="left", padx=5, pady=2)

        # Main container for the three sections
        main_frame = ctk.CTkFrame(self.camera_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=2)

        # Leftmost section (Camera Parameters)
        param_frame = ctk.CTkFrame(main_frame, width=300)
        param_frame.pack(side="left", fill="y", padx=10)
        param_label = ctk.CTkLabel(param_frame, text="Camera Parameters")
        param_label.pack(pady=10)

        # Middle section (Live Camera Feed)
        cam_frame = ctk.CTkFrame(main_frame, width=500, height=400)
        cam_frame.pack(side="left", expand=True, padx=10)
        # cam_label = ctk.CTkLabel(cam_frame, text="Camera 1 Feed")
        # cam_label.pack(expand=True)

        # Frame for the camera feed
        self.cam_frame1 = ctk.CTkFrame(cam_frame, width=700, height=400)
        self.cam_frame1.pack(pady=10)

        # Label to display the camera feed
        self.cam_label1 = ctk.CTkLabel(self.cam_frame1, text="Camera 1 Feed")
        self.cam_label1.pack(expand=True)

        # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
        status_frame = ctk.CTkFrame(main_frame, width=400)
        status_frame.pack(side="right", fill="y", padx=10)

        status_label = ctk.CTkLabel(status_frame, text="Current Status")
        status_label.pack(pady=5)
        # Create a label to display pass/fail and total bolts processed
        self.current_label = ctk.CTkLabel(status_frame, text="Pass/Fail", width=180)
        self.current_label.pack(pady=6)
        self.current_label.configure(text_color="#000000", fg_color="#f9f9f9", corner_radius=8)

        results_label = ctk.CTkLabel(status_frame, text="Last 10 Results")
        results_label.pack(pady=(20, 5))  # Add vertical distance above

        # Frame to hold the last 10 results
        results_frame = ctk.CTkFrame(status_frame)
        results_frame.pack(pady=5)

        # Create 10 small circles to represent the last 10 results
        self.result_circles = []
        for i in range(10):
            circle = ctk.CTkLabel(results_frame, text="●", text_color="red", width=2, height=2)
            circle.grid(row=i // 5, column=i % 5, padx=2, pady=2)
            self.result_circles.append(circle)

        last_image_label = ctk.CTkLabel(status_frame, text="Last Not Good Product Image")
        last_image_label.pack(pady=(20, 5))  # Add vertical distance above

    def setup_camera_tab2(self):
        """Set up the camera feed tab for Camera 2."""
        self.add_logo(self.camera_tab2)

        # Frame for the camera feed
        self.cam_frame2 = ctk.CTkFrame(self.camera_tab2, width=700, height=400)
        self.cam_frame2.pack(pady=10)

        # Label to display the camera feed
        self.cam_label2 = ctk.CTkLabel(self.cam_frame2, text="Camera 2 Feed")
        self.cam_label2.pack(expand=True)

        # Frame for buttons
        button_frame = ctk.CTkFrame(self.camera_tab2)
        button_frame.pack(pady=10)

        # Start button to start the camera feed
        start_button = ctk.CTkButton(button_frame, text="Start", command=self.start_camera)
        start_button.grid(row=0, column=0, padx=5)

        # Stop button to stop the camera feed
        stop_button = ctk.CTkButton(button_frame, text="Stop", command=self.stop_camera)
        stop_button.grid(row=0, column=1, padx=5)

        # Stats label
        stats_label = ctk.CTkLabel(self.camera_tab2, text="Stats: N/A")
        stats_label.pack(pady=10)
        
if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()