import customtkinter as ctk
import cv2
import threading
from PIL import Image, ImageTk
import time
import tkinter.messagebox as messagebox
import webbrowser
from modules.accident_detection import AccidentDetection
from modules.accidents_tab import create_accidents_tab, read_accident_log
from modules.helmet_tab import create_helmet_tab
from modules.numberplate_tab import create_numberplate_tab  # Import the numberplate tab module
import requests
import geocoder

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
        self.accidents = []  # Initialize the accidents attribute
        
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
        create_accidents_tab(self)
        create_helmet_tab(self)  # Initialize helmet detection tab
        create_numberplate_tab(self)  # Initialize numberplate detection tab
        
    def create_dashboard(self):
        """ Creates the layout for the first dashboard tab """
        # Top analytics row
        self.analytics_frame = ctk.CTkFrame(self.tab1)
        self.analytics_frame.pack(expand=True ,padx=10, pady=5, side='top', anchor='n')
        
        # Add logo to the dashboard
        self.logo_label = ctk.CTkLabel(self.analytics_frame, image=self.logo_image, text="")
        self.logo_label.pack(side='left', padx=10, pady=10)

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
        
        self.update_dashboard_statistics()  # Initialize dashboard statistics

        # Weather Info
        self.weather_frame = ctk.CTkFrame(self.analytics_frame)
        self.weather_frame.pack(side='left', padx=5)
        self.weather_label = ctk.CTkLabel(self.weather_frame, text="Weather: - | Temperature: - | Fog: -")
        self.weather_label.pack(side='left', padx=10, pady=5)
        
        self.update_dashboard_statistics()  # Initialize dashboard statistics
        self.update_weather_info()  # Initialize weather information

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

    def update_dashboard_statistics(self):
        accidents_today, last_accident = read_accident_log()
        self.accident_label.configure(text=f"Accidents Today: {accidents_today}")
        self.last_accident_label.configure(text=f"Last Accident: {last_accident}")

    def update_weather_info(self):
        g = geocoder.ip('me')
        location = f"{g.latlng[0]},{g.latlng[1]}"
        url = f"https://api.open-meteo.com/v1/forecast?latitude={g.latlng[0]}&longitude={g.latlng[1]}&current_weather=true"

        weather_codes = {
            0: "Clear",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing Rime Fog",
            51: "Drizzle: Light",
            53: "Drizzle: Moderate",
            55: "Drizzle: Dense",
            56: "Freezing Drizzle: Light",
            57: "Freezing Drizzle: Dense",
            61: "Rain: Slight",
            63: "Rain: Moderate",
            65: "Rain: Heavy",
            66: "Freezing Rain: Light",
            67: "Freezing Rain: Heavy",
            71: "Snow Fall: Slight",
            73: "Snow Fall: Moderate",
            75: "Snow Fall: Heavy",
            77: "Snow Grains",
            80: "Rain Showers: Slight",
            81: "Rain Showers: Moderate",
            82: "Rain Showers: Violent",
            85: "Snow Showers: Slight",
            86: "Snow Showers: Heavy",
            95: "Thunderstorm: Slight or Moderate",
            96: "Thunderstorm with Slight Hail",
            99: "Thunderstorm with Heavy Hail"
        }

        try:
            response = requests.get(url)
            data = response.json()
            weather = data['current_weather']['weathercode']
            temperature = data['current_weather']['temperature']
            fog = "Yes" if weather in [45, 48] else "No"  # Example weather codes for fog

            weather_description = weather_codes.get(weather, "Unknown")

            self.weather_label.configure(
                text=f"Weather: {weather_description} | Temperature: {temperature}°C | Fog: {fog}"
            )
        except Exception as e:
            self.weather_label.configure(text="Weather: - | Temperature: - | Fog: -")
            print(f"Error fetching weather data: {e}")

    def on_close(self):
        """ Stops camera threads on exit """
        self.running = False
        self.destroy()
        
if __name__ == "__main__":
    app = AccidentEyeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
