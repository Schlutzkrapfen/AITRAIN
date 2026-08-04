from queue import Empty

from pathlib import Path
import yaml


def get_classes(classes_dir:Path) -> list[str]:
    """
       Read class names from a text file, one class per line.

       Args:
           classes_dir (Path): Path to the text file containing class names,
               with one class name per line.

       Returns:
           list[str]: A list of non-empty, stripped class names read from the file.

       Raises:
           ValueError: If the classes cannot be retrieved (e.g. invalid content
               in the file).
           FileNotFoundError: If the file specified by `classes_dir` does not exist.
       """

    try:
        with open(classes_dir, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except ValueError as e:
        raise ValueError(f"Error can't get classes:{e}")
    except FileNotFoundError:
        raise FileNotFoundError("classes_dir does not exist")


def make_yaml(classes_dir:Path, path_to_yaml:Path=Path("data.yaml"), path_to_pictures:Path=Path("images")):
    """
    Generate a data.yaml configuration file for YOLO training.

    Reads class names from `classes_dir` and writes a YAML file describing
    the dataset structure (number of classes, class names, and paths to
    the training/validation image folders) as expected by YOLO.

    Args:
        classes_dir (Path): Path to the text file containing class names,
            one per line.
        path_to_yaml (str, optional): Output path for the generated YAML
            file. Defaults to "data.yaml".
        path_to_pictures (str, optional): Base path to the images folder,
            used to build the "train" and "val" subdirectory paths.
            Defaults to "images".

    Raises:
        ValueError: If no classes could be retrieved from `classes_dir`.

    Note:
        Writes the YAML file to `path_to_yaml.
    """
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
