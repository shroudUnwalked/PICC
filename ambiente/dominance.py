#!/usr/bin/env python3

# original by charles leifer: https://charlesleifer.com/blog/using-python-and-k-means-to-find-the-dominant-colors-in-images/
from collections import namedtuple
from math import sqrt
import random
try:
    import Image
except ImportError:
    from PIL import Image
import shelve
from os import path
import os

MY_PATH = path.abspath(path.dirname(__file__))
DATA_SHELVE_DIR = path.join(MY_PATH, "shelves")
DOMINANT_COLORS_SHELVE = path.join(DATA_SHELVE_DIR, "dominant_colors.shelve") # for each imagepath, contains a list of int-encoded colors
os.makedirs(DATA_SHELVE_DIR, exist_ok=True)

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))

def colorz(filename, n=3):
    img = Image.open(filename)
    img.thumbnail((200, 200))

    # mainly needed for gifs
    rgb_img = img.convert('RGB')
    img = rgb_img

    w, h = img.size

    points = get_points(img)
    try:
        clusters = kmeans(points, n, 1)
    except ValueError as e:
        print("Encoundered ValueError in kmeans because there are not enough colors for making {} clusters.\nUsing only one cluster to be on the safe side...".format(n))
        clustersx = kmeans(points, k=1, min_diff=1)
        # use the clustersx n times
        clusters = clustersx * n
    rgbs = [map(int, c.center.coords) for c in clusters]
    return map(rtoh, rgbs)

def euclidean(p1, p2):
    return sqrt(sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))

def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)

def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while 1:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

def str_color_to_int(colo):
    if colo.startswith('#'):
        colo = colo[1:]
    i = int(colo, 16)
    if i >= 2**23:
        i -= 2**24
    return i

def int_to_color_str(int_colo):
    return '#%06x'%((int_colo+2**24)%2**24)

def extract_color_information(imagepath, num_colors=5, shelfpath=DOMINANT_COLORS_SHELVE, reuse=True, verbose=True):
    with shelve.open(shelfpath) as shelf:
        fpath = path.normpath(path.abspath(imagepath))
        if verbose:
            print("Extracting color info from {}".format(fpath))
        if reuse and fpath in shelf.keys():
            return # we already have the colors
        shelf[fpath] = list(map(str_color_to_int, colorz(imagepath, n=num_colors)))

def setup_for_all_dirs(training_dirs):
    for dirpath in training_dirs:
        files_in_dirpath = os.listdir(dirpath)
        for f in files_in_dirpath:
            try:
                extract_color_information(path.join(dirpath, f))
            except OSError:
                print("Cannot open {} for reading color values".format(f))
