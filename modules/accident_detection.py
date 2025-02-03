from ultralytics import YOLO

class AccidentDetection:
    def __init__(self, model_path="pt_files/vehicle.pt"):
        self.model = YOLO(model_path)

    def detect_accident(self, frame):
        accident_results = self.model(frame)
        return accident_results