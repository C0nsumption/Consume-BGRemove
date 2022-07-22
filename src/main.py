import io
import os
import PySimpleGUI as sg
from PIL import Image
import BG_remover as bg

file_types = [("JPEG (*.jpg)", "*.jpg"),
              ("All files (*.*)", "*.*")]


# GUI layout: each list is a row in the GUI
layout = [
    [sg.Image(key="-IMAGE-")],
    [sg.Text("Image File"), sg.Input(size=(25, 1), key="-FILE-"), sg.FileBrowse(file_types=file_types), sg.Button("Load Image", key='-LOADIMAGE-'),],
    [sg.Text("Adjust sliders to remove anypixel within that minimum range of color.")],
    [sg.Text("0 = Black    255 = White      Slightly adjust sliders to refine edge.")],
    [sg.Text("Red", font=16), sg.Slider(range=(0, 255), orientation='h', key='-RED-', default_value=250)], 
    [sg.Text("Blue", font=16),sg.Slider(range=(0, 255), orientation='h', key='-BLUE-', default_value=250)], 
    [sg.Text("Green", font=16),sg.Slider(range=(0, 255), orientation='h', key='-GREEN-', default_value=250)], 
    [sg.Button("Remove BG", key='-REMOVEBG-')],
    [sg.Button("Save Result", key='-SAVERESULT-')]
]

# Creating our actual window (pass in GUI layout)
window = sg.Window("BG Remover", layout)

# Event loop for our window
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # loads image into memory if it exist
    if event == "-LOADIMAGE-":
        filename = values["-FILE-"]
        if os.path.exists(filename):
            image = Image.open(values["-FILE-"])
            image.thumbnail((400, 400))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            window["-IMAGE-"].update(data=bio.getvalue())

    # removes bg from image and reloads result back into memory
    if event == "-REMOVEBG-":
        image = bg.convertImage(image, values['-RED-'], values['-BLUE-'], values['-GREEN-'])
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        window["-IMAGE-"].update(data=bio.getvalue())

    # saves image.
    if event == "-SAVERESULT-":
        # checks for an instance of image variable in locals to prevent crashing
        if 'image' in locals():
            image.save('result.png', format="PNG")
        else:
            print('you must select an image')
        


window.close()
if __name__ == "__main__":
    pass