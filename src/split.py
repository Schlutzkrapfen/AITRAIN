import os
import sys


script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
paths = ["images/train","images/val","label/train","label/val"]


def make_folder_structer():
   '''makes the default folder structer that it can now '''
   for path in paths:
      try:
         os.makedirs(path)
      except FileExistsError:
         print(f"Directory '{path}' already exist.")
      except PermissionError:
          print(f"Permission denied: Unable to create '{path}'.")
      except Exception as e:
         print(f"An error occurred at '{path}': {e}")



def split():
   '''splits the images and labes in train and val  different'''
   make_folder_structer()

