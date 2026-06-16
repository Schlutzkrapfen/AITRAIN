import yaml


def get_classes(classes_dir):
    try:
        with open(classes_dir, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error:{e}")
        return classes_dir


def make_yaml(classes_dir, path_to_yaml="data.yaml", path_to_pictures="images"):
    """Generate data.yaml config file for YOLO training."""
    classes = get_classes(classes_dir)
    if classes is None:
        ValueError

    data = {
        "nc": len(classes),
        "names": {i: class_name for i, class_name in enumerate(classes)},
        "train": f"{path_to_pictures}/train",
        "val": f"{path_to_pictures}/val",
    }

    with open(path_to_yaml, "w") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
