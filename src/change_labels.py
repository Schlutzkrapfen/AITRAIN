from pathlib import Path
import yaml

from helper_functions import _load_name_to_id, get_label_path

TRAIN_MENU = """
How you want to change labels:
    0 - Delete Label(s)
    1 - Merge Label(s)
    2 - Finish
"""


def change_labels():
    while True:
        answer = input(TRAIN_MENU).strip()
        match answer:
            case "0":
                remove_labels()
            case "1":
                modify_labels()
            case "2":
                return
            case _:
                print("Error: not a valid input")
                continue


def get_input(labels: dict[str, int], input_text: str,needs_two:bool= False) -> list[int]:
    while True:
        answers = input(input_text).strip().split(",")
        numbers: list[int] = []
        try:
            for answer in answers:
                answer = answer.strip()
                if answer.lower() == "done":
                    return [-1]

                if answer in labels:
                    name: str = answer
                    number: int = labels[name]
                    numbers.append(number)

                elif answer.isdigit():
                    number = int(answer)
                    matches: list[str] = [n for n, i in labels.items() if i == number]
                    if not matches:
                        raise ValueError(f"No label with id {number} found.")
                    name = matches[0]
                    numbers.append(number)
                else:
                    raise ValueError(f"Not a valid name or number: {answer}")
            numbers =  list(set(numbers))

            if needs_two and len(numbers) <= 1:
                raise ValueError("Needs more than one number")

            return numbers
        except ValueError as e:
            print(f"{e} try again")


def remove_numbers_from_labes(numbers: list[int], paths: set[Path]):
    for number in numbers:
        for path in paths:
            with open(path, "r") as f:
                lines = f.readlines()

            updated_lines: list[str] = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts: list[str] = line.split()
                class_id: int = int(parts[0])

                if class_id < number:
                    updated_lines.append(line)
                elif class_id == number:
                    continue
                else:
                    parts[0] = str(class_id - 1)
                    updated_lines.append(" ".join(parts))

            with open(path, "w") as f:
                _written = f.write("\n".join(updated_lines) + "\n" if updated_lines else "")
                print(f"Updated labels in {path}")

def load_names(path: str = "data.yaml") -> dict[int,str]:
    """Read only the names dict from the yaml file."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)


    return data["names"]

def modify_numbers_from_yaml(numbers: list[int], path: str = "data.yaml"):
    """Replaces target names with a master label and shifts remaining keys down.

        Args:
            numbers: A list where the first element is the source index (master),
                and all subsequent elements are target indices to be overwritten.
            path: The file path to the YAML file.
        """
    names:dict[int,str] =  load_names(path)
    updated_lines:dict[int,str] = {}
    targets = sorted(numbers[1:])
    for key, value in names.items():
        if key in targets:
            updated_lines[key] = names[numbers[0]]
            continue


        shift = sum(1 for num in targets if num < key)
        updated_lines[key - shift] = value

    write_yaml(updated_lines, path)


def remove_numbers_from_yaml(numbers: list[int], path: str = "data.yaml"):
    names:dict[int,str] =  load_names(path)
    updated_lines:dict[int,str] = {}
    targets = sorted(numbers)
    for key, value in names.items():
        if key in targets:
                # Skip/delete this key
                continue

        shift = sum(1 for num in targets if num < key)
        updated_lines[key - shift] = value
    write_yaml(updated_lines, path)



def write_yaml(names:dict[int,str], path:str= "data.yaml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}

    data["names"] = names

    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False)


def remove_labels():
    """Interactively prompts the user to delete specific labels from the dataset.

        Loads current labels, asks the user for the names or IDs of the labels to
        remove, and updates both the label text files (train/val) and the configuration YAML.
        """
    labels: dict[str, int] = _load_name_to_id()
    print(f"Attention the labels are order first the Name than the ID \n{labels}")
    number: list[int] = get_input(
        labels,
        "Which label do you want to delete (name(s) or number(s), or 'done') with ',' split the numbers or names : ",
    )
    if number == [-1]:
        print("skipped")
        return
    paths: set[Path] = get_label_path(Path("labels/train"))
    paths.update(get_label_path(Path("labels/val")))
    remove_numbers_from_labes(number, paths)
    remove_numbers_from_yaml(number)

def modify_labels():
    labels: dict[str, int] = _load_name_to_id()
    print(labels)
    number: list[int] = get_input(
        labels,
        "Which label do you want to combine (name(s) or number(s), or 'done') with ',' split the numbers or names, the first name will be used :\n as an example if you give as input 2,0 .0 will be changed to 2  ",
    )

    if number == [-1]:
        print("skipped")
        return
    paths: set[Path] = get_label_path(Path("labels/train"))
    paths.update(get_label_path(Path("labels/val")))

    remove_numbers_from_yaml(number[1:])
