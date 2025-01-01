import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO

# Initialize global variables
cap = None
stop_live_detection = False
input_image_label = None
output_image_label = None

def select_image():
    # Open a file dialog to select an image
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        preview_image(file_path)  # Show the input image in the GUI
        process_image(file_path)

def preview_image(file_path):
    global input_image_label
    # Display the selected input image
    image = Image.open(file_path)
    image = image.resize((300, 300))  # Resize for display
    photo = ImageTk.PhotoImage(image)

    if input_image_label is None:
        input_image_label = tk.Label(root, image=photo, bg="#E2E3E0")  # Match the background color
        input_image_label.image = photo
        input_image_label.pack(pady=10)
    else:
        input_image_label.config(image=photo)
        input_image_label.image = photo

def process_image(file_path):
    global output_image_label
    # Run YOLOv8 detection
    results = model(file_path)
    
    # Access the first result
    result = results[0]
    
    # Generate the output image with detections
    output_image = result.plot()  # `plot` creates an image with the detections
    
    # Save the detected image to a file
    output_path = "detected_output.jpg"
    cv2.imwrite(output_path, cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR))  # Convert to BGR for OpenCV
    
    # Display the detected output image in the GUI
    display_output_image(output_path)

def display_output_image(image_path):
    global output_image_label
    # Display the detected image in the Tkinter window
    image = Image.open(image_path)
    image = image.resize((300, 300))  # Resize for display
    photo = ImageTk.PhotoImage(image)

    if output_image_label is None:
        output_image_label = tk.Label(root, image=photo, bg="#E2E3E0")  # Match the background color
        output_image_label.image = photo
        output_image_label.pack(pady=10)
    else:
        output_image_label.config(image=photo)
        output_image_label.image = photo

def start_live_detection():
    global cap, stop_live_detection, input_image_label, output_image_label
    stop_live_detection = False
    cap = cv2.VideoCapture(0)  # Open the system camera

    # Hide input and output images
    if input_image_label:
        input_image_label.destroy()
        input_image_label = None

    if output_image_label:
        output_image_label.destroy()
        output_image_label = None

    live_detection_loop()

def live_detection_loop():
    global cap, stop_live_detection, output_image_label
    if stop_live_detection or not cap.isOpened():
        return  # Stop live detection if the flag is set or the camera is closed

    ret, frame = cap.read()  # Read a frame from the camera
    if not ret:
        return  # Stop if the frame cannot be captured

    # Run YOLOv8 detection on the frame
    results = model(frame)
    result = results[0]
    output_frame = result.plot()  # Annotate the frame with detections

    # Convert the frame to an ImageTk object for display
    output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    img = Image.fromarray(output_frame)
    img = img.resize((300, 300))  # Resize for display
    photo = ImageTk.PhotoImage(img)

    if output_image_label is None:
        output_image_label = tk.Label(root, image=photo, bg="#E2E3E0")  # Match the background color
        output_image_label.image = photo
        output_image_label.pack(pady=10)
    else:
        output_image_label.config(image=photo)
        output_image_label.image = photo

    # Schedule the next frame update
    root.after(10, live_detection_loop)

def stop_live():
    global stop_live_detection, cap, output_image_label
    stop_live_detection = True  # Stop the live detection loop
    if cap:
        cap.release()  # Release the camera resource

    # Clear the last frame of detection
    if output_image_label:
        output_image_label.destroy()
        output_image_label = None

# Load your YOLOv8 model
model = YOLO("training_files/best.pt")  # Replace with your model path

# Create the Tkinter window
root = tk.Tk()
root.title("Accident eye")
root.configure(bg="#E2E3E0")  # Set background color to match logo

# # Add logo at the top
# logo_path = r"C:\Users\Parth garg\Documents\Projects\Accident_eye\assets\output\Logo.webp"  # Replace with your logo path
# logo_image = Image.open(logo_path)
# logo_image = logo_image.resize((200, 100))  # Resize for display
# logo_photo = ImageTk.PhotoImage(logo_image)

# logo_label = tk.Label(root, image=logo_photo, bg="#E2E3E0")  # Match the background color
# logo_label.image = logo_photo
# logo_label.pack(pady=10)

# Add buttons with specified colors
select_button = tk.Button(root, text="Select Image", command=select_image, bg="blue", fg="white")
select_button.pack(pady=10)

live_button = tk.Button(root, text="Start Live Detection", command=start_live_detection, bg="green", fg="white")
live_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Live Detection", command=stop_live, bg="red", fg="white")
stop_button.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
