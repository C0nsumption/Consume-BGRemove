# old_main.py

import io
import os
import PySimpleGUI as sg
from PIL import Image
import numpy as np
import bg_remover as bg
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

file_types = [("All files (*.*)", "*.*")]

def update_image(window, image, key):
    img_width, img_height = image.size
    scale = min(400/img_width, 400/img_height)
    new_width, new_height = int(img_width * scale), int(img_height * scale)
    
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    bio = io.BytesIO()
    resized_image.save(bio, format="PNG")
    window[key].erase()
    window[key].draw_image(data=bio.getvalue(), location=(0, new_height))
    
    return new_width, new_height

def process_image(image, color, tolerance, blur_radius, mode, refine):
    try:
        logging.info(f"Processing image... Mode: {mode}, Refine: {refine}")
        colorized = bg.remove_background(image, *color, tolerance, blur_radius, mode=mode, refine=refine)
        logging.info("Image processing completed.")
        return colorized
    except Exception as e:
        logging.error(f"Failed to process image: {str(e)}")
        return None

layout = [
    [sg.Text("Input file:"), sg.Input(size=(25, 1), enable_events=True, key="-IN FILE-"), sg.FileBrowse(file_types=file_types)],
    [sg.Button("Save File", key="-SAVE-"), sg.Button("Exit")],
    [sg.Graph(canvas_size=(400, 400), graph_bottom_left=(0, 0), graph_top_right=(400, 400), key="-IN-", enable_events=True),
     sg.Graph(canvas_size=(400, 400), graph_bottom_left=(0, 0), graph_top_right=(400, 400), key="-OUT-", enable_events=True)],
    [sg.Text("Click on the input image to select background color")],
    [sg.Text("Selected Color:"), sg.Text("", size=(15,1), key="-SELECTED-COLOR-")],
    [sg.Text("Tolerance:"), sg.Slider(range=(0, 100), orientation='h', key='-TOLERANCE-', default_value=30, enable_events=True)],
    [sg.Text("Blur Radius:"), sg.Slider(range=(0, 5), orientation='h', key='-BLUR-', default_value=2, resolution=0.1, enable_events=True)],
    [sg.Text("Mode:"), sg.Radio("Simple", "MODE", key="-SIMPLE-", default=True, enable_events=True), 
     sg.Radio("Advanced", "MODE", key="-ADVANCED-", enable_events=True)],
    [sg.Checkbox("Refine Edges", key="-REFINE-", enable_events=True)]
]

window = sg.Window("Background Remover", layout, size=(850, 650))

image = colorized = None
image_size = (0, 0)
selected_color = None

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "-IN FILE-":
        filename = values["-IN FILE-"]
        if os.path.exists(filename):
            try:
                image = Image.open(filename)
                image_size = update_image(window, image, "-IN-")
                window["-OUT-"].erase()
                window["-SELECTED-COLOR-"].update("")
                selected_color = None
                logging.info(f"Image loaded. Size: {image.size}")
            except Exception as e:
                logging.error(f"Failed to load image: {str(e)}")
                sg.popup_error("Error", f"Failed to load image: {str(e)}")

    if event == "-IN-" and image:
        try:
            x, y = values["-IN-"]
            orig_x = int(x * (image.width / image_size[0]))
            orig_y = int((image_size[1] - y) * (image.height / image_size[1]))
            selected_color = image.getpixel((orig_x, orig_y))[:3]
            window["-SELECTED-COLOR-"].update(f"RGB: {selected_color}")
            logging.info(f"Pixel selected at coordinates ({orig_x}, {orig_y}). Color: {selected_color}")
        except Exception as e:
            logging.error(f"Failed to get pixel color: {str(e)}")
            sg.popup_error("Error", f"Failed to get pixel color: {str(e)}")

    if event in ("-IN-", "-TOLERANCE-", "-BLUR-", "-SIMPLE-", "-ADVANCED-", "-REFINE-") and image and selected_color:
        tolerance = int(values['-TOLERANCE-'])
        blur_radius = float(values['-BLUR-'])
        mode = 'advanced' if values['-ADVANCED-'] else 'simple'
        refine = values['-REFINE-']
        colorized = process_image(image, selected_color, tolerance, blur_radius, mode, refine)
        if colorized:
            update_image(window, colorized, "-OUT-")

    if event == "-SAVE-" and colorized:
        try:
            filename = sg.popup_get_file('Save processed image.', save_as=True, file_types=file_types)
            if filename:
                colorized.save(filename)
                sg.popup_quick_message('Image saved successfully', background_color='green', text_color='white', font='Any 16')
        except Exception as e:
            logging.error(f"Failed to save image: {str(e)}")
            sg.popup_error("Error", f"Failed to save image: {str(e)}")

window.close()