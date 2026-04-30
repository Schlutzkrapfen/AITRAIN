import sys
from pathlib import Path
import shutil

script_directory = Path(sys.argv[0]).resolve().parent

def images_have_labels(image_files,label_files,input_dir) :
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled = image_files.stem - label_files.stem
    missing_labels =  []
    if unlabeled:
        for name in sorted(unlabeled):
            full_path = next(input_dir.glob(f"{name}.*"), None)
            print(f"Missing label: {full_path}")
            missing_labels.append(full_path)
            
    else:
        print("All images have labels.")
    return missing_labels

def labels_have_images(image_files,label_files,text_dir) :
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled =  label_files.stem - image_files.stem
    missing_picture = [] 
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Image: {name}")
            missing_picture.append(Path(text_dir)/(name+".txt"))
    else:
        print("All labels have Images.")
    return missing_picture

def move_to_trash_folder(paths,trash_folder,name="file"):
    '''moves file to a folder'''
    for path in paths:
        if path.exists():
            trash_folder.mkdir(parents=True, exist_ok=True) 
            shutil.move(str(path), trash_folder / path.name)
    print(f"moved every {name} that has no pair was moved to {trash_folder}")

