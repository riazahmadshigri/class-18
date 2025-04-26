from PIL import Image
from collections import defaultdict
from pathlib import Path

def analyze_image_modes(folder):
    folder_path = Path(folder)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    mode_counts = defaultdict(int)

    for img_file in folder_path.glob("*"):
        if img_file.suffix.lower() in image_extensions:
            try:
                img = Image.open(img_file)
                mode_counts[img.mode] += 1
            except Exception as e:
                print(f"❌ Could not process {img_file.name}: {e}")

    print(f"\n📁 Folder: {folder}")
    for mode, count in mode_counts.items():
        print(f" - {mode}: {count} images")

# === USAGE ===
folders = [
    "train/images",
    "valid/images",
    "test/images"
]

for folder in folders:
    analyze_image_modes(folder)
