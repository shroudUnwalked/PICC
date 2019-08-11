#!/usr/bin/env python3

from PIL import Image, GifImagePlugin
from tempfile import mkdtemp
from dataclasses import dataclass
from os import path

META_WORD_IS_A_GIF = "###THIS#FILE#IS#A#GIF###"

def gif_to_frames(gifpath, max_frames=5, verbose=False):
    with Image.open(gifpath) as img:
        if verbose:
            print("Animated: {}".format(img.is_animated))
            print("N_Frames: {}".format(img.n_frames))
            print("Type: {}".format(img.format))
        tmpdir = mkdtemp()
        gifinfo = GifInfo(tmpdir=tmpdir, frames = [])
        if img.n_frames <= max_frames:
            for i in range(img.n_frames):
                img.seek(i)
                savepath = path.normpath(path.join(tmpdir, '{}.png'.format(i)))
                try_save_catch(img, savepath)
                gifinfo.frames.append(savepath)
        else:
            for i in range(max_frames):
                img.seek(img.n_frames // max_frames * i)
                savepath = path.normpath(path.join(tmpdir, '{}.png'.format(i)))
                try_save_catch(img, savepath)
                gifinfo.frames.append(savepath)
        return gifinfo

def try_save_catch(img, savepath):
    try:
        img.save(savepath)
        return ""
    except (KeyError, ValueError):
        try:
            img.save(savepath+'.png')
            return ".png"
        except (KeyError, ValueError):
            try:
                img.save(savepath+'.jpg')
                return ".jpg"
            except (KeyError, ValueError):
                # final desperate attempt
                img.save(savepath+'.'+img.format)
                return '.'+img.format



@dataclass
class GifInfo:
    frames : list
    tmpdir : str = None
