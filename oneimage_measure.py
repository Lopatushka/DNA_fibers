from ij import IJ, WindowManager
from ij.gui import WaitForUserDialog, GenericDialog
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager
import os

# ---------------------------------
# HELPERS
# ---------------------------------
def clear_results_and_rois():
    IJ.run("Clear Results")

    rm = RoiManager.getInstance()
    if rm is not None:
        rm.reset()

def close_image(imp):
    if imp is not None:
        imp.close()
        
def close_all_images():
    for wid in WindowManager.getIDList() or []:
        imp = WindowManager.getImage(wid)
        if imp is not None:
            imp.close()
            
def safe_name(text):
    return text.replace(" ", "_").lower()

# ---------------------------------
# MAIN FUNCTION
# ---------------------------------
def main():
    # Ask user about the folder with data
    input_dir = IJ.getDirectory("Choose a directory with data to analyze")
    if input_dir is None:
        return
    
    IJ.run("Set Measurements...", "display decimal=3")

    
    # Find the following substrings in the filenames: "_merged.png" and "_chromatin.png"
    substring_1 = "_merged.png"
    substring_2 = "_chromatin.png"
    
    files = os.listdir(input_dir)
    
    # ---------------------------------
    # Find the two images
    # ---------------------------------
    for filename in files:
        filename_low = filename.lower()
            
        if substring_1 in filename_low:
            path_1 = os.path.join(input_dir, filename)
                
        elif substring_2 in filename_low:
            path_2 = os.path.join(input_dir, filename)
            
    # Process only folders where both files were found
    if path_1 is None or path_2 is None:
        IJ.error('The pair of images are not found! Stopping.')
        return
    
    # Open images
    imp_1 = IJ.openImage(path_1)
    imp_2 = IJ.openImage(path_2)
            
    if imp_1 is None or imp_2 is None:
        IJ.error("Cannot open images.")
        return
    
    # Show images
    imp_1.show()
    imp_2.show()
    
    # Location of images on the screen
    win1 = imp_1.getWindow()
    win2 = imp_2.getWindow()

    win1.setLocation(20, 50)

    x = win1.getX() + win1.getWidth() + 20
    y = win1.getY()

    win2.setLocation(x, y)
    
    # ---------------------------------
    # Measurements
    # ---------------------------------
    
    # Clear ROI Manager and Results table at the end
    #clear_results_and_rois()
    
    IJ.log("Done!")
    
if __name__ == "__main__":
    main()