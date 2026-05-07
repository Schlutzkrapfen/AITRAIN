import yaml
def get_classes(classes_dir):
    with open(classes_dir, "r") as f:
        return [line.strip() for line in f if line.strip()]

def make_yaml(classes_dir):
    """Generate data.yaml config file for YOLO training."""
    classes = get_classes(classes_dir)

    data = {
        "nc":    len(classes),
        "names": {i: class_name for i, class_name in enumerate(classes)} , 
        "train": "images/train",
        "val":   "images/val",
    }

    with open("data.yaml", "w") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

