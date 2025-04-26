from PIL import Image, ImageOps
from pathlib import Path

def convert_images_to_grayscale(input_folder, output_folder):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Supported image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

    for image_file in input_path.iterdir():
        if image_file.suffix.lower() in image_extensions:
            try:
                # Open and auto-rotate based on EXIF
                img = Image.open(image_file)
                img = ImageOps.exif_transpose(img)

                # Convert to grayscale
                img = img.convert('L')

                # Save to output folder
                save_path = output_path / image_file.name
                img.save(save_path)

                print(f"✅ Converted: {image_file.name}")
            except Exception as e:
                print(f"❌ Failed to convert {image_file.name}: {e}")

    print(f"\n🎉 Done! Grayscale images saved to: {output_path.resolve()}")

# === USAGE EXAMPLE ===
input_folder = 'dataset new annotation'            # e.g., 'dataset/train/images'
output_folder = 'new annotate' # e.g., 'dataset/train/gray_images'

convert_images_to_grayscale(input_folder, output_folder)
