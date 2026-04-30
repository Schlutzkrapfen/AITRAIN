from ultralytics import YOLO

# 1. Load a pretrained model (n = nano, the fastest version)
model = YOLO('yolov8x.pt') 

# 2. Train the model
results = model.train(
    data='data.yaml', 
  epochs=1000 ,
  patience=100 ,
  batch=8 ,
  imgsz=1280,
  hsv_h=0.0,
    hsv_s=0.5,
    hsv_v=0.7,
    degrees= 45,
    translate=0.0,
    scale=0.5,
    flipud =1,
    fliplr=1,
    mosaic=1,
    cutmix = 0.2,
    erasing=0.4,
    shear=40,
)
