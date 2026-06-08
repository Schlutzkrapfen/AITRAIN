import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

from helper_functions import (
    change_yaml_to_id_output,
    get_classnames,
    get_images_from_ordered,
    get_images_path,
    get_label_from_ordered,
    get_label_path,
    move_to_trash_folder,
    sanitize_folder_name,
)

script_directory = Path(os.path.dirname(os.path.abspath(sys.argv[0])))

FOLDER_STRUCTURE = ["images/train", "images/val", "labels/train", "labels/val"]


def _make_folder_structure(trash_folder):
    """Create the required folder structure, prompting user to clear any that already exist."""
    choice = None
    for path in FOLDER_STRUCTURE:
        full_path = script_directory / path
        try:
            os.makedirs(full_path)
        except FileExistsError:
            print(f"Directory for files already exists, for train and val data")
            if choice == None:
                choice = (
                    input("Remove files inside it? No (N), Yes (y): ").strip().lower()
                )
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
    val_pairs = pairs[split_index:]

    for img, lbl in train_pairs:
        shutil.copy2(str(img), script_directory / "images/train" / Path(img).name)
        shutil.copy2(str(lbl), script_directory / "labels/train" / Path(lbl).name)

    for img, lbl in val_pairs:
        shutil.copy2(str(img), script_directory / "images/val" / Path(img).name)
        shutil.copy2(str(lbl), script_directory / "labels/val" / Path(lbl).name)

    print(f"Done: {len(train_pairs)} train pairs, {len(val_pairs)} val pairs.")

    choice = (
        input(
            f"Do you want to remove old files in {os.path.dirname(input_dir)}? No (n), Yes (Y): "
        )
        .strip()
        .lower()
    )
    if choice != "n":
        move_to_trash_folder(images, trash_folder, "Picutre")
        move_to_trash_folder(labels, trash_folder, "label")


def copy_everything_for_single_traning(
    path_to_pictures, path_to_labels, split_prozent=None, yaml_path="data.yaml"
):
    """
    Prepares and copies images and labels for single-label training.

    Flattens and re-splits the incoming data, ignoring any pre-existing
    'train' or 'val' directory structures to accommodate potential updates.

    Args:
        path_to_pictures (str): Source path containing the images.
        path_to_labels (str): Source path containing the corresponding labels.
    """
    images = get_images_from_ordered(path_to_pictures)
    labels = get_label_from_ordered(path_to_labels)

    print(f"{len(images)} images found {len(labels)} labels found")
    classnames = get_classnames(labels, yaml_path)

    classname_to_images = defaultdict(list)
    classname_to_labels = defaultdict(list)

    for i, names in enumerate(classnames):
        current_image_path = images[i]
        current_label_path = labels[i]

        for single_name in set(names):
            classname_to_images[single_name].append(current_image_path)
            classname_to_labels[single_name].append(current_label_path)

    if split_prozent == None:
        split_prozent = _get_split_ratio()

    save_pictures_single_folder(classname_to_images, split_prozent)
    save_label_single_folder(classname_to_labels, split_prozent)


def save_label_single_folder(classname_to_labels, split_prozent):
    for split_type, current_label in classname_to_labels.items():
        sanitized_name = sanitize_folder_name(split_type)
        split_index = int(len(current_label) * split_prozent)
        print(f"found {len(current_label)} labels that are connected to {split_type}")
        train_labels = current_label[:split_index]
        val_labels = current_label[split_index:]
        for label in train_labels:
            new_label = shutil.copy2(
                label, f"single_label_runs/{sanitized_name}/label/train"
            )
            formatt_lines(new_label=new_label, split_type=split_type)

        for label in val_labels:
            new_label = shutil.copy2(
                label, f"single_label_runs/{sanitized_name}/label/val"
            )
            formatt_lines(new_label=new_label, split_type=split_type)


def save_pictures_single_folder(classname_to_images, split_prozent):
    for split_type, current_images in classname_to_images.items():
        sanitize_name = sanitize_folder_name(split_type)
        split_index = int(len(current_images) * split_prozent)
        train_images = current_images[:split_index]
        val_images = current_images[split_index:]
        print(
            f"found {len(current_images)} images that are connected to {sanitize_name}"
        )
        for image in train_images:
            shutil.copy2(image, f"single_label_runs/{sanitize_name}/images/train")
        for image in val_images:
            shutil.copy2(image, f"single_label_runs/{sanitize_name}/images/val")


def formatt_lines(new_label, split_type):
    with open(new_label, "r") as f:
        lines = f.readlines()
    filtered_lines = []
    for line in lines:
        parts = line.split()
        if not parts:
            continue
        id = change_yaml_to_id_output(split_type)
        if int(parts[0]) == id:
            parts[0] = "0"
            filtered_lines.append(" ".join(parts) + "\n")
    with open(new_label, "w") as f:
        f.writelines(filtered_lines)
