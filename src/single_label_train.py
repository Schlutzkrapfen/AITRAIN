import os
import yaml
import shutil
from pathlib import Path
from make_yaml import make_yaml
from split import copy_everything_for_single_traning
from train import train
YOLO_MODEL_FINAL = 'yolov8x.pt'
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

def make_yamls()-> list[Path]:
    folder_paths = make_file_structer("data.yaml")
    paths = []
    for folder in folder_paths:
        single_label = [os.path.basename(folder)]
        folder_path = os.path.join(folder,"data.yaml")
        make_yaml(single_label,folder_path)
        paths.append(folder_path)
    return paths
    


def train_on_each_label():

    yaml_paths = make_yamls()
    
    copy_everything_for_single_traning(Path("images"),Path("labels"))
    for path in yaml_paths:
        train(None,path)
  



