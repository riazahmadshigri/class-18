import os
import shutil
from pathlib import Path
from collections import defaultdict
import yaml

def load_class_names(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
        if isinstance(data['names'], list):
            return {str(i): name for i, name in enumerate(data['names'])}
        return {str(k): v for k, v in data['names'].items()}

def find_image_file(image_dir, stem):
    for ext in ['.jpg', '.jpeg', '.png']:
        img = image_dir / f"{stem}{ext}"
        if img.exists():
            return img
    return None

def extract_one_image_per_class(dataset_dir, output_dir, yaml_path):
    image_dir = Path(dataset_dir) / 'train' / 'images'
    label_dir = Path(dataset_dir) / 'train' / 'labels'
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    class_names = load_class_names(yaml_path)
    collected = {}  # class_id: image path

    print("Scanning label files...")
    for label_file in sorted(label_dir.glob('*.txt')):
        stem = label_file.stem
        image_path = find_image_file(image_dir, stem)
        if image_path is None:
            print(f"⚠️ Image not found for label: {stem}")
            continue

        with open(label_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                class_id = line.strip().split()[0]
                if class_id not in collected:
                    collected[class_id] = image_path
                    print(f"✅ Found image for class {class_id}: {image_path.name}")
                if len(collected) == len(class_names):
                    break  # got all classes

        if len(collected) == len(class_names):
            break

    # Copy files to output and rename
    for class_id, img_path in collected.items():
        class_name = class_names.get(class_id, f"class_{class_id}")
        dst_path = output_dir / f"{class_name}{img_path.suffix}"
        shutil.copy(img_path, dst_path)
        print(f"📁 Copied {img_path.name} → {dst_path.name}")

    print(f"\n🎉 Done! Copied {len(collected)} images to {output_dir.resolve()}")

# === USAGE ===
dataset_dir = '.'  # e.g. '/home/user/yolodata'
yaml_path = Path(dataset_dir) / 'data.yaml'
output_dir = 'signs'

extract_one_image_per_class(dataset_dir, output_dir, yaml_path)
