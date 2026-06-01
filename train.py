import optuna
import json
import os
import csv
from datetime import datetime
import yaml
from ultralytics import YOLO
YOLO_MODEL_FINAL = 'yolov8x.pt'
EPOCHS_FINAL = 1000
yaml_path= "data.yaml"

def make_file_structer():
    os.makedirs("./single_label_runs", exist_ok=True) 
    with open(yaml_path) as stream:
        try:
            for items in yaml.safe_load(stream)["names"].values():
                print(items)
                os.makedirs(f"single_label_runs/{items}/Train/",exist_ok=True)

        except yaml.YAMLError as exc:
            print(exc)
def init():
    make_file_structer()
def train_on_single_label():
    os.mkdir()
    pass
def train_with_imporfment():
    YOLO_MODEL = 'yolov8x.pt'
    TRIALS = 300
    EPOCHS_SEARCH = 300

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

        model = YOLO(YOLO_MODEL)

        # Suggest hyperparameters for this trial
        params = dict(
            hsv_v     = trial.suggest_float('hsv_v',     0.1,  0.5),
            degrees   = trial.suggest_float('degrees',   0,    20),
            translate = trial.suggest_float('translate', 0.0,  0.2),
            scale     = trial.suggest_float('scale',     0.05, 0.3),
            shear     = trial.suggest_float('shear',     0.0,  10.0),
            fliplr    = trial.suggest_float('fliplr',    0.0,  0.5),
            mosaic    = trial.suggest_float('mosaic',    0.0,  0.3),
            erasing   = trial.suggest_float('erasing',   0.1,  0.5),
            lr0       = trial.suggest_float('lr0',       1e-4, 1e-2, log=True),
            lrf       = trial.suggest_float('lrf',       0.001,0.1,  log=True),
            cls       = trial.suggest_float('cls',       0.5,  3.0),
            box       = trial.suggest_float('box',       5.0,  12.0),
        )

        results = model.train(
            data='data.yaml',
            epochs=EPOCHS_SEARCH,
            imgsz=1280,
            batch=6,
            patience=50,
            verbose=False,
            # Fixed params — not part of the search
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

        # Find the most recently created run folder (= this trial's folder)
        runs_dir = 'runs/detect'
        all_folders = sorted(
            os.listdir(runs_dir),
            key=lambda x: os.path.getmtime(os.path.join(runs_dir, x))
        )
        run_folder = all_folders[-1]

        # ── Append trial result to CSV ────────────────────────────────────────────
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trial.number, round(mAP50, 6), run_folder,
                *[round(params[k], 6) for k in params],
                round(duration, 2),
                start_time.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # ── Save a trial_info.json inside the run folder ──────────────────────────
        run_info = {
            'trial_number': trial.number,
            'mAP50': mAP50,
            'duration_minutes': round(duration, 2),
            'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'is_best': False,  # updated after all trials complete
            'params': params,
            'fixed_params': {
                'hsv_h': 0.0, 'hsv_s': 0.0, 'flipud': 0.0,
                'cutmix': 0.0, 'auto_augment': False, 'optimizer': 'AdamW',
                'epochs': EPOCHS_SEARCH, 'imgsz': 1280, 'batch': 6, 'patience': 50
            },
            'all_metrics': results.results_dict  # includes mAP50, mAP50-95, precision, recall
        }

        with open(os.path.join(runs_dir, run_folder, 'trial_info.json'), 'w') as f:
            json.dump(run_info, f, indent=2)

        all_trials_data.append(run_info)

        print(f"\n✅ Trial {trial.number:>3} | mAP50: {mAP50:.4f} | "
              f"lr0: {params['lr0']:.5f} | box: {params['box']:.2f} | "
              f"folder: {run_folder} | {duration:.1f} min")

        return mAP50

    # ── Run the hyperparameter search ─────────────────────────────────────────────
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=TRIALS)

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
    train(best)
 

    print(f"\n🏆 Best trial: #{best_num} | mAP50: {study.best_value:.4f}")
    print(f"📊 Trial log saved to: {LOG_FILE}")
    print(f"📋 Full summary saved to: {SUMMARY_FILE}")

def train(best):
   # Fresh instance required here too — same reason as inside objective()
    model = YOLO(YOLO_MODEL_FINAL)
    model.train(
        data='data.yaml',
        epochs=EPOCHS_FINAL,
        patience=100,
        batch=6,
        imgsz=1280,
        **best,
        # Fixed params — not part of the search
        hsv_h=0.0,
        hsv_s=0.0,
        flipud=0.0,
        cutmix=0.0,
        auto_augment=False,
        optimizer='AdamW',
    )
init()