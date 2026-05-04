from ultralytics import YOLO

# 1. Load a pretrained model (n = nano, the fastest version)
model = YOLO('yolov8x.pt') 

# 2. Train the model
results = model.train(
    data='data.yaml',
    epochs=1000,
    patience=100,
    batch=6,
    imgsz=1280,

    # HSV — kill hue/sat, keep mild brightness
    hsv_h=0.0,
    hsv_s=0.0,       # was 0.5 — meaningless on grayscale
    hsv_v=0.3,       # was 0.7 — softer brightness shift

    # Geometry — conservative for anatomy
    degrees=15,      # was 45 — X-rays have orientation meaning
    shear=5,         # was 40 — hugely reduced
    scale=0.2,       # was 0.5 — less zoom distortion
    translate=0.1,   # was 0.0 — small translations are fine/helpful

    # Flips — keep both (chest/spine can be flipped)
    flipud=0.5,      # was 1.0 — probabilistic, not always
    fliplr=0.5,

    # Mosaic — reduce or disable
    mosaic=0.3,      # was 1.0 — use sparingly

    # These were okay, slightly tuned
    cutmix=0.1,      # was 0.2 — lighter
    erasing=0.3,     # was 0.4 — lighter

    # Disable — conflicts with manual settings
    auto_augment=False,  # was True
)
