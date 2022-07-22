from PIL import Image

    
def convertImage(img, red, blue, green):
    print('removing')
    img = img.convert("RGBA")
    data = img.getdata()
  
    newData = []
  
    for item in data:
        if item[0] >= red and item[1] >= blue and item[2] >= green:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
  
    img.putdata(newData)
    return img


if __name__ == "__main__":
    convertImage()
