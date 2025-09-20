"""Tests for watermark configuration and rendering."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

from photo_watermark.core.watermark import (
    WatermarkConfig, WatermarkRenderer, WatermarkPosition
)
from photo_watermark.exceptions import InvalidConfigError


class TestWatermarkPosition:
  """Test WatermarkPosition enum."""

  def test_position_values(self):
    """Test that all position values are correctly defined."""
    expected_positions = {
        'top-left', 'top-center', 'top-right',
        'left-center', 'center', 'right-center',
        'bottom-left', 'bottom-center', 'bottom-right'
    }

    actual_positions = {pos.value for pos in WatermarkPosition}
    assert actual_positions == expected_positions


class TestWatermarkConfig:
  """Test WatermarkConfig dataclass."""

  def test_default_config(self):
    """Test default configuration values."""
    config = WatermarkConfig()

    assert config.font_size == 32
    assert config.color == "white"
    assert config.position == WatermarkPosition.BOTTOM_RIGHT
    assert config.margin == 10
    assert config.font_path is None
    assert config.outline_width == 1
    assert config.outline_color == "black"
    assert config.opacity == 255

  def test_custom_config(self):
    """Test custom configuration values."""
    config = WatermarkConfig(
        font_size=48,
        color="red",
        position=WatermarkPosition.TOP_LEFT,
        margin=20,
        opacity=128
    )

    assert config.font_size == 48
    assert config.color == "red"
    assert config.position == WatermarkPosition.TOP_LEFT
    assert config.margin == 20
    assert config.opacity == 128

  def test_invalid_font_size(self):
    """Test validation of invalid font size."""
    with pytest.raises(ValueError, match="Font size must be positive"):
      WatermarkConfig(font_size=0)

    with pytest.raises(ValueError, match="Font size must be positive"):
      WatermarkConfig(font_size=-10)

  def test_invalid_opacity(self):
    """Test validation of invalid opacity."""
    with pytest.raises(ValueError, match="Opacity must be between 0 and 255"):
      WatermarkConfig(opacity=-1)

    with pytest.raises(ValueError, match="Opacity must be between 0 and 255"):
      WatermarkConfig(opacity=256)

  def test_invalid_margin(self):
    """Test validation of invalid margin."""
    with pytest.raises(ValueError, match="Margin must be non-negative"):
      WatermarkConfig(margin=-5)


class TestWatermarkRenderer:
  """Test WatermarkRenderer class."""

  def setup_method(self):
    """Set up test fixtures."""
    self.config = WatermarkConfig(
        font_size=24,
        color="white",
        position=WatermarkPosition.BOTTOM_RIGHT,
        margin=10
    )
    self.renderer = WatermarkRenderer(self.config)

  def test_init(self):
    """Test renderer initialization."""
    assert self.renderer.config == self.config
    assert self.renderer._font_cache == {}

  def test_parse_color_named(self):
    """Test parsing named colors."""
    test_cases = [
        ("white", (255, 255, 255)),
        ("black", (0, 0, 0)),
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("gray", (128, 128, 128)),
        ("grey", (128, 128, 128)),
    ]

    for color_str, expected in test_cases:
      result = self.renderer._parse_color(color_str)
      assert result == expected

  def test_parse_color_hex(self):
    """Test parsing hex colors."""
    test_cases = [
        ("#FF0000", (255, 0, 0)),
        ("#00FF00", (0, 255, 0)),
        ("#0000FF", (0, 0, 255)),
        ("#F00", (255, 0, 0)),  # Short format
        ("#0F0", (0, 255, 0)),
        ("#00F", (0, 0, 255)),
        ("#FF0000FF", (255, 0, 0, 255)),  # With alpha
    ]

    for color_str, expected in test_cases:
      result = self.renderer._parse_color(color_str)
      assert result == expected

  def test_parse_color_rgb(self):
    """Test parsing RGB colors."""
    test_cases = [
        ("rgb(255, 0, 0)", (255, 0, 0)),
        ("rgba(255, 0, 0, 128)", (255, 0, 0, 128)),
        ("rgb(128,128,128)", (128, 128, 128)),  # No spaces
    ]

    for color_str, expected in test_cases:
      result = self.renderer._parse_color(color_str)
      assert result == expected

  def test_parse_color_invalid(self):
    """Test parsing invalid colors defaults to white."""
    invalid_colors = [
        "invalid_color",
        "#GGG",
        "rgb(300, 0, 0)",  # Values too high
        ""
    ]

    for color_str in invalid_colors:
      result = self.renderer._parse_color(color_str)
      assert result == (255, 255, 255)  # Default to white

  def test_calculate_position_bottom_right(self):
    """Test position calculation for bottom-right."""
    image_size = (800, 600)
    text_size = (100, 30)

    position = self.renderer._calculate_position(image_size, text_size)

    # bottom-right: (img_width - text_width - margin, img_height - text_height - margin)
    expected = (800 - 100 - 10, 600 - 30 - 10)
    assert position == expected

  def test_calculate_position_center(self):
    """Test position calculation for center."""
    config = WatermarkConfig(position=WatermarkPosition.CENTER)
    renderer = WatermarkRenderer(config)

    image_size = (800, 600)
    text_size = (100, 30)

    position = renderer._calculate_position(image_size, text_size)

    # center: ((img_width - text_width) // 2, (img_height - text_height) // 2)
    expected = ((800 - 100) // 2, (600 - 30) // 2)
    assert position == expected

  def test_calculate_position_top_left(self):
    """Test position calculation for top-left."""
    config = WatermarkConfig(position=WatermarkPosition.TOP_LEFT, margin=15)
    renderer = WatermarkRenderer(config)

    image_size = (800, 600)
    text_size = (100, 30)

    position = renderer._calculate_position(image_size, text_size)

    # top-left: (margin, margin)
    expected = (15, 15)
    assert position == expected

  @patch('photo_watermark.core.watermark.platform.system')
  @patch('photo_watermark.core.watermark.os.path.exists')
  @patch('photo_watermark.core.watermark.ImageFont.truetype')
  def test_get_default_font_windows(self, mock_truetype, mock_exists, mock_system):
    """Test getting default font on Windows."""
    mock_system.return_value = "Windows"
    mock_exists.side_effect = lambda path: path == "C:/Windows/Fonts/arial.ttf"
    mock_font = MagicMock()
    mock_truetype.return_value = mock_font

    font = self.renderer._get_default_font()

    assert font == mock_font
    mock_truetype.assert_called_with("C:/Windows/Fonts/arial.ttf", 24)

  @patch('photo_watermark.core.watermark.platform.system')
  @patch('photo_watermark.core.watermark.os.path.exists')
  @patch('photo_watermark.core.watermark.ImageFont.load_default')
  def test_get_default_font_fallback(self, mock_load_default, mock_exists, mock_system):
    """Test fallback to default font when system fonts not found."""
    mock_system.return_value = "Unknown"
    mock_exists.return_value = False
    mock_font = MagicMock()
    mock_load_default.return_value = mock_font

    font = self.renderer._get_default_font()

    assert font == mock_font
    mock_load_default.assert_called_once()

  def test_preview_watermark(self):
    """Test watermark preview functionality."""
    image_size = (800, 600)
    text = "2024-03-15"

    preview = self.renderer.preview_watermark(image_size, text)

    assert "position" in preview
    assert "text_size" in preview
    assert "text" in preview
    assert preview["text"] == text
    assert preview["font_size"] == 24
    assert preview["color"] == "white"
    assert preview["watermark_position"] == "bottom-right"

    # Check that position is a tuple of two integers
    assert isinstance(preview["position"], tuple)
    assert len(preview["position"]) == 2
    assert all(isinstance(x, int) for x in preview["position"])

  def create_test_image(self) -> Image.Image:
    """Create a test image for rendering tests."""
    return Image.new('RGB', (400, 300), color='blue')

  def test_render_watermark_basic(self):
    """Test basic watermark rendering."""
    image = self.create_test_image()
    text = "2024-03-15"

    # This should not raise an exception
    result = self.renderer.render_watermark(image, text)

    assert isinstance(result, Image.Image)
    assert result.size == image.size
    assert result.mode == image.mode
    # Ensure it's a copy, not the same object
    assert result is not image

  def test_render_watermark_with_outline(self):
    """Test watermark rendering with outline."""
    config = WatermarkConfig(
        outline_width=2,
        outline_color="black"
    )
    renderer = WatermarkRenderer(config)
    image = self.create_test_image()
    text = "2024-03-15"

    result = renderer.render_watermark(image, text)

    assert isinstance(result, Image.Image)
    assert result.size == image.size

  def test_render_watermark_with_opacity(self):
    """Test watermark rendering with custom opacity."""
    config = WatermarkConfig(opacity=128)
    renderer = WatermarkRenderer(config)
    image = self.create_test_image()
    text = "2024-03-15"

    result = renderer.render_watermark(image, text)

    assert isinstance(result, Image.Image)
    assert result.size == image.size

  def test_font_caching(self):
    """Test that fonts are cached properly."""
    # First call should cache the font
    font1 = self.renderer._get_font()

    # Second call should return cached font
    font2 = self.renderer._get_font()

    assert font1 is font2
    assert len(self.renderer._font_cache) == 1
