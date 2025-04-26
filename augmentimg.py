import os
import cv2
import random
import shutil
from pathlib import Path
import numpy as np

from tqdm import tqdm

# --- Augmentations ---
def adjust_brightness(image, factor):
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)

def horizontal_flip(image, labels):
    flipped_img = cv2.flip(image, 1)
    h, w = image.shape[:2]
    new_labels = []
    for label in labels:
        cls, x, y, bw, bh = label
        x = 1 - x  # Flip x
        new_labels.append([cls, x, y, bw, bh])
    return flipped_img, new_labels

def rotate_image_and_labels(image, labels, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_img = cv2.warpAffine(image, rot_mat, (w, h), flags=cv2.INTER_LINEAR)

    new_labels = []
    for label in labels:
        cls, x, y, bw, bh = label
        # Convert to pixel
        px = x * w
        py = y * h

        new_coords = rot_mat @ np.array([px, py, 1])
        new_x, new_y = new_coords[0] / w, new_coords[1] / h

        new_labels.append([cls, new_x, new_y, bw, bh])
    return rotated_img, new_labels

# --- Load labels ---
def load_labels(label_path):
    with open(label_path, 'r') as f:
        lines = f.readlines()
    return [list(map(float, line.strip().split())) for line in lines]

def save_labels(new_path, labels):
    with open(new_path, 'w') as f:
        for l in labels:
            f.write(' '.join(f'{x:.6f}' for x in l) + '\n')

# --- Process Folder ---
def augment_folder(folder_path):
    image_dir = os.path.join(folder_path, "images")
    label_dir = os.path.join(folder_path, "labels")

    image_files = list(Path(image_dir).glob("*.jpg")) + list(Path(image_dir).glob("*.png"))

    for img_path in tqdm(image_files, desc=f"Augmenting {folder_path}"):
        label_path = os.path.join(label_dir, img_path.stem + ".txt")
        if not os.path.exists(label_path):
            continue

        image = cv2.imread(str(img_path))
        labels = load_labels(label_path)

        augmentations = [
            ("lowbright", adjust_brightness(image, 0.5), labels),
            ("highbright", adjust_brightness(image, 1.5), labels),
            # ("flipped", *horizontal_flip(image, labels)),
            ("rotated", *rotate_image_and_labels(image, labels, angle=15))
        ]

        for suffix, aug_img, aug_labels in augmentations:
            new_img_name = f"{img_path.stem}_{suffix}{img_path.suffix}"
            new_lbl_name = f"{img_path.stem}_{suffix}.txt"

            cv2.imwrite(os.path.join(image_dir, new_img_name), aug_img)
            save_labels(os.path.join(label_dir, new_lbl_name), aug_labels)

# --- Main ---
dataset_root = "."
for split in ["train", "valid", "test"]:
    augment_folder(os.path.join(dataset_root, split))
