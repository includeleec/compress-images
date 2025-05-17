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
- Progress bar for visual feedback
- Option to preserve original files
- Detailed compression statistics
"""

import os
import sys
import re
import time
import random
import unicodedata
import shutil
from pathlib import Path
from datetime import datetime

# Try to import required packages
try:
    from PIL import Image
    print("Pillow is installed.")
except ImportError:
    print("Pillow (PIL) is required for this script.")
    print("Please install it with: pip install pillow")
    sys.exit(1)

# Try to import optional packages for enhanced UI
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    COLOR_SUPPORT = True
except ImportError:
    COLOR_SUPPORT = False
    print("For colored output, install colorama: pip install colorama")

# Try to import tqdm for progress bar
try:
    from tqdm import tqdm
    PROGRESS_BAR_SUPPORT = True
except ImportError:
    PROGRESS_BAR_SUPPORT = False
    print("For progress bar support, install tqdm: pip install tqdm")

# Supported image formats
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff']

# Helper functions for colored output
def print_info(message):
    """Print an info message, with color if available."""
    if COLOR_SUPPORT:
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
    else:
        print(message)

def print_success(message):
    """Print a success message, with color if available."""
    if COLOR_SUPPORT:
        print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
    else:
        print(message)

def print_warning(message):
    """Print a warning message, with color if available."""
    if COLOR_SUPPORT:
        print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")
    else:
        print(message)

def print_error(message):
    """Print an error message, with color if available."""
    if COLOR_SUPPORT:
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")
    else:
        print(message)

def print_header(message):
    """Print a header message, with color if available."""
    if COLOR_SUPPORT:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{message}{Style.RESET_ALL}")
    else:
        print("=" * 60)
        print(message)
        print("=" * 60)

def sanitize_filename(filename):
    """Generate a random number with '-compress' suffix for the compressed image filename."""
    # Get the extension from the original filename
    extension = os.path.splitext(filename)[1]

    # Generate a random number between 10000 and 99999
    random_number = random.randint(10000, 99999)

    # Create the new filename with the random number and "-compress" suffix
    sanitized = f"{random_number}-compress"

    return sanitized + extension

def compress_image(input_path, output_path, quality=85, max_width=1920, output_format=None, preserve_original=False):
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

            # Get original dimensions and size
            width, height = img.size
            original_size = os.path.getsize(input_path)
            was_resized = False

            # Resize if width exceeds max_width
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)
                was_resized = True
                print_info(f"Resized from {width}x{height} to {max_width}x{new_height}")

            # Create a temporary file for compression
            temp_output_path = str(output_path) + ".temp"

            # Save with compression
            img.save(temp_output_path, format=save_format, quality=quality, optimize=True)

            # Get file size reduction
            compressed_size = os.path.getsize(temp_output_path)
            reduction = (1 - compressed_size / original_size) * 100

            # Check if the compression actually reduced the file size
            if compressed_size >= original_size and not was_resized and output_path.suffix == Path(input_path).suffix:
                print_warning(f"Compression did not reduce file size for {input_path}")
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                return False

            # Move the temporary file to the final destination
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_output_path, output_path)

            # If preserve_original is True and the output path is different from the input path,
            # create a backup of the original file
            if preserve_original and str(input_path) != str(output_path):
                backup_dir = Path(input_path).parent / "originals"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / Path(input_path).name
                if not backup_path.exists():
                    shutil.copy2(input_path, backup_path)

            # Print compression results
            print_success(f"Compressed: {input_path} -> {output_path}")
            if reduction > 0:
                print_success(f"Size reduction: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB ({reduction:.1f}%)")
            else:
                print_warning(f"Size change: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB ({reduction:.1f}%)")

            # Return compression statistics
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'reduction': reduction,
                'was_resized': was_resized
            }
    except PermissionError:
        print_error(f"Permission denied: Cannot access {input_path} or write to {output_path}")
        return {'success': False, 'error': 'permission_denied'}
    except Exception as e:
        print_error(f"Error processing {input_path}: {e}")
        return {'success': False, 'error': str(e)}

def process_directory(directory, quality, max_width, output_format, preserve_original=False):
    """Process all images in a directory and its subdirectories."""
    directory = Path(directory)
    if not directory.exists():
        print_error(f"Directory not found: {directory}")
        return

    # Count total images for progress tracking
    print_info("Scanning directory for images...")
    image_paths = [path for path in directory.glob('**/*')
                  if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS]
    total_images = len(image_paths)

    if total_images == 0:
        print_warning(f"No supported images found in {directory}")
        return

    print_info(f"Found {total_images} images to process")

    # Statistics
    stats = {
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'resized_images': 0,
        'errors': {}
    }

    # Create a timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Process each file with progress bar if available
    if PROGRESS_BAR_SUPPORT:
        iterator = tqdm(image_paths, desc="Compressing images", unit="image")
    else:
        iterator = image_paths
        print_info("Processing images...")

    # Create a subdirectory for compressed images with format "compress-[size]-[format]-[quality]"
    format_name = output_format if output_format != 'original' else 'original'
    compress_dir_name = f"compress-{max_width}-{format_name}-{quality}"

    for path in iterator:
        stats['processed'] += 1

        # Create output path with sanitized filename
        relative_path = path.relative_to(directory)
        parent_dir = relative_path.parent

        # Create a compress subdirectory in the same directory as the original image
        compress_subdir = parent_dir / compress_dir_name

        # Generate the new filename
        sanitized_name = sanitize_filename(relative_path.name)

        # Set the output path to be in the compress subdirectory
        output_path = directory / compress_subdir / sanitized_name

        # Change extension if output format is specified
        if output_format and output_format != 'original':
            output_path = output_path.with_suffix(f'.{output_format}')

        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Compress the image
        if not PROGRESS_BAR_SUPPORT:
            print_info(f"[{stats['processed']}/{total_images}] Processing: {path}")

        result = compress_image(path, output_path, quality, max_width, output_format, preserve_original)

        # Update statistics
        if isinstance(result, dict) and result.get('success', False):
            stats['successful'] += 1
            stats['total_original_size'] += result['original_size']
            stats['total_compressed_size'] += result['compressed_size']
            if result.get('was_resized', False):
                stats['resized_images'] += 1
        else:
            stats['failed'] += 1
            error_type = result.get('error', 'unknown') if isinstance(result, dict) else 'unknown'
            stats['errors'][error_type] = stats['errors'].get(error_type, 0) + 1

    # Print summary
    print_header("\nCompression Summary")
    print_success(f"Processed: {stats['processed']} images")
    print_success(f"Successfully compressed: {stats['successful']} images")
    if stats['failed'] > 0:
        print_warning(f"Failed: {stats['failed']} images")
        for error, count in stats['errors'].items():
            print_warning(f"  - {error}: {count} images")

    if stats['successful'] > 0:
        total_reduction = (1 - stats['total_compressed_size'] / stats['total_original_size']) * 100
        saved_space = (stats['total_original_size'] - stats['total_compressed_size']) / (1024 * 1024)

        print_success(f"Total size reduction: {stats['total_original_size']/1024/1024:.2f}MB -> {stats['total_compressed_size']/1024/1024:.2f}MB")
        print_success(f"Space saved: {saved_space:.2f}MB ({total_reduction:.1f}%)")
        if stats['resized_images'] > 0:
            print_info(f"Resized {stats['resized_images']} images to fit maximum width of {max_width}px")

    # Generate report file
    format_name = output_format if output_format != 'original' else 'original'
    compress_dir_name = f"compress-{max_width}-{format_name}-{quality}"
    report_path = directory / f"compression_report_{timestamp}.txt"
    try:
        with open(report_path, 'w') as f:
            f.write(f"Image Compression Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Directory: {directory}\n")
            f.write(f"Quality: {quality}\n")
            f.write(f"Maximum width: {max_width}px\n")
            f.write(f"Output format: {output_format}\n")
            f.write(f"Preserve originals: {preserve_original}\n")
            f.write(f"Compressed images directory: {compress_dir_name}/\n\n")

            f.write(f"Total images processed: {stats['processed']}\n")
            f.write(f"Successfully compressed: {stats['successful']}\n")
            f.write(f"Failed: {stats['failed']}\n\n")

            if stats['successful'] > 0:
                f.write(f"Original size: {stats['total_original_size']/1024/1024:.2f}MB\n")
                f.write(f"Compressed size: {stats['total_compressed_size']/1024/1024:.2f}MB\n")
                f.write(f"Space saved: {saved_space:.2f}MB ({total_reduction:.1f}%)\n")
                f.write(f"Resized images: {stats['resized_images']}\n\n")

            if stats['failed'] > 0:
                f.write("Errors:\n")
                for error, count in stats['errors'].items():
                    f.write(f"  - {error}: {count} images\n")

        print_info(f"Detailed report saved to: {report_path}")
    except Exception as e:
        print_warning(f"Could not save report: {e}")

    return stats

def main():
    """Main function to run the interactive image compression script."""
    print_header("Image Compression Tool")
    print_info("This tool compresses images in a directory with customizable settings.")

    # Get directory from user
    while True:
        directory = input("Enter the directory path containing images to compress: ").strip()
        if os.path.isdir(directory):
            break
        print_error("Invalid directory path. Please try again.")

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
            print_warning("Quality must be between 1 and 100.")
        except ValueError:
            print_warning("Please enter a valid number.")

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
            print_warning("Width must be a positive number.")
        except ValueError:
            print_warning("Please enter a valid number.")

    # Get output format
    print_info("\nOutput format options:")
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
            print_warning("Please enter a valid option (1-4).")

    # Ask if user wants to preserve original files
    preserve_original = input("\nPreserve original files in an 'originals' subfolder? (y/n, default: n): ").strip().lower() == 'y'

    # Create the output directory name
    format_name = output_format if output_format != 'original' else 'original'
    compress_dir_name = f"compress-{max_width}-{format_name}-{quality}"

    # Confirm settings
    print_info("\nCompression Settings:")
    print(f"Directory: {directory}")
    print(f"Quality: {quality}")
    print(f"Maximum width: {max_width}px")
    print(f"Output format: {output_format}")
    print(f"Preserve originals: {'Yes' if preserve_original else 'No'}")
    print(f"Compressed images will be saved in: {compress_dir_name}/ subdirectory")

    confirm = input("\nProceed with these settings? (y/n): ").strip().lower()
    if confirm != 'y':
        print_warning("Operation cancelled.")
        return

    # Process the directory
    try:
        process_directory(directory, quality, max_width, output_format, preserve_original)
        print_success("\nCompression process completed!")
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
    except Exception as e:
        print_error(f"\nAn unexpected error occurred: {e}")

    print_info("\nThank you for using the Image Compression Tool!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
