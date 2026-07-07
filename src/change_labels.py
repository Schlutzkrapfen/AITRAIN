from ast import While

from helper_functions import _load_name_to_id

TRAIN_MENU = """
How you want to change labels:
    0 - Delete Label(s)
    1 - Merge Label(s)
    2 - Finish
"""
VALID_CHOICES = {"0", "1", "2"}


def change_labels():
    while True:
        answer = input(TRAIN_MENU).strip()
        if answer not in VALID_CHOICES:
            print("Error: not a valid input")
            continue
        match answer:
            case "0":
                remove_labels()
            case "1":
                pass
            case "2":
                return


def get_input(labels: dict[str, int], input_text: str) -> list[int]:
    while True:
        answers = input(input_text).strip().split()
        numbers = []
        try:
            for answer in answers:
                if answer.lower() == "done":
                    return [-1]

                if answer in labels:
                    name = answer
                    number = labels[name]
                    numbers.append(number)

                elif answer.isdigit():
                    number = int(answer)
                    matches = [n for n, i in labels.items() if i == number]
                    if not matches:
                        raise ValueError(f"No label with id {number} found.")
                        continue
                    name = matches[0]
                    numbers.append(number)
                else:
                    raise ValueError(f"Not a valid name or number: {answer}")

            return numbers
        except ValueError as e:
            print(f"{e} try again")


def remove_labels():
    labels = _load_name_to_id()
    print(labels)
    number = get_input(
        labels, "Which label do you want to delete (name or number, or 'done'): "
    )
    if number == [-1]:
        return
