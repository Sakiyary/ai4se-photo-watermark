# AI4SE Photo Watermark

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python command-line tool for adding date watermarks to photos using EXIF data. Automatically extracts the date taken from image metadata and overlays it as a customizable watermark.

## Features

- 📸 **EXIF Date Extraction**: Automatically reads shooting date from image metadata
- 🎨 **Customizable Watermarks**: Control font size, color, position, and opacity
- 📁 **Batch Processing**: Process single images or entire directories
- 🔤 **Multiple Fonts**: Support for system fonts and custom font files
- 🎯 **9 Position Presets**: Place watermarks anywhere on your images
- 🛡️ **Error Handling**: Graceful handling of missing EXIF data and unsupported formats
- ⚡ **Performance Optimized**: Efficient processing with minimal memory usage

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/Sakiyary/ai4se-photo-watermark.git
cd ai4se-photo-watermark
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### As a Package

```bash
pip install -e .
```

## Quick Start

### Basic Usage

Add watermarks to all images in a directory:
```bash
python -m photo_watermark /path/to/photos
```

Process a single image:
```bash
python -m photo_watermark /path/to/photo.jpg
```

### Custom Styling

```bash
# Large white text in top-right corner
python -m photo_watermark /path/to/photos --font-size 48 --color white --position top-right

# Red text with black outline
python -m photo_watermark /path/to/photos --color red --outline-color black --outline-width 2

# Semi-transparent watermark
python -m photo_watermark /path/to/photos --opacity 128
```

## Command Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--font-size` | `-s` | 32 | Font size for watermark text |
| `--color` | `-c` | white | Text color (name, hex, or RGB) |
| `--position` | `-p` | bottom-right | Watermark position |
| `--margin` | `-m` | 10 | Margin from edges in pixels |
| `--opacity` | | 255 | Text opacity (0-255) |
| `--outline-width` | | 1 | Width of text outline |
| `--outline-color` | | black | Color of text outline |
| `--font-path` | | | Path to custom font file |
| `--output` | `-o` | | Output path (single files only) |
| `--quality` | `-q` | 95 | JPEG quality (1-100) |
| `--verbose` | `-v` | | Enable verbose output |
| `--quiet` | | | Suppress progress output |

### Position Options

- `top-left`, `top-center`, `top-right`
- `left-center`, `center`, `right-center`  
- `bottom-left`, `bottom-center`, `bottom-right`

### Color Formats

- **Named colors**: `white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `gray`
- **Hex colors**: `#FF0000`, `#00FF00`, `#0000FF`
- **RGB format**: `rgb(255, 0, 0)`, `rgba(255, 0, 0, 128)`

## Examples

### Directory Processing
```bash
# Process all images in 'vacation_photos' directory
python -m photo_watermark ./vacation_photos

# Output will be saved to 'vacation_photos_watermark' directory
```

### Custom Styling Examples
```bash
# Large golden text in bottom-left with custom margin
python -m photo_watermark ./photos --font-size 40 --color "#FFD700" --position bottom-left --margin 20

# Centered semi-transparent text
python -m photo_watermark ./photos --position center --opacity 128

# Custom font with outline
python -m photo_watermark ./photos --font-path "/path/to/font.ttf" --outline-width 3
```

### Single File Processing
```bash
# Process single file with custom output location
python -m photo_watermark photo.jpg --output watermarked_photo.jpg
```

## Supported Formats

- **Input**: JPEG (.jpg, .jpeg), TIFF (.tif, .tiff)
- **Output**: Same as input format with optional quality control for JPEG

## How It Works

1. **EXIF Reading**: Extracts shooting date from image metadata using multiple fallback methods
2. **Date Formatting**: Converts date to YYYY-MM-DD format  
3. **Watermark Rendering**: Creates text overlay with specified styling
4. **Position Calculation**: Places watermark according to position and margin settings
5. **Image Processing**: Applies watermark and saves to output location

## Error Handling

- **No EXIF Date**: Images without date metadata are skipped with a warning
- **Unsupported Formats**: Non-JPEG/TIFF files are ignored
- **Missing Files**: Clear error messages for file not found issues
- **Permission Errors**: Helpful suggestions for access problems

## Project Structure

```
src/photo_watermark/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point
├── cli.py                   # Command line interface
├── core/                    # Core functionality
│   ├── exif_reader.py       # EXIF data extraction
│   ├── image_processor.py   # Image processing pipeline
│   └── watermark.py         # Watermark rendering engine
├── utils/                   # Utility functions
│   ├── file_utils.py        # File operations
│   └── validators.py        # Input validation
└── exceptions.py            # Custom exceptions
```

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black src/ tests/

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=photo_watermark

# Run specific test file
pytest tests/test_exif_reader.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pillow](https://pillow.readthedocs.io/) for image processing
- Uses [ExifRead](https://github.com/ianare/exif-py) for EXIF data extraction
- CLI powered by [Click](https://click.palletsprojects.com/)

## Troubleshooting

### Common Issues

**Q: "No EXIF date found" for all images**
A: Some cameras don't store date information in EXIF. Try using images from a different camera or smartphone.

**Q: Watermark appears too small/large**
A: Adjust the `--font-size` parameter. For high-resolution images, try larger values (64, 96, 128).

**Q: Custom font not working**
A: Ensure the font file path is correct and the font format is supported (.ttf, .otf).

**Q: Permission denied errors**
A: Make sure you have write permissions for the output directory.

---

For more information, issues, or feature requests, visit the [GitHub repository](https://github.com/Sakiyary/ai4se-photo-watermark).