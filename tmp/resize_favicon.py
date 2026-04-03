from PIL import Image
import os

img_path = r"c:\Users\Admin\Desktop\CareerVerse\static\images\favicon_v5_final.png"
with Image.open(img_path) as img:
    img = img.convert("RGBA")
    bbox = img.getbbox()
    print(f"Original size: {img.size}")
    print(f"Bounding box of content: {bbox}")
    
    # Create a new transparent image of the same size
    new_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    
    # Calculate target size for the content (e.g. 70% of original size)
    content = img.crop(bbox)
    w, h = content.size
    ratio = 0.7
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    content_resized = content.resize((new_w, new_h), Image.LANCZOS)
    
    # Paste centered
    x = (img.size[0] - new_w) // 2
    y = (img.size[1] - new_h) // 2
    new_img.paste(content_resized, (x, y), content_resized)
    
    # Save as backup and then overwrite
    backup_path = img_path + ".bak"
    if not os.path.exists(backup_path):
        os.rename(img_path, backup_path)
    new_img.save(img_path)
    print(f"Saved smaller favicon to {img_path}")
