#!/usr/bin/env python3
import sys
from PIL import Image, ImageOps
import dominance as d
import shelve
from os import path

def add_borders(image, colors_as_hex):
    return image

def visualize_colors(impath):
    imp = path.normpath(path.abspath(impath))
    d.extract_color_information(imp, reuse=True) # if it is already there, it will be reused
    with shelve.open(d.DOMINANT_COLORS_SHELVE) as colorshelf:
        colors_as_ints = colorshelf[imp]
    colors_as_hex = list(map(d.int_to_color_str, colors_as_ints))
    print("Relevant Colors: {}".format(colors_as_hex))
    with Image.open(imp) as image:
        for colo in colors_as_hex:
            image = ImageOps.expand(image, border=100, fill=colo)
        image.show()

if __name__ == "__main__":
    visualize_colors(impath=sys.argv[1])
