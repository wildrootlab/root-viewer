import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure

def genVisual(tmpImages, tmpROIs):
    mask = np.genfromtxt(f"{tmpROIs}roi.csv", delimiter=',')
    fluorescence_change = []
    
    for file in os.listdir(tmpImages):
        image = io.imread(f"{tmpImages}/{file}")
        props = measure.regionprops_table(
        mask.astype(np.uint8),
        intensity_image=image,
        properties=('label', 'area', 'intensity_mean')
        )
        fluorescence_change.append(props['intensity_mean'])

    fluorescence_change /= fluorescence_change[0]  # normalization
    fig, ax = plt.subplots()
    ax.plot(fluorescence_change)
    ax.grid()
    ax.set_title('Change in fluorescence intensity at ROI')
    ax.set_xlabel('Frames')
    ax.set_ylabel('Normalized total intensity')
    dl = downloadLocation()
    plt.savefig(rf"{dl}/FIG.png")
    print("\nFigure Saved!", rf"{dl}/FIG.png")

def downloadLocation():
    dw = input(r"""
Define a download location. Note default loaction will be the current working directory.
Download Path:
""")
    if len(dw) == 0:
        dw = os.getcwd()
    return dw