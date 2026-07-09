from ij import IJ, WindowManager
from ij.plugin import ChannelSplitter
from ij.gui import GenericDialog
from ij.plugin.frame import RoiManager
from ij.gui import ShapeRoi
from ij.plugin.filter import BackgroundSubtracter
from ij.measure import Measurements, ResultsTable
from ij.process import ImageStatistics
from ij.gui import NonBlockingGenericDialog
from ij.gui import WaitForUserDialog
from ij.plugin.filter import Analyzer
import os
import csv
import traceback

# ---------------------------------
# MAIN FUNCTION
# ---------------------------------
def main():
    # Check if at least one image is opened
    ids = WindowManager.getIDList()
    if not ids:
        IJ.error("No images open.")
        return
    
    # Opened images checking and filtration
    images = [] # store images in the list
    for wid in ids:
        imp = WindowManager.getImage(wid)
        if imp is None:
            continue
        else:
            images.append(imp)
        
    # Check if there are some suitable images
    if not images:
        IJ.error("No suitable images found (only derived windows are open)!")
        return
    
    # Keep only unique images
    unique_images = sorted(list(set(images)))
    n = len(unique_images) # total amount of images to process
    
    # TEST CODE: 1 image
    #  Take pixel size 
    #imp = unique_images[0]
    
    # ---------------------------------
    # Iterate through all unique images
    # ---------------------------------
    for call_id, imp in enumerate(unique_images, start=1):
        # Make Log message
        msg = "Processing image {}/{}: {}".format(
            call_id,
            n,
            imp.getTitle()
        )
        IJ.log(msg)
        
        # Get pixel size
        cal = imp.getCalibration()
        if cal.scaled():
            pixel_width = cal.pixelWidth
            pixel_height = cal.pixelHeight
            unit = cal.getUnit()
            
            IJ.log("Pixel size: {} x {} {}".format(
            pixel_width,
            pixel_height,
            unit
            ))
    
    # Split image and acess them individually    
    channels = ChannelSplitter.split(imp)
    c1 = channels[0] # fibers 1
    c2 = channels[1] # fibers 1
    c3 = channels[2] # chromatin
    
    

if __name__ == "__main__":
    main()