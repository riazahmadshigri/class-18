import os
import shutil

# Paths
root_dir = "new-raw"
images_dir = os.path.join(root_dir, "images")
labels_dir = os.path.join(root_dir, "labels")
output_dir = os.path.join(root_dir, "by_class")

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Process all label files
for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)
    with open(label_path, "r") as f:
        lines = f.readlines()

    # Get all unique class IDs from this label file
    class_ids = set()
    for line in lines:
        if line.strip():
            parts = line.strip().split()
            class_ids.add(parts[0])  # class index is the first element

    # Copy label and corresponding image into each class folder
    image_name = os.path.splitext(label_file)[0]
    for class_id in class_ids:
        class_folder = os.path.join(output_dir, class_id)
        os.makedirs(os.path.join(class_folder, "images"), exist_ok=True)
        os.makedirs(os.path.join(class_folder, "labels"), exist_ok=True)

        # Copy label file
        shutil.copy(label_path, os.path.join(class_folder, "labels", label_file))

        # Copy image file (supports jpg, png, jpeg)
        for ext in [".jpg", ".jpeg", ".png"]:
            image_path = os.path.join(images_dir, image_name + ext)
            if os.path.exists(image_path):
                shutil.copy(image_path, os.path.join(class_folder, "images", image_name + ext))
                break

print("Dataset successfully separated by class.")
