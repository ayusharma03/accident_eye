import customtkinter as ctk
import cv2
import threading
from PIL import Image, ImageTk
import time
import tkinter.messagebox as messagebox
import webbrowser
from modules.accident_detection import AccidentDetection
from detect_person import detect_accident_in_frame, save_frames, accidents, accident_detector
from datetime import datetime
from modules.accidents_tab import create_accidents_tab

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
        self.consecutive_frames_with_accident = 0
        self.consecutive_frames_without_accident = 0
        self.frames_buffer = []

        
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
        # Example list of accidents with timestamps
        self.accidents = [
            {"timestamp": "2023-10-01 12:00:00", "details": "Accident 1 details"},
            {"timestamp": "2023-10-02 14:30:00", "details": "Accident 2 details"},
            {"timestamp": "2023-10-03 09:15:00", "details": "Accident 3 details"},
            # Add more accidents as needed
        ]
        # self.start_cameras()
        # Dashboard Tab Layout
        self.create_dashboard()
        create_accidents_tab(self)
        
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
            label = ctk.CTkLabel(self.camera_rows_frame, text=f" ", width=550, height=330, corner_radius=10)
            label.grid(row=i//2, column=i%2, padx=5, pady=5)
            self.camera_labels.append(label)

    def on_close(self):
        """ Stops camera threads on exit """
        self.running = False
        self.destroy()
        
if __name__ == "__main__":
    app = AccidentEyeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
