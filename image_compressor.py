#!/usr/bin/env python3
"""
Image Compression Script

This script compresses images in a specified directory with user-defined settings.
Features:
- Interactive command-line interface
- Customizable compression quality
- Maximum width setting with aspect ratio preservation
- Format conversion options
- Recursive directory traversal
- English filename conversion
"""

import os
import sys
import re
import time
from pathlib import Path
import unicodedata

# Check for required packages and install if missing
try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    print("Pillow package not found. Attempting to install...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image, UnidentifiedImageError
        print("Pillow installed successfully!")
    except Exception as e:
        print(f"Error installing Pillow: {e}")
        print("Please install manually with: python -m pip install pillow")
        sys.exit(1)

# Supported image formats
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff']

def sanitize_filename(filename):
    """Convert non-English filename to English and sanitize it."""
    # Get the base name without extension
    base_name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]

    # Check if the filename contains non-ASCII characters
    if not all(ord(c) < 128 for c in base_name):
        # Convert non-ASCII characters to their closest ASCII equivalents
        normalized = unicodedata.normalize('NFKD', base_name)
        # Keep only ASCII characters
        ascii_text = ''.join(c for c in normalized if ord(c) < 128)
        # Remove any special characters and replace spaces with hyphens
        sanitized = re.sub(r'[^\w\s-]', '', ascii_text).strip().lower()
        sanitized = re.sub(r'[\s]+', '-', sanitized)

        # If nothing remains after sanitization (e.g., all characters were non-ASCII)
        # generate a simple timestamp-based name
        if not sanitized:
            sanitized = f"image-{int(time.time())}"
    else:
        # If already ASCII, just sanitize
        sanitized = re.sub(r'[^\w\s-]', '', base_name).strip().lower()
        sanitized = re.sub(r'[\s]+', '-', sanitized)

    return sanitized + extension

def compress_image(input_path, output_path, quality=85, max_width=1920, output_format=None):
    """Compress an image with the specified settings."""
    try:
        with Image.open(input_path) as img:
            # Get original format if output_format is None
            img_format = output_format or img.format

            # Convert format string to Pillow format
            if img_format.lower() == 'webp':
                save_format = 'WEBP'
            elif img_format.lower() in ['jpg', 'jpeg']:
                save_format = 'JPEG'
            else:
                save_format = img_format.upper()

            # Resize if width exceeds max_width
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
                print(f"Resized from {width}x{height} to {max_width}x{new_height}")

            # Save with compression
            img.save(output_path, format=save_format, quality=quality, optimize=True)

            # Get file size reduction
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            reduction = (1 - compressed_size / original_size) * 100

            print(f"Compressed: {input_path} -> {output_path}")
            print(f"Size reduction: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB ({reduction:.1f}%)")

            return True
    except UnidentifiedImageError:
        print(f"Skipping unsupported file: {input_path}")
        return False
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def process_directory(directory, quality, max_width, output_format):
    """Process all images in a directory and its subdirectories."""
    directory = Path(directory)
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return

    # Count total images for progress tracking
    total_images = sum(1 for path in directory.glob('**/*') if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS)
    processed = 0
    successful = 0

    print(f"Found {total_images} images to process")

    # Process each file
    for path in directory.glob('**/*'):
        if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS:
            processed += 1

            # Create output path with sanitized filename
            relative_path = path.relative_to(directory)
            sanitized_name = sanitize_filename(relative_path.name)
            output_path = directory / relative_path.parent / sanitized_name

            # Change extension if output format is specified
            if output_format and output_format != 'original':
                output_path = output_path.with_suffix(f'.{output_format}')

            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Compress the image
            print(f"[{processed}/{total_images}] Processing: {path}")
            if compress_image(path, output_path, quality, max_width, output_format):
                successful += 1

    print(f"\nCompression complete: {successful} of {processed} images processed successfully")

def main():
    """Main function to run the interactive image compression script."""
    print("=" * 60)
    print("Image Compression Tool")
    print("=" * 60)

    # Get directory from user
    while True:
        directory = input("Enter the directory path containing images to compress: ").strip()
        if os.path.isdir(directory):
            break
        print("Invalid directory path. Please try again.")

    # Get quality setting
    while True:
        quality_input = input("Enter compression quality (1-100, default 85): ").strip()
        if not quality_input:
            quality = 85
            break
        try:
            quality = int(quality_input)
            if 1 <= quality <= 100:
                break
            print("Quality must be between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    # Get max width
    while True:
        width_input = input("Enter maximum width in pixels (default 1920): ").strip()
        if not width_input:
            max_width = 1920
            break
        try:
            max_width = int(width_input)
            if max_width > 0:
                break
            print("Width must be a positive number.")
        except ValueError:
            print("Please enter a valid number.")

    # Get output format
    print("\nOutput format options:")
    print("1. WebP (default, recommended for best compression)")
    print("2. JPEG")
    print("3. PNG")
    print("4. Original format (keep each image's original format)")

    while True:
        format_input = input("Choose output format (1-4): ").strip()
        if not format_input or format_input == '1':
            output_format = 'webp'
            break
        elif format_input == '2':
            output_format = 'jpg'
            break
        elif format_input == '3':
            output_format = 'png'
            break
        elif format_input == '4':
            output_format = 'original'
            break
        else:
            print("Please enter a valid option (1-4).")

    # Confirm settings
    print("\nCompression Settings:")
    print(f"Directory: {directory}")
    print(f"Quality: {quality}")
    print(f"Maximum width: {max_width}px")
    print(f"Output format: {output_format}")

    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return

    # Process the directory
    process_directory(directory, quality, max_width, output_format)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
