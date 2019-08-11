#!/usr/bin/env python3
# This file is about collecting words into a bag

import sys
from os import path
from os import makedirs
import os
from . import single
import re
import shelve

# veryverbose = True means that verbosity is activated in other files as well
# verbose = True is limited to this file

MY_PATH = path.abspath(path.dirname(__file__))
SHELVE_DIR = path.join(MY_PATH, "shelves")
BUCKETSHELVE = path.join(SHELVE_DIR, "buckets.shelve")
makedirs(SHELVE_DIR, exist_ok=True)

def collect_list(imgpath, verbose=True, veryverbose=False):
    (noninverted_texts, inverted_texts) = single.run_with_gif_support(imgpath, veryverbose)
    all_words = []
    for s in noninverted_texts + inverted_texts:
        for w in s.split():
            all_words.append(w)
    if veryverbose:
        print("\nAll Words for {}:".format(path.basename(imgpath)))
        print(all_words)
    return all_words

def smart_collect(imgpath, verbose=True, veryverbose=False):
    all_words = collect_list(imgpath, verbose, veryverbose)
    # replace uncommon characters that are likely just lines with spaces
    spacy_words = [w for word in all_words for w in respaceify(word)]
    # remove words of a minimum length, including zero-length as returned by respaceify
    long_words = [w.upper() for w in spacy_words if len(w)>2]
    if veryverbose:
        print("Long Words:")
        print(list(long_words))
    wordcounts = exact_word_count(long_words)
    if verbose:
        print("Exact Words:")
        print(sorted(wordcounts, key=lambda x: x[1]))
    return wordcounts

def respaceify(word:str):
    # do not filter hashtags since I use them as meta character
    return re.split('[\\\:/;,%\.\s|¦"\[\]{}\*\$\?\)\(~]', word)

def exact_word_count(wordlist):
    if len(wordlist) == 0: return []
    sorted_words = sorted(wordlist)
    nex = sorted_words[0]
    counter = 1
    res = []
    for i in range(len(sorted_words)):
        if i+1 < len(sorted_words):
            cur = nex
            nex = sorted_words[i+1]
            if cur == nex:
                counter += 1
            else:
                res.append((cur, counter))
                counter = 1
    return res # list of (word, wordcount)

def build_bucket_for_single_image(imgpath, reuse=True, verbose=True, veryverbose=False):
    global BUCKETSHELVE
    if reuse:
        with shelve.open(BUCKETSHELVE) as bucketshelve:
            if str(imgpath) in bucketshelve.keys():
                print("Bucket already exists. (And that is good)")
                return # because we already have this

    # we do not want words in our bucket that are unlikely to exist
    wordcounts = smart_collect(imgpath, verbose=False, veryverbose=veryverbose)
    lesscounts = list(filter(lambda tup: tup is not None and tup[1]>1, wordcounts))
    if verbose:
        print("Words: ")
        print(sorted(lesscounts, key=lambda x: x[1]))
    # store bucket for this image
    bucketshelve = shelve.open(BUCKETSHELVE)
    # store sorted by word
    bucketshelve[str(imgpath)] = sorted(lesscounts, key=lambda x: x[0])
    bucketshelve.close()

if __name__ == "__main__":
    makedirs(SHELVE_DIR, exist_ok=True)
    build_bucket(sys.argv[1])
