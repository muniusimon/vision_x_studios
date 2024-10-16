from PIL import Image, ImageFilter

def apply_filter(image_path, filter_type):
    image = Image.open(image_path)
    if filter_type == "BLUR":
        return image.filter(ImageFilter.BLUR)
    elif filter_type == "CONTOUR":
        return image.filter(ImageFilter.CONTOUR)
    # Add more filters as needed
    return image
from PIL import Image, ImageFilter
import os

def resize_image(input_path, output_path, size):
    """
    Resize an image to the given size.
    """
    try:
        img = Image.open(input_path)
        img = img.resize(size)
        img.save(output_path)
        print(f"Image resized and saved at {output_path}")
    except Exception as e:
        print(f"Error resizing image: {e}")

def apply_blur(input_path, output_path):
    """
    Apply blur to an image.
    """
    try:
        img = Image.open(input_path)
        img = img.filter(ImageFilter.BLUR)
        img.save(output_path)
        print(f"Blurred image saved at {output_path}")
    except Exception as e:
        print(f"Error applying blur to image: {e}")

def convert_to_grayscale(input_path, output_path):
    """
    Convert an image to grayscale.
    """
    try:
        img = Image.open(input_path)
        grayscale_img = img.convert("L")
        grayscale_img.save(output_path)
        print(f"Grayscale image saved at {output_path}")
    except Exception as e:
        print(f"Error converting image to grayscale: {e}")
