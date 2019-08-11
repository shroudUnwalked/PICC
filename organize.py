#!/usr/bin/env python3
# USAGE: python organize.py image_dir_path
import run
import sys
from os import path, makedirs
import os
import shutil
from defineLabels import TRAINING_LABELS_SHELVE
import shelve
from ocr.single import BadImageFileException

MY_PATH = path.abspath(path.dirname(__file__))
OUTPUT_DIR = path.join(MY_PATH, "output")
makedirs(OUTPUT_DIR, exist_ok=True)

def query_all_in_dir(dirpath, use_rf=True):
    setup_output_dirs()
    dpath = path.normpath(path.abspath(dirpath))
    files_in_dirpath = os.listdir(dpath)
    for filename in files_in_dirpath:
        fpath = path.join(dirpath, filename)
        if not file_in_any(filename):
            try:
                if use_rf:
                    label = run.query(fpath)
                else: # use MLP
                    run.query_mlp(fpath)
                targetpath = target_path(filename, label[0])
                if not path.exists(targetpath):
                    print("Label: {}\n".format(label))
                    shutil.copy(fpath, targetpath)
                else:
                    print("Path already exists:\n{}\n".format(targetpath))
            except BadImageFileException as bife:
                print("Not an image file. Not querying.")
        else:
            print("Skipping file because it was already assigned. Delete it in output if it was wrongly assigned.")

def setup_output_dirs():
    with shelve.open(TRAINING_LABELS_SHELVE) as sh:
        labels = set(sh.values())
    for label in labels:
        makedirs(path.join(OUTPUT_DIR, label), exist_ok=True)

def target_path(filename, label):
    return path.join(OUTPUT_DIR, label, filename)

def file_in_any(filename):
    for root, dirs, files in os.walk(OUTPUT_DIR):
        if filename in files:
            return True
    return False


if __name__ == "__main__":
    query_all_in_dir(sys.argv[1])
