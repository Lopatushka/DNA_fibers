from ij import IJ, WindowManager
from ij.plugin import ChannelSplitter, ContrastEnhancer, RGBStackMerge
from ij.process import ImageConverter
import os
import csv
import traceback


def save_imp(imp, ext, dir):
    """
    Save the image in the specified format and directory.
    
    Parameters:
        imp (ImagePlus): The image to save.
        ext (str): The file extension (e.g., 'tif', 'png').
        dir (str): The directory where the image will be saved.
    """
    # Construct the full path for saving
    save_path = os.path.join(dir, "{}.{}".format(imp.getTitle(), ext))
    
    # Save the image based on the specified extension
    if ext.lower() == "tif":
        IJ.saveAs(imp, "Tiff", save_path)
    elif ext.lower() == "png":
        IJ.saveAs(imp, "PNG", save_path)
    else:
        IJ.error("Unsupported file format: {}".format(ext))

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
    
    # Ask user where to save outputs
    output_dir = IJ.getDirectory("Choose a directory to save data")
    if output_dir is None:
        IJ.error("No output directory is selected!")
        return
    
    # Keep only unique images
    unique_images = sorted(list(set(images)))
    n = len(unique_images) # total amount of images to process
    
    # ---------------------------------
    # Iterate through all unique images
    # ---------------------------------
    for call_id, imp in enumerate(unique_images, start=1):
        imp_name = imp.getTitle().split(".")[0] # get image name without extension
        # Make Log message
        msg = "Processing image {}/{}: {}".format(
            call_id,
            n,
            imp_name
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
        IJ.run(c3, "RGB Color", "")
        
        # --- Automatic brightness/contrast ---
        ce = ContrastEnhancer()
        
        # channel 1, red
        ce.stretchHistogram(c1, 0.55)
        c1.updateAndDraw()
        
        # channel 2, green
        ce.stretchHistogram(c2, 0.65)
        c2.updateAndDraw()
        
        # channel 3, grey
        ce.stretchHistogram(c3, 0.15)
        c3.updateAndDraw()
        
        # --- Changes names of splitted images ---
        c1.setTitle("{}_fibers1_red".format(imp_name))
        c2.setTitle("{}_fibers1_green".format(imp_name))
        
        c3.setTitle("{}_chromatin".format(imp_name))
        #c3.show()
        #for i, ch in enumerate(channels, start=1):
            #ch.show()
            
        # Put C1 into the red channel and C2 into the green channel
        rgb = RGBStackMerge.mergeChannels([c1, c2, None, None, None, None, None], False)
        
        # Convert Composite/Stack -> RGB
        ImageConverter(rgb).convertToRGB()
        
        # IMPORTANT: restore calibration
        rgb.setCalibration(imp.getCalibration().copy())

        # Set name for merged image
        rgb.setTitle("{}_merged".format(imp_name))
        
        # --- Add scale bar to the rgb and chromatim images ---
        # copy images
        rgb_copy = rgb.duplicate()
        rgb_copy.setTitle(rgb.getTitle() + "_ruler")
        
        c3_copy = c3.duplicate()
        c3_copy.setTitle(c3.getTitle() + "_ruler")
        
        IJ.run(
        rgb_copy,
        "Scale Bar...",
        "width=20 height=4 font=18 color=White background=None location=[Lower Right] bold overlay"
        )
        IJ.run(
        c3_copy,
        "Scale Bar...",
        "width=20 height=4 font=18 color=White background=None location=[Lower Right] bold overlay"
        )
        
        # Create new directory for each image and save data
        save_dir = os.path.join(output_dir, imp_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        save_imp(rgb, "png", save_dir)
        save_imp(c1, "png", save_dir)
        save_imp(c2, "png", save_dir)
        save_imp(c3, "png", save_dir)
        
        save_imp(rgb_copy, "png", save_dir)
        save_imp(c3_copy, "png", save_dir)

        IJ.log("Images are saved in {}".format(save_dir))
        
        # Check calibration of the images
        for img in [c1, rgb]:
            cal = img.getCalibration()
            print(img.getTitle())
            print("pixelWidth:", cal.pixelWidth)
            print("pixelHeight:", cal.pixelHeight)
            print("unit:", cal.getUnit())
            

    # Close all opened images
    for wid in WindowManager.getIDList() or []:
        WindowManager.getImage(wid).close()
    
    

if __name__ == "__main__":
    main()