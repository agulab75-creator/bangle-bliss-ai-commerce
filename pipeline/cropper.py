import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import imagehash
import shutil

def get_bangle_bounding_box(image_path: Path):
    """
    Reads an image, converts to HSV to threshold the bangle from the background,
    and returns the bounding box (x, y, w, h).
    """
    # Read image using OpenCV
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Bangle Isolation Strategy:
    # Most bangles are highly saturated (colored glass/gold) and stand out from neutral backgrounds.
    # We threshold based on saturation and value to separate jewelry from plain surfaces.
    # S > 25 (removes white/gray/black backgrounds)
    # OR V < 220 (removes bright white backgrounds if the bangle is dark/metallic)
    
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]
    
    # Create masks
    mask_s = cv2.inRange(s_channel, 25, 255)
    mask_v = cv2.inRange(v_channel, 0, 220)
    
    # Combine masks: pixel is foreground if it's colorful OR it's somewhat dark (not pure white background)
    combined_mask = cv2.bitwise_or(mask_s, mask_v)
    
    # Clean up the mask using morphological operations to remove small noise (dust, specks)
    kernel = np.ones((5,5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours (outlines of the objects)
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Fallback if no contours found (extremely rare)
        return 0, 0, img.shape[1], img.shape[0]
        
    # Assume the largest contour by area is our bangle stack
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Add a small padding (e.g., 5% of the width) so it's not cropped too tight
    padding = int(w * 0.05)
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(img.shape[1] - x, w + 2 * padding)
    h = min(img.shape[0] - y, h + 2 * padding)
    
    return x, y, w, h

def process_raw_images(raw_dir: Path, output_dir: Path):
    """
    Deduplicates images using imagehash and crops them tightly using HSV masking.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    seen_hashes = {}
    
    print(f"Scanning raw images in {raw_dir}...")
    
    import itertools
    for img_path in itertools.chain(raw_dir.glob("*.[jJ][pP][gG]"), raw_dir.glob("*.[jJ][pP][eE][gG]")):
        # 1. Deduplication (imagehash.phash)
        pil_img = Image.open(img_path)
        img_hash = imagehash.phash(pil_img)
        
        # Check against existing hashes for near-duplicates (Hamming distance < 10)
        is_duplicate = False
        for seen_hash, seen_path in seen_hashes.items():
            if img_hash - seen_hash < 10:
                print(f"Skipping {img_path.name} - Duplicate of {seen_path.name}")
                is_duplicate = True
                break
                
        if is_duplicate:
            continue
            
        seen_hashes[img_hash] = img_path
        print(f"Processing {img_path.name}...")
        
        # 2. Isolate/Crop
        x, y, w, h = get_bangle_bounding_box(img_path)
        
        # Crop the image using the bounding box
        cropped_img = pil_img.crop((x, y, x + w, y + h))
        
        # Save as consistent source crop
        # Filename convention for sources: src-cropped-<original_name>
        output_name = f"src-cropped-{img_path.stem}.jpg"
        cropped_img.save(output_dir / output_name, "JPEG", quality=95)
        print(f"  -> Saved perfectly cropped source as {output_name}")

if __name__ == "__main__":
    base_dir = Path("~/Desktop/My Bangle Bliss")
    raw_dir = base_dir / "raw"
    source_crops_dir = base_dir / "source-crops"
    
    process_raw_images(raw_dir, source_crops_dir)
