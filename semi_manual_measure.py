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
    
    # --- Iteration ---
    n_files = 0
    for root, dirs, files in os.walk(input_dir):
        
        path_1 = None
        path_2 = None
        
        # ---------------------------------
        # Find the two images
        # ---------------------------------
        for filename in files:
            filename_low = filename.lower()
            
            if substring_1 in filename_low:
                path_1 = os.path.join(root, filename)
                
            elif substring_2 in filename_low:
                path_2 = os.path.join(root, filename)
            
        # process only folders where both files were found
        if path_1 is None or path_2 is None:
            continue
        
        # Open the two images
        #IJ.log("Opening files: {} and {}".format(path_1, path_2))

        imp_1 = IJ.openImage(path_1)
        imp_2 = IJ.openImage(path_2)
            
        if imp_1 is None or imp_2 is None:
            IJ.log("Cannot open images.")
            continue
                
        n_files += 1
        IJ.log("Processing image pair {}: {}".format(n_files, root))
        
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
                
        count = 0
            
        while count < 2:
            # Clear ROI Manager and Results table
            clear_results_and_rois()
            
            # Open ROI Manager if not already open
            rm = RoiManager.getInstance()
            if rm is None:
                rm = RoiManager()

            # Ask what will be measured
            gd = GenericDialog("Measurement type")
            gd.addChoice(
                    "Measure:",
                    ["Fiber length", "Interorigin distance", "Next", "Stop analysis"],
                    "Fiber length"
            )
            gd.showDialog()

            if gd.wasCanceled():
                measurement_type = "Next"
            else:
                measurement_type = gd.getNextChoice()

            # Skip pair and go to next folder
            if measurement_type == "Next":
                IJ.log("Moving to next image pair: {}".format(root))
                break
            
            # Stop analysis
            elif measurement_type == "Stop analysis":
                IJ.log("Analysis stopped by user.")
                close_all_images()
                return
            
            count += 1
                
            WaitForUserDialog(
                    "Manual measurements",
                    "Measure: {}\n\n"
                    "Click OK to save these results.\n"
                    "You will then be asked again for another measurement type.".format(
                        measurement_type
                    )
            ).show()
            
            # Show results table and run measurement command
            rt = ResultsTable.getResultsTable()
            rm.runCommand(imp_1, "Measure")
            
            # Add column
            for row in range(rt.size()):
                rt.setValue("Measurement_type", row, measurement_type.replace(" ", "_"))
                
            if rt.size() > 0:
                name = os.path.basename(root)
                #name = os.path.basename(filename_low).split(substring_1)[0]
                save_path = os.path.join(root, name + "_" + measurement_type + ".csv")

                rt.save(save_path)
                IJ.log("Saved {} measurements: {}".format(measurement_type, save_path))
                        
            else:
                IJ.log("No measurements made for {} in {}".format(
                    measurement_type,
                    root
                ))

        # Close images only after user skips/cancels this image pair
        close_image(imp_1)
        close_image(imp_2)
    
    # Clear ROI Manager and Results table at the end
    clear_results_and_rois()
    
    IJ.log("Done!")
    
        
if __name__ == "__main__":
    main()