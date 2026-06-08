import os
from pathlib import Path

import yaml
from sympy.logic.boolalg import false

from controll import check_files_exist
from helper_functions import sanitize_folder_name
from make_yaml import make_yaml
from split import copy_everything_for_single_traning
from train import train


def make_file_structer(yaml_path):
    os.makedirs("./single_label_runs", exist_ok=True)
    folder_paths = []
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
    paths = []
    for folder in folder_paths:
        single_label = [os.path.basename(folder)]
        folder_path = os.path.join(folder, "data.yaml")
        make_yaml(single_label, folder_path)
        paths.append(folder_path)
    return paths


def train_on_each_label():

    yaml_paths = make_yamls()
    copy_everything_for_single_traning(Path("images"), Path("labels"))

    for path in yaml_paths:
        base_path = os.path.dirname(path)
        label_path = os.path.join(base_path, "labels/train")
        image_path = os.path.join(base_path, "images/train")
        print(image_path)
        if not check_files_exist(Path(image_path), Path(label_path), ask_what_do=False):
            continue
        train(None, path)
    # disabled for testing reasiing
