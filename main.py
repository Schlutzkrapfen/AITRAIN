import os
import sys
from pathlib import Path

USER_DATA_DIR = "user_data"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from controll import check_files_exist
from make_yaml import make_yaml
from single_label_train import train_on_each_label, train_on_single_label
from split import split
from summery import make_summery
from train import train

base_dir = Path("./InputFolder")
input_dir = base_dir / "images"
text_dir = base_dir / "labels"
trash_folder = Path("./Trash")
classes_dir = base_dir / "classes.txt"

MENU = """
What do you want to do?
  0 (default) - Everything (1-4)
  1 - Check if there are Input Files
  2 - Split up the Input Files
  3 - Train
  4 - Get a Summary
  5 - Quit
"""

TRAIN_MENU = """
What do you want to train:
    0 - Single Run
    1 - Every Label and splitt up the folder
    2 - A Single Label

"""

VALID_CHOICES = {"0", "1", "2", "3", "4", "5", ""}
VALID_CHOICES_TRAIN = {"0", "1", "2"}


def main():
    while True:
        while True:
            answer = input(MENU).strip()

            if answer in VALID_CHOICES:
                answer = answer if answer != "" else "0"
                break

            print(f"Invalid input '{answer}'. Please enter a number between 0 and 5.\n")

        print(f"You chose: {answer}")

        match answer:
            case "0":
                if check_files_exist(input_dir, text_dir, trash_folder):
                    split(input_dir, text_dir, trash_folder)
                    make_yaml(classes_dir)
                # train()
                make_summery()
                print("finished")
                print("closing")
                break
            case "1":
                check_files_exist(input_dir, text_dir, trash_folder)
            case "2":
                if check_files_exist(input_dir, text_dir, trash_folder):
                    split(input_dir, text_dir, trash_folder)
                    make_yaml(classes_dir)
            case "3":
                while True:
                    print("War: Training is in Devolpment is not finished")
                    answer_train = input(TRAIN_MENU).strip()

                    if answer in VALID_CHOICES_TRAIN:
                        break
                    match answer_train:
                        case "0":
                            train()
                        case "1":
                            train_on_each_label()
                        case "2":
                            train_on_single_label()

            case "4":
                make_summery()
            case "5":
                break
        print("finished")
        answer = (
            input("Do you want to do something else. N no, y yes: ").strip().lower()
        )
        if answer != "y":
            print("closing")
            break


if __name__ == "__main__":
    main()
