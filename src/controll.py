import sys
from pathlib import Path
import shutil
import os
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
script_directory = Path(sys.argv[0]).resolve().parent

def images_have_labels(image_files,label_files,input_dir) :
    """Check that every image in the directory has a corresponding .txt label file."""

    print(image_files)
    image_stems = {Path(f).name for f in image_files}
    label_stems = {Path(f).name for f in label_files}
    unlabeled = image_stems - label_stems
    missing_labels =  []
    if unlabeled:
        for name in sorted(unlabeled):
           print(f"Missing Label: {name}")
            
           found = None
           for ext in IMAGE_EXTENSIONS:
                   if (Path(input_dir) / (name + ext)).exists():
                       found = Path(input_dir) / (name + ext)
                       break
                
           if(found ==None):
               continue
           missing_labels.append(found)
            
    else:
        print("All images have labels.")
    return missing_labels

def check_if_labels_empty(labels_path):
   empty = []
   for labels in labels_path:
       if os.path.getsize(labels) == 0:
           empty.append(labels)

   print(f"Empty labels: {len(empty)}")
   print(empty[:10])
   return empty

def labels_have_images(image_files, label_files, text_dir):
    """Check that every image in the directory has a corresponding .txt label file."""
    image_stems = {Path(f).name for f in image_files}
    label_stems = {Path(f).name for f in label_files}
    unlabeled = label_stems - image_stems
    missing_picture = []
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Image: {name}")
            missing_picture.append(Path(text_dir) / (name + ".txt"))
    else:
        print("All labels have Images.")
    return missing_picture

def chec_val_and_train_dublicates(images_path,val_path):
    '''Checks if any labels are in train and Label class'''
    train_files = set(os.listdir(images_path))
    val_files = set(os.listdir(val_path))

    overlap = train_files & val_files
    print(f"Direct overlap: {len(overlap)}")
    overlap = images_path & val_path
    print(f"Direct overlap: {len(overlap)}")
    pass
def move_to_trash_folder(paths,trash_folder,name="file"):
    '''moves file to a folder'''
    for path in paths:
        if path.is_file():
            trash_folder.mkdir(parents=True, exist_ok=True) 
            shutil.move(str(path), trash_folder / path.name)
        else:
            print(f"ERROR: {path} not found")
    print(f"moved every {name} that has no pair to {trash_folder}")

