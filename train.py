import optuna
import json
import os
import csv
from datetime import datetime
from ultralytics import YOLO


trails = 300
epochs_param_finding = 300

# ── Log file setup ────────────────────────────────────────────────────────────
LOG_FILE = 'trials_log.csv'
SUMMARY_FILE = 'trials_summary.json'


# Create CSV with header
with open(LOG_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'trial_num', 'mAP50', 'run_folder',
        'hsv_v', 'degrees', 'translate', 'scale', 'shear',
        'fliplr', 'mosaic', 'erasing',
        'lr0', 'lrf', 'cls', 'box',
        'duration_min', 'timestamp'
    ])

all_trials_data = []

def objective(trial):
    start_time = datetime.now()
    model = YOLO('yolov8n.pt')  

    params = dict(
    hsv_v     = trial.suggest_float('hsv_v',     0.1,  0.25),
    degrees   = trial.suggest_float('degrees',   0,    5),
    translate = trial.suggest_float('translate', 0.05, 0.2),
    scale     = trial.suggest_float('scale',     0.04, 0.30),  # keep wide, trial 338 proves it
    shear     = trial.suggest_float('shear',     0.0,  5.0),   # loosened back, 280 shows mid-high can work
    fliplr    = trial.suggest_float('fliplr',    0.2,  0.5),
    mosaic    = trial.suggest_float('mosaic',    0.03, 0.25),
    erasing   = trial.suggest_float('erasing',   0.1,  0.5),   # kept wide, insufficient data
    lr0       = trial.suggest_float('lr0',       5e-5, 5e-4, log=True),  # most confident change
    lrf       = trial.suggest_float('lrf',       0.001,0.08, log=True),  # loosened, trial 280 shows low lrf works
    cls       = trial.suggest_float('cls',       2.3,  3.2),   # now confident enough to tighten
    box       = trial.suggest_float('box',       4.5,  7.0),   # 8 trials all under 5.7
)

    results = model.train(
        data='data.yaml',
        epochs=epochs_param_finding,
        imgsz=1280,
        batch=6,
        patience=50,
        verbose=False,
        hsv_h=0.0,
        hsv_s=0.0,
        flipud=0.0,
        cutmix=0.0,
        auto_augment=False,
        optimizer='AdamW',
        **params,
    )

    mAP50 = results.results_dict['metrics/mAP50(B)']
    duration = (datetime.now() - start_time).total_seconds() / 60
    run_folder = str(results.save_dir)

    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            trial.number, round(mAP50, 6), run_folder,
            *[round(params[k], 6) for k in params],
            round(duration, 2),
            start_time.strftime('%Y-%m-%d %H:%M:%S')
        ])

    run_info = {
        'trial_number': trial.number,
        'mAP50': mAP50,
        'duration_minutes': round(duration, 2),
        'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'is_best': False,
        'params': params,
        'fixed_params': {
            'hsv_h': 0.0, 'hsv_s': 0.0, 'flipud': 0.0,
            'cutmix': 0.0, 'auto_augment': False, 'optimizer': 'AdamW',
            'epochs': epochs_param_finding, 'imgsz': 1280, 'batch': 6, 'patience': 50
        },
        'all_metrics': results.results_dict
    }

    with open(os.path.join(run_folder, 'trial_info.json'), 'w') as f:
        json.dump(run_info, f, indent=2)  

    all_trials_data.append(run_info)

    print(f"\n✅ Trial {trial.number:>3} | mAP50: {mAP50:.4f} | "
          f"lr0: {params['lr0']:.5f} | box: {params['box']:.2f} | "
          f"folder: {run_folder} | {duration:.1f} min")

    return mAP50

# ── Run the hyperparameter search ─────────────────────────────────────────────
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=1)

# ── Mark the best trial in its trial_info.json ────────────────────────────────
best_num = study.best_trial.number
runs_dir = 'runs/detect'

for folder in os.listdir(runs_dir):
    info_path = os.path.join(runs_dir, folder, 'trial_info.json')
    if os.path.exists(info_path):
        with open(info_path, 'r') as f:
            info = json.load(f)
        if info.get('trial_number') == best_num:
            info['is_best'] = True
            with open(info_path, 'w') as f:
                json.dump(info, f, indent=2)

# ── Save global summary of all trials sorted by mAP50 ────────────────────────
summary = {
    'best_trial': best_num,
    'best_mAP50': study.best_value,
    'best_params': study.best_params,
    'total_trials': len(study.trials),
    'all_trials': sorted(all_trials_data, key=lambda x: x['mAP50'], reverse=True)
}

with open(SUMMARY_FILE, 'w') as f:
    json.dump(summary, f, indent=2)

# ── Final training using the best hyperparameters found ───────────────────────
best = study.best_params
model =  YOLO('yolov8x.pt')
model.train(
    data='data.yaml',
    epochs=1000,
    patience=300,
    batch=6,
    imgsz=1280,
    **best,
    hsv_h=0.0,
    hsv_s=0.0,
    flipud=0.0,
    cutmix=0.0,
    auto_augment=False,
    optimizer='AdamW',
)

print(f"\n🏆 Best trial: #{best_num} | mAP50: {study.best_value:.4f}")
print(f"📊 Trial log saved to: {LOG_FILE}")
print(f"📋 Full summary saved to: {SUMMARY_FILE}")
