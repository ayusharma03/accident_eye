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
        # Ensure the frame is in the correct format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        bike_results = self.bike_model(frame_rgb)
        number_plates = []

        for bike in bike_results:
            bike_image = bike.orig_img  # Get the original image of the bike
            bike_image_rgb = cv2.cvtColor(bike_image, cv2.COLOR_BGR2RGB)  # Convert to RGB
            helmet_count = 0
            plate_count = 0

            for _ in range(10):  # Check 10 frames
                helmet_results = self.helmet_model(bike_image_rgb)
                if not helmet_results:
                    helmet_count += 1
                    plate_results = self.plate_model(bike_image_rgb)
                    for plate in plate_results:
                        number_plate = self.extract_number_plate(plate)
                        if number_plate != "Unknown":
                            plate_count += 1

            if helmet_count >= 8 and plate_count >= 8:  # Confirm if 8 out of 10 frames meet the condition
                number_plates.append(number_plate)

        return bike_results  # Return bike results if helmet is detected

    def extract_number_plate(self, plate):
        # Assuming plate is a cropped image of the number plate
        gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        result = self.ocr_reader.readtext(gray_plate)
        number_plate_text = result[0][-2] if result else "Unknown"
        return number_plate_text

    def process_video(self, app, video_path):
        """Process the uploaded video file."""
        while True:  # Loop the video
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                helmet_results = self.detect_helmet(frame)
                # ...additional processing...

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img_tk = ctk.CTkImage(light_image=img, size=(700, 500))
                app.cam_label.configure(image=img_tk)
                app.cam_label.image = img_tk

                time.sleep(0.03)  # Control the frame rate

            cap.release()