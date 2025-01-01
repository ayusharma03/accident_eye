import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import torch
import os
import subprocess


class DetectionThread(QThread):
    detection_complete = pyqtSignal(str)  # Signal to indicate detection is complete
    script_output = pyqtSignal(str)  # Signal to emit script output

    def __init__(self, model_path, input_file):
        super().__init__()
        self.model_path = model_path
        self.input_file = input_file
        self.stop_flag = False  # Flag to safely stop the thread

    def stop(self):
        """Set the stop flag to terminate detection."""
        self.stop_flag = True

    def run(self):
        """Run YOLO detection in a separate thread."""
        try:
            from ultralytics import YOLO

            # Check for GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.script_output.emit(f"Using device: {device}")

            model = YOLO(self.model_path)
            results = model(self.input_file, device=device)
            
            # Save the output
            output_dir = os.path.join(os.path.dirname(self.input_file), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "labeled_output.jpg")
            results[0].save(output_dir)  # Save the result
            
            # Emit the path to the labeled image
            self.detection_complete.emit(output_path)
        except Exception as e:
            self.detection_complete.emit(f"Error: {e}")

    def stop(self):
        """Set the stop flag to terminate detection."""
        self.stop_flag = True


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

        # Label to display selected file
        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_label)

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
                background-color: #373A40;
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
        self.button_layout.addWidget(self.select_file_button)

        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.start_detection)
        self.start_button.setStyleSheet("""
            QPushButton {
                padding: 6px;
                background-color: #373A40;
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
                background-color: #373A40;
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
        self.button_layout.addWidget(self.stop_button)

        self.layout.addLayout(self.button_layout)

        self.model_path = r"training_files/best.pt"
        self.selected_file = None
        self.detection_thread = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Image Files (*.jpg *.png *.jpeg)"
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"Selected File: {file_path}")
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio
            ))
        else:
            self.file_label.setText("No file selected")

    def start_detection(self):
        if not self.selected_file:
            self.file_label.setText("Please select a file before starting detection.")
            return
        self.file_label.setText(f"Processing: {self.selected_file}")
        self.detection_thread = DetectionThread(self.model_path, self.selected_file)
        self.detection_thread.detection_complete.connect(self.on_detection_complete)
        self.detection_thread.start()

    def on_detection_complete(self, result):
        if "Error:" in result:
            self.file_label.setText(result)
        else:
            self.file_label.setText("Detection completed. Showing labeled output.")
            self.show_output_image(result)

    def show_output_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio
        ))

    def stop_detection(self):
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            self.detection_thread.quit()
            self.file_label.setText("Detection stopped.")
            print("Detection stopped.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow {
            font-size: 14px;
            color: #eeeeee;
            background-color: #333333;
            border: 1px solid #444444;
            padding: 10px;
        }
        QLabel {
            font-size: 14px;
            color: #eeeeee;
            background-color: #333333;
            border: 1px solid #444444;
            padding: 10px;
        }
        QPushButton {
            font-size: 14px;
            color: #eeeeee;
            background-color: #333333;
            border: 1px solid #444444;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #444444;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
    """)
    window = AccidentDetectionApp()
    window.show()
    sys.exit(app.exec_())
