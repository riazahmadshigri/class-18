# # !pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
# # !pip install -U ultralytics
#  #!pip install flask
#  #!pip install flask_socketio


from ultralytics import YOLO,settings
from flask import Flask, render_template,jsonify
# from flask_socketio import SocketIO
import cv2
import base64
import torch
import numpy as np
import os



# project = "runs/detect"
# name = "train_run"
# last_ckpt_path = f"{project}/{name}/weights/last.pt"
# best_ckpt_path = f"{project}/{name}/weights/best.pt"
# # Set a unique cache directory for each project
# os.environ["ULTRALYTICS_CACHE_DIR"] = os.path.join(os.getcwd(), "ultralytics_cache2")

# # Reload settings after setting the new cache directory
# settings.reset()

# # Load the YOLO model (always start with pretrained weights)
# model = YOLO("yolov8n.pt")

# # Resume training if a checkpoint exists
# if os.path.exists(last_ckpt_path):
#     print(f"Resuming training from last checkpoint: {last_ckpt_path}")
#     model.load(last_ckpt_path)
# elif os.path.exists(best_ckpt_path):
#     print(f"Resuming training from best checkpoint: {best_ckpt_path}")
#     model.load(best_ckpt_path)
# else:
#     print("Starting new training with yolov8n.pt")

# model = YOLO('best-tst.pt')  # Ensure the correct model path

# # # Train the model
# model.val(
#     data="data.yaml",
# )



from ultralytics import YOLO
from flask import Flask, request, jsonify
from flask_sock import Sock
import cv2
import base64
import numpy as np
import base64
import time

os.environ["ULTRALYTICS_CACHE_DIR"] = os.path.join(os.getcwd(), "ultralytics_cache2")

# Reload settings after setting the new cache directory
settings.reset()


app = Flask(__name__)
sock = Sock(app)  # Initialize Flask-Sock WebSocket

# Load the YOLOv8 model
# model = YOLO('best-full-and-final-tuning-left.pt')  # Ensure the correct model path
model = YOLO('best-adamw.pt')  # Ensure the correct model path

SAVE_DIR = "received_frames"
os.makedirs(SAVE_DIR, exist_ok=True)
def fix_base64_padding(data):
    return data + "=" * (-len(data) % 4)  # Adds missing '=' if needed

def process_frame(frame):
    results = model(frame, conf=0.7, iou=0.9, show=True)[0]  # Extract first result

    # Check if model has class names
    if hasattr(model.model, "names"):
        class_names = model.model.names
    else:
        return {"error": "Model does not have a 'names' attribute."}

    best_pred = None
    best_conf = -1

    # Loop through all predictions
    for pred in results.boxes:
        class_id = int(pred.cls[0])      # Class ID
        confidence = float(pred.conf[0]) # Confidence score
        bbox = list(map(int, pred.xyxy[0].tolist()))  # Bounding box coordinates

        # Update if this prediction has higher confidence
        if confidence > best_conf:
            best_conf = confidence
            best_pred = {
                "label": class_names[class_id],
                "confidence": round(confidence, 2),
                "bbox": bbox
            }

    # Return the best detection
    if best_pred:
        return {"detections": [best_pred]}
    else:
        return {"detections": []}

    

@sock.route('/predict')  # WebSocket on /predict
def handle_frame(ws):
    while True:
        try:
            data = ws.receive()  # Receive frame from WebSocket
            if not data:
                ws.send(json.dumps({"error": "No frame data received"}))
                continue
            import json
            data = json.loads(data)

            # Ensure data contains 'frame' key
            frame_data = data.get('frame')
            
                # Fix Base64 padding issue
            # fixed_frame_data = fix_base64_padding(data)

            # Decode Base64 to OpenCV format
            decoded_data = base64.b64decode(frame_data)
            np_arr = np.frombuffer(decoded_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Convert to 3-channel grayscale (i.e., grayscale in RGB format)
            gray_3channel = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            if gray_3channel is None:
                ws.send(json.dumps({"error": "Invalid image format"}))
                continue
            
            # Process frame with YOLO
            # image_path = os.path.join(SAVE_DIR, f"frame_{int(time.time())}.jpg")
            # cv2.imwrite(image_path, frame)
            # print(f"✅ Image saved at: {image_path}")
            result = process_frame(gray_3channel)
            print(result)
            
            # Send result back to client
            ws.send(json.dumps(result))

        except Exception as e:
            print(f"Error processing frame: {e}")
            ws.send(json.dumps({"error": str(e)}))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
