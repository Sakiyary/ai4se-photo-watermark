"""Tests for EXIF reader functionality."""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

from photo_watermark.core.exif_reader import ExifReader


class TestExifReader:
  """Test cases for ExifReader class."""

  def setup_method(self):
    """Set up test fixtures."""
    self.reader = ExifReader()

  def test_init(self):
    """Test ExifReader initialization."""
    reader = ExifReader()
    assert reader is not None

  def test_extract_date_taken_file_not_found(self):
    """Test handling of non-existent file."""
    with pytest.raises(FileNotFoundError):
      self.reader.extract_date_taken("non_existent_file.jpg")

  def test_parse_datetime_string_valid_formats(self):
    """Test parsing various valid datetime formats."""
    test_cases = [
        ("2024:03:15 14:30:25", datetime(2024, 3, 15, 14, 30, 25)),
        ("2024-03-15 14:30:25", datetime(2024, 3, 15, 14, 30, 25)),
        ("2024:03:15", datetime(2024, 3, 15)),
        ("2024-03-15", datetime(2024, 3, 15)),
    ]

    for date_str, expected in test_cases:
      result = self.reader._parse_datetime_string(date_str)
      assert result == expected

  def test_parse_datetime_string_invalid_formats(self):
    """Test parsing invalid datetime formats."""
    invalid_cases = [
        "",
        "   ",
        "invalid_date",
        "2024/03/15",  # Unsupported format
        "0000:00:00 00:00:00",  # Would be handled by calling method
    ]

    for date_str in invalid_cases:
      result = self.reader._parse_datetime_string(date_str)
      assert result is None

  def test_format_date(self):
    """Test date formatting."""
    date_obj = datetime(2024, 3, 15, 14, 30, 25)
    result = self.reader.format_date(date_obj)
    assert result == "2024-03-15"

  def test_is_supported_format(self):
    """Test supported file format checking."""
    supported_files = [
        "image.jpg",
        "image.jpeg",
        "image.JPG",
        "image.JPEG",
        "image.tiff",
        "image.tif",
        "image.TIFF",
        "image.TIF"
    ]

    unsupported_files = [
        "image.png",
        "image.bmp",
        "image.gif",
        "document.pdf",
        "file.txt"
    ]

    for filename in supported_files:
      assert self.reader.is_supported_format(filename)

    for filename in unsupported_files:
      assert not self.reader.is_supported_format(filename)

  @patch('photo_watermark.core.exif_reader.Image.open')
  def test_extract_with_pil_success(self, mock_image_open):
    """Test successful EXIF extraction with PIL."""
    # Mock PIL Image and EXIF data
    mock_image = MagicMock()
    mock_image.__enter__ = MagicMock(return_value=mock_image)
    mock_image.__exit__ = MagicMock(return_value=None)

    # Simulate EXIF data with DateTimeOriginal
    mock_exif = {
        306: "2024:03:15 14:30:25"  # DateTime tag
    }
    mock_image.getexif.return_value = mock_exif
    mock_image_open.return_value = mock_image

    # Mock TAGS to return the correct tag name
    with patch('photo_watermark.core.exif_reader.TAGS', {306: "DateTime"}):
      result = self.reader._extract_with_pil(Path("test.jpg"))

    assert result == datetime(2024, 3, 15, 14, 30, 25)

  @patch('photo_watermark.core.exif_reader.Image.open')
  def test_extract_with_pil_no_exif(self, mock_image_open):
    """Test PIL extraction with no EXIF data."""
    mock_image = MagicMock()
    mock_image.__enter__ = MagicMock(return_value=mock_image)
    mock_image.__exit__ = MagicMock(return_value=None)
    mock_image.getexif.return_value = {}
    mock_image_open.return_value = mock_image

    result = self.reader._extract_with_pil(Path("test.jpg"))
    assert result is None

  @patch('photo_watermark.core.exif_reader.Image.open')
  def test_extract_with_pil_exception(self, mock_image_open):
    """Test PIL extraction with exception."""
    mock_image_open.side_effect = Exception("PIL error")

    result = self.reader._extract_with_pil(Path("test.jpg"))
    assert result is None

  @patch('builtins.open')
  @patch('photo_watermark.core.exif_reader.exifread.process_file')
  def test_extract_with_exifread_success(self, mock_process_file, mock_open):
    """Test successful EXIF extraction with exifread."""
    # Mock exifread tags
    mock_tags = {
        "EXIF DateTimeOriginal": MagicMock()
    }
    mock_tags["EXIF DateTimeOriginal"].__str__ = lambda: "2024:03:15 14:30:25"
    mock_process_file.return_value = mock_tags

    result = self.reader._extract_with_exifread(Path("test.jpg"))
    assert result == datetime(2024, 3, 15, 14, 30, 25)

  @patch('builtins.open')
  @patch('photo_watermark.core.exif_reader.exifread.process_file')
  def test_extract_with_exifread_no_tags(self, mock_process_file, mock_open):
    """Test exifread extraction with no relevant tags."""
    mock_process_file.return_value = {}

    result = self.reader._extract_with_exifread(Path("test.jpg"))
    assert result is None

  @patch('builtins.open')
  @patch('photo_watermark.core.exif_reader.exifread.process_file')
  def test_extract_with_exifread_exception(self, mock_process_file, mock_open):
    """Test exifread extraction with exception."""
    mock_open.side_effect = Exception("File error")

    result = self.reader._extract_with_exifread(Path("test.jpg"))
    assert result is None

  def test_get_formatted_date_success(self):
    """Test getting formatted date in one step."""
    with patch.object(self.reader, 'extract_date_taken') as mock_extract:
      mock_extract.return_value = datetime(2024, 3, 15, 14, 30, 25)

      result = self.reader.get_formatted_date("test.jpg")
      assert result == "2024-03-15"

  def test_get_formatted_date_no_date(self):
    """Test getting formatted date when no date found."""
    with patch.object(self.reader, 'extract_date_taken') as mock_extract:
      mock_extract.return_value = None

      result = self.reader.get_formatted_date("test.jpg")
      assert result is None

  def create_test_image_file(self) -> Path:
    """Create a test image file for integration testing."""
    # Create a temporary image file
    temp_dir = Path(tempfile.gettempdir())
    test_image_path = temp_dir / "test_image.jpg"

    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    image.save(test_image_path)

    return test_image_path

  def test_integration_with_real_image(self):
    """Integration test with a real image file (no EXIF)."""
    test_image = self.create_test_image_file()

    try:
      # This should return None as our generated image has no EXIF
      result = self.reader.extract_date_taken(test_image)
      assert result is None

      # Test the formatted date method too
      formatted = self.reader.get_formatted_date(test_image)
      assert formatted is None

    finally:
      # Cleanup
      if test_image.exists():
        test_image.unlink()

  def test_path_handling(self):
    """Test that both string and Path objects work."""
    test_image = self.create_test_image_file()

    try:
      # Test with string path
      result1 = self.reader.extract_date_taken(str(test_image))

      # Test with Path object
      result2 = self.reader.extract_date_taken(test_image)

      # Both should give same result
      assert result1 == result2

    finally:
      if test_image.exists():
        test_image.unlink()
