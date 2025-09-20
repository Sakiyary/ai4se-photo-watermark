"""Tests for CLI interface."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from photo_watermark.cli import main
from photo_watermark.core.watermark import WatermarkPosition


class TestCLI:
  """Test CLI interface."""

  def setup_method(self):
    """Set up test fixtures."""
    self.runner = CliRunner()

  def create_test_image_file(self, suffix=".jpg") -> Path:
    """Create a temporary test image file."""
    from PIL import Image

    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    # Create a simple test image
    image = Image.new('RGB', (200, 150), color='red')
    image.save(temp_path)

    return temp_path

  def test_help_command(self):
    """Test help command."""
    result = self.runner.invoke(main, ['--help'])

    assert result.exit_code == 0
    assert 'Add date watermarks to photos using EXIF data' in result.output
    assert '--font-size' in result.output
    assert '--color' in result.output
    assert '--position' in result.output

  def test_version_command(self):
    """Test version command."""
    result = self.runner.invoke(main, ['--version'])

    assert result.exit_code == 0
    assert '1.0.0' in result.output

  @patch('photo_watermark.cli.ImageProcessor')
  def test_basic_command_success(self, mock_processor_class):
    """Test basic command execution."""
    # Create test image
    test_image = self.create_test_image_file()

    # Mock processor
    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (1, 1)  # processed, total
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image)])

      assert result.exit_code == 0
      assert 'Completed successfully!' in result.output

      # Verify processor was called correctly
      mock_processor.process_path.assert_called_once()

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_command_with_custom_options(self, mock_processor_class):
    """Test command with custom styling options."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (1, 1)
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [
          str(test_image),
          '--font-size', '48',
          '--color', 'red',
          '--position', 'top-left',
          '--margin', '20',
          '--opacity', '128'
      ])

      assert result.exit_code == 0

      # Check that processor was called with correct config
      call_args = mock_processor.process_path.call_args
      config = call_args[0][1]  # Second argument is config

      assert config.font_size == 48
      assert config.color == 'red'
      assert config.position == WatermarkPosition.TOP_LEFT
      assert config.margin == 20
      assert config.opacity == 128

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_verbose_mode(self, mock_processor_class):
    """Test verbose output mode."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (1, 1)
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image), '--verbose'])

      assert result.exit_code == 0
      assert 'Configuration:' in result.output
      assert 'Font size:' in result.output
      assert 'Color:' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_quiet_mode(self, mock_processor_class):
    """Test quiet output mode."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (1, 1)
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image), '--quiet'])

      assert result.exit_code == 0
      # Should have minimal output in quiet mode
      assert 'Summary:' not in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  def test_file_not_found(self):
    """Test handling of non-existent file."""
    result = self.runner.invoke(main, ['non_existent_file.jpg'])

    assert result.exit_code == 2  # Click error code
    assert 'does not exist' in result.output or 'No such file' in result.output

  @patch('photo_watermark.cli.ImageProcessor')
  def test_unsupported_format(self, mock_processor_class):
    """Test handling of unsupported file format."""
    # Create test PNG file (unsupported)
    test_image = self.create_test_image_file(suffix=".png")

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = False
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image)])

      assert result.exit_code == 1
      assert 'Unsupported file format' in result.output
      assert 'Supported formats' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_no_images_processed(self, mock_processor_class):
    """Test handling when no images are processed."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (0, 1)  # 0 processed, 1 total
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image)])

      assert result.exit_code == 1
      assert 'No images were processed successfully' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_no_files_found(self, mock_processor_class):
    """Test handling when no supported files are found."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (0, 0)  # 0 processed, 0 total
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image)])

      assert result.exit_code == 1
      assert 'No supported image files found' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  def test_invalid_font_size(self):
    """Test handling of invalid font size."""
    test_image = self.create_test_image_file()

    try:
      result = self.runner.invoke(main, [str(test_image), '--font-size', '0'])

      assert result.exit_code == 1
      assert 'Error:' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  def test_invalid_color(self):
    """Test handling of invalid color."""
    test_image = self.create_test_image_file()

    try:
      result = self.runner.invoke(
          main, [str(test_image), '--color', 'invalid_color'])

      assert result.exit_code == 1
      assert 'Error:' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  def test_invalid_position(self):
    """Test handling of invalid position."""
    test_image = self.create_test_image_file()

    try:
      result = self.runner.invoke(
          main, [str(test_image), '--position', 'invalid-position'])

      # Click should catch this before our validation
      assert result.exit_code == 2

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_processing_exception(self, mock_processor_class):
    """Test handling of processing exceptions."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.side_effect = Exception("Processing failed")
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image)])

      assert result.exit_code == 1
      assert 'Error during processing' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_keyboard_interrupt(self, mock_processor_class):
    """Test handling of keyboard interrupt."""
    test_image = self.create_test_image_file()

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.side_effect = KeyboardInterrupt()
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(test_image)])

      assert result.exit_code == 1
      assert 'Operation cancelled by user' in result.output

    finally:
      if test_image.exists():
        test_image.unlink()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_directory_processing_output(self, mock_processor_class):
    """Test output format for directory processing."""
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (2, 3)  # 2 processed, 3 total
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [str(temp_dir)])

      assert result.exit_code == 0
      assert 'Summary:' in result.output
      assert 'Processed: 2 images' in result.output
      assert 'Skipped: 1 image' in result.output
      assert 'Total: 3 images' in result.output
      assert 'Output directory:' in result.output
      assert '_watermark' in result.output

    finally:
      if temp_dir.exists():
        temp_dir.rmdir()

  @patch('photo_watermark.cli.ImageProcessor')
  def test_custom_output_path(self, mock_processor_class):
    """Test custom output path for single file."""
    test_image = self.create_test_image_file()
    output_path = Path(tempfile.gettempdir()) / "custom_output.jpg"

    mock_processor = MagicMock()
    mock_processor.is_supported_format.return_value = True
    mock_processor.process_path.return_value = (1, 1)
    mock_processor_class.return_value = mock_processor

    try:
      result = self.runner.invoke(main, [
          str(test_image),
          '--output', str(output_path)
      ])

      assert result.exit_code == 0

      # Check that custom output path was passed
      call_args = mock_processor.process_path.call_args
      assert call_args[1]['output_path'] == output_path

    finally:
      if test_image.exists():
        test_image.unlink()
      if output_path.exists():
        output_path.unlink()
