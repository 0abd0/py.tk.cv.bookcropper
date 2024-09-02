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

def crop_and_split_image(image_path, output_folder, top_pixels, bottom_pixels, left_pixels, right_pixels, split_image, split_position, auto_crop):
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

    if split_image and split_position:
        # Split the image into two parts
        height, width = trimmed_image.shape[:2]
        if split_position < width:
            left_part = trimmed_image[:, :split_position]
            right_part = trimmed_image[:, split_position:]
            
            # Save the split images
            left_output_path = os.path.join(output_folder, 'left_' + os.path.basename(image_path))
            right_output_path = os.path.join(output_folder, 'right_' + os.path.basename(image_path))
            cv2.imwrite(left_output_path, left_part)
            cv2.imwrite(right_output_path, right_part)
            
            # Optionally, show the split images
            Image.open(left_output_path).show()
            Image.open(right_output_path).show()
        else:
            messagebox.showerror("Error", "Split position is beyond the image width!")
    else:
        # Save the single cropped/trimmed image
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        cv2.imwrite(output_path, trimmed_image)
        # Optionally, show the processed image
        Image.open(output_path).show()

def process_images():
    input_folder_path = input_folder_path_var.get()
    output_folder_path = output_folder_path_var.get()
    try:
        top_pixels = int(top_pixels_var.get())
        bottom_pixels = int(bottom_pixels_var.get())
        left_pixels = int(left_pixels_var.get())
        right_pixels = int(right_pixels_var.get())
        split_position = int(split_position_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for pixels!")
        return
    
    split_image = split_image_var.get()
    auto_crop = auto_crop_var.get()
    
    if not input_folder_path or not output_folder_path:
        messagebox.showerror("Error", "Please select both input and output folders!")
        return
    
    os.makedirs(output_folder_path, exist_ok=True)
    
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder_path, filename)
            crop_and_split_image(image_path, output_folder_path, top_pixels, bottom_pixels, left_pixels, right_pixels, split_image, split_position, auto_crop)
    
    messagebox.showinfo("Success", "Images processed and saved.")

# Setup Tkinter
app = tk.Tk()
app.title("Image Processor")

# Variables
input_folder_path_var = tk.StringVar()
output_folder_path_var = tk.StringVar()
top_pixels_var = tk.StringVar()
bottom_pixels_var = tk.StringVar()
left_pixels_var = tk.StringVar()
right_pixels_var = tk.StringVar()
split_position_var = tk.StringVar()
auto_crop_var = tk.BooleanVar(value=True)
split_image_var = tk.BooleanVar(value=False)

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

tk.Checkbutton(app, text="Split Image into 2 Parts", variable=split_image_var).pack(pady=10)

tk.Label(app, text="Position to Split Image (in pixels):").pack(pady=10)
tk.Entry(app, textvariable=split_position_var, width=10).pack(pady=5)

tk.Button(app, text="Process Images", command=process_images).pack(pady=20)

app.mainloop()
