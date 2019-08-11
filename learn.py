#!/usr/bin/env python3
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

from defineLabels import TRAINING_LABELS_SHELVE, TESTING_LABELS_SHELVE, WORDBAG_SHELVE
from defineLabels import DATA_SHELVE_DIR
import defineLabels as dfl

from ocr.krampus import BUCKETSHELVE # imagepath to bucket
import ocr.krampus as krampus

import numpy as np
import shelve

from os import path, makedirs

import datetime

import ambiente.dominance as dominance
from ambiente.dominance import DOMINANT_COLORS_SHELVE

TRAINED_CLASSIFIERS_SHELVE = path.join(DATA_SHELVE_DIR, "classifiers.shelve") # store trained classifiers
RANDOM_FOREST_KEY = "random-forest"
MLP_KEY = "mlp"
DATE_KEY_PREFIX = "date--"

# make sure bucketshelve is open already
def encode_wordbag(bucketshelve, line_path):
    line_as_list_of_tuples = bucketshelve[line_path]
    line_as_dict = dict(line_as_list_of_tuples)
    with shelve.open(WORDBAG_SHELVE) as bag_of_all:
        # order irrelevant as long as it is always the same... but that means we better order it
        # if a word has no count, the count is 0
        line_dict = {k:line_as_dict.get(k, 0) for k in bag_of_all.keys()}
        ##print("BAG OF ALL KEYS: \n{}".format(list(bag_of_all.keys())))
        line_encoded = np.empty((len(bag_of_all.keys()),))
        for (counter, (ke, va)) in enumerate(sorted(line_dict.items(), key=lambda tup:tup[0])):
            line_encoded[counter] = va
    return line_encoded
    # line_encoded is a numpy array of the values. they are ordered by the keys.

def encode_ambiente(line_path):
    with shelve.open(DOMINANT_COLORS_SHELVE) as shelf:
        yoghurt = shelf.get(path.normpath(path.abspath(line_path)), None)
        return np.array(yoghurt) if yoghurt is not None else None

