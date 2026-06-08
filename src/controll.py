import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

from helper_functions import (
    get_images_names,
    get_label_path,
    get_text_files_names,
    move_to_trash_folder,
)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
script_directory = Path(sys.argv[0]).resolve().parent


def images_have_labels(image_files, label_files, input_dir):
    """Check that every image in the directory has a corresponding .txt label file."""

    image_stems = {Path(f).name for f in image_files}
    label_stems = {Path(f).name for f in label_files}
    unlabeled = image_stems - label_stems
    missing_labels = []
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Label: {name}")

            found = None
            for ext in IMAGE_EXTENSIONS:
                if (Path(input_dir) / (name + ext)).exists():
                    found = Path(input_dir) / (name + ext)
                    break

            if found == None:
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


def chec_val_and_train_dublicates(images_path, val_path):
    """Checks if any labels are in train and Label class"""
    train_files = set(os.listdir(images_path))
    val_files = set(os.listdir(val_path))

    overlap = train_files & val_files
    print(f"Direct overlap: {len(overlap)}")
    overlap = images_path & val_path
    print(f"Direct overlap: {len(overlap)}")
    pass


def _prompt_action(count: int, item_type: str, reason_type: str = "orphaned") -> str:
    """Ask user how to handle orphaned files. Returns 'r'(remove), 'y'(continue), or exits."""
    while True:
        choice = (
            input(
                f"{count} {reason_type} {item_type}(s) found. Remove (r), stop (n), or continue (y)? "
            )
            .strip()
            .lower()
        )
        if choice in ("r", "y"):
            return choice
        elif choice == "n":
            sys.exit(0)
        print("Invalid input, please enter r, n or y")


def check_if_images_labels_exits(images_path, text_path) -> bool:
    """checks if any labels or images exist"""
    if not images_path:
        print("No images in folder")
        return False

    if not text_path:
        print("No labels in folder")
        return False
    return True


def check_if_duplicates_exist(images_path) -> bool:
    """goes true the image folder and returns stops and aks what it should with duplicated images"""
    hash_map = defaultdict(list)

    # 1. Hash every file — O(n)
    for filename in os.listdir(images_path):
        filepath = os.path.join(images_path, filename)
        if not os.path.isfile(filepath):
            continue

        file_hash = hash_file(filepath)
        hash_map[file_hash].append(filepath)

    # 2. Filter to only groups with more than one file
    duplicate_groups = [paths for paths in hash_map.values() if len(paths) > 1]

    if not duplicate_groups:
        print("No duplicates found.")
        return False
    else:
        print(duplicate_groups)
        choice = _prompt_action(
            len(duplicate_groups), item_type="image", reason_type="dubplicate"
        )
        if choice == "r":
            for group in duplicate_groups:
                # Keep the first, delete the rest
                for path in group[1:]:
                    os.remove(path)
                    print(f"  Deleted: {path}")
                print(
                    f"Removed {sum(len(g) - 1 for g in duplicate_groups)} duplicate(s)."
                )


def hash_file(filepath, chunk_size=8192):
    """Returns an MD5 hash of the file's contents."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def check_files_exist(input_dir, text_dir, trash_folder="Trash") -> bool:
    """Validate image/label pairs and prompt user to resolve mismatches before training."""
    images_path = get_images_names(input_dir)
    print(images_path)
    print(input_dir)
    text_path = get_text_files_names(text_dir)
    if not check_if_images_labels_exits(images_path, text_path):
        return False

    # Check images missing labels
    single_images = images_have_labels(images_path, text_path, input_dir)
    if single_images:
        if _prompt_action(len(single_images), "image") == "r":
            move_to_trash_folder(single_images, trash_folder, "image")
            images_path = [f for f in images_path if f not in single_images]

    # Check labels missing images
    single_labels = labels_have_images(images_path, text_path, text_dir)
    if single_labels:
        if _prompt_action(len(single_labels), "label") == "r":
            move_to_trash_folder(single_labels, trash_folder, "label")
            text_path = [f for f in text_path if f not in single_labels]

    # Check empty label files
    empty_labels = check_if_labels_empty(get_label_path(text_dir))
    if empty_labels:
        if _prompt_action(len(empty_labels), "empty label") == "r":
            for label in empty_labels:
                stem = Path(label).stem
                for split in ["train", "val"]:
                    for ext in [".jpg", ".jpeg", ".png"]:
                        img = input_dir / split / (stem + ext)
                        if img.exists():
                            move_to_trash_folder(img, trash_folder, "image")
            move_to_trash_folder(empty_labels, trash_folder, "label")
            text_path = [f for f in text_path if f not in empty_labels]

    images_path = get_images_names(input_dir)
    text_path = get_text_files_names(text_dir)
    check_if_duplicates_exist(images_path=input_dir)
    if not check_if_images_labels_exits(images_path, text_path):
        return False
    else:
        return True
