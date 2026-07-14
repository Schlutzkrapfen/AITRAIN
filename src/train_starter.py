
from train import train

from single_label_train import train_on_each_label,train_on_single_label
TRAIN_MENU = """
What do you want to train:
    0 - Single Run
    1 - Every Label and splitt up the folder
    2 - A Single Label

"""
def start_train():
    while True:
                        print("War: Training is in Devolpment is not finished")
                        answer_train = input(TRAIN_MENU).strip()

                        match answer_train:
                            case "0":
                                train()
                            case "1":
                                train_on_each_label()
                            case "2":
                                train_on_single_label()
                            case _:
                                print("Error: not a valid input")
                                continue

                        break
