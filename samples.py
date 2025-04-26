import os
import yaml
from pathlib import Path
from collections import defaultdict

def load_class_names(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
        if isinstance(data['names'], list):  # sometimes names are list
            return {str(i): name for i, name in enumerate(data['names'])}
        return {str(k): v for k, v in data['names'].items()}

def count_classes_in_yolo_labels(base_dir):
    subsets = ['train', 'valid']
    class_counts = {subset: defaultdict(int) for subset in subsets}

    for subset in subsets:
        label_dir = Path(base_dir) / subset / 'labels'
        if not label_dir.exists():
            print(f"Warning: {label_dir} does not exist.")
            continue

        for label_file in label_dir.glob('*.txt'):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        class_id = parts[0]
                        class_counts[subset][class_id] += 1

    return class_counts

def print_class_summary(class_counts, class_names):
    all_class_ids = sorted(set(class_id for counts in class_counts.values() for class_id in counts))

    print(f"{'Class ID':<8} | {'Class Name':<15} | {'Train Count':<12} | {'Valid Count'}")
    print('-' * 60)
    for class_id in all_class_ids:
        name = class_names.get(class_id, 'Unknown')
        train = class_counts['train'].get(class_id, 0)
        valid = class_counts['valid'].get(class_id, 0)
        print(f"{class_id:<8} | {name:<15} | {train:<12} | {valid}")

# ==== Usage ====

dataset_dir = '.'  # e.g., '/home/user/mydataset'
yaml_path = Path(dataset_dir) / 'data.yaml'

class_names = load_class_names(yaml_path)
class_counts = count_classes_in_yolo_labels(dataset_dir)
print_class_summary(class_counts, class_names)
