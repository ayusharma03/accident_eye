import customtkinter as ctk
import cv2
import threading
from modules.accident_detection import AccidentDetection
from modules.helmet_detection import HelmetDetection
from modules.numberplate_detection import NumberplateDetection
from modules.vehicle_detection import VehicleDetection

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Traffic Monitoring System")

        # Initialize detection modules
        self.accident_detector = AccidentDetection()
        self.helmet_detector = HelmetDetection()
        self.numberplate_detector = NumberplateDetection()
        self.vehicle_detector = VehicleDetection()

        # UI Elements
        self.video_label = ctk.CTkLabel(self, text="Video Feed")
        self.video_label.pack()

        self.start_button = ctk.CTkButton(self, text="Start Detection", command=self.start_detection)
        self.start_button.pack()

    def start_detection(self):
        cap = cv2.VideoCapture(1)  # Change to video file if needed
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Create threads for each detection module
            threads = []
            results = {}

            def run_detection(detector, name):
                results[name] = detector(frame)

            detectors = {
                "accident": self.accident_detector.detect_accident,
                "helmet": self.helmet_detector.detect_helmet,
                "numberplate": self.numberplate_detector.detect_numberplate,
                "vehicle": self.vehicle_detector.detect_vehicle,
            }

            for name, detector in detectors.items():
                thread = threading.Thread(target=run_detection, args=(detector, name))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Draw bounding boxes on the frame
            for name, detection_results in results.items():
                for result in detection_results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = App()
    app.mainloop()
