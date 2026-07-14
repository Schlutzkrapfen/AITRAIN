import os
from pathlib import Path

import yaml

from controll import check_files_exist
from helper_functions import sanitize_folder_name
from make_yaml import make_yaml
from split import copy_everything_for_single_traning
from train import train


def make_file_structer(yaml_path:str):
    os.makedirs("./single_label_runs", exist_ok=True)
    folder_paths:list[str] = []
    with open(yaml_path) as stream:
        try:
            for items in yaml.safe_load(stream)["names"].values():
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
                folder_paths.append(target_path)
        except yaml.YAMLError as exc:
            print(exc)
    return folder_paths


def make_yamls() -> list[Path]:
    folder_paths = make_file_structer("data.yaml")
    paths:list[Path] = []
    for folder in folder_paths:
        single_label = [os.path.basename(folder)]
        folder_path = os.path.join(folder, "data.yaml")
        make_yaml(single_label, folder_path)
        paths.append(Path(folder_path))
    return paths


def get_input(default_path: str = "single_label_runs") -> str:
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


def train_on_single_label():
    path = get_input()
    try:
        train(None, str(path))
    except Exception as e:
        print(f"Error:{e}")


def train_on_each_label():

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
            train(None, str(path))
        except Exception as e:
            print(f"this broke bacause: {e}")
            continue
