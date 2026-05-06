import sys
import os

from pathlib import Path

USER_DATA_DIR = 'user_data' 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from controll import check
from split import  split

base_dir = Path("./InputFolder")
input_dir = base_dir / "images"
text_dir = base_dir / "labels"
trash_folder = Path("./Trash")


check(input_dir,text_dir,trash_folder)
split(input_dir,text_dir,trash_folder)
#make_yaml()
#train()