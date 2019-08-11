#!/usr/bin/env python3
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from tkinter import PhotoImage
import os
import shutil

MY_PATH = os.path.abspath(os.path.dirname(__file__))
COPY_TO_DIR = os.path.join(MY_PATH, "manual_output")


class Class1(Frame):

    def __init__(self, master, labels, keys):
        Frame.__init__(self, master)
        self.grid()

        self.master = master        
        self.LABELS = labels
        self.imsources = self.next_if_available() # create generator
        self.question1_UI(num_buttons=len(labels), labels=labels, keys=keys)
    
    def question1_UI(self, num_buttons, labels, keys):
        NUM_ROWS = 4
        self.master.title("GUI")
        
        impath = 'Picture.png'
        self.current_image_path = impath
        with Image.open(impath) as im:
            im.thumbnail((800,800), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(im)

        self.label1 = Label(self, image=img)
        self.label1.image = img
        self.label1.grid(row = 0, column = 0, rowspan = NUM_ROWS, sticky=NW)
        IMG_WIDTH_IN_COLS = 1

        self.buttons = []
        for i in range(num_buttons):
            button_lbl = labels[i]
            button_key = keys[i]

            def btn_cli(val=i, label=button_lbl):
                return self.button_clicked(val, label)

            new_button = Button(self, bg='white', text='{} : {}'.format(button_lbl, button_key), font=('MS', 8, 'bold'), 
                    command = btn_cli)

            def btn_cli_ev(event, val=i, label=button_lbl):
                return self.button_clicked(val, label)

            self.bind(button_key, btn_cli_ev)
            r = i % NUM_ROWS
            # row + NUM_ROWS*col = num buttons including the current one
            c = int( (i - r)/NUM_ROWS ) + IMG_WIDTH_IN_COLS
            new_button.grid(row = r, column = c, sticky = S)
            self.buttons.append(new_button)


        # actually start
        try:
            (impath, prediction) = next(self.imsources)
            self.next_image(impath, prediction, self.LABELS)
        except StopIteration as s:
            self.finished()

    def change_image(self, impath):
        with Image.open(impath) as im:
            im.thumbnail((800,800), Image.ANTIALIAS)
            self.label1.image = ImageTk.PhotoImage(im)
            self.label1.configure(image=self.label1.image)
            self.current_image_path = impath
    
    def button_clicked(self, button_id, button_label):
        button = self.buttons[button_id]
        button.configure(bg='blue')
        copy_image_to_actual_output_dir(self.current_image_path, button_label)
        button.configure(bg='white')
        try:
            (impath, prediction) = next(self.imsources)
            self.next_image(impath, prediction, self.LABELS)
        except StopIteration as s:
            self.finished()

    def finished(self):
        for button in self.buttons:
            button.configure(bg='red')

    def next_image(self, imagepath, prediction, all_labels):
        for button in self.buttons:
            button.configure(bg='white')

        # highlight predicted label
        try:
            index = all_labels.index(prediction)
            button_pred = self.buttons[index]
            button_pred.configure(bg='green')
        except ValueError:
            print("prediction button not found for image {}".format(imagepath))
            index = None

        # set current image
        self.change_image(imagepath)

    def next_if_available(self):
        # returns imagepath and predicted label as tuple
        for root, dirs, files in os.walk('output'):
            for f in files:
                yield (os.path.join(root, f), os.path.basename(root))



def main():
    LABELS = get_labels_from_output()
    setup_outdir(LABELS)
    KEYS = get_keys(len(LABELS))
    
    root = Tk()
    ex = Class1(root, labels=LABELS, keys=KEYS)
    ex.focus_set()
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),
    root.winfo_screenheight()))         
    #root.attributes("-fullscreen", True)
    root.mainloop()  

def get_labels_from_output(outputdir='output'):
    l = os.listdir(outputdir)
    return l

def get_keys(n):
    a = ['a', 's', 'd', 'f', 'c', 'e', 'g', 'v', 'r', 'w', 'j', 'l']
    return a[:n]

def setup_outdir(labels):
    for l in labels:
        os.makedirs(os.path.join(COPY_TO_DIR, l), exist_ok=True)

def copy_image_to_actual_output_dir(current_file, label):
    shutil.move(current_file, os.path.join(COPY_TO_DIR, label))

if __name__ == '__main__':
    main()  
