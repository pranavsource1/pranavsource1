"""
Quick diagnostic: dump ASCII art to terminal so we can see what it looks like
before embedding in SVG.
"""
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

# Simple 10-char ramp (proven to work for portraits)
RAMP = " .:-=+*#%@"

img = Image.open(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")

# Print image info
print(f"Image size: {img.size}")
print(f"Image mode: {img.mode}")

# Convert to grayscale
img = img.convert("L")

# Check brightness distribution
arr = np.array(img)
print(f"Min pixel: {arr.min()}, Max pixel: {arr.max()}, Mean: {arr.mean():.1f}, Median: {np.median(arr):.1f}")

# Show histogram in 10 bins
hist, bins = np.histogram(arr.flatten(), bins=10, range=(0, 255))
print("\nBrightness histogram:")
for i in range(10):
    bar = "#" * (hist[i] * 50 // hist.max())
    print(f"  {int(bins[i]):3d}-{int(bins[i+1]):3d}: {bar} ({hist[i]})")

# Auto contrast
img2 = ImageOps.autocontrast(img, cutoff=1)
arr2 = np.array(img2)
print(f"\nAfter autocontrast - Min: {arr2.min()}, Max: {arr2.max()}, Mean: {arr2.mean():.1f}")

# Simple resize and ASCII conversion
width = 80
aspect = img2.height / img2.width
char_aspect = 2.0  # terminal chars are ~2x taller than wide
height = int(width * aspect / char_aspect)
img3 = img2.resize((width, height), Image.Resampling.LANCZOS)

arr3 = np.array(img3)

# Print ASCII art
print(f"\nASCII preview ({width}x{height}):")
print("-" * width)
for row in arr3:
    line = ""
    for val in row:
        idx = int(val / 255 * (len(RAMP) - 1))
        line += RAMP[idx]
    # Encode safely for Windows console
    sys.stdout.buffer.write((line + "\n").encode("ascii", errors="replace"))
print("-" * width)
