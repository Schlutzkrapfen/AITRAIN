import sys
import os

from pathlib import Path

# Allow imports from the src/ folder
USER_DATA_DIR = 'user_data' 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from controll import get_images, get_text_files,images_have_labels,move_to_trash_folder, labels_have_images
input_dir = Path("./InputFolder/images")
text_dir = Path("./InputFolder/labels")
trash_folder = Path("./InputFolder/Trash")
def check():
    images_path = get_images(input_dir)
    text_path = get_text_files(text_dir)
    single_images = images_have_labels(images_path,text_path,input_dir)
    if len(single_images) > 0:
        choice = input(f"Missing {len(single_images)} label/s found. Remove (r) image/s, stop (n), or Continue (Y)? ").strip().lower()
        if choice == "r":
            move_to_trash_folder(single_images, "image")
        elif choice == "n":
            sys.exit(0)          
        elif choice == "y":
            pass
    single_labels = labels_have_images(images_path,text_path,text_dir)
    if len(single_labels) > 0:
        while True:
            choice = input(f"Missing {len(single_labels)} image/s found. Remove (r) label/s, stop (n), or Continue (Y)? ").strip().lower()
            if choice == "r":
                move_to_trash_folder(single_labels, "label")
                return
            elif choice == "n":
                sys.exit(0)          
            elif choice == "y":
                return
            else:
                print("Invalid input, please enter r, n or y")
        

check()