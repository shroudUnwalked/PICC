#!/usr/bin/env python3
# Takes an image and makes the dark text easier to recognize
# This seems to work well on blurry text
# https://stackoverflow.com/a/51691727/2550406
import sys
from PIL import Image

def clarify(imagepath, threshold=40):
    with Image.open(imagepath) as im:
        # grayscale and enlarging helps
        ima = im.convert('L').resize([3 * _ for _ in im.size], Image.BICUBIC)
        # tresholding: make light points lighter
        imag = ima.point(lambda p: p > threshold and p + 100)
        return imag

if __name__ == "__main__":
    image = clarify(sys.argv[1])
    image.save(sys.argv[2])
