"""Image processing and watermark application."""

import logging
from pathlib import Path
from typing import List, Optional, Union, Tuple

from PIL import Image

from .exif_reader import ExifReader
from .watermark import WatermarkConfig, WatermarkRenderer


# Configure logging
logger = logging.getLogger(__name__)


class ImageProcessor:
  """Handles image loading, processing, and watermark application."""

  def __init__(self):
    """Initialize the image processor."""
    self.exif_reader = ExifReader()
    self.supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif'}

  def load_image(self, image_path: Union[str, Path]) -> Image.Image:
    """
    Load an image from file path.

    Args:
        image_path: Path to the image file

    Returns:
        PIL Image object

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image format is not supported
        IOError: If image cannot be loaded
    """
    image_path = Path(image_path)

    if not image_path.exists():
      raise FileNotFoundError(f"Image file not found: {image_path}")

    if not self.is_supported_format(image_path):
      raise ValueError(f"Unsupported image format: {image_path.suffix}")

    try:
      image = Image.open(image_path)
      # Convert to RGB if necessary (handles RGBA, CMYK, etc.)
      if image.mode != 'RGB':
        image = image.convert('RGB')
      return image
    except Exception as e:
      raise IOError(f"Failed to load image {image_path}: {str(e)}")

  def save_image(
      self,
      image: Image.Image,
      output_path: Union[str, Path],
      quality: int = 95
  ) -> None:
    """
    Save image to file.

    Args:
        image: PIL Image object to save
        output_path: Path where to save the image
        quality: JPEG quality (1-100), only used for JPEG files

    Raises:
        IOError: If image cannot be saved
    """
    output_path = Path(output_path)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
      # Determine save parameters based on file extension
      save_kwargs = {}
      if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
        save_kwargs['quality'] = quality
        save_kwargs['optimize'] = True

      image.save(output_path, **save_kwargs)
      logger.info(f"Saved watermarked image to: {output_path}")

    except Exception as e:
      raise IOError(f"Failed to save image to {output_path}: {str(e)}")

  def add_watermark(
      self,
      image: Image.Image,
      watermark_text: str,
      config: WatermarkConfig
  ) -> Image.Image:
    """
    Add watermark to an image.

    Args:
        image: PIL Image object
        watermark_text: Text to use as watermark
        config: Watermark configuration

    Returns:
        New PIL Image object with watermark applied
    """
    renderer = WatermarkRenderer(config)
    return renderer.render_watermark(image, watermark_text)

  def process_single_image(
      self,
      input_path: Union[str, Path],
      output_path: Union[str, Path],
      config: WatermarkConfig
  ) -> bool:
    """
    Process a single image: load, add watermark, save.

    Args:
        input_path: Path to input image
        output_path: Path for output image
        config: Watermark configuration

    Returns:
        True if processing successful, False otherwise
    """
    try:
      # Load image
      image = self.load_image(input_path)

      # Extract date from EXIF
      date_text = self.exif_reader.get_formatted_date(input_path)

      if date_text is None:
        logger.warning(f"No EXIF date found in {input_path}, skipping")
        return False

      # Add watermark
      watermarked_image = self.add_watermark(image, date_text, config)

      # Save result
      self.save_image(watermarked_image, output_path)

      logger.info(f"Successfully processed {input_path} -> {output_path}")
      return True

    except Exception as e:
      logger.error(f"Failed to process {input_path}: {str(e)}")
      return False

  def find_image_files(self, directory: Union[str, Path]) -> List[Path]:
    """
    Find all supported image files in a directory.

    Args:
        directory: Directory to search

    Returns:
        List of image file paths
    """
    directory = Path(directory)

    if not directory.exists():
      raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
      raise ValueError(f"Path is not a directory: {directory}")

    image_files = []

    for file_path in directory.iterdir():
      if file_path.is_file() and self.is_supported_format(file_path):
        image_files.append(file_path)

    # Sort files for consistent processing order
    return sorted(image_files)

  def process_directory(
      self,
      input_dir: Union[str, Path],
      config: WatermarkConfig,
      progress_callback: Optional[callable] = None
  ) -> Tuple[int, int]:
    """
    Process all images in a directory.

    Args:
        input_dir: Input directory containing images
        config: Watermark configuration
        progress_callback: Optional callback function for progress updates
                          Called with (current_index, total_files, filename, success)

    Returns:
        Tuple of (processed_count, total_files)
    """
    input_dir = Path(input_dir)

    # Create output directory
    output_dir = input_dir.parent / f"{input_dir.name}_watermark"
    output_dir.mkdir(exist_ok=True)

    # Find all image files
    image_files = self.find_image_files(input_dir)

    if not image_files:
      logger.warning(f"No supported image files found in {input_dir}")
      return 0, 0

    logger.info(f"Found {len(image_files)} image files to process")

    processed_count = 0

    for i, image_path in enumerate(image_files):
      # Create output path with same filename
      output_path = output_dir / image_path.name

      # Process the image
      success = self.process_single_image(image_path, output_path, config)

      if success:
        processed_count += 1

      # Call progress callback if provided
      if progress_callback:
        progress_callback(i + 1, len(image_files), image_path.name, success)

    logger.info(
        f"Processing complete: {processed_count}/{len(image_files)} images processed")
    return processed_count, len(image_files)

  def process_path(
      self,
      input_path: Union[str, Path],
      config: WatermarkConfig,
      output_path: Optional[Union[str, Path]] = None,
      progress_callback: Optional[callable] = None
  ) -> Tuple[int, int]:
    """
    Process a file or directory path.

    Args:
        input_path: Path to image file or directory
        config: Watermark configuration
        output_path: Optional output path (for single files)
        progress_callback: Optional progress callback

    Returns:
        Tuple of (processed_count, total_files)
    """
    input_path = Path(input_path)

    if not input_path.exists():
      raise FileNotFoundError(f"Path not found: {input_path}")

    if input_path.is_file():
      # Process single file
      if output_path is None:
        # Create output path in same directory with _watermark suffix
        output_path = input_path.parent / \
            f"{input_path.stem}_watermark{input_path.suffix}"

      success = self.process_single_image(input_path, output_path, config)

      if progress_callback:
        progress_callback(1, 1, input_path.name, success)

      return (1 if success else 0), 1

    elif input_path.is_dir():
      # Process directory
      return self.process_directory(input_path, config, progress_callback)

    else:
      raise ValueError(f"Invalid path type: {input_path}")

  def is_supported_format(self, file_path: Union[str, Path]) -> bool:
    """
    Check if file format is supported.

    Args:
        file_path: Path to file

    Returns:
        True if format is supported
    """
    return Path(file_path).suffix.lower() in self.supported_formats

  def get_image_info(self, image_path: Union[str, Path]) -> dict:
    """
    Get information about an image file.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with image information
    """
    image_path = Path(image_path)

    try:
      image = self.load_image(image_path)
      date_text = self.exif_reader.get_formatted_date(image_path)

      return {
          "path": str(image_path),
          "size": image.size,
          "mode": image.mode,
          "format": image.format,
          "has_exif_date": date_text is not None,
          "exif_date": date_text,
          "file_size": image_path.stat().st_size,
          "supported": True
      }

    except Exception as e:
      return {
          "path": str(image_path),
          "error": str(e),
          "supported": False
      }
