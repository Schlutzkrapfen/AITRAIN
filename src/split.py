import os
import sys
from pathlib import Path
from helper_functions import move_to_trash_folder,get_images_path, get_label_path

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
paths = ["images/train","images/val","label/train","label/val"]


def make_folder_structer(trash_folder):
   '''makes the default folder structer that it can now '''
   for path in paths:
      try:
         os.makedirs(path)
      except FileExistsError:
         print(f"Directory '{path}' already exist.")
         choice = input(
            f"Want to remove the files in it no (N), yes (y)? "
         ).strip().lower()
         if choice == "y":
            for files in Path(path).iterdir():
               move_to_trash_folder(files,trash_folder,"file")
      except PermissionError:
          print(f"Permission denied: Unable to create '{path}'.")
      except Exception as e:
         print(f"An error occurred at '{path}': {e}")


def find_all_equal_files(input_dir,text_dir):
   
   images_paths= get_images_path(input_dir)
   label_path = get_label_path(text_dir)

def split(trash_folder):
   '''splits the images and labes in train and val  different'''
   make_folder_structer(trash_folder)
   Path()



