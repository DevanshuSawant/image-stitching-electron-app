from time import sleep
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfile

import stitch_connect as stcu

def upload_file():
    f_types = [('Jpg Files', '*.jpg'), ('PNG Files', '*.png'), ('BMP Files', '*.bmp')]  
    filename = tk.filedialog.askopenfilenames(multiple=True, filetype=f_types)
    stcu.getStitchResult(filename)

upload_file()


print('done')