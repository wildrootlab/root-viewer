import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import fnmatch
import os
class Window(tk.Frame):
    def __init__(self, parent, numberOfImages):
        self.parent = parent
        self.imageNum = 1
        self.numberOfImages = numberOfImages
        self.points = []
        # Image Label (pre-lodaed)
        self.path = rf"C:\Users\Daniel\Desktop\Work\lab\tmp\images\{self.imageNum}.tif"
        self.img = ImageTk.PhotoImage(Image.open(self.path))

         
        # Canvas Preloaded
        self.canvas= Canvas(self.parent, width= self.img.height(), height= self.img.height())
        self.canvas.pack(fill="both", expand="yes")
        self.canvas.bind("<Motion>", self.obtainXY)
        self.canvas.bind("<B1-Motion>", self.print_points)
        self.canvas.bind("<ButtonRelease-1>", self.connectShape)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img, anchor=NW)

        self.initialize_user_interface()

    def initialize_user_interface(self):
        self.parent.title("Images!")
        self.buttonNext = tk.Button(self.parent,text=">", command=self.clickNextButton)
        self.buttonBack = tk.Button(self.parent,text="<", command=self.clickBackButton)
        self.buttonNext.pack(side = "right")
        self.buttonBack.pack(side = "left")
        
        self.buttonNext = tk.Button(self.parent,text=">>", command=self.clickNextButton2)
        self.buttonBack = tk.Button(self.parent,text="<<", command=self.clickBackButton2)
        self.buttonNext.pack(side = "right")
        self.buttonBack.pack(side = "left")

        self.ImageText = Label(self.parent, text = f"Image {self.imageNum} out of {self.numberOfImages}")
        self.ImageText.pack(side='top')

    def clickNextButton(self):
        if self.imageNum < self.numberOfImages - 1:
            self.imageNum += 1
            self.imageUpdate()
        if self.imageNum >= self.numberOfImages - 1:
            self.imageNum = self.numberOfImages
            self.imageUpdate()

    def clickBackButton(self):
        if self.imageNum > 1:
            self.imageNum -= 1
            self.imageUpdate()
        if self.imageNum <= 1:
            self.imageNum = 1
            self.imageUpdate()

    def clickNextButton2(self):
        if self.imageNum < self.numberOfImages - 5:
            self.imageNum += 5
            self.imageUpdate()
        if self.imageNum >= self.numberOfImages - 5:
            self.imageNum = self.numberOfImages
            self.imageUpdate()
    
    def clickBackButton2(self):
        if self.imageNum > 5:
            self.imageNum -= 5
            self.imageUpdate()
        if self.imageNum <= 5:
            self.imageNum = 1
            self.imageUpdate()

    def imageUpdate(self):
        self.path = rf"C:\Users\Daniel\Desktop\Work\lab\tmp\images\{self.imageNum}.tif"
        print(self.imageNum, self.path)
        self.img2 = ImageTk.PhotoImage(Image.open(self.path))
        self.canvas.delete(self.canvasImg)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img2, anchor=NW)
        self.canvas.tag_lower(self.canvasImg)


        self.ImageText2 = f"Image {self.imageNum} out of {self.numberOfImages}"
        self.ImageText.configure(text=self.ImageText2)
        self.ImageText.text = self.ImageText2
    
    def obtainXY(self, event):
        self.previous_x, self.previous_y = event.x, event.y

    def print_points(self, event):
        # appends each point while button is pressed
        self.points.append([self.previous_x,self.previous_y])
        
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
                width=2)
        self.points = [] # reset points list
    
    class ResizingCanvas(Canvas):
        def __init__(self,parent,**kwargs):
            Canvas.__init__(self,parent,**kwargs)
            self.bind("<Configure>", self.on_resize)
            self.height = self.winfo_reqheight()
            self.width = self.winfo_reqwidth()

        def on_resize(self,event):
            # determine the ratio of old width/height to new width/height
            wscale = float(event.width)/self.width
            hscale = float(event.height)/self.height
            self.width = event.width
            self.height = event.height
            # resize the canvas 
            self.config(width=self.width, height=self.height)
            # rescale all the objects tagged with the "all" tag
            self.scale("all",0,0,wscale,hscale)
        

numberOfImages = len(fnmatch.filter(os.listdir(f"{os.getcwd()}/tmp/images"), '*.*'))   
root = tk.Tk()
root.title("Image")
root.configure(background='grey')
root.wm_title("Tkinter button")

app = Window(root, numberOfImages)
root.mainloop()