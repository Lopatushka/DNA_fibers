from ij import IJ, WindowManager
import os

# ---------------------------------
# MAIN FUNCTION
# ---------------------------------
def main():
    input_dir = IJ.getDirectory("Choose a directory")
    search_string = "_merged.png"
    
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if (
                search_string.lower() in filename.lower()
            ):
                path = os.path.join(root, filename)

                IJ.log("Opening: {}".format(path))

                imp = IJ.openImage(path)
                if imp is not None:
                    imp.show()
        
if __name__ == "__main__":
    main()