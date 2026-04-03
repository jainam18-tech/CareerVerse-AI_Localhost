# import cv2

# def preprocess_image(image_path):
#     img = cv2.imread(image_path)

#     img = cv2.resize(img, None, fx=2.5, fy=2.5)

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Increase contrast
#     gray = cv2.equalizeHist(gray)

#     thresh = cv2.threshold(
#         gray, 0, 255,
#         cv2.THRESH_BINARY + cv2.THRESH_OTSU
#     )[1]

#     return thresh

import cv2
import numpy as np
from PIL import Image


def preprocess_image(pil_image):
    """
    Advanced preprocessing for marksheet OCR.
    Improves clarity, contrast and removes noise.
    """

    # Convert PIL to OpenCV format
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Resize if too large (for stability)
    height, width = img.shape[:2]
    if width > 1500:
        scale = 1500 / width
        img = cv2.resize(img, None, fx=scale, fy=scale)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Remove noise
    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)

    # Increase contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(denoised)

    # Adaptive thresholding (better for tables)
    thresh = cv2.adaptiveThreshold(
        contrast,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    # Optional: morphological closing to connect broken text
    kernel = np.ones((1,1), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Convert back to PIL
    final_image = Image.fromarray(processed)

    return final_image

