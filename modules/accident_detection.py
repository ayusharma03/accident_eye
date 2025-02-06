from ultralytics import YOLO

class AccidentDetection:
    def __init__(self, model_path="pt_files/accidents.pt"):
        self.model = YOLO(model_path)

    def detect_accident(self, frame):
        accident_results = self.model(frame)
        accident_class_names = [self.model.names[int(box.cls)] for result in accident_results for box in result.boxes]
        return accident_results, accident_class_names