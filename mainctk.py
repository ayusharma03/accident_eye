import customtkinter as ctk
from PIL import Image, ImageTk
import time
import cv2
import threading
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("assets/theme_blue.json")

class CameraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Camera Application Prototype")
        self.geometry("1200x700")
        
        # Initialize timer variables
        self.start_time = None
        self.running = False
        self.camera_running_tab1 = False  # Track if camera is running in tab 1
        self.camera_running_tab2 = False  # Track if camera is running in tab 2

        # Load Logo
        self.logo_image = ctk.CTkImage(Image.open("assets/brand.png"), size=(100, 50))

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
    
    def update_status_indicator(self, color, tab):
        """Update the status indicator color."""
        if tab == 1:
            self.status_indicator_tab1.configure(text_color=color)
        else:
            self.status_indicator_tab2.configure(text_color=color)

    def start_timer(self, tab):
        """Start the camera and update the status indicator."""
        if not self.running:
            self.start_time = time.time() - (self.elapsed_time if hasattr(self, 'elapsed_time') else 0)
            self.running = True
            self.update_timer(tab)
            self.update_status_indicator("green", tab)  # Change to green when camera is live

    def stop_timer(self, tab):
        """Stop the camera and update the status indicator."""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False
            self.update_status_indicator("red", tab)  # Change to red when camera is stopped

    def update_timer(self, tab):
        """Update the timer label every second while it's running."""
        if self.running:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_text = f"{hours:02}:{minutes:02}:{seconds:02}"
            if tab == 1:
                self.camera_timer_tab1.configure(text=f"Time: {timer_text}")
            else:
                self.camera_timer_tab2.configure(text=f"Time: {timer_text}")
            self.after(1000, lambda: self.update_timer(tab))  # Update every second
    
    def start_camera(self, tab):
        """Start the webcam feed."""
        if tab == 1:
            if not hasattr(self, 'selected_camera_index_tab1'):
                messagebox.showerror("Error", "Please select a camera from the dropdown menu in Tab 1.")
                return
            if not self.camera_running_tab1:
                # self.cap_tab1 = cv2.VideoCapture(self.selected_camera_index_tab1)  # Initialize the webcam with the selected index
                self.cap_tab1 = cv2.VideoCapture(0)  
                self.camera_running_tab1 = True
                self.camera_thread_tab1 = threading.Thread(target=lambda: self.update_camera_feed(tab), daemon=True)
                self.camera_thread_tab1.start()
            else:
                messagebox.showerror("Error", "Camera is already running in Tab 1.")
        else:
            if not hasattr(self, 'selected_camera_index_tab2'):
                messagebox.showerror("Error", "Please select a camera from the dropdown menu in Tab 2.")
                return
            if not self.camera_running_tab2:
                self.cap_tab2 = cv2.VideoCapture(self.selected_camera_index_tab2)  # Initialize the webcam with the selected index
                self.camera_running_tab2 = True
                self.camera_thread_tab2 = threading.Thread(target=lambda: self.update_camera_feed(tab), daemon=True)
                self.camera_thread_tab2.start()
            else:
                messagebox.showerror("Error", "Camera is already running in Tab 2.")

    def stop_camera(self, tab):
        """Stop the webcam feed."""
        if tab == 1:
            if self.camera_running_tab1:
                self.camera_running_tab1 = False
                if self.cap_tab1:
                    self.cap_tab1.release()  # Release the webcam
                self.cam_label1.configure(image=None)  # Clear the camera feed
        else:
            if self.camera_running_tab2:
                self.camera_running_tab2 = False
                if self.cap_tab2:
                    self.cap_tab2.release()  # Release the webcam
                self.cam_label2.configure(image=None)  # Clear the camera feed

    def update_camera_feed(self, tab):
        """Update the camera feed in the GUI."""
        while (tab == 1 and self.camera_running_tab1) or (tab == 2 and self.camera_running_tab2):
            if tab == 1:
                ret, frame = self.cap_tab1.read()  # Read a frame from the webcam
            else:
                ret, frame = self.cap_tab2.read()  # Read a frame from the webcam
            if ret:
                # Convert the frame to a format suitable for CTkLabel
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ctk.CTkImage(light_image=img, size=(660, 500))

                # Update the label with the new frame
                if tab == 1:
                    self.cam_label1.configure(image=img_tk)
                    self.cam_label1.image = img_tk  # Keep a reference to avoid garbage collection
                else:
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

        # Detect available cameras and populate the combo box with indexes
        available_cameras = {"Camera 1": 1, "Camera 2": 2}

        self.camera_list_tab1 = ctk.CTkOptionMenu(button_frame, values=list(available_cameras.keys()), fg_color="white", text_color="black")
        self.camera_list_tab1.set("Select Camera")
        self.camera_list_tab1.pack(fill="x", padx=5, pady=5)

        def on_camera_select_tab1(choice):
            if choice == "Select Camera":
                print("Select a valid camera")
            else:
                self.selected_camera_index_tab1 = available_cameras[choice]
            print(f"Selected Camera Index: {self.selected_camera_index_tab1}")

        self.camera_list_tab1.configure(command=on_camera_select_tab1)

        # Button container with left alignment but keeping buttons smaller
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(fill="x", padx=5, pady=5)  # Ensuring buttons stay within frame width

        self.toggle_button_tab1 = ctk.CTkButton(button_container, text="On", width=50, command=lambda: (
            self.toggle_button_tab1.configure(text="Off" if self.toggle_button_tab1.cget("text") == "On" else "On"),
            self.start_timer(1) if self.toggle_button_tab1.cget("text") == "Off" else self.stop_timer(1),
            self.start_camera(1) if self.toggle_button_tab1.cget("text") == "Off" else self.stop_camera(1)
        ))
        self.toggle_button_tab1.pack(side="left", padx=5, pady=5)  # Small width for text fitting

        self.trigger_mode_tab1 = False  # Initialize trigger mode state
        trigger_button_tab1 = ctk.CTkButton(button_container, text="Trigger Mode", command=lambda: (
            setattr(self, 'trigger_mode_tab1', not self.trigger_mode_tab1),
            trigger_button_tab1.configure(text="Continuous Mode" if self.trigger_mode_tab1 else "Trigger Mode")
        ))
        trigger_button_tab1.pack(side="left", padx=5, pady=5, expand=True, fill="x")  # Expand trigger button to take remaining space

        # Timer on the right side
        timer_frame_tab1 = ctk.CTkFrame(top_row)
        timer_frame_tab1.pack(side="right", padx=10, pady=10)  # Align at top-right (timer)
        self.camera_timer_tab1 = self.add_timer(timer_frame_tab1)

        # Status indicator (Camera Live/Off)
        status_indicator_frame_tab1 = ctk.CTkFrame(top_row)
        status_indicator_frame_tab1.pack(side="right", padx=10, pady=10)

        # Add the colored indicator (dot)
        self.status_indicator_tab1 = ctk.CTkLabel(status_indicator_frame_tab1, text="●")
        self.status_indicator_tab1.pack(side="left", padx=5, pady=2)
        self.update_status_indicator("red", 1)  # Initial state is red (camera off)

        # Add the "Live" label next to the indicator
        self.live_label_tab1 = ctk.CTkLabel(status_indicator_frame_tab1, text="Live")
        self.live_label_tab1.pack(side="left", padx=5, pady=2)

        # Main container for the three sections
        main_frame_tab1 = ctk.CTkFrame(self.camera_tab)
        main_frame_tab1.pack(fill="both", expand=True, padx=10, pady=2)

        # Leftmost section (Camera Parameters)
        param_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=300)
        param_frame_tab1.pack(side="left", fill="y", padx=10)
        param_label_tab1 = ctk.CTkLabel(param_frame_tab1, text="Camera Parameters")
        param_label_tab1.pack(pady=10)

        # Middle section (Live Camera Feed)
        cam_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=500, height=400)
        cam_frame_tab1.pack(side="left", expand=True, padx=10)

        # Frame for the camera feed
        self.cam_frame1 = ctk.CTkFrame(cam_frame_tab1, width=700, height=400)
        self.cam_frame1.pack(pady=10)

        # Label to display the camera feed
        self.cam_label1 = ctk.CTkLabel(self.cam_frame1, text="")
        self.cam_label1.pack(expand=True)

        # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
        status_frame_tab1 = ctk.CTkFrame(main_frame_tab1, width=400)
        status_frame_tab1.pack(side="right", fill="y", padx=10)

        status_label_tab1 = ctk.CTkLabel(status_frame_tab1, text="Current Status")
        status_label_tab1.pack(pady=5)
        # Create a label to display pass/fail and total bolts processed
        self.current_label_tab1 = ctk.CTkLabel(status_frame_tab1, text="Pass/Fail", width=180)
        self.current_label_tab1.pack(pady=6)
        self.current_label_tab1.configure(text_color="#000000", fg_color="#f9f9f9", corner_radius=8)

        results_label_tab1 = ctk.CTkLabel(status_frame_tab1, text="Last 10 Results")
        results_label_tab1.pack(pady=(20, 5))  # Add vertical distance above

        # Frame to hold the last 10 results
        results_frame_tab1 = ctk.CTkFrame(status_frame_tab1)
        results_frame_tab1.pack(pady=5)

        # Create 10 small circles to represent the last 10 results
        self.result_circles_tab1 = []
        for i in range(10):
            circle = ctk.CTkLabel(results_frame_tab1, text="●", text_color="red", width=2, height=2, font=("Arial", 22))
            circle.grid(row=i // 5, column=i % 5, padx=8, pady=2)
            self.result_circles_tab1.append(circle)
            last_image_label_tab1 = ctk.CTkLabel(status_frame_tab1, text="Last Not Good Product Image")
            last_image_label_tab1.pack(pady=(20, 5))  # Add vertical distance above

            # Frame to hold the last not good product image
            last_image_frame_tab1 = ctk.CTkFrame(status_frame_tab1, width=200, height=200)
            last_image_frame_tab1.pack(pady=5)

            # Label to display the last not good product image
            self.last_image_display_tab1 = ctk.CTkLabel(last_image_frame_tab1, text="")
            self.last_image_display_tab1.pack(expand=True)


    def setup_camera_tab2(self):
        """Set up the camera feed tab for Camera 2."""
        # Create main container for top row
        top_row = ctk.CTkFrame(self.camera_tab2)  # Set a specific height for the top row
        top_row.pack(fill="x", pady=0)  # Reduced the pady to 0 for less space

        # Logo on the left side of the top row
        logo_frame = ctk.CTkFrame(top_row)
        logo_frame.pack(side="left", anchor="nw", padx=10, pady=10)  # Align at top-left (logo) with padding
        self.add_logo(logo_frame)  # Add the logo to this frame

        button_frame = ctk.CTkFrame(top_row)
        button_frame.pack(side="left", padx=10, pady=10, fill="x")  # Ensure it spans horizontally

        # Detect available cameras and populate the combo box with indexes
        available_cameras = {"Camera 1": 1, "Camera 2": 2}

        self.camera_list_tab2 = ctk.CTkOptionMenu(button_frame, values=list(available_cameras.keys()), fg_color="white", text_color="black")
        self.camera_list_tab2.set("Select Camera")
        self.camera_list_tab2.pack(fill="x", padx=5, pady=5)

        def on_camera_select_tab2(choice):
            if choice == "Select Camera":
                print("Select a valid camera")
            else:
                self.selected_camera_index_tab2 = available_cameras[choice]
            print(f"Selected Camera Index: {self.selected_camera_index_tab2}")

        self.camera_list_tab2.configure(command=on_camera_select_tab2)

        # Button container with left alignment but keeping buttons smaller
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(fill="x", padx=5, pady=5)  # Ensuring buttons stay within frame width

        self.toggle_button_tab2 = ctk.CTkButton(button_container, text="On", width=50, command=lambda: (
            self.toggle_button_tab2.configure(text="Off" if self.toggle_button_tab2.cget("text") == "On" else "On"),
            self.start_timer(2) if self.toggle_button_tab2.cget("text") == "Off" else self.stop_timer(2),
            self.start_camera(2) if self.toggle_button_tab2.cget("text") == "Off" else self.stop_camera(2)
        ))
        self.toggle_button_tab2.pack(side="left", padx=5, pady=5)  # Small width for text fitting

        self.trigger_mode_tab2 = False  # Initialize trigger mode state
        trigger_button_tab2 = ctk.CTkButton(button_container, text="Trigger Mode", command=lambda: (
            setattr(self, 'trigger_mode_tab2', not self.trigger_mode_tab2),
            trigger_button_tab2.configure(text="Continuous Mode" if self.trigger_mode_tab2 else "Trigger Mode")
        ))
        trigger_button_tab2.pack(side="left", padx=5, pady=5, expand=True, fill="x")  # Expand trigger button to take remaining space

        # Timer on the right side
        timer_frame_tab2 = ctk.CTkFrame(top_row)
        timer_frame_tab2.pack(side="right", padx=10, pady=10)  # Align at top-right (timer)
        self.camera_timer_tab2 = self.add_timer(timer_frame_tab2)

        # Status indicator (Camera Live/Off)
        status_indicator_frame_tab2 = ctk.CTkFrame(top_row)
        status_indicator_frame_tab2.pack(side="right", padx=10, pady=10)

        # Add the colored indicator (dot)
        self.status_indicator_tab2 = ctk.CTkLabel(status_indicator_frame_tab2, text="●")
        self.status_indicator_tab2.pack(side="left", padx=5, pady=2)
        self.update_status_indicator("red", 2)  # Initial state is red (camera off)

        # Add the "Live" label next to the indicator
        self.live_label_tab2 = ctk.CTkLabel(status_indicator_frame_tab2, text="Live")
        self.live_label_tab2.pack(side="left", padx=5, pady=2)

        # Main container for the three sections
        main_frame_tab2 = ctk.CTkFrame(self.camera_tab2)
        main_frame_tab2.pack(fill="both", expand=True, padx=10, pady=2)

        # Leftmost section (Camera Parameters)
        param_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=300)
        param_frame_tab2.pack(side="left", fill="y", padx=10)
        param_label_tab2 = ctk.CTkLabel(param_frame_tab2, text="Camera Parameters")
        param_label_tab2.pack(pady=10)

        # Middle section (Live Camera Feed)
        cam_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=500, height=400)
        cam_frame_tab2.pack(side="left", expand=True, padx=10)

        # Frame for the camera feed
        self.cam_frame2 = ctk.CTkFrame(cam_frame_tab2, width=700, height=400)
        self.cam_frame2.pack(pady=10)

        # Label to display the camera feed
        self.cam_label2 = ctk.CTkLabel(self.cam_frame2, text="")
        self.cam_label2.pack(expand=True)

        # Rightmost section (Detection Status, Last 10 Results, Last Not Good Product Image)
        status_frame_tab2 = ctk.CTkFrame(main_frame_tab2, width=400)
        status_frame_tab2.pack(side="right", fill="y", padx=10)

        status_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Current Status")
        status_label_tab2.pack(pady=5)
        # Create a label to display pass/fail and total bolts processed
        self.current_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Pass/Fail", width=180)
        self.current_label_tab2.pack(pady=6)
        self.current_label_tab2.configure(text_color="#000000", fg_color="#f9f9f9", corner_radius=8)

        results_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Last 10 Results")
        results_label_tab2.pack(pady=(20, 5))  # Add vertical distance above

        # Frame to hold the last 10 results
        results_frame_tab2 = ctk.CTkFrame(status_frame_tab2)
        results_frame_tab2.pack(pady=5)

        # Create 10 small circles to represent the last 10 results
        self.result_circles_tab2 = []
        for i in range(10):
            circle = ctk.CTkLabel(results_frame_tab2, text="●", text_color="red", width=2, height=2, font=("Arial", 22))
            circle.grid(row=i // 5, column=i % 5, padx=8, pady=2)
            self.result_circles_tab2.append(circle)
            last_image_label_tab2 = ctk.CTkLabel(status_frame_tab2, text="Last Not Good Product Image")
            last_image_label_tab2.pack(pady=(20, 5))  # Add vertical distance above

            # Frame to hold the last not good product image
            last_image_frame_tab2 = ctk.CTkFrame(status_frame_tab2, width=200, height=200)
            last_image_frame_tab2.pack(pady=5)

            # Label to display the last not good product image
            self.last_image_display_tab2 = ctk.CTkLabel(last_image_frame_tab2, text="")
            self.last_image_display_tab2.pack(expand=True)
        
if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()