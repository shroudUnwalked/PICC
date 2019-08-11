#!/usr/bin/env python3
# This file helps you set up the directory structure and performs OCR.
# it also splits the incoming data in to a training_set and a testing_set. Only the training set is used for building the bag of words - even if there are no measures for how accurate the guesses are currently.

# USAGE: python defineLabels.py label1dir label2dir thedir/label3subdir
import sys
import shelve
from ocr import krampus 
from os import path
from os import makedirs
from ocr.single import BadImageFileException
import os
import random
import wipe

MY_PATH = path.abspath(path.dirname(__file__))
DATA_SHELVE_DIR = path.join(MY_PATH, "shelves")
LABELDIRS_SHELVE = path.join(DATA_SHELVE_DIR, "labeldirs.shelve") # list all directories aka labels
TRAINING_LABELS_SHELVE = path.join(DATA_SHELVE_DIR, "traininglabels.shelve") # maps file pathes to labels. Is used in learn.py as training data.
TESTING_LABELS_SHELVE = path.join(DATA_SHELVE_DIR, "testinglabels.shelve") # lists the files in the test set and their labels
WORDBAG_SHELVE = path.join(DATA_SHELVE_DIR, "wordbag.shelve") # contains the bag of all words from the training set
WORDBAG_PER_LABEL_DIR = path.join(DATA_SHELVE_DIR, "per_label_bags") # contains a shelf for each label which is the bag
LABELCOUNT_SHELVE = path.join(DATA_SHELVE_DIR, "labelcount.shelve") # contains a number of images per label
makedirs(DATA_SHELVE_DIR, exist_ok=True)
makedirs(WORDBAG_PER_LABEL_DIR, exist_ok=True)

WORDBAG_LABELS_SHELVE_NAMES = []

def setup_labels(training_dirs):
    with shelve.open(LABELDIRS_SHELVE) as shelf:
        shelf["training_dirs"] = map(path.normpath, training_dirs)
    # build bag of words
    build_word_buckets_for_training()
    # merge the words from each training label into a bag
    merge_word_buckets_for_labels_from_training()
    # merge the words from the training set into one big bag
    merge_word_buckets_from_training()
    print("\nMerged Word Bag from Training Set:")
    print(sort_word_bag_desc())

# should_wipe_sometimes indicates that the temporary image files should not remain there forever
def build_word_buckets_for_training(training_ratio=0.8, should_wipe_sometimes=True):
    random.seed()
    filenum=0
    with shelve.open(LABELDIRS_SHELVE) as shelf_training_dirs:
        with shelve.open(TRAINING_LABELS_SHELVE) as shelf_train:
            with shelve.open(TESTING_LABELS_SHELVE) as shelf_test:
                # remove old content of these shelves so that the test set is not accidentally also in the training set
                shelf_test.clear()
                shelf_train.clear()

                # build bucket for each image and store in respective shelf
                for dirpath in shelf_training_dirs["training_dirs"]:
                    files_in_dirpath = os.listdir(dirpath)
                    totalnum = len(files_in_dirpath)
                    for counter_files, f in enumerate(files_in_dirpath):
                        filenum+=1
                        # wipe tempdata sometimes
                        if should_wipe_sometimes and (counter_files % 100 == 0):
                            wipe.wipe_temp_data()
                        # random decision based on training_ratio
                        r = random.randint(0, 100)
                        if r > 100*training_ratio:
                            # this is test data
                            shelf = shelf_test
                        else:
                            #this is training data
                            shelf = shelf_train
                        try:
                            fpath = path.join(dirpath, f)
                            print("Building word bucket for {}".format(fpath))
                            krampus.build_bucket_for_single_image(fpath)
                            # for filepath store label
                            label = dir_to_label(dirpath)
                            shelf[fpath]=label
                            print("[{}] [{} of {} in {}]\tHandled file {}\n".format(filenum, counter_files, totalnum, label, fpath))
                        except BadImageFileException as e:
                            print("Ex: {}".format(e))
                            continue
    if should_wipe_sometimes:
        wipe.wipe_temp_data()

def merge_word_buckets_from_training():
    """This would likely be faster if done from the already merged label buckets instead of every image all over again."""
    # abort by deleting the source images. That will only keep the ones that are already processed.
    with shelve.open(TRAINING_LABELS_SHELVE) as training_shelf:
        with shelve.open(krampus.BUCKETSHELVE) as bucket_shelf:
            with shelve.open(WORDBAG_SHELVE) as bag:
                # training_shelf maps imagepaths to labels
                # bucket_shelf maps imagepaths to lists of (str, int) tuples that represent words and their number of occurrences per that image
                loopcnt = 0
                for impath in training_shelf.keys():
                    imbucket = bucket_shelf[impath]
                    loopcnt = loopcnt + 1 if loopcnt < 100 else 0
                    for (word, occurrences) in imbucket:
                        try:
                            prev_occ = bag[word]
                        except Exception:
                            # word has not yet been written
                            prev_occ = 0
                        bag[word] = prev_occ + occurrences
                    # bag for 100 images should guesstimately fit into ram
                    if loopcnt == 100:
                        bag.sync()

def merge_word_buckets_for_labels_from_training():
    global WORDBAG_LABELS_SHELVE_NAMES
    # training_shelf maps imagepaths to labels
    with shelve.open(TRAINING_LABELS_SHELVE) as training_shelf:
        # bucket_shelf maps imagepaths to lists of (str, int) tuples that represent words and their number of occurrences per that image
        with shelve.open(krampus.BUCKETSHELVE) as bucket_shelf:
            opened_label_shelves = {}
            loopcnt = 0
            for impath in training_shelf.keys():
                imlabel = training_shelf[impath]
                if imlabel in opened_label_shelves.keys():
                    label_shelf = opened_label_shelves[imlabel]
                else:
                    # create a wordbag shelf for the label
                    WORDBAG_FOR_LABEL = wbfl(imlabel) # contains the bag of all words from the training set
                    label_shelf = shelve.open(WORDBAG_FOR_LABEL)
                    opened_label_shelves[imlabel]=label_shelf
                # now the shelf for this label is opened in label_shelf
                imbucket = bucket_shelf[impath] # words of current image
                loopcnt = loopcnt + 1 if loopcnt < 100 else 0 # sync every 100 images so that it fits into ram
                for (word, occurrences) in imbucket:
                    try:
                        prev_occ = label_shelf[word]
                    except Exception:
                        # word has not yet been written, ever
                        prev_occ = 0
                    label_shelf[word] = prev_occ + occurrences

                # count the images per label
                with shelve.open(LABELCOUNT_SHELVE) as lbcnt_shelf:
                    try:
                        lbcnt_shelf[imlabel] += 1
                    except KeyError:
                        lbcnt_shelf[imlabel] = 1

                # every 100 images, clean ram again
                if loopcnt == 100:
                    label_shelf.sync()
            # close all label-specific shelves again
            map(lambda s: s.close(), opened_label_shelves.values())
            # save the shelve names
            WORDBAG_LABELS_SHELVE_NAMES = opened_label_shelves.keys()

def sort_word_bag_desc():
    with shelve.open(WORDBAG_SHELVE) as bag:
        z = zip(bag.keys(), bag.values())
        return sorted(z, key=lambda x:x[1], reverse=True)

def wbfl(imlabel):
    return path.join(WORDBAG_PER_LABEL_DIR, "wordbag_for_label_{}.shelve".format(imlabel)) # contains the bag of all words from the training set

def dir_to_label(dirname):
    return path.basename(dirname)


if __name__ == "__main__":
    setup_labels(sys.argv[1:])
