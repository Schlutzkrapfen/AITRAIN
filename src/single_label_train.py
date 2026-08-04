
import os
import yaml

from pathlib import Path

from yaml.representer import YAMLError
from controll import check_files_exist
from helper_functions import sanitize_folder_name
from make_yaml import make_yaml
from split import copy_everything_for_single_traning
from train import train
from typing import cast


def make_file_structer(yaml_path:Path)-> list[Path]:
    """
       Create a per-class folder structure for single-label training runs.

       Reads class names from a YOLO-style YAML file's "names" key and creates,
       for each class, a sanitized folder with images/labels subfolders split
       into train/val:

           single_label_runs/<class_name>/{images,labels}/{train,val}

       Args:
           yaml_path: Path to the dataset YAML file containing a "names" key.

       Returns:
           List of created folder paths, one per class.
           Raises:
                  YAMLError: If the file at `yaml_path` cannot be parsed as valid YAML.

    """
    os.makedirs("./single_label_runs", exist_ok=True)
    folder_paths:list[Path] = []
    with open(yaml_path) as stream:
        try:
            for items in cast(str,yaml.safe_load(stream)["names"].values()):
                target_path = os.path.join(
                    "single_label_runs", sanitize_folder_name(items)
                )
                for split in ["train", "val"]:
                    os.makedirs(
                        os.path.join(target_path, "images", split), exist_ok=True
                    )
                    os.makedirs(
                        os.path.join(target_path, "labels", split), exist_ok=True
                    )
                folder_paths.append(Path(target_path))
        except yaml.YAMLError as exc:
            raise YAMLError(exc)
    return folder_paths


def make_yamls() -> list[Path]:
    folder_paths = make_file_structer(Path("data.yaml"))
    paths:list[Path] = []
    for folder in folder_paths:
        single_label =Path(os.path.basename(folder))
        folder_path = Path(os.path.join(folder, "data.yaml"))
        make_yaml(single_label, folder_path)
        paths.append(folder_path)
    return paths


def get_input(default_path: str = "single_label_runs") -> str:
    """
        Prompt the user to enter a label name and validate it against an existing folder.

        Repeatedly asks the user for input until a valid label is provided. The label
        is combined with `default_path` to form a path, and the prompt loops until
        that path exists on disk.

        Args:
            default_path: Base directory in which the label subfolder should exist.
                           Defaults to "single_label_runs".

        Returns:
            The validated path (default_path joined with the user's label) that
            exists on the filesystem.
        """
    while True:
        user_input = input(
            f"Please enter a label you want to train (look at the folder {default_path} )"
        )
        if input == "":
            continue
        path = os.path.join(default_path, user_input)
        print(path)
        print(os.path.exists(path))
        if os.path.exists(Path(path)):
            return path


def train_on_single_label(test_run:bool = False):
    path = get_input()
    try:
        train(None, Path(path),test_run=test_run)
    except Exception as e:
        print(f"Error:{e}")


def train_on_each_label(test_run:bool = False):

    yaml_paths = make_yamls()
    copy_everything_for_single_traning(Path("images"), Path("labels"))

    for path in yaml_paths:
        base_path = os.path.dirname(path)
        label_path = os.path.join(base_path, "labels/train")
        label_val_path = os.path.join(base_path, "labels/val")
        image_path = os.path.join(base_path, "images/train")
        image_val_path = os.path.join(base_path, "labels/val")
        print(image_path)
        if not check_files_exist(
            Path(image_path), Path(label_path), deleted_automaticly=True
        ) and not check_files_exist(
            Path(image_val_path),
            Path(label_val_path),
            deleted_automaticly=True,
        ):
            continue
        try:
            train(None, Path(path),test_run=test_run)
        except Exception as e:
            print(f"this broke bacause: {e}")
            continue
