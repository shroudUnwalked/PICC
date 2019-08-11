#!/usr/bin/env python3
import defineLabels
import ambiente.dominance as dominance
import sys
import learn as l
import wipe as w

def prepare():
    # gather Word-Information for each image
    defineLabels.setup_labels(sys.argv[1:])

    # gather Color-Information for each image
    dominance.setup_for_all_dirs(sys.argv[1:])

def learn():
    l.run()

def query_mlp(impath):
    # alternative to query which uses Random Forest
    return l.query_impath(impath, classifier="mlp")

def query(impath):
    return l.query_impath(impath)

def query_ui(impath):    
    print("Result: {}".format(query(impath)))

if __name__ == "__main__":
    prepare()
    learn()
    w.wipe_temp_data()
