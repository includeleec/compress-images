# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based image compression tool that processes images in directories with customizable quality, format conversion, and resizing options. The project consists of two main scripts:

- `compress_images.py` - Full-featured interactive compression tool with progress tracking, statistics, and reporting
- `image_compressor.py` - Simpler version of the compression tool without advanced features

## Key Commands

### Running the main compression tool
```bash
python compress_images.py
```

### Creating test images for development
```bash
python create_test_images.py
```

### Checking Python environment and dependencies
```bash
python check_python.py
```

## Dependencies

### Required
- **Pillow (PIL)**: Core image processing library
  ```bash
  pip install pillow
  ```

### Optional (for enhanced UX)
- **colorama**: Colored terminal output
- **tqdm**: Progress bar support
  ```bash
  pip install colorama tqdm
  ```

## Architecture

### Core Components

**compress_images.py** (main script):
- Interactive CLI with user prompts for compression settings
- Progress tracking with tqdm integration when available
- Comprehensive error handling and reporting
- Organized output structure in subdirectories (`compress-{width}-{format}-{quality}/`)
- Detailed compression reports with timestamps
- Optional original file preservation in `originals/` subfolder
- Random filename generation for compressed files (`{random_number}-compress.{ext}`)

**image_compressor.py** (simplified version):
- Basic compression functionality
- ASCII filename sanitization for non-English filenames
- Auto-installation of Pillow if missing

### Key Functions

- `sanitize_filename()`: Handles non-ASCII filenames (compress_images.py uses random naming, image_compressor.py uses ASCII conversion)
- `compress_image()`: Core compression logic with quality, resizing, and format conversion
- `process_directory()`: Recursive directory processing with statistics tracking

### File Organization

- Compressed images are saved in organized subdirectories with naming pattern: `compress-{max_width}-{format}-{quality}/`
- Original files can be preserved in `originals/` subdirectory (compress_images.py only)
- Compression reports generated as `compression_report_{timestamp}.txt`

### Supported Formats

Input/Output: JPG, JPEG, PNG, BMP, WebP, TIFF

## Development Notes

- The codebase follows a functional programming approach with clear separation of concerns
- Error handling is comprehensive in compress_images.py with graceful degradation for missing optional dependencies
- Both scripts handle non-ASCII filenames but use different strategies (random vs ASCII conversion)
- No test framework is currently in place - testing is done with manually created test images