#!/usr/bin/env python3
from . import addborder
from . import clarify
from . import invert as inv
from . import ocr
from PIL import Image
from os import path
from os import makedirs
from . import gifsupport
import shutil

class BadImageFileException(Exception):
    def __init__(self, message, custom_content):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        # Custom Code
        self.custom_content = custom_content

def setup_dirs_if_necessary():
    global MY_PATH, CLARIFIED_DIR, BORDERED_DIR, INVERTED_DIR, NOALPHA_DIR
    MY_PATH = path.abspath(path.dirname(__file__))
    CLARIFIED_DIR = path.join(MY_PATH, 'clarified')
    makedirs(CLARIFIED_DIR, exist_ok=True)
    BORDERED_DIR = path.join(MY_PATH, 'bordered')
    makedirs(BORDERED_DIR, exist_ok=True)
    INVERTED_DIR = path.join(MY_PATH, 'inverted')
    makedirs(INVERTED_DIR, exist_ok=True)
    NOALPHA_DIR = path.join(MY_PATH, 'noalpha')
    makedirs(NOALPHA_DIR, exist_ok=True)

def run_with_gif_support(imagepath, verbose=True):
    # filter out videos or other unopenable things
    try:
        with Image.open(imagepath) as img:
            if img.format == "GIF":
                gifinfo = gifsupport.gif_to_frames(imagepath) 
            else:
                return run(imagepath, verbose=verbose)

            o = []
            i = []
            for framepath in gifinfo.frames:
                (orig_texts, inv_texts) = run(framepath, verbose=verbose)
                o.extend(orig_texts)
                i.extend(inv_texts)

            if gifinfo.tmpdir is not None:
                shutil.rmtree(gifinfo.tmpdir)
                gifinfo.tmpdir = None

            # store information that this is a gif
            # store it twice per frame, to encode the frame number like that as well
            # TWICE, because if it is only there once, it will be ignored
            for ii in range(0,len(gifinfo.frames)):
                o.append(gifsupport.META_WORD_IS_A_GIF)
                i.append(gifsupport.META_WORD_IS_A_GIF)

            return (o, i)
    except OSError as e:
        print("{}\nSkipping File {}".format(e, imagepath))
        raise BadImageFileException(e.strerror, e)


def run(imagepath, verbose=True):
    """returns a tuple with lists of strings, where each string is the whole text of the image as recognized"""
    setup_dirs_if_necessary()
    original_texts = []
    inverted_texts = []

    # run with different thresholds for different results of light or dark text recognition
    for threshold in (15, 30, 100, 200, 235):
        # if text is dark, it is nice like this
        text_original = pipeline(imagepath, False, clarify_threshold=threshold)
        # This sometimes fails, so we try the same on the inversion of the image
        text_inverted = pipeline(imagepath, True, clarify_threshold=threshold)
        if verbose:
            print("------\nThreshold: {}".format(threshold))
            print("Non-Inverted:\t{}\n---\nInverted:\t{}".format(text_original, text_inverted))
        original_texts.append(text_original)
        inverted_texts.append(text_inverted)
    return (original_texts, inverted_texts)

def pipeline(imagepath, invert:bool, clarify_threshold=100):
    global CLARIFIED_DIR, BORDERED_DIR, INVERTED_DIR, NOALPHA_DIR
    # determine filename
    fname_full = path.basename(imagepath)
    filename, file_extension = path.splitext(fname_full)
    postfix = 'inv' if invert else 'noninv'
    name = "{}_{}_{}{}".format(filename, clarify_threshold, postfix, file_extension)
    # remove transparency
    with Image.open(imagepath) as original_image:
        noalpha_image = remove_transparency(original_image)
        noalpha_path = path.join(NOALPHA_DIR, name)
        # if no extension was available, gifsupport figures it out and returns it.
        perhaps_additional_extension = gifsupport.try_save_catch(noalpha_image, noalpha_path)
        name = name + perhaps_additional_extension
        noalpha_path = noalpha_path + perhaps_additional_extension
    noalpha_image.close()
    # invert image?
    if invert:
        inverse = inv.invert(noalpha_path)
        inverted_path = path.join(INVERTED_DIR, name)
        gifsupport.try_save_catch(inverse, inverted_path)
        inverse.close()
    im_d_clarified = clarify.clarify(inverted_path if invert else noalpha_path, threshold=clarify_threshold)
    # image is now grayscale
    im_d_clarified_path = path.join(CLARIFIED_DIR, name)
    gifsupport.try_save_catch(im_d_clarified, im_d_clarified_path)
    im_d_clarified.close()
    im_d_bordered = addborder.addborder(im_d_clarified_path,
            immode='L', borderwidth=60)
    # safe the clarified and bordered image
    im_d_bordered_path = path.join(BORDERED_DIR, name)
    gifsupport.try_save_catch(im_d_bordered, im_d_bordered_path)
    im_d_bordered.close()
    # now try to find the text
    return ocr.ocr_core(im_d_bordered_path)

# https://stackoverflow.com/a/35859141/2550406
def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGB", im.size, bg_colour)
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im
