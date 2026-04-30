
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def get_images_path(directory:Path) :
    '''Gets all the paths of images out of a folder with endings png, jpg and jpeg'''
    return   {f for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}

def get_label_path(directory:Path):
    '''gets all the paths of labels in a folder'''
    return {f for f in directory.iterdir() if f.suffix.lower() == ".txt"}

def get_images_names(directory:Path) :
    '''Gets all the names of images out of a folder endings png, jpg and jpeg'''
    return   {f.stem for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}

def get_text_files_names(directory:Path):
    '''gets all the names of labels in a folder ending (txt)'''
    return {f.stem for f in directory.iterdir() if f.suffix.lower() == ".txt"}