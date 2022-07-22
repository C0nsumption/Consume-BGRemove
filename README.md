# octo-waffle
<img src="https://github.com/ConsumptionParadox/octo-waffle/blob/main/img/LoadPhoto.png" width="300">
<img src="https://github.com/ConsumptionParadox/octo-waffle/blob/main/img/RemoveBG.png" width="300">

This a python based image background remover. This is more so meant for product photography where backgrounds are primarily white, black, or any another uniform color separate from the colors of the product itself. 

### Requirements
* Python3 (written and tested on Python 3.10)
* PYsimpleGUI
* PIL ( pillow )

### Instruction
1. To start the application, run 'python main.py' in the containing folder. This will bring up the GUI:

<img src="https://github.com/ConsumptionParadox/octo-waffle/blob/main/img/GUI.png" width="300">

2. Load an image in to the software by first browsing and selecting the desired image file. Once your file has been selected, press the 'Load Image' button to load the image data into memory for processing:

<img src="https://github.com/ConsumptionParadox/octo-waffle/blob/main/img/LoadPhoto.png" width="300">

3. Fine tune the red, blue, and green sliders for the appropriate background color. In the the example image, the background color is primarily white so 250 is a good value for all three. White has a RGB value of (255, 255, 255) but I use (250, 250, 250) to minimize the outline resulting from any colors interpolated from the transition area between subject and background. Once you have your desired color, press the 'Remove BG' button. This removes the BG: 

<img src="https://github.com/ConsumptionParadox/octo-waffle/blob/main/img/RemoveBG.png" width="300">

4. If the result is satisfactory, select the 'Save Result' button to save the image as 'result.png':

<img src="https://github.com/ConsumptionParadox/octo-waffle/blob/main/img/Result.png" width="300">





