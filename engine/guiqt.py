from pathlib import Path
from tkinter import Label, Tk, Canvas, Entry, Text, Button, PhotoImage ,Menu ,filedialog ,Toplevel 
from tkinter.font import Font
from PIL import Image,ImageTk ,ImageGrab
import customtkinter 
from customtkinter import *
import cv2
import sys
import math
import upload_multiple as um
import numpy as np
import tkinter as tk
myroot=customtkinter.CTk()
myroot.title('Image Stitching App')
myroot.geometry("800x600")
# DEFINE FONT
my_font = customtkinter.CTkFont(family="Montserrat", size=42)
# def resize_button(self, event):
#         # Get the height of the screen
#         screen_height = self.winfo_screenheight()

#         # Set the width of the button to be half the height of the screen
#         self.my_button.config(width=screen_height // 2)
add_button_image1=ImageTk.PhotoImage(Image.open("C:/College work/Electron GUI/engine/assets1/frame0/button_1.png"))
add_button_image2=ImageTk.PhotoImage(Image.open("C:/College work/Electron GUI/engine/assets1/frame0/button_2.png"))
add_button_image3=ImageTk.PhotoImage(Image.open("C:/College work/Electron GUI/engine/assets1/frame0/button_3.png"))

##create button
frame = customtkinter.CTkFrame(master=myroot)
frame.pack(fill="both", expand=True)

# frame.bind("<Configure>",command=resize_button)
add_image = ImageTk.PhotoImage(Image.open("engine/assets1/frame0/image_2.png").resize((90,50)))
label = Label(frame, image= add_image)
label.pack(pady=30, padx=10)

label = customtkinter.CTkLabel(master=frame,text="Image Stitching Tool",font=my_font)
label.pack(pady=12, padx=10)

class App:
        def __init__(self, master):
            self.master = master
            self.master.title("Image Viewer")
            self.master.geometry("800x600")

            self.images = []
            self.image_labels = []
            self.dragging = None
            self.drag_start = None
            self.zoom_scale=1.0

            self.canvas = tk.Canvas(self.master)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.bind("<Button-1>", self.on_drag_start)
            self.canvas.bind("<B1-Motion>", self.on_drag_motion)
            self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)
            self.canvas.bind("<MouseWheel>", self.on_zoom)

            menu = Menu(self.master)
            self.master.config(menu=menu)
            file_menu = Menu(menu)
            menu.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Open", command=self.open_images)
            file_menu.add_command(label="SAVE",command=self.save_canvas)
            file_menu.add_command(label="CLEAR ALL",command=self.clear_all)


        def clear_all(self):
            self.images = []
            self.image_labels = []
            self.canvas.delete("all")

        def open_images(self):
            filenames = filedialog.askopenfilenames(filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")))
            for filename in filenames:
                image = cv2.imread(filename)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.images.append(Image.fromarray(image))
                self.image_labels.append(None)
            self.show_images()

        def show_images(self):
            self.canvas.delete("all")
            for i, image in enumerate(self.images):
                width, height = image.size
                aspect_ratio = width / height
                max_width = self.canvas.winfo_width() / len(self.images)
                max_height = self.canvas.winfo_height()
                if aspect_ratio > 1:
                    width = min(max_width, width)
                    height = width / aspect_ratio
                else:
                    height = min(max_height, height)
                    width = height * aspect_ratio
                image = image.resize((int(width), int(height)), Image.LANCZOS)
                self.image_labels[i] = ImageTk.PhotoImage(image)
                x = i * (self.canvas.winfo_width() / len(self.images))
                y = (self.canvas.winfo_height() - height) / 2
                self.canvas.create_image(x, y, image=self.image_labels[i])
                self.original_width = self.canvas.winfo_width()
                self.original_height = self.canvas.winfo_height()

        def on_drag_start(self, event):
            item = self.canvas.find_closest(event.x, event.y)
            if item:
                x0, y0, x1, y1 = self.canvas.bbox(item)
                if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                    self.dragging = item[0]
                    self.drag_start = (event.x, event.y)

        def on_drag_motion(self, event):
                if self.dragging:
                    dx = event.x - self.drag_start[0]
                    dy = event.y - self.drag_start[1]
                    self.canvas.move(self.dragging, dx, dy)
                    self.drag_start = (event.x, event.y)

        def on_drag_release(self, event):
                self.dragging = None
            
            
        def on_mousewheel(self, event):
                if event.delta > 0:
                    # Zoom in
                    self.canvas.scale("all", event.x, event.y, 1.2, 1.2)
                elif event.delta < 0:
                    # Zoom out- q2AW3
                    self.canvas.scale("all", event.x, event.y, 0.8, 0.8)

        def on_zoom(self, event):
                if event.delta > 0:
            # Zoom in
                    self.zoom_scale *= 1.1
                elif event.delta < 0:
            # Zoom out
                    self.zoom_scale /= 1.1
        # Clamp the zoom scale to reasonable values
                self.zoom_scale = max(0.1, min(10, self.zoom_scale))
        #   Update the canvas size
                self.canvas.config(width=math.ceil(self.original_width * self.zoom_scale), 
                height=math.ceil(self.original_height * self.zoom_scale))
    
        def run_app():
            myroot.withdraw()
            root = tk.Toplevel()
            app = App(root)
            root.mainloop()
        def go_back():
             myroot.iconify()

        def save_canvas(self):
            filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if filename:
                x0 = self.canvas.winfo_rootx()
                y0 = self.canvas.winfo_rooty()
                x1 = x0 + self.canvas.winfo_width()
                y1 = y0 + self.canvas.winfo_height()
                ImageGrab.grab().crop((x0, y0, x1, y1)).save(filename)
screenWidth = myroot.winfo_screenwidth()
screenHeight = myroot.winfo_screenheight()

button_1 = customtkinter.CTkButton(master=frame,fg_color="#312F49",text="Stitch Images with overlapping sections",command=um.uploadWindow,corner_radius=10,width= 400,height=200)
# button_1.width =(screenWidth/10)
button_2 = customtkinter.CTkButton(master=frame,fg_color="#312F49",text="Stitch Images Manually ",command=App.run_app,corner_radius=10,width= 400,height=200)
# button_2.width =(screenWidth/120)
# button_3 = customtkinter.CTkButton(master=frame,fg_color="#312F49",text=" Stitch Images with Non-overlapping sections",corner_radius=10,width= 400,height=200)
# # button_3.width =(screenWidth/12)

button_1.pack(padx=10,pady=10)
button_2.pack(padx=10,pady=10)
# button_3.pack(padx=10,pady=10)


myroot.mainloop()