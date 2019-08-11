## PICC - Porn Image Collection Classifier

_Contains a GUI for quickly sorting your images manually_.

Performs text recognition to extract features of your images. Performs k-Means to extract color information from your images. Then trains a Random Forest on your training data and predicts a label for your new query data.

Accuracy is - depending on the dataset - only around 40%, but the `gui.py` makes it easier to sort than doing it purely manually. Also, the fact that there _is_ a prediction makes it more fun to do the manual correction.

Try it on your own files! It obviously works best on captioned images. For uncaptioned images, PICC can only use the dominant colors. If PICC does not work out for you, perhaps [this generic-image-classification program](https://github.com/xuetsing/image-classification-tensorflow) works better for you (Not Affiliated - I just tried it on my own data as well and had also around 40%. Perhaps I just need more data.)

### TRAINING

```bash
python run.py ./dirpath/to/images/of/label1 N:\dirpath\to\images\of\label2 ./data/label3
```


This will preprocess any images (JPG, GIF, PNG, ...) in the given directories.

* Store the words found in a shelf
* Store the dominant colors in a shelf

It will build a random forest on 80% of the data and compute a score based on the remaining 20%.

> Note: You can stop the program at any time during preprocessing without losing much progress.
> Learning will need to be restarted if aborted however.
> Either way, you can continue the process by running above command again.
> If preprocessing had finished last time, you can also directly run
>
> ```bash
> python -c "import run; run.learn()"
> ```
>



> Note: The stored preprocessing data is path-based. If you move your images to a different location, they are like new images to PICC

### QUERYING

    python queryui.py data/image/to/classify.jpg
This will output a human-readable prediction for the a given **single image**.



```bash
python organize.py  data/images_to_sort/
```

This will copy all images from the given **directory** to a directory called 'output', within a subdirectory with the label name.

### OTHER

    python -c "import learn; learn.run(use_random_forest=False, use_mlp=True)"

This will do the learning (requires preprocessing has been done!) using a multilayered perceptron instead of a random forest. You can modify the setup of the MLP by modifying learn.py.

### MANUAL CORRECTION

```bash
python gui.py
```
Reads all images from `output` and allows you to move them to `manual_output` with key presses. Green button is the recommendation of the classifier. Either click the button or press the associated key. To get the images into output, run `organize.py` first (see above).



If you want to use this to sort images independently of the training, place empty directories like this and dump all your images into one of them.

```
output/
  target1/
  target2/
  target3/
    mypic1.png
    mypic2.png
```

This way, the gui will work (and always mark target3 as prediction in green)


### REQUIREMENTS
​    [Tesseract](https://github.com/tesseract-ocr/tesseract/wiki) installed on the system. ([Link](https://github.com/UB-Mannheim/tesseract/wiki) for windows)
​    pytesseract
​    scikit-learn
​    numpy
​    pillow

    See requirements.txt for the output of `conda list -e > requirements.txt`  
    See environment.yml for use with `conda env create -f environment.yml`

Note that Tesseract needs installation outside of conda.