import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from change_labels import change_labels
from controll import check_files_exist
from make_yaml import make_yaml
from split import split
from summery import make_summery
from train_starter import start_train


USER_DATA_DIR = "user_data"


base_dir = Path("./InputFolder")
input_dir = base_dir / "images"
text_dir = base_dir / "labels"
trash_folder = Path("./Trash")
classes_dir = base_dir / "classes.txt"

MENU = """
What do you want to do?
  0 (default) - Everything (1-5)
  1 - Check if there are Input Files
  2 - Split up the Input Files
  3 - Delete/Merges Labels
  4 - Train
  5 - Get a Summary
  6 - Quit
"""

def main():
    """Main Programm"""
    while True:
        answer = input(MENU).strip()
        print(f"You chose: {answer}")

        match answer:
            case "0":
                if check_files_exist(input_dir, text_dir, trash_folder):
                    split(input_dir, text_dir, trash_folder)
                    make_yaml(classes_dir)

                start_train()
                make_summery()
                print("finished")
                print("closing")
                break
            case "1":
                _bool =  check_files_exist(input_dir, text_dir, trash_folder)

            case "2":
                if check_files_exist(input_dir, text_dir, trash_folder):
                    split(input_dir, text_dir, trash_folder)
                    make_yaml(classes_dir)
            case "3":
                change_labels()
            case "4":
                start_train()
            case "5":
                make_summery()
            case "6":
                break
            case _:
                print(f"Invalid input '{answer}'. Please enter a number between 0 and 5.\n")
                continue
        print("finished")
        answer = (
            input("Do you want to do something else. N no, y yes: ").strip().lower()
        )
        if answer != "y":
            print("closing")
            break


if __name__ == "__main__":
    main()
