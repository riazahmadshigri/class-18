from ultralytics import YOLO
import cv2
import os
# Get Android asset path via Chaquopy

def predict(image_path: str) -> list:

    from android.os import Environment
    from com.chaquo.python import Python
    from java.io import FileOutputStream
    from java.io import InputStreamReader

# Get app context
    context = Python.getPlatform().getApplication()

# Where to copy the model
    file_path = os.path.join(context.getFilesDir().getAbsolutePath(), "best.pt")

# Check if the model is already copied
    if not os.path.exists(file_path):
    # Read the model from assets
        asset_manager = context.getAssets()
        input_stream = asset_manager.open("best.pt")
        output_stream = FileOutputStream(file_path)

    # Copy the file
        buffer = bytearray(1024)
        length = 0
        while (input_stream.read(buffer)) != -1:
            output_stream.write(buffer)

        input_stream.close()
        output_stream.close()


        model=YOLO(file_path)
        results = model(image_path)
        predictions = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            predictions.append({
                "class": result.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": [x1, y1, x2-x1, y2-y1]  # [x, y, width, height]
            })

    return predictions