# technically, MLP could be removed in favor for random forest.
def run(reuse=False, store_classifier=True, use_mlp=False, use_random_forest=True):
    # check whether training data is even needed
    need_training_data_anew = False
    recreated_MLP = False
    recreated_RF = False
    with shelve.open(TRAINED_CLASSIFIERS_SHELVE) as tcshelf:
        if reuse and use_mlp:
            try:
                clf = tcshelf[MLP_KEY]
                clf_date = tcshelf[DATE_KEY_PREFIX + MLP_KEY]
                print("Reusing trained MLP Classifier from {}".format(clf_date))
            except KeyError:
                reuse = False # load as if not reusing because it does not exist
        if use_mlp and not reuse:
            print("Creating untrained MLP Classifier")
            need_training_data_anew = True
            recreated_MLP = True
            clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(1000,), max_iter=200)
        if reuse and use_random_forest:
            try:
                rf = tcshelf[RANDOM_FOREST_KEY]
                rf_date = tcshelf[DATE_KEY_PREFIX + RANDOM_FOREST_KEY]
                print("Reusing trained Random Forest Classifier from {}".format(rf_date))
            except KeyError:
                reuse = False
        if use_random_forest and not reuse:
            print("Creating untrained Random Forest Classifier")
            need_training_data_anew = True
            recreated_RF = True
            rf = RandomForestClassifier(n_estimators=400)


    with shelve.open(WORDBAG_SHELVE) as bag_of_all:
        num_words_per_bag = len(bag_of_all.keys())

    with shelve.open(DOMINANT_COLORS_SHELVE) as coloshelf:
        num_colors_per_image = len(next(iter(coloshelf.values()),0))
        # assuming that all images have the same color count.

    num_features = num_words_per_bag + num_colors_per_image

    # get training data
    _warn_cnt_one = 0
    if need_training_data_anew:
        with shelve.open(BUCKETSHELVE) as bucketshelve:
            with shelve.open(TRAINING_LABELS_SHELVE) as train_path_label_shelf:
                num_entries = len(train_path_label_shelf.keys())
                X_train = np.empty((num_entries, num_features)).astype('double')
                y_train = np.empty((num_entries,)).astype(str)
                for i, line in enumerate(train_path_label_shelf.items()):
                    (line_path, line_y) = line
                    line_bucket_words = encode_wordbag(bucketshelve, line_path)
                    line_bucket_colors = encode_ambiente(line_path)
                    if line_bucket_colors is None:
                        # color information is missing. recompute it.
                        dominance.extract_color_information(line_path)
                        line_bucket_colors = encode_ambiente(line_path)
                        if line_bucket_colors is None:
                            print("WARN: could not compute colors for {}".format(line_path))
                            _warn_cnt_one += 1

                    line_bucket = np.concatenate([line_bucket_words, line_bucket_colors], axis=0)
                    print("Learning Training-line: {}".format(line))
                    print("There are {} features".format(num_features))
                    print("There were {} warnings regarding missing color info.".format(_warn_cnt_one))
                    #with np.printoptions(threshold=np.inf):
                    #    print(line_bucket)
                    print("")
                    X_train[i,:] = line_bucket
                    y_train[i] = line_y

    # get testing data
    with shelve.open(BUCKETSHELVE) as bucketshelve:
        with shelve.open(TESTING_LABELS_SHELVE) as testing_path_label_shelf:
            num_entries = len(testing_path_label_shelf.keys())
            X_test = np.empty((num_entries, num_features)).astype('double')
            y_test = np.empty((num_entries,)).astype(str)
            for i, line in enumerate(testing_path_label_shelf.items()):
                line_path, line_y = line
                line_bucket_words = encode_wordbag(bucketshelve, line_path)
                line_bucket_colors = encode_ambiente(line_path)
                if line_bucket_colors is None:
                    # color information is missing. recompute it.
                    dominance.extract_color_information(line_path)
                    line_bucket_colors = encode_ambiente(line_path)
                line_bucket = np.concatenate([line_bucket_words, line_bucket_colors], axis=0)
                X_test[i,:] = line_bucket
                y_test[i] = line_y

    # Now the data for each image consists of a row of features.
    # First are all the words as numbers of occurrences
    # then are n=5 (unless changed in dominance.py) numbers that correspond to colors and can be turned back

    use_training_data_for_testing = False
    if use_training_data_for_testing:
        print("WARNING: TESTING DATA IS THE SAME AS TRAINING DATA")
        X_test = X_train
        y_test = y_train


    # MLP Classifier
    if use_mlp:
        if recreated_MLP:
            clf.fit(X_train, y_train)
        mlp_score = clf.score(X_test, y_test)
        # store trained classifier
        if store_classifier:
            with shelve.open(TRAINED_CLASSIFIERS_SHELVE) as trained_shelf:
                trained_shelf[MLP_KEY] = clf
                trained_shelf[DATE_KEY_PREFIX + MLP_KEY] = datetime.datetime.now()

        print("\nMLP Score: {}".format(mlp_score))

    # Random Forest
    if use_random_forest:
        if recreated_RF:
            rf.fit(X_train, y_train)
        # Feature importances
        print("\n--- Feature importances ---")
        feat_imps = sorted(enumerate(rf.feature_importances_), key=lambda tup:tup[1], reverse=True)
        with shelve.open(WORDBAG_SHELVE) as bag_of_all:
            keys = sorted(bag_of_all.keys(), key=lambda tup:tup[0])
            keys.extend(['color{}'.format(i) for i in range(num_colors_per_image)])
            for (count, (num, imp)) in enumerate(feat_imps):
                key = keys[num]
                print("Feature: {}\t\t\tImportance:{}".format(key, imp))
                if count > 100:
                    break

        # store trained classifier
        if store_classifier:
            with shelve.open(TRAINED_CLASSIFIERS_SHELVE) as trained_shelf:
                trained_shelf[RANDOM_FOREST_KEY] = rf
                trained_shelf[DATE_KEY_PREFIX + RANDOM_FOREST_KEY] = datetime.datetime.now()
        print("\nRandom Forest Score: {}".format(rf.score(X_test, y_test)))


# expects a wordbag in 2d, of one or more samples
def query_rf(encoded_data):
    with shelve.open(TRAINED_CLASSIFIERS_SHELVE) as tcshelf:
        rf = tcshelf[RANDOM_FOREST_KEY]
        rf_date = tcshelf[DATE_KEY_PREFIX + RANDOM_FOREST_KEY]
        print("Querying trained Random Forest Classifier from {}".format(rf_date))
    return rf.predict(encoded_data)

def query_mlp(encoded_data):
    with shelve.open(TRAINED_CLASSIFIERS_SHELVE) as tcshelf:
        mlp = tcshelf[MLP_KEY]
        mlp_date = tcshelf[DATE_KEY_PREFIX + MLP_KEY]
        print("Querying trained MLP Classifier from{}".format(mlp_date))
    return mlp.predict(encoded_data)

# call this to query
def query_impath(impath, classifier="rf"):
    npath = path.normpath(impath)
    # build words
    krampus.build_bucket_for_single_image(npath, reuse=True)
    with shelve.open(BUCKETSHELVE) as bucketshelve:
        en_wordbag = encode_wordbag(bucketshelve, npath)
    # build dominant colors
    dominance.extract_color_information(impath, reuse=True)
    with shelve.open(DOMINANT_COLORS_SHELVE) as colorshelf:
        color_np_arr = encode_ambiente(npath)
    # combine the information
    en_wordbag_and_color = np.concatenate([en_wordbag, color_np_arr], axis=0)
    if classifier == "rf":
        return query_rf(en_wordbag_and_color.reshape((1,-1)))
    elif classifier == "mlp":
        return query_mlp(en_wordbag_and_color.reshape((1,-1)))
    else:
        raise NotImplementedError("Classifier querying not implemented yet!")
