import os
import yaml
from collections import defaultdict

# === Config ===
project_root = os.getcwd()  # change if running from a different dir
data_yaml_path = os.path.join(project_root, 'data.yaml')

# Load class info
with open(data_yaml_path, 'r') as file:
    config = yaml.safe_load(file)
class_names = config['names']
num_classes = config['nc']

# Hardcoded folder locations
label_dirs = {
    'train': os.path.join(project_root, 'train', 'labels'),
    'valid': os.path.join(project_root, 'valid', 'labels'),
    'test': os.path.join(project_root, 'test', 'labels')
}

# Count dictionary
counts = {
    'train': defaultdict(int),
    'valid': defaultdict(int),
    'test': defaultdict(int)
}

# Counting function
def count_labels(label_dir, split):
    if not os.path.exists(label_dir):
        print(f"⚠️ Missing: {label_dir}")
        return
    for file in os.listdir(label_dir):
        if file.endswith('.txt'):
            with open(os.path.join(label_dir, file), 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        class_id = int(line.strip().split()[0])
                        if 0 <= class_id < num_classes:
                            counts[split][class_id] += 1
                    except ValueError:
                        continue  # ignore bad lines

# Run counting
for split, path in label_dirs.items():
    count_labels(path, split)

# Print class distribution
print("\n📊 Class Sample Distribution:\n")
header = f"{'Class ID':<9} {'Name':<20} {'Train':>7} {'Valid':>7} {'Test':>7} {'Total':>7}"
print(header)
print("-" * len(header))

for class_id in range(num_classes):
    name = class_names[class_id] if class_id < len(class_names) else f"Class_{class_id}"
    train_c = counts['train'][class_id]
    valid_c = counts['valid'][class_id]
    test_c = counts['test'][class_id]
    total = train_c + valid_c + test_c
    print(f"{class_id:<9} {name:<20} {train_c:>7} {valid_c:>7} {test_c:>7} {total:>7}")

# Check for missing classes
print("\n🚨 Classes with 0 samples:")
missing = [i for i in range(num_classes) if counts['train'][i] + counts['valid'][i] + counts['test'][i] == 0]
if missing:
    for i in missing:
        print(f"- {i}: {class_names[i]}")
else:
    print("✅ All classes have samples.")
