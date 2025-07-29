import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import json
import os

# === Configuration ===
target_width = 492
target_height = 162
output_path = "image json.txt"
max_colors = 16

# === Globals ===
original_image = None
processed_image = None
preview_label = None

# === Image Processing ===
def process_image():
    global processed_image
    if original_image is None:
        return

    img = original_image.resize((target_width, target_height), Image.LANCZOS)

    # Apply brightness and contrast
    brightness = brightness_var.get()
    contrast = contrast_var.get()
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)

    # Reduce colors
    img = img.convert("P", palette=Image.ADAPTIVE, colors=max_colors)
    if not dithering_var.get():
        img = img.convert("RGB")  # No dithering (clean)
    else:
        img = img.convert("RGB")  # With dithering (built-in from palette)

    processed_image = img
    update_preview()

# === Update Preview ===
def update_preview():
    if processed_image is None:
        return
    scale = 2  # Upscale preview to 2x
    preview_size = (target_width * scale, target_height * scale)
    img_large = processed_image.resize(preview_size, Image.NEAREST)
    tk_img = ImageTk.PhotoImage(img_large)
    preview_label.config(image=tk_img)
    preview_label.image = tk_img  # Keep reference!


# === Save JSON ===
def save_json():
    if processed_image is None:
        messagebox.showerror("No image", "Please load and process an image first.")
        return

    pixels = []
    for y in range(target_height):
        for x in range(target_width):
            r, g, b = processed_image.getpixel((x, y))
            hex_color = "#{:02X}{:02X}{:02X}".format(r, g, b)
            pixels.append(hex_color)

    try:
        with open(output_path, "w") as f:
            json.dump(pixels, f)
        messagebox.showinfo("Saved", f"Saved image json to:\n{os.path.abspath(output_path)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save JSON:\n{e}")

# === Load Image ===
def load_image():
    global original_image
    filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
    path = filedialog.askopenfilename(title="Select an image", filetypes=filetypes)
    if not path:
        return

    try:
        img = Image.open(path).convert("RGB")
        original_image = img
        process_image()
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image:\n{e}")

# === GUI Setup ===
root = tk.Tk()
root.title("CC:Tweaked Image to 16-Color JSON")
root.geometry("600x500")

frame = tk.Frame(root)
frame.pack(pady=10)

# Buttons
btn_load = tk.Button(frame, text="📂 Load Image", command=load_image)
btn_load.grid(row=0, column=0, padx=5)

btn_save = tk.Button(frame, text="💾 Save JSON", command=save_json)
btn_save.grid(row=0, column=1, padx=5)

# Dithering toggle
dithering_var = tk.BooleanVar(value=True)
chk_dither = tk.Checkbutton(root, text="Use Dithering", variable=dithering_var, command=process_image)
chk_dither.pack(pady=5)

# Sliders
def add_slider(label, var, from_, to_, resolution, command):
    row = tk.Frame(root)
    row.pack(fill="x", padx=20)
    tk.Label(row, text=label, width=12).pack(side="left")
    scale = tk.Scale(row, variable=var, from_=from_, to=to_, resolution=resolution, orient=tk.HORIZONTAL, command=lambda e: command())
    scale.pack(fill="x", expand=True)

brightness_var = tk.DoubleVar(value=1.0)
contrast_var = tk.DoubleVar(value=1.0)

add_slider("Brightness", brightness_var, 0.2, 2.0, 0.05, process_image)
add_slider("Contrast", contrast_var, 0.2, 2.0, 0.05, process_image)

# Preview
preview_label = tk.Label(root)
preview_label.pack(pady=10)

# Run GUI
root.mainloop()
