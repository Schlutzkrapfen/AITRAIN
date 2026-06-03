import os
import yaml
import shutil
from make_yaml import make_yaml
def make_file_structer(yaml_path):
    os.makedirs("./single_label_runs", exist_ok=True) 
    folder_paths = []
    with open(yaml_path) as stream:
        try:
            for items in yaml.safe_load(stream)["names"].values():
                target_path = f"single_label_runs/{items}"
                os.makedirs(target_path,exist_ok=True)
                os.makedirs(os.path.join(target_path,"images/train"),exist_ok=True )
                os.makedirs(os.path.join(target_path,"images/val"),exist_ok=True )
                os.makedirs(os.path.join(target_path,"label/train"),exist_ok=True )
                os.makedirs(os.path.join(target_path,"label/val"),exist_ok=True )
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


def train_on_each_label():
    pass



