import os
import random
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


def _make_folder_structure(trash_folder: Path):
    """Creates the required train/val folder structure.

        Prompts the user once whether to clear existing folders (moving
        contents to `trash_folder`); the choice applies to all folders.

        Args:
            trash_folder (Path): Destination for cleared files.

        Raises:
            PermissionError: If a folder cannot be created.
        """
    choice = None
    for path in FOLDER_STRUCTURE:
        full_path = script_directory / path
        try:
            os.makedirs(full_path)
        except FileExistsError:
            print("Directory for files already exists, for train and val data")
            if choice is None:
                choice = (
                    input("Remove files inside it? No (N), Yes (y): ").strip().lower()
                )
            if choice == "y":
                move_to_trash_folder(list(full_path.iterdir()), trash_folder, "file")
        except PermissionError:
            raise PermissionError(f"Permission denied: unable to create '{full_path}'.")


def _get_split_ratio(text: str = "What percentage for training? (e.g. 80): ") -> float:
    """Prompts the user for a train/val split percentage.

        Repeatedly asks the user for input until a valid integer percentage
        between 0 and 99 (inclusive) is entered, then converts it to a ratio.

        Args:
            text (str): The prompt message shown to the user. Defaults to
                "What percentage for training? (e.g. 80): ".

        Returns:
            float: The entered percentage expressed as a ratio (e.g. 80
            becomes 0.8).
        """
    while True:
        amount = input(text).strip()
        if amount.isdigit() and 0 <= int(amount) < 100:
            return int(amount) / 100
        print("Please enter a number between 0 and 99.")


def split(input_dir: Path, text_dir: Path, trash_folder: Path):
    """Splits matched image/label pairs into train and val folders.

        Pairs sorted images from `input_dir` with sorted labels from
        `text_dir`, copies them into train/val folders based on a
        user-provided ratio, then optionally moves the originals to
        `trash_folder`.

        Args:
            input_dir (Path): Directory with source images.
            text_dir (Path): Directory with source labels.
            trash_folder (Path): Destination for removed originals.

        Note:
            Pairing is by sorted order, not filename matching — mismatched
            files between directories could misalign pairs.
        """
    _make_folder_structure(trash_folder)

    images = sorted(get_images_path(input_dir))
    labels = sorted(get_label_path(text_dir))
    pairs = list(zip(images, labels))

    split_index = int(len(pairs) * _get_split_ratio())
    train_pairs = pairs[:split_index]
    val_pairs = pairs[split_index:]

    for img, lbl in train_pairs:
        _move0 = shutil.copy2(str(img), script_directory / "images/train" / Path(img).name)
        _move1 = shutil.copy2(str(lbl), script_directory / "labels/train" / Path(lbl).name)

    for img, lbl in val_pairs:
        _move2 = shutil.copy2(str(img), script_directory / "images/val" / Path(img).name)
        _move3 = shutil.copy2(str(lbl), script_directory / "labels/val" / Path(lbl).name)

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
    path_to_pictures: Path,
    path_to_labels: Path,
    split_prozent: float | None = None,
    yaml_path: str = "data.yaml",
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

    classname_to_images: defaultdict[str, list[Path]] = defaultdict(list)
    classname_to_labels: defaultdict[str, list[Path]] = defaultdict(list)

    for i, names in enumerate(classnames):
        current_image_path = images[i]
        current_label_path = labels[i]

        for single_name in set(names):
            classname_to_images[single_name].append(current_image_path)
            classname_to_labels[single_name].append(current_label_path)

    if split_prozent is None:
        split_prozent = _get_split_ratio()

    save_pictures_single_folder(classname_to_images, split_prozent)
    save_label_single_folder(classname_to_labels, split_prozent)
    add_prozent = _get_split_ratio(
        "How much % pictures do you want to add empty labels against overfitting (e. 10%) "
    )
    _list =  add_empty_pictures(classname_to_images, prozent=add_prozent)


