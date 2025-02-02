from ultralytics import YOLO

class HelmetDetection:
    def __init__(self, model_path="pt_files/helmet.pt"):
        self.model = YOLO(model_path)

    def detect_helmet(self, frame):
        helmet_results = self.model(frame)
        return helmet_results