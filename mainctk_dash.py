import customtkinter as ctk
import cv2
import threading
from PIL import Image, ImageTk

class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Camera Dashboard")
        self.geometry("1000x600")
        
        # Tab View
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill='both', expand=True)
        
        self.tab1 = self.tabview.add("Dashboard")
        self.tab2 = self.tabview.add("Accidents")
        self.tab3 = self.tabview.add("Helmet Detection")
        self.tab4 = self.tabview.add("Speed Detection")
        self.tab5 = self.tabview.add("Number Plate Detection")
        
        # Dashboard Tab Layout
        self.create_dashboard()
        
        # Camera Capture
        self.cameras = [0, 1, 2, 3]  # Update with actual camera indexes
        self.frames = [None] * 4
        self.running = True
        self.start_cameras()
        
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
        
    def start_cameras(self):
        """ Starts threads to capture video from cameras """
        self.threads = []
        for i, cam in enumerate(self.cameras):
            thread = threading.Thread(target=self.capture_video, args=(i, cam))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
    def capture_video(self, index, cam_index):
        """ Captures video frames from a camera """
        cap = cv2.VideoCapture(cam_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 400))  # Resize for UI
                img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.frames[index] = img
                self.update_camera_feed(index)
        cap.release()
    
    def update_camera_feed(self, index):
        """ Updates the UI with the latest camera frame """
        if self.frames[index]:
            self.camera_labels[index].configure(image=self.frames[index])
            self.camera_labels[index].image = self.frames[index]
    
    def on_close(self):
        """ Stops camera threads on exit """
        self.running = False
        self.destroy()
        
if __name__ == "__main__":
    app = DashboardApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
