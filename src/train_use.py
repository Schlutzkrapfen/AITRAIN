#class YAMLFILE()
import os
from pathlib import Path
from ultralytics import YOLO
import ultralytics


INPUT_FOLDER: Path = Path("./InputFolder/test")
RESULT_FOLDER: Path = Path("./result")
AI_FOLDER: Path = Path("./runs/detect")
AI_POSITION:Path = Path("./weights")
AI_GET_TEXT = """Which Ai Modell do you want (write done if you want to break): """
MENU ="""What do you want to do:
0: Use a test folder end add boxes
1: Make a Picture for each label the Ai finds. (This makes more sense when the Modell hasen't had the same labels as they are now )
2: Done
    """
def get_correct_cls(names: dict, cls: int, classes_txt: Path) -> int:
    """
        Find the line number of a class name in a classes.txt file.

        Looks up the name for `cls` in `names`, then searches `classes_txt`
        line by line for a matching name (whitespace-stripped).

        Args:
            names: Mapping of class index -> class name.
            cls: Key into `names` for the class to look up.
            classes_txt: Path to a text file with one class name per line.

        Returns:
            The 0-indexed line number in `classes_txt` matching `names[cls]`.

        Raises:
            ValueError: If no matching line is found.
        """

    with open(classes_txt, "rt") as myfile:
        for i, myline in enumerate(myfile):
            if myline.strip() == str(names[cls]).strip():
                return i
    raise ValueError("Something went wrong")


def try_ai(yolo_model: YOLO, input: Path, output_folder: Path =Path("./Results")):
    """
    Run YOLO object detection on an image and save the results.

    Runs inference on the given image, writes the detected bounding boxes
    (in normalized xywh format, one per line, prefixed by class id) to a
    .txt file named after the input image, and saves an annotated copy of
    the image if any detections were found.

    Args:
        yolo_model (YOLO): The yolo Model.
        input (Path): Path to the input image.
        output_folder (Path): Folder where the label .txt file and the
            annotated image will be saved. Defaults to "./Results".
    """
    classes_txt = make_classes_file(yolo_model.names, output_folder)
    filename, _ = os.path.splitext(os.path.basename(input))
    save_path: Path = Path( os.path.join(output_folder, f"labels/{filename}.txt"))
    results: list[ultralytics.engine.results.Results] = yolo_model(input, save_txt=None)
    with open(save_path, "a") as file:
        for idx, prediction in enumerate(results[0].boxes.xywhn):
            cls = int(results[0].boxes.cls[idx].item())
            file.write(
                f"{get_correct_cls(yolo_model.names, cls, classes_txt)} {prediction[0].item()} {prediction[1].item()} {prediction[2].item()} {prediction[3].item()}\n"
            )

    if not results or len(results[0].boxes) <= 0:
        print(f"No detections for {input}")
        return

    results[0].save(os.path.join(output_folder, "images/", os.path.basename(input)))

def find_Model(answer: str) -> YOLO:
    folder = AI_FOLDER / answer
    if not folder.exists() or not folder.is_dir():
        raise ValueError("No folder found with this name")

    yolo_models_found: list[Path] = list(folder.rglob("*.pt"))

    if len(yolo_models_found) <= 0:
        raise ValueError("No YOLO file found in folder")

    if len(yolo_models_found) == 1:
        return YOLO(yolo_models_found[0])

    while True:
        ans = input(
            f"Which model should you use, give a number for (type done for returning): {yolo_models_found}"
        ).strip()
        if ans.lower() == "done":
            raise ValueError("Exited by user")
        if not ans.isdigit():
            print("Not a valid number, try again")
            continue
        elif  int(ans) >= len(yolo_models_found):
            print("to big of a number, try again")
            continue
        number = int(ans)
        print(f"You chose number {number} and model {yolo_models_found[number]}")
        return YOLO(yolo_models_found[number])


def get_ai() -> list[YOLO]:
    while (True):
        folders = [f.name for f in AI_FOLDER.iterdir() if f.is_dir()]

        answer = input(f"{AI_GET_TEXT} {folders}").strip()
        if answer.lower()== "done":
            raise ValueError("Exitided by user")
        try:
            return [find_Model(answer)]
        except ValueError as e:
            print(f"Wrong input: {e}")
            continue



def ai_with_input_folder():
    make_folder_structer(output_folder=RESULT_FOLDER)
    try:
        models = get_ai()
    except ValueError as e:
        print(e)
        return
    for yolo_model in models:
        make_classes_file(yolo_model.names, RESULT_FOLDER)
        for image_file in os.listdir(INPUT_FOLDER):
            _, end = os.path.splitext(os.path.basename(image_file))
            if end != ".jpg" and end != ".png":
                continue
            image_path = Path(os.path.join(INPUT_FOLDER, image_file))

            try_ai(yolo_model, image_path, RESULT_FOLDER)

def cut_input_pictures():
    try:
       models = get_ai()
    except ValueError as e:
        print(e)
        return

def use_train():
    while(True):
       answer =  input(MENU).strip()
       match answer:
           case "0":
               ai_with_input_folder()
               return
           case "1":
               cut_input_pictures()
               return
           case "2":
               return
           case _:
               print("Not a valid number, try again")
               continue






def make_classes_file(names: dict[int,str], output_folder: Path) -> Path:
    """
        Create or update a classes.txt file listing label names.

        Writes each name from `names` to `classes.txt` inside `output_folder`,
        one per line. If the file already exists, its existing entries are
        preserved and only names not already present are appended, avoiding
        duplicates.

        Args:
            names: Dictionary mapping label ids (int) to label names (str).
            output_folder: Path to the folder where classes.txt is
                created or updated.

        Returns:
            Path: The path to the classes.txt file.
        """
    save_path: str = os.path.join(output_folder, "classes.txt")

    existing: set[str] = set()

    if os.path.isfile(save_path):
        with open(save_path, "rt") as myfile:
            existing = {line.strip() for line in myfile}
    with open(save_path, "a") as file:
        for idx in sorted(names.keys()):
            name = names[idx]
            if name.strip() in existing:
                continue
            file.write(f"{name}\n")

            existing.add(name)
    return Path(save_path)


def make_folder_structer(output_folder: Path, delete_files: bool = True):
    """Create the output folder structure for results.

    Creates the given output folder (if it doesn't already exist) along
    with two subfolders inside it: "labels" and "images".

    Args:
        output_folder (str): Path to the base output folder.
        """
    labels_path: str = os.path.join(output_folder, "labels")
    if delete_files and os.path.isfile(os.path.join(output_folder, "classes.txt")):
        for images_file in os.listdir(labels_path):
            os.remove(os.path.join(labels_path, images_file))
        os.remove(os.path.join(output_folder, "classes.txt"))
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(labels_path, exist_ok=True)
    os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
