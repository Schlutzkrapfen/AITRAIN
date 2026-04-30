import sys
from pathlib import Path

# Use pathlib for cleaner path handling
script_directory = Path(sys.argv[0]).resolve().parent
input_dir = Path("./InputFolder/images")
text_dir = Path("./InputFolder/labels")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def images_have_labels(image_files,label_files) -> int:
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled = image_files - label_files
    missing_labels = 0
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing label: {name}")
            missing_labels += 1
            
    else:
        print("All images have labels.")
    return missing_labels


def get_images(directory:Path) :
    return   {f.stem for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}

def get_text_files(directory:Path):
    return {f.stem for f in directory.iterdir() if f.suffix.lower() == ".txt"}
def labels_have_images(image_files,label_files) -> int:
    """Check that every image in the directory has a corresponding .txt label file."""

    unlabeled =  label_files - image_files
    missing_picture = 0
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Image: {name}")
            missing_picture +=1 
            
    else:
        print("All labels have Images.")
    return missing_picture


def main():
    images_path = get_images(input_dir)
    text_path = get_text_files(text_dir)
    print (f"Labels Missing{images_have_labels(images_path,text_path)}")

    print (f"Images Missing{labels_have_images(images_path,text_path)}")


main()