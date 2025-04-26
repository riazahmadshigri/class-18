import os
import shutil
import yaml
from collections import defaultdict

# Load class info from data.yaml
with open("data.yaml", "r") as f:
    data = yaml.safe_load(f)

class_names = data["names"]
num_classes = data["nc"]

# Paths
train_img_dir = "train/images"
train_lbl_dir = "train/labels"
valid_img_dir = "valid/images"
valid_lbl_dir = "valid/labels"

# Count samples per class in valid/labels
valid_counts = defaultdict(int)

# Count the number of samples per class in valid
for file in os.listdir(valid_lbl_dir):
    if not file.endswith(".txt"):
        continue
    with open(os.path.join(valid_lbl_dir, file)) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 1:
                try:
                    class_id = int(parts[0])
                    valid_counts[class_id] += 1
                except ValueError:
                    continue

# Find classes needing more samples in valid (less than 5 samples)
underrepresented_classes = [cls_id for cls_id in range(num_classes) if valid_counts[cls_id] < 5]
print(f"🔍 Classes needing more samples in valid/: {underrepresented_classes}")

# Move files from train to valid (only for underrepresented classes)
moved = 0

# Iterate through the classes that need more samples
for cls in underrepresented_classes:
    needed_samples = 5 - valid_counts[cls]
    print(f"🔍 Moving {needed_samples} samples for class {cls} to valid folder.")
    
    # Track moved samples for the current class
    moved_for_class = 0

    # Iterate through the train labels folder and move samples for the underrepresented class
    for file in os.listdir(train_lbl_dir):
        if not file.endswith(".txt"):
            continue
        
        file_path = os.path.join(train_lbl_dir, file)
        
        # Read the label file and check if it contains the underrepresented class
        with open(file_path) as f:
            class_ids = [int(line.strip().split()[0]) for line in f if line.strip()]

        # If the class is in the file and we haven't moved enough samples yet, move the sample
        if cls in class_ids and moved_for_class < needed_samples:
            basename = os.path.splitext(file)[0]
            img_extensions = ['.jpg', '.png', '.jpeg']
            img_src = None
            
            # Find matching image file
            for ext in img_extensions:
                candidate = os.path.join(train_img_dir, basename + ext)
                if os.path.exists(candidate):
                    img_src = candidate
                    break
            
            if not img_src:
                continue  # No matching image found

            # Target paths
            lbl_dst = os.path.join(valid_lbl_dir, file)
            img_dst = os.path.join(valid_img_dir, os.path.basename(img_src))

            # Move the image and label files to valid folder
            shutil.move(file_path, lbl_dst)
            shutil.move(img_src, img_dst)
            moved += 1
            moved_for_class += 1

            # Update the valid count for the class
            valid_counts[cls] += 1

        # If we've moved enough samples for this class, skip further files
        if moved_for_class >= needed_samples:
            break

    # If we've moved enough samples for this class, continue to the next class
    if moved_for_class >= needed_samples:
        print(f"✅ Moved {moved_for_class} samples for class {cls}. Now it has {valid_counts[cls]} samples in valid.")
    else:
        print(f"⚠️ Couldn't move enough samples for class {cls}. Only moved {moved_for_class}.")

print(f"\n✅ Total samples moved from train ➝ valid: {moved}")
