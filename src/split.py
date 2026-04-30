import os
import sys



script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

# get the path or directory
folder_dir = "./InputFolder"
for images in os.listdir(folder_dir):

    # check if the image ends with png or jpg or jpeg
    if (images.endswith(".png") or images.endswith(".jpg")\
        or images.endswith(".jpeg")):
        # display
        print(images)
