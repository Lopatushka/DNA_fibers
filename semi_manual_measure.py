from ij import IJ
from ij.gui import WaitForUserDialog, GenericDialog
from ij.measure import ResultsTable
import os

# ---------------------------------
# MAIN FUNCTION
# ---------------------------------
def main():
    # Ask user about the folder with data
    input_dir = IJ.getDirectory("Choose a directory")
    
    # Find the following substrings in the filenames: "_merged.png" and "_chromatin.png"
    substring_1 = "_merged.png"
    substring_2 = "_chromatin.png"
    
    # --- Iteration ---
    for root, dirs, files in os.walk(input_dir):
        
        path_1 = None
        path_2 = None

        for filename in files:
            
            if  substring_1.lower() in filename.lower():
                path_1 = os.path.join(root, filename)
                
            if substring_2.lower() in filename.lower():
                path_2 = os.path.join(root, filename)
            
            # process only folders where both files were found
            if path_1 is None or path_2 is None:
                continue

            IJ.log("Opening files: {} and {}".format(path_1, path_2))

            imp_1 = IJ.openImage(path_1)
            imp_2 = IJ.openImage(path_2)
            
            if imp_1 is not None:
                imp_1.show()
            if imp_2 is not None:
                imp_2.show()
                
            # Repeat measurements for the same image pair
            while True:

                # Clear previous measurements
                IJ.run("Clear Results")
            
                # Ask what will be measured
                gd = GenericDialog("Measurement type")
                gd.addChoice(
                    "Measure:",
                    ["Fiber length", "Interorigin distance", "Skip this image", "Stop analysis"],
                    "Fiber length"
                )

                gd.showDialog()

            if gd.wasCanceled():
                measurement_type = "Skip this image pair"
            else:
                measurement_type = gd.getNextChoice()

            # Skip pair and go to next folder
            if measurement_type == "Skip this image pair":
                IJ.log("Skipped image pair: {}".format(root))
                break
            
            # Stop analysis
            if measurement_type == "Stop analysis:":
                IJ.log("Analysis stopped by user.")
                return
            
            # Wait for user
            WaitForUserDialog(
                "Manual measurements",
                "Measure: {}\n\n"
                "Click OK to save these results.\n"
                "You will then be asked again for another measurement type.".format(
                    measurement_type
                )
            ).show()
            
            # Save Results table
            rt = ResultsTable.getResultsTable()
            
            if rt.size() > 0:
                folder_name = os.path.basename(root)
                save_path = os.path.join(root, folder_name + "_" + measurement_type + ".csv")

                rt.save(save_path)
                IJ.log("Saved {} measurements: {}".format(measurement_type, save_path))
            else:
                IJ.log("No measurements made for {} in {}".format(
                    measurement_type,
                    root
                ))

       # Close images only after user skips/cancels this image pair
        if imp_1 is not None:
            imp_1.close()

        if imp_2 is not None:
            imp_2.close()

if __name__ == "__main__":
    main()