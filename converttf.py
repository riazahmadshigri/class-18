from ultralytics import YOLO,settings
import os


# YOLO Specific (if using Ultralytics/YOLOv5/v8)
from ultralytics import YOLO  # Requires: pip install ultralytics
os.environ["ULTRALYTICS_CACHE_DIR"] = os.path.join(os.getcwd(), "ultralytics_cache5")

# # Reload settings after setting the new cache directory
settings.reset()

model = YOLO("best-adamw.pt")

# Load YOLOv8 model
# Convert to ONNX
model.export(format='onnx')
