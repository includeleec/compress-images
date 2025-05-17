# Tiny Images

A powerful and flexible image compression tool that helps you reduce image file sizes while maintaining quality.

## Features

- Interactive command-line interface
- Customizable compression quality
- Maximum width setting with aspect ratio preservation
- Format conversion options (JPG, PNG, WebP, etc.)
- Recursive directory traversal
- Non-ASCII filename handling
- Progress bar for visual feedback
- Option to preserve original files
- Detailed compression statistics and reports
- Compressed images are stored in organized subdirectories

## Requirements

### Python Version
- Python 3.6 or higher (Tested with Python 3.13.3)

### Required Packages
- Pillow (PIL): For image processing

### Optional Packages (for enhanced experience)
- colorama: For colored terminal output
- tqdm: For progress bar support

## Installation

1. Clone or download this repository:
   ```
   git clone https://github.com/yourusername/tiny-images.git
   cd tiny-images
   ```

2. Install the required packages:
   ```powershell
   pip install pillow
   ```

3. Install optional packages for enhanced experience:
   ```powershell
   pip install colorama tqdm
   ```

## Usage

### Basic Usage

Run the main compression script:

```powershell
python compress_images.py
```

The script will guide you through an interactive process to:
1. Select the directory containing images
2. Set compression quality (1-100)
3. Set maximum width (preserving aspect ratio)
4. Choose output format (JPG, PNG, WebP, or original)
5. Decide whether to preserve original files

### Output Structure

Compressed images are saved in a subdirectory with the naming format:
```
compress-[max_width]-[format]-[quality]
```

For example, if you set:
- Maximum width: 1920px
- Output format: webp
- Quality: 85

Your compressed images will be saved in:
```
compress-1920-webp-85/
```

### Compression Report

After compression, a detailed report is generated with:
- Compression settings
- Number of processed images
- Success/failure statistics
- Total size reduction
- Space saved
- Any errors encountered

The report is saved as `compression_report_[timestamp].txt` in the processed directory.

## Examples

### Example 1: Basic Compression

```powershell
python compress_images.py
```
Then follow the prompts to compress images with default settings.

### Example 2: Create Test Images

To create sample test images for testing the compression tool:

```powershell
python create_test_images.py
```

This will create various test images in the `test_images` directory with different sizes and formats.

## Tips for Best Results

1. **Quality Settings**:
   - 85-95: High quality, moderate compression
   - 70-85: Good balance between quality and file size
   - 50-70: Higher compression, some visible quality loss

2. **Format Selection**:
   - JPG: Best for photographs and complex images
   - PNG: Best for images with transparency or text
   - WebP: Modern format with good compression and quality

3. **Maximum Width**:
   - 1920px is a good default for most web and display purposes
   - Use higher values for images that need to be printed or displayed on large screens

## Troubleshooting

If you encounter any issues:

1. Ensure you have the required Python version and packages installed
2. Check file permissions in the directories you're working with
3. For large batches of images, ensure you have sufficient disk space

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
