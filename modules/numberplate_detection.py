from ultralytics import YOLO

class NumberplateDetection:
    def __init__(self, model_path="pt_files/no_plate.pt"):
        self.model = YOLO(model_path)

    def detect_numberplate(self, frame):
        numberplate_results = self.model(frame)
        return numberplate_results