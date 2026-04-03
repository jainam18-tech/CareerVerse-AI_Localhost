from PIL import Image
import os

images = ["static/images/favicon_v5_final.png", "static/images/realistic_logo.png", "static/images/DataVidwan.jpeg"]
for img_path in images:
    full_path = os.path.join(r"c:\Users\Admin\Desktop\CareerVerse", img_path)
    if os.path.exists(full_path):
        with Image.open(full_path) as img:
            print(f"{img_path}: {img.size}")
    else:
        print(f"{img_path}: Not found")
