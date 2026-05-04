import sys
import os

from pathlib import Path

# Allow imports from the src/ folder
USER_DATA_DIR = 'user_data' 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from controll import images_have_labels,move_to_trash_folder, labels_have_images
from helper_functions import get_images_names, get_text_files_names, get_label_path, get_images_path

base_dir = Path("./InputFolder")
input_dir = base_dir / "images"
text_dir = base_dir / "labels"
trash_folder = Path("./Trash")

def check():
    images_path = get_images_names(input_dir)
    if (not images_path):
        print("No Images in Folder")
        return
    text_path = get_text_files_names(text_dir)
    if (not text_path):
        print("no Labels in Folder")
        return
    
    single_images = images_have_labels(images_path,text_path,input_dir)
    if len(single_images) > 0:
        while True:
            choice = input(f"Missing {len(single_images)} label/s found. Remove (r) image/s, stop (n), or Continue (Y)? ").strip().lower()
            if choice == "r":
                move_to_trash_folder(single_images,trash_folder, "image")
                break
            elif choice == "n":
                sys.exit(0)          
            elif choice == "y":
                break
            else:
                print("Invalid input, please enter r, n or y")
    
    single_labels = labels_have_images(images_path,text_path,text_dir)
    if len(single_labels) > 0:
        while True:
            choice = input(f"Missing {len(single_labels)} image/s found. Remove (r) label/s, stop (n), or Continue (Y)? ").strip().lower()
            if choice == "r":
                move_to_trash_folder(single_labels,trash_folder ,"label")
                break
            elif choice == "n":
                sys.exit(0)          
            elif choice == "y":
                break
            else:
                print("Invalid input, please enter r, n or y")
        
def split():
    labels =  get_label_path(input_dir)
    images = get_images_path(text_dir)
    print(labels)

check()
split()
#make_yaml()
#train()