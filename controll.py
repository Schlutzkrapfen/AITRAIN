import sys
from pathlib import Path

# Use pathlib for cleaner path handling
script_directory = Path(sys.argv[0]).resolve().parent
input_dir = Path("./InputFolder/images")
text_dir = Path("./InputFolder/labels")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def images_have_labels(image_files,label_files) -> bool:
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled = image_files - label_files
    has_label = True
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing label: {name}")
            has_label = False
            
    else:
        print("All images have labels.")
    return has_label


def get_images(directory:Path) :
    return   {f.stem for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}

def get_text_files(directory:Path):
    return {f.stem for f in directory.iterdir() if f.suffix.lower() == ".txt"}
def labels_have_images(image_files,label_files) -> bool:
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled =  label_files - image_files
    has_label = True
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Image: {name}")
            has_label = False
            
    else:
        print("All labels have Images.")
    return has_label


def main():
    images_path = get_images(input_dir)
    text_path = get_text_files(text_dir)
    images_have_labels(images_path,text_path)
    labels_have_images(images_path,text_path)


main()