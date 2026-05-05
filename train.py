import optuna
import json
from ultralytics import YOLO


def objective(trial):
    model = YOLO('yolov8x.pt')

    results = model.train(
        data='data.yaml',
        epochs=40,
        imgsz=1280,
        batch=6,
        patience=100,
        verbose=False,

        # Augmentation params to tune
        hsv_v=trial.suggest_float('hsv_v', 0.1, 0.5),
        degrees=trial.suggest_float('degrees', 0, 20),
        translate=trial.suggest_float('translate', 0.0, 0.2),
        scale=trial.suggest_float('scale', 0.05, 0.3),
        shear=trial.suggest_float('shear', 0.0, 10.0),
        fliplr=trial.suggest_float('fliplr', 0.0, 0.5),
        mosaic=trial.suggest_float('mosaic', 0.0, 0.3),
        erasing=trial.suggest_float('erasing', 0.1, 0.5),

        # Training params to tune
        lr0=trial.suggest_float('lr0', 1e-4, 1e-2, log=True),
        lrf=trial.suggest_float('lrf', 0.001, 0.1, log=True),
        cls=trial.suggest_float('cls', 0.5, 3.0),
        box=trial.suggest_float('box', 5.0, 12.0),

        # Fixed
        hsv_h=0.0,
        hsv_s=0.0,
        flipud=0.0,
        cutmix=0.0,
        auto_augment=False,
        optimizer='AdamW',
    )

    return results.results_dict['metrics/mAP50(B)']


# ── Search ──────────────────────────────────────────────────────────────────

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=300)  

# ── Save results immediately ─────────────────────────────────────────────────

print("Best params:", study.best_params)
print("Best mAP50: ", study.best_value)

with open('best_hyperparams.json', 'w') as f:
    json.dump(study.best_params, f, indent=2)
print("Saved to best_hyperparams.json")

# ── Final training with best params ─────────────────────────────────────────

best = study.best_params

model = YOLO('yolov8m.pt')
model.train(
    data='data.yaml',
    epochs=1000,
    patience=100,
    batch=6,
    imgsz=1280,
    **best,

    # Fixed values not part of the search
    hsv_h=0.0,
    hsv_s=0.0,
    flipud=0.0,
    cutmix=0.0,
    auto_augment=False,
    optimizer='AdamW',
)