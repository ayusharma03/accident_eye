from ultralytics import YOLO

class NumberplateDetection:
    def __init__(self, model_path="pt_files/no_plate.pt"):
        self.model = YOLO(model_path)

    def detect_numberplate(self, frame):
        results = self.model(frame)
        class_names = [result.names[0] for result in results]  # Extract the first name from each result
        return results, class_names