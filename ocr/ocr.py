#!/usr/bin/env python3
try:  
    from PIL import Image
except ImportError:  
    import Image
import pytesseract
import sys

def ocr_core(filename):  
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(Image.open(filename), lang='eng')  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text

if __name__ == "__main__":
    print(ocr_core('{}/{}'.format(sys.argv[1], sys.argv[2])))
