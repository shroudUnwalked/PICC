#!/usr/bin/env python3
# remove precomputed things. EVERYTHING. Just so we can debug from a clean state.
import os
import shutil

# purge() removes also preprocessing data! This takes time to recompute and it is usually not neccessary to get rid of
def purge():
    currdir = os.path.dirname(os.path.abspath(__file__))

    wipe_temp_data()
    wipe_persistent_data()

    try:
        shutil.rmtree(os.path.join(currdir, 'ocr', 'shelves'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

    try:
        shutil.rmtree(os.path.join(currdir, 'ambiente', 'shelves'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

# This is data that has to do with learning and training.
# it should be rather quick to reconstruct this data
# but i am unsure if you ever need to. I guess you need to if you change your dataset by removing data points from it.
def wipe_persistent_data():
    currdir = os.path.dirname(os.path.abspath(__file__))
    try:
        shutil.rmtree(os.path.join(currdir, 'shelves'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

def wipe_temp_data():
    currdir = os.path.dirname(os.path.abspath(__file__))
    try:
        shutil.rmtree(os.path.join(currdir, 'ocr', 'bordered'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

    try:
        shutil.rmtree(os.path.join(currdir, 'ocr', 'inverted'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

    try:
        shutil.rmtree(os.path.join(currdir, 'ocr', 'clarified'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

    try:
        shutil.rmtree(os.path.join(currdir, 'ocr', 'noalpha'))
    except OSError as e:
        print ("Wipe Error: %s - %s." % (e.filename, e.strerror))

if __name__ == "__main__":
    print("USAGE:")
    print("  python -c \"import wipe; wipe.wipe_temp_data()\"")
    print("  python -c \"import wipe; wipe.purge()\"")
