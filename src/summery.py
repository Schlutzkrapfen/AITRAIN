import os
import pandas as pd
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



