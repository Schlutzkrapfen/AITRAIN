import sys
import os

from pathlib import Path

USER_DATA_DIR = 'user_data' 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from controll import check_files_exist
from split import  split
from make_yaml  import make_yaml
from summery import find_best_mAp50_95


base_dir = Path("./InputFolder")
input_dir = base_dir / "images"
text_dir = base_dir / "labels"
trash_folder = Path("./Trash")
classes_dir =  base_dir/"classes.txt"

MENU = """
What do you want to do?
  0 (default) - Everything (1-4)
  1 - Check if there are Input Files
  2 - Split up the Input Files
  3 - Train
  4 - Get a Summary
"""

VALID_CHOICES = {"0", "1", "2", "3", "4", ""}
def main():
    while True:
        while True:
            answer = input(MENU).strip()

            if answer in VALID_CHOICES:
                answer = answer if answer != "" else "0" 
                break

            print(f"Invalid input '{answer}'. Please enter a number between 0 and 4.\n")

        print(f"You chose: {answer}")

        match answer:
            case "0" :
                if check_files_exist(input_dir,text_dir,trash_folder):
                    split(input_dir,text_dir,trash_folder)
                    make_yaml(classes_dir)
                #train()
                find_best_mAp50_95()
                print("finished")
                print("closing")
                break
            case "1":
                check_files_exist(input_dir,text_dir,trash_folder)
            case "2":
                if check_files_exist(input_dir,text_dir,trash_folder):
                    split(input_dir,text_dir,trash_folder)
                    make_yaml(classes_dir)
            case "3":
                print("Training is currently unavailable.")
            case "4":
                find_best_mAp50_95()
        print("finished")
        answer = input("Do you want to do something else. N no, y yes: ").strip().lower()
        if answer != "y":
            print("closing")
            break

if __name__ == "__main__":
    main()