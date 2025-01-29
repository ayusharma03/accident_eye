import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import torch
import os


class DetectionThread(QThread):
    detection_complete = pyqtSignal(str)  # Signal to indicate detection is complete
    script_output = pyqtSignal(str)  # Signal to emit script output

    def __init__(self, model_path, input_file, is_video=False):
        super().__init__()
        self.model_path = model_path
        self.input_file = input_file
        self.is_video = is_video
        self.stop_flag = False  # Flag to safely stop the thread

    def stop(self):
        """Set the stop flag to terminate detection."""
        self.stop_flag = True

    def run(self):
        """Run YOLO detection in a separate thread."""
        try:
            from ultralytics import YOLO
            import cv2
            
            # Check for GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.script_output.emit(f"Using device: {device}")
            if torch.cuda.is_available():
                print("CUDA is available.")
                print("Device:", torch.cuda.get_device_name(0))  # PyTorch CUDA version
                print("CUDA Version:", torch.version.cuda)  # Torch-specific CUDA 
            else:
                print("CUDA is not available. Using CPU.")
            model = YOLO(self.model_path)
            
            if self.is_video:
                cap = cv2.VideoCapture(self.input_file)
                output_dir = os.path.join(os.path.dirname(self.input_file), "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "labeled_output.mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

                while cap.isOpened() and not self.stop_flag:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model(frame, device=device)[0]
                    for result in results:
                        for box in result.boxes.xyxy:
                            x1, y1, x2, y2 = map(int, box)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    out.write(frame)

                cap.release()
                out.release()
            else:
                results = model(self.input_file, device=device)
                output_dir = os.path.join(os.path.dirname(self.input_file), "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "labeled_output.jpg")
                results[0].save(output_path)  # Save the result
            
            # Emit the path to the labeled image or video
            self.detection_complete.emit(output_path)
        except Exception as e:
            self.detection_complete.emit(f"Error: {e}")


class LiveDetectionThread(QThread):
    frame_processed = pyqtSignal(QPixmap)  # Signal to emit processed frame

    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.stop_flag = False  # Flag to safely stop the thread

    def stop(self):
        """Set the stop flag to terminate detection."""
        self.stop_flag = True

    def run(self):
        """Run YOLO detection on live camera feed in a separate thread."""
        try:
            # Check for GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = YOLO(self.model_path)

            cap = cv2.VideoCapture(1)  # Open the default camera
            while not self.stop_flag:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert frame to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = model(rgb_frame, device=device)[0]

                # Draw bounding boxes on the frame
                for result in results:
                    for box in result.boxes.xyxy:
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Convert frame to QPixmap and emit signal
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                self.frame_processed.emit(pixmap)

            cap.release()
        except Exception as e:
            print(f"Error: {e}")


class AccidentDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accident Detection GUI")
        self.setGeometry(100, 100, 800, 600)

        # Initialize central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Title and logo layout
        self.title_layout = QHBoxLayout()
        self.layout.addLayout(self.title_layout)

        # Logo
        self.logo_label = QLabel()
        self.logo_pixmap = QPixmap("assets/logo.png")  # Replace with your logo path
        self.logo_label.setPixmap(self.logo_pixmap.scaled(400,100 , Qt.KeepAspectRatio))
        self.title_layout.addWidget(self.logo_label)

        # Title
        self.title_label = QLabel("Accident Detection Application")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.title_layout.addWidget(self.title_label)

        # Image display labels
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(600, 400)
        self.layout.addWidget(self.image_label)

        # Buttons layout
        self.button_layout = QHBoxLayout()

        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        self.select_file_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.button_layout.addWidget(self.select_file_button)

        self.select_video_button = QPushButton("Select Video")
        self.select_video_button.clicked.connect(self.select_video)
        self.select_video_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #17A2B8;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        self.button_layout.addWidget(self.select_video_button)

        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.start_detection)
        self.start_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #28A745;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Detection")
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #DC3545;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.button_layout.addWidget(self.stop_button)

        self.start_live_button = QPushButton("Start Live Detection")
        self.start_live_button.clicked.connect(self.start_live_detection)
        self.start_live_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #FFC107;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #c69500;
            }
        """)
        self.button_layout.addWidget(self.start_live_button)

        self.stop_live_button = QPushButton("Stop Live Detection")
        self.stop_live_button.clicked.connect(self.stop_live_detection)
        self.stop_live_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #DC3545;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.button_layout.addWidget(self.stop_live_button)

        self.layout.addLayout(self.button_layout)

        # Label to display selected file
        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_label)

        self.model_path = r"training_files/best11s_470imgs.pt"
        self.selected_file = None
        self.is_video = False
        self.detection_thread = None
        self.live_detection_thread = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Image Files (*.jpg *.png *.jpeg)"
        )
        if file_path:
            self.selected_file = file_path
            self.is_video = False
            self.file_label.setText(f"Selected File: {file_path}")
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
        else:
            self.file_label.setText("No file selected")

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if file_path:
            self.selected_file = file_path
            self.is_video = True
            self.file_label.setText(f"Selected Video: {file_path}")
        else:
            self.file_label.setText("No video selected")

    def start_detection(self):
        if not self.selected_file:
            self.file_label.setText("Please select a file or video before starting detection.")
            return
        self.file_label.setText(f"Processing: {self.selected_file}")
        self.detection_thread = DetectionThread(self.model_path, self.selected_file, self.is_video)
        self.detection_thread.detection_complete.connect(self.on_detection_complete)
        self.detection_thread.start()

    def on_detection_complete(self, result):
        if "Error:" in result:
            self.file_label.setText(result)
        else:
            self.file_label.setText("Detection completed. Showing labeled output.")
            self.show_output_image(result)

    def show_output_image(self, image_path):
        if self.is_video:
            self.file_label.setText(f"Labeled video saved at: {image_path}")
        else:
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def stop_detection(self):
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            self.detection_thread.quit()
            self.file_label.setText("Detection stopped.")
            print("Detection stopped.")

    def start_live_detection(self):
        self.live_detection_thread = LiveDetectionThread(self.model_path)
        self.live_detection_thread.frame_processed.connect(self.update_live_frame)
        self.live_detection_thread.start()

    def update_live_frame(self, pixmap):
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def stop_live_detection(self):
        if self.live_detection_thread and self.live_detection_thread.isRunning():
            self.live_detection_thread.stop()
            self.live_detection_thread.quit()
            self.file_label.setText("Live detection stopped.")
            print("Live detection stopped.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow {
            font-size: 14px;
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            padding: 10px;
        }
        QLabel {
            font-size: 14px;
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            padding: 10px;
        }
        QPushButton {
            font-size: 14px;
            color: #FFFFFF;
            background-color: #007BFF;
            border: 1px solid #CCCCCC;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:pressed {
            background-color: #004085;
        }
    """)
    window = AccidentDetectionApp()
    window.show()
    sys.exit(app.exec_())
