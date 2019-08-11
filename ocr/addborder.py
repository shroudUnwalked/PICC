#!/usr/bin/env python
from PIL import Image
import sys

def addborder(impath, immode="RGB", borderwidth=30):
    with Image.open(impath) as old_im:
        old_size = old_im.size
        new_size = tuple(_ + borderwidth for _ in old_size)
        new_im = Image.new(immode, new_size)   ## this is black
        new_im.paste(old_im, (int((new_size[0]-old_size[0])/2),
                              int((new_size[1]-old_size[1])/2)))

        return new_im

if __name__ == "__main__":
    im = addborder(sys.argv[1])
    im.save(sys.argv[2])
