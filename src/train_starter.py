
from train import train,train_with_imporfment

from single_label_train import train_on_each_label,train_on_single_label
TRAIN_MENU = """
What do you want to train:
    0 - Single Run
    1 - Hypertune the Run
    2 - Every Label and splitt up the folder
    3 - A Single Label
    4 - Done(Return)

"""
def start_train():
    """Displays a menu for selecting a training mode and runs it.

        Prompts the user to choose between a single training run,
        hyperparameter tuning, training on every label with folder
        splitting, or training on a single label. Repeats until a
        valid option is selected and executed, or the user chooses
        to exit.
        """
    while True:
        print("War: Training is in Devolpment is not finished")
        answer_train = input(TRAIN_MENU).strip()
        match answer_train:
            case "0":
                train()
            case "1":
                train_with_imporfment()
            case "2":
                train_on_each_label()
            case "3":
                train_on_single_label()
            case "4":
                print("Exiting")
                break
            case _:
                print("Error: not a valid input")
                continue

        break
