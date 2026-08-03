
from train import train,train_with_imporfment

from single_label_train import train_on_each_label,train_on_single_label
TRAIN_MENU = """
What do you want to train (add "t" after the number, e.g. "0t", to run a
quick test: faster, lighter, and a "n" if you don't need a GPU):
    0 - Single Run
    1 - Hypertune the Run
    2 - Every Label and split up the folder
    3 - A Single Label
    4 - Done (Return)

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
        choice = answer_train
        flags = ""
        while choice and choice[-1] in "tn":
            flags += choice[-1]
            choice = choice[:-1]

        test_run = "t" in flags
        no_gpu = "n" in flags

        match choice:
            case "0":
                train(test_run=test_run,no_gpu=no_gpu)
            case "1":
                train_with_imporfment()
            case "2":
                train_on_each_label(test_run=test_run)
            case "3":
                train_on_single_label(test_run=test_run)
            case "4":
                print("Exiting")
                break
            case _:
                print("Error: not a valid input")
                continue

        break
