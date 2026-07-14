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
    
    IJ.log("Processing image pair from the folder: {}".format(input_dir))
    
    # ---------------------------------
    # Measurements
    # ---------------------------------
    count = 0
            
    while count < 2:
            # Clear ROI Manager and Results table
            clear_results_and_rois()

            # Ask what will be measured
            gd = GenericDialog("Measurement type")
            gd.addChoice(
                    "Measure:",
                    ["Fiber length", "Interorigin distance"],
                    "Interorigin distance"
            )
            gd.showDialog()

            if gd.wasCanceled():
                IJ.log("Analysis stopped by user.")
                close_all_images()
                return
            
            else:
                measurement_type = gd.getNextChoice()
            
            # Open ROI Manager if not already open
            rm = RoiManager.getInstance()
            if rm is None:
                rm = RoiManager()
            
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
            
            # Save Results table if is not empty    
            if rt.size() > 0:
                name = os.path.basename(input_dir)
                save_path_rt = os.path.join(input_dir, name + "_" + measurement_type + ".csv")
                if os.path.isfile(save_path_rt):
                    IJ.log("File with measurements of {} will be replaced: {}".format(measurement_type, save_path_rt))
                else:
                    IJ.log("Saved {} measurements: {}".format(measurement_type, save_path_rt))

                rt.save(save_path_rt)
                
            else:
                IJ.log("There is no measurements of {} to save".format(measurement_type))
                
            # Save ROI manager if needed
            if rm is not None and rm.getCount() > 0:
                save_path_rm = os.path.join(input_dir, name + "_" + measurement_type + ".zip")
                if os.path.isfile(save_path_rt):
                     IJ.log("File with ROIs of {} will be replaced: {}".format(measurement_type, save_path_rt))
                else:
                    IJ.log("Saved {} ROIs: {}".format(measurement_type, save_path_rm))
                    
                rm.save(save_path_rm)
                     
            else:
                IJ.log("No measurements of {} were maden in {}".format(
                    measurement_type,
                    input_dir
                ))

    # Finishing
    close_all_images()
    clear_results_and_rois() 
    
    IJ.log("Done!")
    
if __name__ == "__main__":
    main()