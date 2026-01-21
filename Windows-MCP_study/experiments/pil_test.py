from PIL import ImageGrab, Image

# 全画面をキャプチャ
im: Image.Image = ImageGrab.grab(all_screens=True)
im.save("screenshot.png")
