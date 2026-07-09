from ij import IJ, WindowManager
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


if __name__ == "__main__":
    main()