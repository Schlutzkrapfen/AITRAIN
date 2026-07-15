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


def images_have_labels(image_files:set[Path], label_files:list[Path], input_dir:Path)-> list[Path]:
    """Check that every image in the directory has a corresponding .txt label file."""

    image_stems = {Path(f).name for f in image_files}
    label_stems = {Path(f).name for f in label_files}
    unlabeled = image_stems - label_stems
    missing_labels:list[Path] = []
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Label: {name}")

            found = None
            for ext in IMAGE_EXTENSIONS:
                if (Path(input_dir) / (name + ext)).exists():
                    found = Path(input_dir) / (name + ext)
                    break

            if found is None:
                continue
            missing_labels.append(found)

    else:
        print("All images have labels.")
    return missing_labels


def check_if_labels_empty(labels_path:list[Path])->list[Path]:
    empty:list[Path] = []
    for labels in labels_path:
        if os.path.getsize(labels) == 0:
            empty.append(labels)

    print(f"Empty labels: {len(empty)}")
    print(empty[:10])
    return empty


def labels_have_images(image_files:list[Path], label_files:list[Path], text_dir:Path)->list[Path]:
    """Check that every image in the directory has a corresponding .txt label file."""
    image_stems = {Path(f).name for f in image_files}
    label_stems = {Path(f).name for f in label_files}
    unlabeled = label_stems - image_stems
    missing_picture:list[Path] = []
    if unlabeled:
        for name in sorted(unlabeled):
            print(f"Missing Image: {name}")
            missing_picture.append(Path(text_dir) / (name + ".txt"))
    else:
        print("All labels have Images.")
    return missing_picture


def chec_val_and_train_dublicates(images_path:Path, val_path:Path):
    """Checks if any labels are in train and Label class"""
    train_files = set(os.listdir(images_path))
    val_files = set(os.listdir(val_path))

    overlap = train_files & val_files
    print(f"Direct overlap: {len(overlap)}")


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


def check_if_images_labels_exits(images_path:Path, text_path:Path) -> bool:
    """checks if any labels or images exist"""
    if not any(images_path.iterdir()):
        print("No images in folder")
        return False

    if not any(text_path.iterdir()):
        print("No labels in folder")
        return False
    return True


def check_if_duplicates_exist(images_path: Path, delete_automatic: bool = False) -> bool:
    """goes true the image folder and returns stops and aks what it should with duplicated images"""
    hash_map = defaultdict(list)

    # 1. Hash every file — O(n)
    for filename in os.listdir(images_path):
        filepath = os.path.join(images_path, filename)
        if not os.path.isfile(filepath):
            continue

        file_hash = hash_file(Path(filepath))
        hash_map[file_hash].append(filepath)

    # 2. Filter to only groups with more than one file
    duplicate_groups = [paths for paths in hash_map.values() if len(paths) > 1]

    if not duplicate_groups:
        print("No duplicates found.")
        return False
    else:
        print(duplicate_groups)
        if delete_automatic:
            choice = _prompt_action(
                len(duplicate_groups), item_type="image", reason_type="dubplicate"
            )
        else:
            choice = "r"
        if choice == "r":
            for group in duplicate_groups:
                # Keep the first, delete the rest
                for path in group[1:]:
                    os.remove(path)
                    print(f"  Deleted: {path}")
                print(
                    f"Removed {sum(len(g) - 1 for g in duplicate_groups)} duplicate(s)."
                )

        return True


def hash_file(filepath:Path, chunk_size:int=8192):
    """Returns an MD5 hash of the file's contents."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def check_files_exist(
    input_dir:Path,
    text_dir:Path,
    trash_folder:Path = Path("Trash"),
    deleted_automaticly: bool = False,
) -> bool:
    """Validate image/label pairs and prompt user to resolve mismatches before training."""

    images_path = get_images_names(input_dir)
    print(images_path)
    print(input_dir)
    text_path = get_text_files_names(text_dir)
    if not check_if_images_labels_exits(input_dir,text_dir):
        return False

    # Check images missing labels
    single_images = images_have_labels(images_path, text_path, input_dir)
    if single_images:
        if not deleted_automaticly:
            if _prompt_action(len(single_images), "image") == "r":
                move_to_trash_folder(single_images, trash_folder, "image")
                images_path = [f for f in images_path if f not in single_images]
        else:
            move_to_trash_folder(single_images, trash_folder, "image")
            images_path = [f for f in images_path if f not in single_images]

    # Check labels missing images
    single_labels = labels_have_images(list(images_path), text_path, text_dir)
    if single_labels:
        if not deleted_automaticly:
            if _prompt_action(len(single_labels), "label") == "r":
                move_to_trash_folder(single_labels, trash_folder, "label")
                text_path = [f for f in text_path if f not in single_labels]
        else:
            move_to_trash_folder(single_labels, trash_folder, "label")
            text_path = [f for f in text_path if f not in single_labels]

    # Check empty label files
    empty_labels = check_if_labels_empty(list(get_label_path(text_dir)))
    if empty_labels:
        if deleted_automaticly:
            if _prompt_action(len(empty_labels), "empty label") == "r":
                for label in empty_labels:
                    stem = Path(label).stem
                    for split in ["train", "val"]:
                        for ext in [".jpg", ".jpeg", ".png"]:
                            img = input_dir / split / (stem + ext)
                            if img.exists():
                                move_to_trash_folder([img], trash_folder, "image")
                move_to_trash_folder(empty_labels, trash_folder, "label")
                text_path = [f for f in text_path if f not in empty_labels]
        else:
            for label in empty_labels:
                stem = Path(label).stem
                for split in ["train", "val"]:
                    for ext in [".jpg", ".jpeg", ".png"]:
                        img = input_dir / split / (stem + ext)
                        if img.exists():
                            move_to_trash_folder([img], trash_folder, "image")
            move_to_trash_folder(empty_labels, trash_folder, "label")
            text_path = [f for f in text_path if f not in empty_labels]

    images_path = get_images_names(input_dir)
    text_path = get_text_files_names(text_dir)
    _bool = check_if_duplicates_exist(
        images_path=input_dir, delete_automatic=deleted_automaticly
    )
    if not check_if_images_labels_exits(input_dir, text_dir):
        return False
    else:
        return True
