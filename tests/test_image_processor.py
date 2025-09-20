"""Tests for image processing functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest
from PIL import Image

from photo_watermark.core.image_processor import ImageProcessor
from photo_watermark.core.watermark import WatermarkConfig, WatermarkPosition
from photo_watermark.exceptions import ImageProcessingError


class TestImageProcessor:
  """Test ImageProcessor class."""

  def setup_method(self):
    """Set up test fixtures."""
    self.processor = ImageProcessor()
    self.test_config = WatermarkConfig(
        font_size=24,
        color="white",
        position=WatermarkPosition.BOTTOM_RIGHT
    )

  def test_init(self):
    """Test processor initialization."""
    assert self.processor.exif_reader is not None
    assert self.processor.supported_formats == {
        '.jpg', '.jpeg', '.tiff', '.tif'}

  def test_is_supported_format(self):
    """Test file format support checking."""
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
      assert self.processor.is_supported_format(filename)

    for filename in unsupported_files:
      assert not self.processor.is_supported_format(filename)

  def create_test_image_file(self, suffix=".jpg") -> Path:
    """Create a temporary test image file."""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    # Create a simple test image
    image = Image.new('RGB', (200, 150), color='red')
    image.save(temp_path)

    return temp_path

  def test_load_image_success(self):
    """Test successful image loading."""
    test_image_path = self.create_test_image_file()

    try:
      image = self.processor.load_image(test_image_path)

      assert isinstance(image, Image.Image)
      assert image.mode == 'RGB'
      assert image.size == (200, 150)

    finally:
      test_image_path.unlink()

  def test_load_image_file_not_found(self):
    """Test loading non-existent image."""
    with pytest.raises(FileNotFoundError):
      self.processor.load_image("non_existent_file.jpg")

  def test_load_image_unsupported_format(self):
    """Test loading unsupported image format."""
    test_image_path = self.create_test_image_file(suffix=".png")

    try:
      with pytest.raises(ValueError, match="Unsupported image format"):
        self.processor.load_image(test_image_path)
    finally:
      test_image_path.unlink()

  def test_save_image_success(self):
    """Test successful image saving."""
    # Create test image
    image = Image.new('RGB', (100, 100), color='blue')

    # Create temporary output path
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    output_path = Path(temp_file.name)
    temp_file.close()
    output_path.unlink()  # Remove the file, keep the path

    try:
      self.processor.save_image(image, output_path)

      # Verify file was created and has correct content
      assert output_path.exists()

      loaded_image = Image.open(output_path)
      assert loaded_image.size == (100, 100)

    finally:
      if output_path.exists():
        output_path.unlink()

  def test_save_image_creates_directory(self):
    """Test that save_image creates output directory if needed."""
    image = Image.new('RGB', (100, 100), color='green')

    # Create temporary directory path that doesn't exist
    temp_dir = Path(tempfile.gettempdir()) / "test_watermark_dir"
    output_path = temp_dir / "test_image.jpg"

    try:
      self.processor.save_image(image, output_path)

      assert output_path.exists()
      assert temp_dir.exists()

    finally:
      if output_path.exists():
        output_path.unlink()
      if temp_dir.exists():
        temp_dir.rmdir()

  def test_add_watermark(self):
    """Test watermark addition to image."""
    image = Image.new('RGB', (300, 200), color='white')
    text = "2024-03-15"

    result = self.processor.add_watermark(image, text, self.test_config)

    assert isinstance(result, Image.Image)
    assert result.size == image.size
    assert result.mode == image.mode
    # Should be a new image object
    assert result is not image

  @patch('photo_watermark.core.image_processor.logger')
  def test_process_single_image_success(self, mock_logger):
    """Test successful single image processing."""
    # Create test image
    test_image_path = self.create_test_image_file()

    # Create output path
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    output_path = Path(temp_file.name)
    temp_file.close()
    output_path.unlink()

    try:
      # Mock EXIF reader to return a date
      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = "2024-03-15"

        result = self.processor.process_single_image(
            test_image_path,
            output_path,
            self.test_config
        )

        assert result is True
        assert output_path.exists()
        mock_exif.assert_called_once_with(test_image_path)

    finally:
      if test_image_path.exists():
        test_image_path.unlink()
      if output_path.exists():
        output_path.unlink()

  @patch('photo_watermark.core.image_processor.logger')
  def test_process_single_image_no_exif(self, mock_logger):
    """Test single image processing with no EXIF date."""
    test_image_path = self.create_test_image_file()
    output_path = Path(tempfile.gettempdir()) / "output.jpg"

    try:
      # Mock EXIF reader to return None (no date)
      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = None

        result = self.processor.process_single_image(
            test_image_path,
            output_path,
            self.test_config
        )

        assert result is False
        assert not output_path.exists()
        mock_logger.warning.assert_called_once()

    finally:
      if test_image_path.exists():
        test_image_path.unlink()
      if output_path.exists():
        output_path.unlink()

  def test_find_image_files_success(self):
    """Test finding image files in directory."""
    # Create temporary directory with test files
    temp_dir = Path(tempfile.mkdtemp())

    try:
      # Create test files
      (temp_dir / "image1.jpg").touch()
      (temp_dir / "image2.jpeg").touch()
      (temp_dir / "image3.tiff").touch()
      (temp_dir / "document.pdf").touch()  # Should be ignored
      (temp_dir / "image4.png").touch()    # Should be ignored

      image_files = self.processor.find_image_files(temp_dir)

      # Should find 3 supported image files, sorted alphabetically
      assert len(image_files) == 3
      assert all(isinstance(f, Path) for f in image_files)

      filenames = [f.name for f in image_files]
      assert "image1.jpg" in filenames
      assert "image2.jpeg" in filenames
      assert "image3.tiff" in filenames
      assert "document.pdf" not in filenames
      assert "image4.png" not in filenames

      # Should be sorted
      assert filenames == sorted(filenames)

    finally:
      # Cleanup
      for file in temp_dir.iterdir():
        file.unlink()
      temp_dir.rmdir()

  def test_find_image_files_directory_not_found(self):
    """Test finding files in non-existent directory."""
    with pytest.raises(FileNotFoundError):
      self.processor.find_image_files("non_existent_directory")

  def test_find_image_files_not_directory(self):
    """Test finding files when path is not a directory."""
    test_file = self.create_test_image_file()

    try:
      with pytest.raises(ValueError, match="Path is not a directory"):
        self.processor.find_image_files(test_file)
    finally:
      test_file.unlink()

  def test_process_directory_success(self):
    """Test successful directory processing."""
    # Create temporary directory with test images
    temp_dir = Path(tempfile.mkdtemp())

    try:
      # Create test image files
      for i in range(3):
        image = Image.new('RGB', (100, 100), color='red')
        image_path = temp_dir / f"test{i}.jpg"
        image.save(image_path)

      # Mock EXIF reader to return dates
      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = "2024-03-15"

        processed, total = self.processor.process_directory(
            temp_dir,
            self.test_config
        )

        assert processed == 3
        assert total == 3

        # Check output directory was created
        output_dir = temp_dir.parent / f"{temp_dir.name}_watermark"
        assert output_dir.exists()

        # Check output files exist
        for i in range(3):
          output_file = output_dir / f"test{i}.jpg"
          assert output_file.exists()

    finally:
      # Cleanup
      self.cleanup_directory(temp_dir)
      output_dir = temp_dir.parent / f"{temp_dir.name}_watermark"
      if output_dir.exists():
        self.cleanup_directory(output_dir)

  def test_process_directory_with_progress_callback(self):
    """Test directory processing with progress callback."""
    temp_dir = Path(tempfile.mkdtemp())
    progress_calls = []

    def progress_callback(current, total, filename, success):
      progress_calls.append((current, total, filename, success))

    try:
      # Create test image
      image = Image.new('RGB', (100, 100), color='blue')
      image_path = temp_dir / "test.jpg"
      image.save(image_path)

      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = "2024-03-15"

        processed, total = self.processor.process_directory(
            temp_dir,
            self.test_config,
            progress_callback=progress_callback
        )

        assert processed == 1
        assert total == 1
        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1, "test.jpg", True)

    finally:
      self.cleanup_directory(temp_dir)
      output_dir = temp_dir.parent / f"{temp_dir.name}_watermark"
      if output_dir.exists():
        self.cleanup_directory(output_dir)

  def test_process_path_single_file(self):
    """Test processing a single file path."""
    test_image_path = self.create_test_image_file()

    try:
      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = "2024-03-15"

        processed, total = self.processor.process_path(
            test_image_path,
            self.test_config
        )

        assert processed == 1
        assert total == 1

        # Check output file was created
        expected_output = test_image_path.parent / \
            f"{test_image_path.stem}_watermark{test_image_path.suffix}"
        assert expected_output.exists()

    finally:
      if test_image_path.exists():
        test_image_path.unlink()
      expected_output = test_image_path.parent / \
          f"{test_image_path.stem}_watermark{test_image_path.suffix}"
      if expected_output.exists():
        expected_output.unlink()

  def test_process_path_directory(self):
    """Test processing a directory path."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
      # Create test image
      image = Image.new('RGB', (100, 100), color='green')
      image_path = temp_dir / "test.jpg"
      image.save(image_path)

      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = "2024-03-15"

        processed, total = self.processor.process_path(
            temp_dir,
            self.test_config
        )

        assert processed == 1
        assert total == 1

    finally:
      self.cleanup_directory(temp_dir)
      output_dir = temp_dir.parent / f"{temp_dir.name}_watermark"
      if output_dir.exists():
        self.cleanup_directory(output_dir)

  def test_process_path_not_found(self):
    """Test processing non-existent path."""
    with pytest.raises(FileNotFoundError):
      self.processor.process_path(
          "non_existent_path",
          self.test_config
      )

  def test_get_image_info_success(self):
    """Test getting image information."""
    test_image_path = self.create_test_image_file()

    try:
      with patch.object(self.processor.exif_reader, 'get_formatted_date') as mock_exif:
        mock_exif.return_value = "2024-03-15"

        info = self.processor.get_image_info(test_image_path)

        assert info['supported'] is True
        assert info['path'] == str(test_image_path)
        assert info['size'] == (200, 150)
        assert info['mode'] == 'RGB'
        assert info['has_exif_date'] is True
        assert info['exif_date'] == "2024-03-15"
        assert 'file_size' in info
        assert isinstance(info['file_size'], int)

    finally:
      test_image_path.unlink()

  def test_get_image_info_error(self):
    """Test getting image information for problematic file."""
    info = self.processor.get_image_info("non_existent_file.jpg")

    assert info['supported'] is False
    assert info['path'] == "non_existent_file.jpg"
    assert 'error' in info

  def cleanup_directory(self, directory: Path):
    """Helper method to cleanup test directories."""
    if directory.exists():
      for file in directory.iterdir():
        if file.is_file():
          file.unlink()
        elif file.is_dir():
          self.cleanup_directory(file)
      directory.rmdir()
