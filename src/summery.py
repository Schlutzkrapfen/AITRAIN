import os
import pandas as pd
detect_folder = "runs/detect"
def find_best_mAp50_95():
    results = []
    try:
        for folder in sorted(os.listdir(detect_folder)):
            csv_path = os.path.join(folder, 'results.csv')
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()
                try:
                    best = df['metrics/mAP50-95(B)'].max()
                    results.append({'run': folder, 'mAP50-95': round(best, 4)})
                except: pass
        df = pd.DataFrame(results).sort_values('mAP50-95', ascending=False)
        print(df.to_string(index=False))
    except FileNotFoundError:
        print(f"File not found {detect_folder}")



