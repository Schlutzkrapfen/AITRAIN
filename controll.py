import sys
from pathlib import Path
import shutil

# Use pathlib for cleaner path handling
script_directory = Path(sys.argv[0]).resolve().parent
input_dir = Path("./InputFolder/images")
text_dir = Path("./InputFolder/labels")
trash_folder = Path("./InputFolder/Trash")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def images_have_labels(image_files,label_files) :
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled = image_files - label_files
    missing_labels =  []
    if unlabeled:
        for name in sorted(unlabeled):
            full_path = next(input_dir.glob(f"{name}.*"), None)
            print(f"Missing label: {full_path}")
            missing_labels.append(full_path)
            
    else:
        print("All images have labels.")
    return missing_labels


def get_images(directory:Path) :
    return   {f.stem for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}

def get_text_files(directory:Path):
    return {f.stem for f in directory.iterdir() if f.suffix.lower() == ".txt"}
def labels_have_images(image_files,label_files) :
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled =  label_files - image_files
    missing_picture = [] 
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Image: {name}")
            missing_picture.append(Path(text_dir)/(name+".txt"))
    else:
        print("All labels have Images.")
    return missing_picture

def move_to_trash_folder(paths,name="file"):
    for path in paths:
        if path.exists():
            trash_folder.mkdir(parents=True, exist_ok=True) 
            shutil.move(str(path), trash_folder / path.name)
    print(f"moved every {name} that has no pair was moved to {trash_folder}")

def main():
    images_path = get_images(input_dir)
    text_path = get_text_files(text_dir)
    single_images = images_have_labels(images_path,text_path)
    if len(single_images) > 0:
        move_to_trash_folder(single_images, "images")

    single_labels = labels_have_images(images_path,text_path)
    if len(single_labels) > 0:
        move_to_trash_folder(single_labels, "label")

main()