from mpmath import re

TRAIN_MENU = """
Do you want to change labels:
    0 - Delete Label(s)
    1 - Merge Label(s)
    2 - Finish
"""
VALID_CHOICES = {"0", "1", "2"}


def change_labels(classes_file: str):
    while True:
        answer = input(TRAIN_MENU).strip()
        if answer not in VALID_CHOICES:
            print("Error: not a valid input")
            continue
        match answer:
            case "0":
                remove_labels(classes_file)
            case "1":
                pass
            case "2":
                return


def remove_labels(classes_file: str):
    print("which Label do you want to delete:")
    file = open(classes_file, "r")
    for lines in file:
        print(lines)
