import os
import yaml
from make_yaml import make_yaml
def make_file_structer(yaml_path):

    os.makedirs("./single_label_runs", exist_ok=True) 
    folder_paths = []
    with open(yaml_path) as stream:
        try:
            for items in yaml.safe_load(stream)["names"].values():
                target_path = f"single_label_runs/{items}"
                os.makedirs(target_path,exist_ok=True)
                folder_paths.append(target_path)
        except yaml.YAMLError as exc:
            print(exc)
    return folder_paths
def make_yamls():
    folder_paths = make_file_structer("data.yaml")
    for folder in folder_paths:
        single_label = [os.path.basename(folder)]
        folder_path = os.path.join(folder,"data.yaml")
        make_yaml(single_label,folder_path)

