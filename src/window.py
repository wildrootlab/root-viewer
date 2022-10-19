import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import fnmatch
import os
import numpy as np
from skimage.draw import polygon
class ImageWindow(tk.Frame):
    def __init__(self, parent, numberOfImages):      
        self.parent = parent
        self.imageNum = 1
        self.numberOfImages = numberOfImages
        self.points = []
        self.ROI = {}
        self.roiNum = 0
        
        # Image Label (pre-lodaed)
        self.path = rf"C:\dev\2P-Analysis\src\tmp\images\{self.imageNum}.tif"
        self.Image = Image.open(self.path)
        self.img = ImageTk.PhotoImage(self.Image)
        self.maskCreated = False
        self.mask = np.zeros((self.img.width(), self.img.height()))
        # Canvas Preloaded
        self.centerFrame = Frame(self.parent, width= self.img.width(), height= self.img.height())
        self.centerFrame.grid(row=1, sticky="ew")
        self.canvas_width = 1000
        self.canvas_height = 1000
        self.canvas= Canvas(self.centerFrame, width= self.img.width(), height= self.img.height())
        self.canvas.pack(fill="both", expand="yes")
        self.canvas.bind("<Motion>", self.obtainXY)
        self.canvas.bind("<B1-Motion>", self.printPoints)
        self.canvas.bind("<ButtonRelease-1>", self.connectShape)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img, anchor=NW)
        
        # Cavas Resizing Handler
        #self.canvas.bind("<Configure>", self.onResize)
        self.height = self.canvas.winfo_reqheight()
        self.width = self.canvas.winfo_reqwidth()
        
        self.initialize_user_interface()

    def initialize_user_interface(self):
        self.topFrame = Frame(self.parent, width= self.img.height(), height= 300)
        self.topFrame.grid(row=0, column=0, sticky="")
        self.topFrameTitle = Label(self.topFrame, text = f"Select ROI with mouse and press enter to save",font=("Arial", 18))
        self.topFrameTitle.grid(row=0, column=0,pady=5,padx=2)

        # Bottom Frames
        self.btmFrame = Frame(self.parent, width= self.img.height(), height= 100)
        self.btmFrame.grid(row=2, column=0, sticky="")
        
        self.imagePaginateBtns = Frame(self.btmFrame)
        self.imagePaginateBtns.grid(sticky="ew")
        self.imagePaginateBtns.grid_columnconfigure(0, weight=1)

        # image pagination buttons and text
        self.buttonNext = tk.Button(self.imagePaginateBtns,text=">", command=self.clickNextButton)
        self.buttonBack = tk.Button(self.imagePaginateBtns,text="<", command=self.clickBackButton)
        self.buttonNext.grid(row=0, column=3)
        self.buttonBack.grid(row=0, column=1)
        
        self.buttonNext2 = tk.Button(self.imagePaginateBtns,text=">>", command=self.clickNextButton2)
        self.buttonBack2 = tk.Button(self.imagePaginateBtns,text="<<", command=self.clickBackButton2)
        self.buttonNext2.grid(row=0, column=4)
        self.buttonBack2.grid(row=0, column=0)

        self.ImageText = Label(self.imagePaginateBtns, text = f"Image {self.imageNum} out of {self.numberOfImages}")
        self.ImageText.grid(row=0, column=2)

    def clickNextButton(self):
        if self.imageNum < self.numberOfImages - 1:
            self.imageNum += 1
            self.imageNumUpdate()
        if self.imageNum >= self.numberOfImages - 1:
            self.imageNum = self.numberOfImages
            self.imageNumUpdate()

    def clickBackButton(self):
        if self.imageNum > 1:
            self.imageNum -= 1
            self.imageNumUpdate()
        if self.imageNum <= 1:
            self.imageNum = 1
            self.imageNumUpdate()

    def clickNextButton2(self):
        if self.imageNum < self.numberOfImages - 5:
            self.imageNum += 5
            self.imageNumUpdate()
        if self.imageNum >= self.numberOfImages - 5:
            self.imageNum = self.numberOfImages
            self.imageNumUpdate()
    
    def clickBackButton2(self):
        if self.imageNum > 5:
            self.imageNum -= 5
            self.imageNumUpdate()
        if self.imageNum <= 5:
            self.imageNum = 1
            self.imageNumUpdate()

    def imageUpdate(self):
        self.img2 = ImageTk.PhotoImage(self.Image)#.resize((self.canvas_width, self.canvas_height))
        self.canvas.delete(self.canvasImg)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img2, anchor=NW)
        self.canvas.tag_lower(self.canvasImg)

    def imageNumUpdate(self):
        self.path = rf"C:\Users\Daniel\Desktop\Work\lab\tmp\images\{self.imageNum}.tif"
        self.Image = self.showMask()
        self.img2 = ImageTk.PhotoImage(self.Image)#.resize((self.canvas_width, self.canvas_height)))

        
        self.canvas.delete(self.canvasImg)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img2, anchor=NW)
        self.canvas.tag_lower(self.canvasImg)

        self.ImageText2 = f"Image {self.imageNum} out of {self.numberOfImages}"
        self.ImageText.configure(text=self.ImageText2)
        self.ImageText.text = self.ImageText2

    def obtainXY(self, event):
        self.previous_x, self.previous_y = event.x, event.y

    def printPoints(self, event):
        # appends each point while button is pressed
        self.points.append((self.previous_x,self.previous_y))

        # creates line from each point pressed to the previous point
        self.canvas.create_line((self.previous_x, self.previous_y, event.x, event.y), 
                              fill='red', 
                              width=2)
        # updates point values
        self.previous_x, self.previous_y = event.x, event.y
    
    def connectShape(self, event):
        """ 
        if original point != a point in the current shape 
        connet last point w/ original
        """
        self.originalPoint = self.points[0]
        self.lastPoint = [event.x,event.y]
        
        if not self.originalPoint == self.lastPoint:
            self.canvas.create_line((
                self.originalPoint[0], self.originalPoint[1], 
                self.lastPoint[0], self.lastPoint[1]), 
                fill='red', 
                width=1)

        self.ROI[self.roiNum] = self.points
        self.points = [] # reset points list
        self.createMask()

    def onResize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.canvas_width = event.width
        self.canvas_height = event.height
        # resize the canvas 
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.tag_lower(self.canvasImg)
        # rescale all the objects tagged with the "all" tag
        self.imageUpdate()
        self.canvas.scale("all",0,0,wscale,hscale)
        print('resize',wscale)

    def createMask(self):
        self.maskCreated = True
        arr = self.ROI[self.roiNum]
        poly = np.array(arr).astype(int) # returns current roi coords
        self.array = np.zeros((self.img.width(), self.img.height()))
         # create empty array
        rr, cc = polygon(poly[:,1], poly[:,0], self.array.shape) # fill array with polygon of roi
        self.array[rr,cc] = 50 # set value of polygon points
        self.mask = np.add(self.array,self.mask)
        self.Image1 = np.array(self.Image)
        self.merge = np.add(self.Image1,self.mask)
        self.Image = Image.fromarray(self.merge)
        
        self.roiNum += 1 # increment ROI key
        self.imageUpdate()
    
    def showMask(self):
        self.path = rf"C:\Users\Daniel\Desktop\Work\lab\tmp\images\{self.imageNum}.tif"
        self.Image = Image.open(self.path)
        if self.maskCreated:
            self.Image1 = np.array(self.Image)
            self.merge = np.add(self.Image1,self.mask)
            self.Image = Image.fromarray(self.merge)
        return self.Image


numberOfImages = len(fnmatch.filter(os.listdir(f"{os.getcwd()}/src/tmp/images"), '*.*'))   

image = tk.Tk()
image.title("Image")
image.configure(background='grey')
image.wm_title("Image")
app = ImageWindow(image, numberOfImages)
image.mainloop()


image = ImageWindow(image, numberOfImages)

image.mainloop()