def add_empty_pictures(
    classname_to_images: defaultdict[str, list[Path]], prozent: float = 0.1
) -> list[Path]:
    """
    Adds background images with empty labels to each class folder.
    Samples images from other classes to act as negative examples,
    which helps the model learn to suppress false positives.

    Args:
        classname_to_images: Mapping of class name to its list of image paths.
        prozent: Fraction of each class's images to add as background samples. Defaults to 0.1 (10%).

    Returns:
        List of paths of all copied background images.
    """
    if prozent == 0:
        return []
    empty_images: list[Path] = []
    all_images = list(
        {img for images in classname_to_images.values() for img in images}
    )
    for split_type, current_images in classname_to_images.items():
        sanitized_name = sanitize_folder_name(split_type)
        dest = f"single_label_runs/{sanitized_name}"
        # Filter the Images (The filter could be removed if the Call of the function
        # is bevor the right labels are used[if Perfomance Problems Remove and change order])
        available_images = [
            img
            for img in all_images
            if not Path(f"{dest}/images/train/{Path(img).name}").exists()
        ]
        picture_add_amount = max(1, round(len(current_images) * prozent))
        sampled = random.sample(
            available_images, min(picture_add_amount, len(available_images))
        )

        for paths in sampled:
            _path =  shutil.copy2(paths, f"{dest}/images/train")
            Path(f"{dest}/labels/train/{Path(paths).stem}.txt").touch()
            empty_images.append(paths)

    return empty_images


def save_label_single_folder(classname_to_labels, split_prozent: float):
    """Splits and saves label files into per-class train/val folders.

       For each class, splits its labels into train/val subsets, copies
       them into `single_label_runs/<class>/labels/{train,val}`, and
       reformats each copy for its single-class context.

       Args:
           classname_to_labels (dict): Maps class name to its list of
               label file paths.
           split_prozent (float): Fraction (0-1) assigned to training.
       """
    for split_type, current_label in classname_to_labels.items():
        sanitized_name = sanitize_folder_name(split_type)
        split_index = int(len(current_label) * split_prozent)
        print(f"found {len(current_label)} labels that are connected to {split_type}")
        train_labels = current_label[:split_index]
        val_labels = current_label[split_index:]
        for label in train_labels:
            new_label = shutil.copy2(
                label, f"single_label_runs/{sanitized_name}/labels/train"
            )
            formatt_lines(new_label=new_label, split_type=split_type)

        for label in val_labels:
            new_label = shutil.copy2(
                label, f"single_label_runs/{sanitized_name}/labels/val"
            )
            formatt_lines(new_label=new_label, split_type=split_type)


def save_pictures_single_folder(classname_to_images, split_prozent: float):
    """Splits and copies image files into per-class train/val folders.

        For each class, splits its images into train/val subsets according
        to `split_prozent` and copies them into
        `single_label_runs/<class>/images/{train,val}`.

        Args:
            classname_to_images (dict): Maps class name to its list of
                image file paths.
            split_prozent (float): Fraction (0-1) assigned to training.
        """
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


def formatt_lines(new_label: str, split_type: str) -> None:
    """Filters and reindexes a label file for single-class training.

       Keeps only lines matching the class ID for `split_type`, remaps
       that ID to "0", and overwrites the file with the result.

       Args:
           new_label (str): Path to the label file to rewrite.
           split_type (str): Class name used to look up the target ID.
       """
    target_id = str(
        change_yaml_to_id_output(split_type)
    )  # ✅ Called once, YAML read once ever

    with open(new_label, "r") as f:
        lines = f.readlines()

    filtered_lines = []
    for line in lines:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == target_id:  # ✅ String compare, no int() cast
            parts[0] = "0"
            filtered_lines.append(" ".join(parts) + "\n")

    with open(new_label, "w") as f:
        f.writelines(filtered_lines)
