import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk

import stitch_connect as stcu

def uploadWindow():

    my_w = tk.Tk()
    my_w.geometry("500x500")  # Size of the window 
    my_font1 = ('times', 18, 'bold')

    l1 = tk.Label(my_w, text='Upload Files & display', width=35, font=my_font1)
    l1.grid(row=1, column=1, columnspan=4)

    b1 = tk.Button(my_w, text='Upload Files', width=20, command=lambda: upload_file())
    b1.grid(row=2, column=1, columnspan=4)

    my_w.mainloop()
    

def upload_file():
    f_types = [('Jpg Files', '*.jpg'), ('PNG Files', '*.png'), ('BMP Files', '*.bmp')]  
    filename = tk.filedialog.askopenfilename(multiple=True, filetypes=f_types)
    stcu.getStitchResult(filename)

upload_file()


