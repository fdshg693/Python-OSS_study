from PIL import ImageGrab, Image

im: Image.Image = ImageGrab.grab(all_screens=True)
im.save("screenshot.png")
print(im)
