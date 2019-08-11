#!/usr/bin/env python3
from PIL import Image
import PIL.ImageOps
import sys

def invert(imagename):
    image = Image.open(imagename)
    # avoid a PIL bug (respectively fixme)
    if image.mode == "P":
        im = image.convert("RGB")
    else:
        im = image
    #print("image mode: {}".format(image.mode))
    inverted = PIL.ImageOps.invert(im)
    image.close()
    return inverted

if __name__ == "__main__":
    convert(sys.argv[1])
