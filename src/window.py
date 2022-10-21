import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import fnmatch
import os
import numpy as np
from skimage.draw import polygon
import tkinter as tk

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
        self.newPath = None
        self.Image = Image.open(self.path)
        self.img = ImageTk.PhotoImage(self.Image)
        self.maskCreated = False
        self.mask = np.zeros((self.img.width(), self.img.height()))
        # Canvas Preloaded
        self.imgWidth = self.img.width()
        self.imgHeight = self.img.height()
        self.centerFrame = Frame(self.parent, width= self.img.width(), height= self.img.height())
        self.centerFrame.grid(row=1, sticky="ew")
        self.canvas= Canvas(self.centerFrame, width= self.img.width(), height= self.img.height())
        self.canvas.pack(fill="both", expand="yes")
        self.canvas.bind("<Motion>", self.obtainXY)
        self.canvas.bind("<B1-Motion>", self.printPoints)
        self.canvas.bind("<ButtonRelease-1>", self.connectShape)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img, anchor=NW)

        # Cavas Resizing Handler
        #self.canvas.bind("<MouseWheel>", self.zoom)
        #self.canvas.bind('<ButtonPress-3>', lambda event: self.canvas.scan_mark(event.x, event.y))
        #self.canvas.bind("<B3-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        #self.canvas.bind("<Configure>", self.onResize)
        #self.newHeight = self.canvas.winfo_reqheight()
        #self.newwidth = self.canvas.winfo_reqwidth()

        self.initialize_user_interface()

    def initialize_user_interface(self):
        self.topFrame = Frame(self.parent, width= self.img.width(), height= 300)
        self.topFrame.grid(row=0, column=0, sticky="")
        self.topFrameTitle = Label(
            self.topFrame, 
            text = f"Select ROI with mouse and press enter to save", 
            font=("Arial", 18))
        self.topFrameTitle.grid(row=0, column=0,pady=5,padx=2)

        # Bottom Frames
        self.btmFrame = Frame(self.parent, width= self.img.width(), height= 100)
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

        self.ImageText = Label(self.imagePaginateBtns, text = f"Image {self.imageNum} \
            out of {self.numberOfImages}")
        self.ImageText.grid(row=0, column=2)
        
        self.buttonReset = tk.Button(self.imagePaginateBtns,text="Submit", command=self.clickSubmitBtn)
        self.buttonReset.grid(row=0, column=5)

        self.rightMainFrame = Frame(self.parent, width= self.img.width(), height= self.img.height())
        self.rightMainFrame.grid(row=1, column=1, sticky="")
        self.rightBtmFrame = Frame(self.parent, width= self.img.width(), height= self.img.height())
        self.rightBtmFrame.grid(row=2, column=1, sticky="")
        self.visButtons = Frame(self.rightBtmFrame)

        self.visButtons.grid(column = 1,sticky="ew")
        self.visButtons.grid_columnconfigure(0, weight=1)

        self.showVisBtn = tk.Button(self.visButtons,text="Visualize", command=self.showVis)
        self.showVisBtn.grid(row=0, column=0)
        self.rightCanvas = Canvas(self.rightMainFrame, width= self.img.width(), height= self.img.height())

    
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

    def clickResetBtn(self):
        self.canvas.config(width = self.imgWidth, height= self.imgHeight)
        self.image = self.Image.resize((self.imgWidth, self.imgHeight))
        self.canvas.delete(self.canvasImg)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img2, anchor=NW)
        self.canvas.tag_lower(self.canvasImg)
    
    def clickSubmitBtn(self):
        for roi, arr in self.ROI.items():
            np.savetxt(f"{os.getcwd()}/src/tmp/rois/{roi}roi.csv", arr, delimiter=",")

    def makeVis(self):
        from skimage import io, measure
        import matplotlib.pyplot as plt
        
        tmpImages = f"{os.getcwd()}/src/tmp/images/"
        tmpROIs = f"{os.getcwd()}/src/tmp/rois/"
        mask = np.genfromtxt(f"{tmpROIs}/0roi.csv", delimiter=',')
        
        fluorescence_change = []

        for file in os.listdir(tmpImages):
            image = io.imread(f"{tmpImages}/{file}")
            props = measure.regionprops_table(
            mask.astype(np.uint8),
            intensity_image=image,
            properties=('label', 'area', 'intensity_mean')
            )
            fluorescence_change.append(props['label'] * props['intensity_mean'])

        fluorescence_change /= fluorescence_change[0]  # normalization
        fig, ax = plt.subplots()
        ax.plot(fluorescence_change)
        ax.grid()
        ax.set_title('Change in fluorescence intensity at ROI')
        ax.set_xlabel('Frames')
        ax.set_ylabel('Normalized total intensity')

        plt.savefig(rf"{os.getcwd()}/src/tmp/fig/1.png")

    def showVis(self):
        self.makeVis
        self.plt = Image.open(rf"{os.getcwd()}/src/tmp/fig/1.png")
        self.plot = ImageTk.PhotoImage(self.plt)

        self.canvasImg2 = self.rightCanvas.create_image(0, 0, image=self.plot, anchor=NE)
        self.canvas.tag_raise(self.canvasImg2)

    def imageUpdate(self):
        #self.image = self.Image.resize((int(self.newWidth), int(self.newHeight)))
        self.img2 = ImageTk.PhotoImage(self.Image)#.resize((int(self.newHeight), int(self.newHeight))))
        self.canvas.delete(self.canvasImg)
        self.canvasImg = self.canvas.create_image(0, 0, image=self.img2, anchor=NW)
        self.canvas.tag_lower(self.canvasImg)

    def imageNumUpdate(self):
        self.newPath = rf"C:\Users\Daniel\Desktop\Work\lab\tmp\images\{self.imageNum}.tif"
        self.imageUpdate()
        self.showMask()
        self.img2 = ImageTk.PhotoImage(self.Image) #.resize((self.canvas_width, self.canvas_height)))

        
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
                              width=1)
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

    def createMask(self):
        self.maskCreated = True
        self.showMask()
        self.imageUpdate()
        self.roiNum += 1
    
    def showMask(self):
        if self.newPath != None and self.newPath != self.path:
            self.Image = Image.open(self.newPath)
            print(self.newPath)
        else: self.Image = Image.open(self.path)
        
        if self.maskCreated:
            for x in self.ROI.values():
                poly = np.array(x).astype(int) # returns current roi coords
                array = np.zeros((self.img.width(), self.img.height()))
                 # create empty array
                rr, cc = polygon(poly[:,1], poly[:,0], array.shape) # fill array with polygon of roi
                array[rr,cc] = 50 # set value of polygon points
                Image1 = np.array(self.Image)
                merge = np.add(Image1,array)
                self.Image = Image.fromarray(merge)

numberOfImages = len(fnmatch.filter(os.listdir(f"{os.getcwd()}/src/tmp/images"), '*.*'))   

image = tk.Tk()
image.title("Image")
image.configure(background='grey')
image.wm_title("Image")
app = ImageWindow(image, numberOfImages)
image.mainloop()


image = ImageWindow(image, numberOfImages)

image.mainloop()