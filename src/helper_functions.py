
from pathlib import Path
import os
import shutil
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def get_images_path(directory:Path) :
    '''Gets all the paths of images out of a folder with endings png, jpg and jpeg'''
    return   {f for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}

def get_label_path(directory:Path):
    '''gets all the paths of labels in a folder'''
    return {f for f in directory.iterdir() if f.suffix.lower() == ".txt"}

def get_images_names(directory:Path) :
    '''Gets all the names of images out of a folder endings png, jpg and jpeg'''
    return {
        f.name[:-len(f.suffix)]
        for f in directory.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS
    }

def get_text_files_names(directory: Path):
    '''gets all the names of labels in a folder ending (txt)'''
    test = []
    for f in directory.iterdir():
        if f.suffix.lower() == ".txt":
            test.append(f.name[:-len(f.suffix)])
    return test

def move_to_trash_folder(paths,trash_folder,name="file"):
    '''moves file to a folder'''
    if not isinstance(paths, list):
        paths = [paths]
    for path in paths:
        if path.is_file():
            trash_folder.mkdir(parents=True, exist_ok=True) 
            shutil.move(str(path), trash_folder / path.name)
        else:
            print(f"ERROR: {path} not found")
    print(f"moved every {name} to {trash_folder}")
