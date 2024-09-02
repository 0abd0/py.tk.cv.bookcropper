import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os
from PIL import Image

def select_input_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        input_folder_path_var.set(folder_selected)

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_folder_path_var.set(folder_selected)

def crop_image(image_path, output_path, top_pixels, bottom_pixels, left_pixels, right_pixels, auto_crop):
    image = cv2.imread(image_path)
    
    if auto_crop:
        # Perform auto-cropping based on detected page borders
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            if len(approx) == 4:
                pts = np.array(approx).reshape(-1, 2)
                rect = cv2.boundingRect(pts)
                x, y, w, h = rect
                cropped_image = image[y:y+h, x:x+w]
            else:
                cropped_image = image
        else:
            cropped_image = image
    else:
        cropped_image = image
    
    # Apply manual trimming if enabled
    if any([top_pixels, bottom_pixels, left_pixels, right_pixels]):
        trimmed_image = cropped_image[
            top_pixels: -bottom_pixels if bottom_pixels else None,
            left_pixels: -right_pixels if right_pixels else None
        ]
    else:
        trimmed_image = cropped_image

    # Save the cropped or trimmed image
    cv2.imwrite(output_path, trimmed_image)
    
    # Optionally, convert to PIL Image for further operations if needed
    pil_image = Image.open(output_path)
    pil_image.show()

def process_images():
    input_folder_path = input_folder_path_var.get()
    output_folder_path = output_folder_path_var.get()
    try:
        top_pixels = int(top_pixels_var.get())
        bottom_pixels = int(bottom_pixels_var.get())
        left_pixels = int(left_pixels_var.get())
        right_pixels = int(right_pixels_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for pixels!")
        return
    
    auto_crop = auto_crop_var.get()
    
    if not input_folder_path or not output_folder_path:
        messagebox.showerror("Error", "Please select both input and output folders!")
        return
    
    os.makedirs(output_folder_path, exist_ok=True)
    
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder_path, filename)
            output_path = os.path.join(output_folder_path, filename)
            crop_image(image_path, output_path, top_pixels, bottom_pixels, left_pixels, right_pixels, auto_crop)
    
    messagebox.showinfo("Success", "Images processed and saved.")

# Setup Tkinter
app = tk.Tk()
app.title("Image Cropper")

# Variables
input_folder_path_var = tk.StringVar()
output_folder_path_var = tk.StringVar()
top_pixels_var = tk.StringVar()
bottom_pixels_var = tk.StringVar()
left_pixels_var = tk.StringVar()
right_pixels_var = tk.StringVar()
auto_crop_var = tk.BooleanVar(value=True)

# GUI Elements
tk.Label(app, text="Select Folder Containing Images:").pack(pady=10)
tk.Entry(app, textvariable=input_folder_path_var, width=50).pack(pady=5)
tk.Button(app, text="Browse", command=select_input_folder).pack(pady=5)

tk.Label(app, text="Select Output Folder:").pack(pady=10)
tk.Entry(app, textvariable=output_folder_path_var, width=50).pack(pady=5)
tk.Button(app, text="Browse", command=select_output_folder).pack(pady=5)

tk.Checkbutton(app, text="Enable Auto-Cropping", variable=auto_crop_var).pack(pady=10)

tk.Label(app, text="Pixels to Trim from Top:").pack(pady=10)
tk.Entry(app, textvariable=top_pixels_var, width=10).pack(pady=5)

tk.Label(app, text="Pixels to Trim from Bottom:").pack(pady=10)
tk.Entry(app, textvariable=bottom_pixels_var, width=10).pack(pady=5)

tk.Label(app, text="Pixels to Trim from Left:").pack(pady=10)
tk.Entry(app, textvariable=left_pixels_var, width=10).pack(pady=5)

tk.Label(app, text="Pixels to Trim from Right:").pack(pady=10)
tk.Entry(app, textvariable=right_pixels_var, width=10).pack(pady=5)

tk.Button(app, text="Process Images", command=process_images).pack(pady=20)

app.mainloop()
