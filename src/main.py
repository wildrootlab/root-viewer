from multiprocessing.spawn import import_main_path
import os
import sys
import shutil
import mask
import visualizations
from PIL import Image
ext = "tif"
tmpImages = f"{os.getcwd()}/src/tmp/images/"
tmpROIs = f"{os.getcwd()}/src/tmp/rois/"
DEBUG = False # set to True to enable Debugging

def debuging(DEBUG):
    try:
        if DEBUG == False:
            sys.tracebacklimit = 0
        elif DEBUG == True:
            sys.tracebacklimit = 1000
            print(f"cwd= {os.getcwd()}")
    except ValueError as err:  
        print(f"Unexpected {err=}, {type(err)=}, \n DEBUG is set to {DEBUG}")
    return DEBUG

def createTmp():
    if os.path.exists(f"{os.getcwd()}/src/tmp") == False:
        os.makedirs(tmpImages)
        os.makedirs(tmpROIs)
        if DEBUG == True:
            print("tmp doesn't exist")

    elif os.path.exists("../tmp/") and os.path.exists(tmpImages) == False:
        os.makedirs(tmpImages)
        if DEBUG == True:
            print("tmp/images doesn't exist")

    elif os.path.exists("../tmp/") and os.path.exists(tmpROIs) == False:
        os.makedirs(tmpROIs)
        if DEBUG == True:
            print("tmp/rois doesn't exist")
    
    elif DEBUG == True:
        print("tmp/images exists")

def clearTmp():
    try:
        if not os.listdir(tmpImages) == []:
            shutil.rmtree(tmpImages)
            os.makedirs(tmpImages)
            if DEBUG == True:
                print("tmp not clear, now cleared")
        else:
            if DEBUG == True:
                print("tmp is already clear")
    except Exception as e:
        print(f"Failed to clear {os.path.join(tmpImages)}. Reason: {e}")

def delTmp():
    try:
        shutil.rmtree(f"{os.getcwd()}/src/tmp")
    
    except Exception as e:
        print(f"Failed to delete {os.getcwd()}/tmp. Reason: {e}")

def directoryValid(dirIn):
    """
    Test if directory exists, else pass error 
    """
    if os.path.exists(dirIn) == False:
        raise Exception("I did not find the folder at, \n" + "'" + str(dirIn) + "'") from None
    
    return os.path.exists(dirIn)

def fileValidation(dirIn):
    """
    Check there are any files in Dir with proper extention
    """    
    if not any(file.endswith(ext) for file in os.listdir(dirIn)):
        raise Exception("No " + ext + " files found in " + str(dirIn))
    
    elif DEBUG == True:

        for file in os.listdir(dirIn):
            if file.endswith(ext):
                print(file)
            else:
                continue
        print("\nThese files will be analyzed \n")
    
    return True

def filesToTmp(dirIn):
    """
    Copy desiered files with proper extension into tmp folder
    """
    count = 1
    try:
        if os.listdir(tmpImages) == []:
            for file in os.listdir(dirIn):
                if file.endswith(ext):
                    src = dirIn +"/"+ file
                    dest = tmpImages+str(count)+".tif"
                    shutil.copy(str(src), str(dest))
                    count += 1
            return True
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (os.path.basename, e))
                
if __name__ == "__main__":
    # set debug mode
    delTmp()
    print(f"Debugging is set to {debuging(DEBUG)}")

    createTmp() # create required tmp folders if not already present
    clearTmp() # clears tmp (incase of tmapering)
    
    # define desired directory of images 
    dirIn = str(input(
    """
    Enter the path for folder containing desired images. 
    (FRAMES MUST BE IN INDIVDUAL TIF FILES) 
    
    Path: 
    """
    ))
    
    if directoryValid(dirIn) and fileValidation(dirIn):

        if filesToTmp(dirIn): # adds the desired images to tmp folder
            val, width, height = mask.imageSizeCheck()

        if val == True:
            mask.selectROI(width, height)# prompts for ROI selection
            visualizations.genVisual(tmpImages, tmpROIs)
            
    
    delTmp()
            
        


"""
WORKFLOW

1. Select folder                                 **DONE**
2. Open popup for selcting images from folder    **DONE**
4. Use ROI to to create mask                     **DONE**
5. Use mask with skimage to make visualizations  **DONE**

"""


