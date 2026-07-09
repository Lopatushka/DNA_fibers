from ij import IJ, WindowManager
from ij.plugin import ChannelSplitter, ContrastEnhancer, RGBStackMerge
from ij.process import ImageConverter
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
    c1 = channels[0] # fibers 1, red
    c2 = channels[1] # fibers 1, green
    c3 = channels[2] # chromatin
    
    # --- Adjust LUT ---
    c3.setActivated()
    IJ.run(c3, "Grays", "")
    
    # --- Automatic brightness/contrast ---
    ce = ContrastEnhancer()
    
    # channel 1, red
    ce.stretchHistogram(c1, 0.55)
    c1.updateAndDraw()
    
    # channel 2, green
    ce.stretchHistogram(c2, 0.65)
    c2.updateAndDraw()
    
    # channel 3, grey
    ce.stretchHistogram(c3, 0.35)
    c3.updateAndDraw()
    

    # --- Show splitted images in FIJI --- 
    for i, ch in enumerate(channels, start=1):
        ch.show()
        
    # Put C1 into the red channel and C2 into the green channel
    rgb = RGBStackMerge.mergeChannels([c1, c2, None, None, None, None, None], False)
    # Convert Composite/Stack -> RGB
    ImageConverter(rgb).convertToRGB()

    rgb.setTitle("Merged")
    rgb.show()
    
    

if __name__ == "__main__":
    main()