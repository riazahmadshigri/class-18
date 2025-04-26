import os

# Define the root directory of your project
project_path = 'new-classes'  # 🔁 <-- Update this to your actual project path

# Define the remapping from current class index to new class index
index_map = {
    5: 3,
    6: 5,
    8: 7,
    12: 9,
    13: 10,
    14: 11,
    17: 12,
    20: 14,
    22: 15,
    23: 16,
    24: 17,
    0: 18,
    3: 19,
    9: 20,
    10: 21,
    17: 22,
    7: 23,
    4: 24,
    14: 25,
    15: 26,
    18: 27,
    20: 28
}

# Subdirectories to look for labels (relative to project_path)
label_dirs = ['train/labels', 'valid/labels', 'test/labels']

def remap_labels(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 1:
            continue
        class_id = int(parts[0])
        if class_id in index_map:
            new_class_id = index_map[class_id]
            parts[0] = str(new_class_id)
            updated_lines.append(" ".join(parts))
        else:
            updated_lines.append(line.strip())  # leave untouched if no remap defined

    with open(file_path, 'w') as file:
        file.write("\n".join(updated_lines) + "\n")

# Process all .txt files in the given directories
for sub_dir in label_dirs:
    label_dir = os.path.join(project_path, sub_dir)
    if not os.path.exists(label_dir):
        continue
    for filename in os.listdir(label_dir):
        if filename.endswith('.txt'):
            remap_labels(os.path.join(label_dir, filename))

print("Label remapping completed.")
