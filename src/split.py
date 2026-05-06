import os
import sys
import shutil
from pathlib import Path
from helper_functions import move_to_trash_folder,get_images_path, get_label_path

script_directory = Path(os.path.dirname(os.path.abspath(sys.argv[0])))

FOLDER_STRUCTURE = [
    "images/train", "images/val",
    "labels/train", "labels/val"   # fixed typo: "label" → "labels"
]

def _make_folder_structure(trash_folder):
    """Create the required folder structure, prompting user to clear any that already exist."""
    for path in FOLDER_STRUCTURE:
        full_path = script_directory / path
        try:
            os.makedirs(full_path)
        except FileExistsError:
            print(f"Directory '{full_path}' already exists.")
            choice = input("Remove files inside it? No (n), Yes (y): ").strip().lower()
            if choice == "y":
                move_to_trash_folder(list(full_path.iterdir()), trash_folder, "file")
        except PermissionError:
            print(f"Permission denied: unable to create '{full_path}'.")
        except Exception as e:
            print(f"Unexpected error at '{full_path}': {e}")


def _get_split_ratio() -> float:
    """Prompt user for a train/val split percentage and return it as a ratio."""
    while True:
        amount = input("What percentage for training? (e.g. 80): ").strip()
        if amount.isdigit() and 0 < int(amount) < 100:
            return int(amount) / 100
        print("Please enter a number between 1 and 99.")


def split(input_dir, text_dir, trash_folder):
    """Split matched image/label pairs into train and val folders."""
    _make_folder_structure(trash_folder)

    images = sorted(get_images_path(input_dir))
    labels = sorted(get_label_path(text_dir))
    pairs = list(zip(images, labels))

    split_index = int(len(pairs) * _get_split_ratio())
    train_pairs = pairs[:split_index]
    val_pairs   = pairs[split_index:]

    for img, lbl in train_pairs:
        shutil.copy2(str(img), script_directory / "images/train" / Path(img).name)
        shutil.copy2(str(lbl), script_directory / "labels/train" / Path(lbl).name)

    for img, lbl in val_pairs:
        shutil.copy2(str(img), script_directory / "images/val" / Path(img).name)
        shutil.copy2(str(lbl), script_directory / "labels/val" / Path(lbl).name)

    print(f"Done: {len(train_pairs)} train pairs, {len(val_pairs)} val pairs.")

    choice = input(f"Do you want to remove old files in {os.path.dirname(input_dir)}? No (n), Yes (Y): ").strip().lower()
    if choice != "n":
        move_to_trash_folder(images,trash_folder,"Picutre")
        move_to_trash_folder(labels,trash_folder,"label")
      
