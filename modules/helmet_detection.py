from ultralytics import YOLO
import cv2
import easyocr  # Add this import for EasyOCR

class HelmetDetection:
    def __init__(self, helmet_model_path="pt_files/helmet.pt", bike_model_path="pt_files/vehicle.pt", plate_model_path="pt_files/no_plate.pt"):
        self.helmet_model = YOLO(helmet_model_path)
        self.bike_model = YOLO(bike_model_path)
        self.plate_model = YOLO(plate_model_path)
        self.ocr_reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader

    def detect_helmet(self, frame):
        bike_results = self.bike_model(frame)
        for bike in bike_results:
            helmet_results = self.helmet_model(bike)
            if not helmet_results:
                plate_results = self.plate_model(bike)
                for plate in plate_results:
                    number_plate = self.extract_number_plate(plate)
                    return number_plate
        return "Helmet detected"

    def extract_number_plate(self, plate):
        # Assuming plate is a cropped image of the number plate
        gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        result = self.ocr_reader.readtext(gray_plate)
        number_plate_text = result[0][-2] if result else "Unknown"
        return number_plate_text