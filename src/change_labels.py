from pathlib import Path

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
                pass
            case "2":
                return
            case _:
                print("Error: not a valid input")
                continue


def get_input(labels: dict[str, int], input_text: str) -> list[int]:
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


def remove_numbers_from_yaml(numbers: list[int], path: str = "data.yaml"):
    for _number in numbers:
        with open(path, "r") as f:
            pass


def remove_labels():
    labels: dict[str, int] = _load_name_to_id()
    print(labels)
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
