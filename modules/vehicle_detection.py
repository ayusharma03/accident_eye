from ultralytics import YOLO

class VehicleDetection:
    def __init__(self, model_path="pt_files/vehicle.pt"):
        self.model = YOLO(model_path)

    def detect_vehicle(self, frame):
        vehicle_results = self.model(frame)
        return vehicle_results