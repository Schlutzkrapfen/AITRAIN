import re
import shutil
from pathlib import Path

import yaml

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def get_images_path(directory: Path) -> set[Path]:
    """Finds all image file paths in a directory.

        Filters for files ending in common image extensions (.png, .jpg, .jpeg).

        Args:
            directory: The Path object pointing to the directory to search.

        Returns:
            A set of Path objects for all matching image files.
        """
    return {f for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}


def get_label_path(directory: Path) -> set[Path]:
    """Finds all label file paths in a directory.

        Filters specifically for files with a .txt extension.

        Args:
            directory: The Path object pointing to the directory to search.

        Returns:
            A set of Path objects for all matching text label files.
        """
    return {f for f in directory.iterdir() if f.suffix.lower() == ".txt"}


def get_images_names(directory: Path) -> set[Path]:
    """Finds all image file paths in a directory.

        Filters for files ending in common image extensions (.png, .jpg, .jpeg).

        Args:
            directory: The Path object pointing to the directory to search.

        Returns:
            A set of Path objects for all matching image files.
        """
    return {f for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS}



def get_text_files_names(directory: Path) -> set[Path]:
    """Extracts the base names (without extensions) of all text files in a directory.

        Args:
            directory: The Path object pointing to the directory to search.

        Returns:
            A set of Path objects containing only the base filenames of the .txt files.
        """
    test:set[Path] = set()
    for f in directory.iterdir():
        if f.suffix.lower() == ".txt":
            test.add(Path(f.name[: -len(f.suffix)]))
    return test


def move_to_trash_folder(paths:list[Path], trash_folder: Path, name: str = "file"):

    """moves file to a (trash) folder"""
    if not isinstance(paths, list):
        paths = [paths]
    for path in paths:
        if path.is_file():
            trash_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), trash_folder / path.name)
        else:
            print(f"ERROR: {path} not found")
    print(f"moved every {name} to {trash_folder}")


def get_label_from_ordered(path_to_labels: Path) -> list[Path]:
    """Returns all Labels that are alrady in a val and Train folder from the path_to_labels they are sorted"""
    labels_set = get_label_path(path_to_labels / "val").union(
        get_label_path(path_to_labels / "train")
    )
    labels = sorted(list(labels_set))
    return labels


def get_images_from_ordered(path_to_pictures: Path) -> list[Path]:
    """Returns all images that are alrady in a val and Train folder from the path_to_pictures they are sorted"""
    images_set = get_images_path(path_to_pictures / "val").union(
        get_images_path(path_to_pictures / "train")
    )
    images = sorted(list(images_set))
    return images


def get_classnames(labels:list[Path], yaml_path: str) -> list[str]:
    """Extracts unique class IDs from label files and maps them to their names via a YAML file.

    Args:
        labels: A list of file paths to the label text files.
        yaml_path: The file path to the dataset YAML configuration file.

    Returns:
        A nested list where each sublist contains the string class names found
        in the corresponding label file.
    """
    unique_ids:list[list[int]] = []
    for label_path in labels:
        try:
            all_class_ids:list[int] = []
            with open(label_path, "r") as file:
                for line in file:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        class_id = cleaned_line.split()[0]
                        all_class_ids.append(int(class_id))

            unique_ids.append(list(set(all_class_ids)))

        except FileNotFoundError:
            print(f"Could not find file: {label_path}")

    with open(yaml_path, "r") as file:
        dataset_info = yaml.safe_load(file)

    class_mapping = dataset_info.get("names", {})
    class_names = []
    for ids in unique_ids:
        class_names.append([class_mapping.get(id, f"Unknown-{id}") for id in ids])
    return class_names


def change_yaml_to_id_output(text: str, yaml_path: str = "data.yaml") -> int:
    """Converts a class name string to its integer ID from a YAML config."""
    return _load_name_to_id(yaml_path).get(text, -1)


def _load_name_to_id(yaml_path: str = "data.yaml") -> dict[str, int]:
    """loads every label out of the yaml file"""
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return {v: k for k, v in data["names"].items()}


def sanitize_folder_name(name: str):
    """Replace / and other invalid path characters with an underscore"""
    return re.sub(r'[<>:"/\\|?*]', "_", name)
