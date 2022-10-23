from matplotlib.widgets import Lasso, Button
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection
from matplotlib import path
import os
import fnmatch
import sys
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import rand
from matplotlib import image as mpimg
from PIL import Image

def imageSizeCheck():
    try:
        heightl = []
        widthl = []
        
        for image in os.listdir(f"{os.getcwd()}/src/tmp/images/"):
            im = Image.open(f"{os.getcwd()}/src/tmp/images/{image}")
            imW, imH = im.size
            widthl.append(imW)
            heightl.append(imH)
        widthl = np.array(widthl)
        heightl = np.array(heightl)
        w = np.all(widthl == widthl[0])
        h = np.all(heightl == heightl[0])
        total = (widthl==heightl).all()

        if w == False or h == False:
           raise Exception(f"Images are not a consistent size.\nWidths Consistent? {w}\nHeights Consistent? {h}")
        if total == False:
            raise Exception(f"Images are not square.\nWidth = {widthl[0]}\nHeight = {heightl[0]}")
        
        elif w == True and h == True and total == True:
            im = Image.open(f"{os.getcwd()}/src/tmp/images/1.tif")
            width, height = im.size
            return True, width, height

    except Exception as e:
        print(f"Image size error:\n {e}")

def selectROI(width, height):
    print("""
        Use your left and right ARROW KEYS to cycle through images.
        Draw a circle around the desired ROI - you'll see it apear in the right plot as a mask.
        Once you have finalized the ROI press ENTER to save and Exit the program.
    """)

    image = 1
    numberOfImages = len(fnmatch.filter(os.listdir(f"{os.getcwd()}/src/tmp/images"), '*.*'))

    cwd = os.getcwd()
    fig, ax = plt.subplots()
    LassoManager(fig, ax, cwd, image, numberOfImages, width, height)
    plt.show()
    return
class LassoManager(object):
    def __init__(self, fig, ax, cwd, image, numberOfImages, width, height):
        self.ax1 = ax
        self.fig = fig
        self.cwd = cwd
        self.canvas = fig.canvas
        self.numberOfImages = numberOfImages
        self.image = image

        self.array = np.zeros((width,height))

        self.fig.suptitle("Select ROI in left plot and press Enter to save")

        
        self.ax1.plot()
        self.ax1.set_xlim([0, width])
        self.ax1.set_ylim([0, height])
        self.ax1.set_aspect('equal')

        self.im = self.ax1.imshow(mpimg.imread(f"{cwd}/src/tmp/images/{image}.tif"), extent=[0, width, 0, height])
        self.msk = self.ax1.imshow(self.array, origin='lower',vmax=1, interpolation='nearest', alpha=0.3)
        
        self.pix = np.arange(width)
        self.xv, self.yv = np.meshgrid(self.pix,self.pix)
        self.pix = np.vstack( (self.xv.flatten(), self.yv.flatten()) ).T

        self.axcut = plt.axes([0.57, 0.01, 0.05, 0.03])
        self.bcut = Button(self.axcut, '->', color='white', hovercolor='#CFCFD4')
        self.bcut.on_clicked(self.onclickf)
        self.bxcut = plt.axes([0.5, 0.01, 0.05, 0.03])
        self.ccut = Button(self.bxcut, '<-', color='white', hovercolor='#CFCFD4')
        self.ccut.on_clicked(self.onclickb)

        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        self.key = self.canvas.mpl_connect("key_press_event", self.onpress)

    def onclickf(self, event):
        if self.image < self.numberOfImages - 5:
            self.image += 5
            self.update()
        if self.image >= self.numberOfImages - 5:
            self.image = self.numberOfImages
            self.update()
    def onclickb(self, event):
        if self.image > 5:
            self.image -= 5
            self.update()
        if self.image <= 5:
            self.image = 1
            self.update()

    def onselect(self, verts): # Update array HERE
        p = path.Path(verts)
        self.ind = p.contains_points(self.pix, radius=1)
        self.array = self.updateArray(self.array, self.ind)
        self.msk.set_data(self.array)
        self.update()
        del self.lasso

    def updateArray(self, array, indices):
        self.lin = np.arange(array.size)
        self.newArray = array.flatten()
        self.newArray[self.lin[indices]] = 1
        self.ROI = self.newArray.reshape(array.shape)
        return self.ROI

    def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        try:
            if event.key == 'enter':
                print("ROI Selected")
                self.ax1.set_title("ROI Selected\nyou may exit the window to continue")
                print(self.ROI)
                np.savetxt(f"{os.getcwd()}/src/tmp/rois/roi.csv", self.ROI, delimiter=",")      
        except Exception as e:
            print(e)
        self.lasso = Lasso(event.inaxes,
                           (event.xdata, event.ydata),
                           self.onselect)
        self.update()
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
    
    def update(self):

        self.im = self.ax1.imshow(mpimg.imread(f"{self.cwd}/src/tmp/images/{self.image}.tif"))
        self.msk = self.ax1.imshow(self.array, origin='lower',vmax=1, interpolation='nearest', alpha=0.3)
        self.ax1.set_xlabel(f"Image {self.image} out of {self.numberOfImages}")
        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)