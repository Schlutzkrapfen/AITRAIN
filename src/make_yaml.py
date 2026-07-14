from queue import Empty

from pathlib import Path
import yaml


def get_classes(classes_dir:Path) -> list[str]:
    try:
        with open(classes_dir, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        raise ValueError(f"Error can't get classes:{e}")


def make_yaml(classes_dir:Path, path_to_yaml:str="data.yaml", path_to_pictures:str="images"):
    """Generate data.yaml config file for YOLO training."""
    classes = get_classes(classes_dir)
    if classes is Empty:
        raise ValueError("classes cannot be None")

    data = {
        "nc": len(classes),
        "names": {i: class_name for i, class_name in enumerate(classes)},
        "train": f"{path_to_pictures}/train",
        "val": f"{path_to_pictures}/val",
    }

    with open(path_to_yaml, "w") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
