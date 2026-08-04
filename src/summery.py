import os
import pandas as pd
from ultralytics import YOLO

detect_folder = os.path.join(os.path.dirname(__file__), '..', 'runs', 'detect')
detect_folder = os.path.abspath(detect_folder)
def find_best_mAp50_95():
    """
        Find and rank the best mAP50-95 score achieved across all training runs.

        Scans every subfolder inside `detect_folder`, looking for a
        `results.csv` file (as produced by YOLO training) in each one. For
        each run found, extracts the best (maximum) value of the
        'metrics/mAP50-95(B)' column, then prints a table of all runs sorted
        from highest to lowest mAP50-95.

        Note:
            Relies on `detect_folder`, which must be defined in the enclosing
            scope (e.g. as a global variable) — it is not a parameter of this
            function.
        """
    results = []
    try:
        for folder in sorted(os.listdir(detect_folder)):
            csv_path = os.path.join(detect_folder, folder, 'results.csv')
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()
                if 'metrics/mAP50-95(B)' in df.columns:
                    best = df['metrics/mAP50-95(B)'].max()
                    results.append({'run': folder, 'mAP50-95': round(best, 4)})
                else:
                    print(f"Warning: no mAP50-95 column in {csv_path}")

    except FileNotFoundError:
        print(f"Folder not found: {detect_folder}")
        return

    if not results:
        print("No results found.")
        return

    df = pd.DataFrame(results).sort_values('mAP50-95', ascending=False)
    print(df.to_string(index=False))


def find_zero_map_classes():
    """
       Identify, for each training run, which classes achieved zero mAP.

       Iterates through every run subfolder inside `detect_folder`, loads the
       corresponding `best.pt` weights (if present), runs validation with
       Ultralytics YOLO, and collects the class names whose per-class mAP is
       exactly 0. Prints a summary table of all runs, ranked from fewest to
       most zero-mAP classes (best runs first).

       Note:
           Relies on `detect_folder`, which must be defined in the enclosing
           scope (e.g. as a global variable) — it is not a parameter of this
           function.

           Returns early if no valid runs with `best.pt` weights are
           found.
       """
    print(f"Looking in: {detect_folder}")
    results = []

    for run in sorted(os.listdir(detect_folder)):
        run_path = os.path.join(detect_folder, run)

        if not os.path.isdir(run_path):          # skip files like .gitkeep
            continue

        weights_path = os.path.join(run_path, 'weights', 'best.pt')

        if not os.path.exists(weights_path):
            print(f"  Skipping '{run}' — no best.pt")
            continue

        print(f"  Validating '{run}'...")
        model = YOLO(weights_path)
        metrics = model.val(verbose=False)

        class_names = model.names
        maps = metrics.box.maps
        zero_classes = [class_names[i] for i, m in enumerate(maps) if m == 0]

        results.append({
            'run':            run,
            'zero_mAP_count': len(zero_classes),
            'zero_classes':   ', '.join(zero_classes)
        })

    if not results:
        print("No valid runs found.")
        return

    df = pd.DataFrame(results).sort_values('zero_mAP_count', ascending=True)
    print("\n--- Runs ranked by fewest zero-mAP classes (best first) ---")
    print(df.to_string(index=False))

def make_summery():
    """
        Print a full summary of all training runs.

        Convenience wrapper that runs both analyses in sequence:
        1. Ranks all runs by their best mAP50-95 score.
        2. Ranks all runs by number of classes with zero mAP.

        Both results are printed directly to the console."""
    find_best_mAp50_95()
    find_zero_map_classes()
