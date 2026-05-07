import os
import pandas as pd
from ultralytics import YOLO

detect_folder = "runs/detect"
def find_best_mAp50_95():
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
    results = []

    for run in sorted(os.listdir(detect_folder)):
        weights_path = os.path.join(detect_folder, run, 'weights', 'best.pt')
        if not os.path.exists(weights_path):
            continue

        print(f"Validating {run}...")
        model = YOLO(weights_path)
        metrics = model.val(verbose=False)

        # per-class mAP50-95
        class_names = model.names  # {0: 'cat', 1: 'dog', ...}
        maps = metrics.box.maps    # array of mAP50-95 per class

        zero_classes = [class_names[i] for i, m in enumerate(maps) if m == 0]
        results.append({
            'run': run,
            'zero_mAP_count': len(zero_classes),
            'zero_classes': ', '.join(zero_classes)
        })

    df = pd.DataFrame(results).sort_values('zero_mAP_count', ascending=True)
    print("\n--- Runs ranked by fewest zero-mAP classes (best first) ---")
    print(df.to_string(index=False))

def make_summery():
    find_best_mAp50_95()
    find_zero_map_classes()