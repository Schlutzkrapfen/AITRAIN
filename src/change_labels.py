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
    """
        Show a menu for editing labels and loop until the user exits.

        Options:
            "0" -> remove_labels() : delete label(s)
            "1" -> modify_labels() : merge label(s)
            "2" -> return          : exit the menu
            other -> print an error and re-prompt
        """
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
    """Prompts the user for label names/IDs and returns their IDs.

       Repeatedly prompts with `input_text` until valid input is given. Accepts
       a comma-separated list of label names, numeric IDs, or "done" to exit
       early. Invalid entries print an error and re-prompt the user.

       Args:
           labels (dict[str, int]): Mapping of label names to IDs.
           input_text (str): Prompt text shown to the user.
           needs_two (bool, optional): If True, requires at least two unique
               IDs. Defaults to False.

       Returns:
           list[int]: Unique label IDs entered, or `[-1]` if "done" was entered.
       """
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
            numbers =   list(dict.fromkeys(numbers))

            if needs_two and len(numbers) <= 1:
                raise ValueError("Needs more than one number")

            return numbers
        except ValueError as e:
            print(f"{e} try again")

def modify_nubers_from_labels(numbers:list[int],paths:set[Path]):
    """
    Reassigns one or more class labels to a target label across label files.

       Takes the first element of `numbers` as the target class ID. For every
       other number in the list (processed in descending order), it rewrites
       matching class IDs to the target value in each label file, and
       decrements any class ID greater than the current number by 1 to keep
       IDs contiguous after the merge.

       Args:
           numbers (list[int]): A list of class IDs. The first element is the
               target ID that subsequent IDs will be merged into. The
               remaining elements are the IDs to be replaced.
           paths (set[Path]): A set of file paths to label files, where each
               line starts with an integer class ID followed by other
               space-separated values.
    """

    target = numbers[0]
    numbers = sorted(numbers[1:], reverse=True)
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
                       parts[0] = str(target)
                       updated_lines.append(" ".join(parts))
                   else:
                       parts[0] = str(class_id - 1)
                       updated_lines.append(" ".join(parts))

               with open(path, "w") as f:
                   _written = f.write("\n".join(updated_lines) + "\n" if updated_lines else "")
                   print(f"Updated labels in {path}")


def remove_numbers_from_labes(numbers: list[int], paths: set[Path]):
    """Removes one or more class labels from label files.

        For each path, iterates over the given class IDs in descending order
        and removes any line whose class ID matches. Class IDs greater than
        the removed ID are decremented by 1 to keep the remaining IDs
        contiguous.

        Args:
            numbers (list[int]): A list of class IDs to remove from the label
                files.
            paths (set[Path]): A set of file paths to label files, where each
                line starts with an integer class ID followed by other
                space-separated values.
    """
    numbers = sorted(numbers, reverse=True)
    for path in paths:
        for number in numbers:
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
    """
        Read only the "names" dict from the YAML file.

        Args:
            path: Path to the YAML file. Defaults to "data.yaml".

        Returns:
            The names in dict[int, str] format.

        Note:
            Expects the YAML file to have a "names" key in
            dict[int, str] format.
        """
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

    write_yaml(updated_lines,len(targets), path)


def remove_numbers_from_yaml(numbers: list[int], path: str = "data.yaml"):
    """
        Remove the given class indices from a YAML label file and
        re-index the remaining classes so numbering stays contiguous.

        Loads the "names" mapping from `path`, deletes the entries whose
        keys are in `numbers`, then shifts each remaining key down by the
        number of removed keys smaller than it (so indices stay
        consecutive with no gaps). The result is written back via
        write_yaml(), which also decreases "nc" by the number of removed
        classes.

        Args:
            numbers: List of class indices to remove.
            path: Path to the YAML file. Defaults to "data.yaml".

        Note:
            Removed keys are not renumbered/kept; they are dropped
            entirely, and all keys above a removed one shift down by 1
            for each smaller removed key.
        """
    names:dict[int,str] =  load_names(path)
    updated_lines:dict[int,str] = {}
    targets = sorted(numbers)
    for key, value in names.items():
        if key in targets:
                # Skip/delete this key
                continue

        shift = sum(1 for num in targets if num < key)
        updated_lines[key - shift] = value
    write_yaml(updated_lines,len(targets) ,path)



def write_yaml(names:dict[int,str],target_amount:int ,path:str= "data.yaml"):
    """
       Write an updated "names" mapping to a YAML file and adjust "nc".

       Reads the existing YAML file at `path`, replaces its "names" key
       with `names`, decreases "nc" (class count) by `target_amount`,
       and overwrites the file with the updated data.

       Args:
           names: New mapping of class index -> class name to store.
           target_amount: Number to subtract from the existing "nc" value.
           path: Path to the YAML file. Defaults to "data.yaml".

       Note:
           Assumes the YAML file already contains an "nc" key that can
           be converted to int.
       """
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}

    data["names"] = names
    data["nc"] = int(data["nc"])-target_amount

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
    """
    Interactively merge two or more labels into one.

    Prompts the user for labels to merge (first entry is the target,
    others get merged into it). If the user enters 'done' ([-1]),
    the merge is skipped.

    Otherwise, collects label files under "labels/train" and
    "labels/val", remaps merged labels via modify_numbers_from_yaml(),
    then removes the now-unused indices via remove_numbers_from_yaml().
    """
    labels: dict[str, int] = _load_name_to_id()
    print(labels)
    number: list[int] = get_input(
        labels,
        "Which label do you want to combine (name(s) or number(s), or 'done') with ',' split the numbers or names, the first name will be used :\n as an example if you give as input 2,0 .0 will be changed to 2  ",
    )

    if number == [-1]:
        print("skipped")
        return
    print(number)
    paths: set[Path] = get_label_path(Path("labels/train"))
    paths.update(get_label_path(Path("labels/val")))
    modify_nubers_from_labels(number,paths)

    remove_numbers_from_yaml(number[1:])
