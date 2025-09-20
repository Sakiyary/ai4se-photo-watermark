"""Watermark configuration and rendering engine."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple, Union, Optional
import platform
import os

from PIL import Image, ImageDraw, ImageFont


class WatermarkPosition(Enum):
  """Enumeration of watermark positions."""
  TOP_LEFT = "top-left"
  TOP_CENTER = "top-center"
  TOP_RIGHT = "top-right"
  LEFT_CENTER = "left-center"
  CENTER = "center"
  RIGHT_CENTER = "right-center"
  BOTTOM_LEFT = "bottom-left"
  BOTTOM_CENTER = "bottom-center"
  BOTTOM_RIGHT = "bottom-right"


@dataclass
class WatermarkConfig:
  """Configuration for watermark rendering."""

  # Text properties
  font_size: int = 32
  color: str = "white"

  # Position
  position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT

  # Spacing and margins
  margin: int = 10

  # Font settings
  font_path: Optional[str] = None

  # Text effects
  outline_width: int = 1
  outline_color: str = "black"
  opacity: int = 255  # 0-255, 255 = fully opaque

  def __post_init__(self):
    """Validate configuration after initialization."""
    if self.font_size <= 0:
      raise ValueError("Font size must be positive")

    if not (0 <= self.opacity <= 255):
      raise ValueError("Opacity must be between 0 and 255")

    if self.margin < 0:
      raise ValueError("Margin must be non-negative")


class WatermarkRenderer:
  """Renders text watermarks on images."""

  def __init__(self, config: WatermarkConfig):
    """
    Initialize the watermark renderer.

    Args:
        config: Watermark configuration
    """
    self.config = config
    self._font_cache = {}

  def render_watermark(
      self,
      image: Image.Image,
      text: str
  ) -> Image.Image:
    """
    Render watermark text on the image.

    Args:
        image: PIL Image object to add watermark to
        text: Text to render as watermark

    Returns:
        New PIL Image object with watermark applied
    """
    # Create a copy to avoid modifying original
    watermarked_image = image.copy()

    # Create drawing context
    draw = ImageDraw.Draw(watermarked_image)

    # Get font
    font = self._get_font()

    # Calculate text size and position
    text_bbox = self._get_text_bbox(draw, text, font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    position = self._calculate_position(
        image.size,
        (text_width, text_height)
    )

    # Parse colors
    text_color = self._parse_color(self.config.color)
    outline_color = self._parse_color(self.config.outline_color)

    # Apply opacity to colors
    if len(text_color) == 3:  # RGB
      text_color = (*text_color, self.config.opacity)
    elif len(text_color) == 4:  # RGBA
      text_color = (*text_color[:3], self.config.opacity)

    # Draw text with outline if specified
    if self.config.outline_width > 0:
      # Draw outline
      for adj_x in range(-self.config.outline_width, self.config.outline_width + 1):
        for adj_y in range(-self.config.outline_width, self.config.outline_width + 1):
          if adj_x != 0 or adj_y != 0:
            outline_pos = (position[0] + adj_x, position[1] + adj_y)
            draw.text(
                outline_pos,
                text,
                font=font,
                fill=outline_color
            )

    # Draw main text
    draw.text(
        position,
        text,
        font=font,
        fill=text_color
    )

    return watermarked_image

  def _get_font(self) -> ImageFont.ImageFont:
    """Get font object, using cache for performance."""
    cache_key = (self.config.font_path, self.config.font_size)

    if cache_key not in self._font_cache:
      try:
        if self.config.font_path and Path(self.config.font_path).exists():
          # Use custom font path
          font = ImageFont.truetype(
              self.config.font_path, self.config.font_size)
        else:
          # Use system default font
          font = self._get_default_font()
      except (OSError, IOError):
        # Fallback to default font
        font = self._get_default_font()

      self._font_cache[cache_key] = font

    return self._font_cache[cache_key]

  def _get_default_font(self) -> ImageFont.ImageFont:
    """Get system default font based on platform."""
    system = platform.system().lower()

    # Try common system fonts
    font_paths = []

    if system == "windows":
      font_paths = [
          "C:/Windows/Fonts/arial.ttf",
          "C:/Windows/Fonts/calibri.ttf",
          "C:/Windows/Fonts/tahoma.ttf"
      ]
    elif system == "darwin":  # macOS
      font_paths = [
          "/System/Library/Fonts/Helvetica.ttc",
          "/System/Library/Fonts/Arial.ttf",
          "/Library/Fonts/Arial.ttf"
      ]
    else:  # Linux and others
      font_paths = [
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "/usr/share/fonts/TTF/arial.ttf"
      ]

    # Try each font path
    for font_path in font_paths:
      try:
        if os.path.exists(font_path):
          return ImageFont.truetype(font_path, self.config.font_size)
      except (OSError, IOError):
        continue

    # Ultimate fallback to PIL default font
    try:
      return ImageFont.load_default()
    except Exception:
      # If even default font fails, create a basic font
      return ImageFont.load_default()

  def _get_text_bbox(
      self,
      draw: ImageDraw.ImageDraw,
      text: str,
      font: ImageFont.ImageFont
  ) -> Tuple[int, int, int, int]:
    """Get text bounding box."""
    try:
      # Use textbbox if available (Pillow 8.0+)
      return draw.textbbox((0, 0), text, font=font)
    except AttributeError:
      # Fallback for older Pillow versions
      text_width, text_height = draw.textsize(text, font=font)
      return (0, 0, text_width, text_height)

  def _calculate_position(
      self,
      image_size: Tuple[int, int],
      text_size: Tuple[int, int]
  ) -> Tuple[int, int]:
    """
    Calculate watermark position based on configuration.

    Args:
        image_size: (width, height) of the image
        text_size: (width, height) of the text

    Returns:
        (x, y) position for the text
    """
    img_width, img_height = image_size
    text_width, text_height = text_size
    margin = self.config.margin

    position_map = {
        WatermarkPosition.TOP_LEFT: (
            margin,
            margin
        ),
        WatermarkPosition.TOP_CENTER: (
            (img_width - text_width) // 2,
            margin
        ),
        WatermarkPosition.TOP_RIGHT: (
            img_width - text_width - margin,
            margin
        ),
        WatermarkPosition.LEFT_CENTER: (
            margin,
            (img_height - text_height) // 2
        ),
        WatermarkPosition.CENTER: (
            (img_width - text_width) // 2,
            (img_height - text_height) // 2
        ),
        WatermarkPosition.RIGHT_CENTER: (
            img_width - text_width - margin,
            (img_height - text_height) // 2
        ),
        WatermarkPosition.BOTTOM_LEFT: (
            margin,
            img_height - text_height - margin
        ),
        WatermarkPosition.BOTTOM_CENTER: (
            (img_width - text_width) // 2,
            img_height - text_height - margin
        ),
        WatermarkPosition.BOTTOM_RIGHT: (
            img_width - text_width - margin,
            img_height - text_height - margin
        ),
    }

    return position_map.get(self.config.position, position_map[WatermarkPosition.BOTTOM_RIGHT])

  def _parse_color(self, color_str: str) -> Tuple[int, ...]:
    """
    Parse color string to RGB(A) tuple.

    Args:
        color_str: Color as string (name, hex, or rgb)

    Returns:
        RGB or RGBA tuple
    """
    color_str = color_str.strip().lower()

    # Handle named colors
    named_colors = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
    }

    if color_str in named_colors:
      return named_colors[color_str]

    # Handle hex colors
    if color_str.startswith("#"):
      hex_color = color_str[1:]
      try:
        if len(hex_color) == 3:
          # Short hex format (#RGB)
          return tuple(int(hex_color[i] * 2, 16) for i in range(3))
        elif len(hex_color) == 6:
          # Full hex format (#RRGGBB)
          return tuple(int(hex_color[i:i+2], 16) for i in range(0, 6, 2))
        elif len(hex_color) == 8:
          # Full hex with alpha (#RRGGBBAA)
          return tuple(int(hex_color[i:i+2], 16) for i in range(0, 8, 2))
      except ValueError:
        # Invalid hex format, fall through to default
        pass

    # Handle RGB/RGBA format "rgb(r,g,b)" or "rgba(r,g,b,a)"
    if color_str.startswith(("rgb(", "rgba(")):
      # Extract numbers from parentheses
      values_str = color_str[color_str.find("(") + 1:color_str.find(")")]
      try:
        values = [int(v.strip()) for v in values_str.split(",")]
        if len(values) in (3, 4):
          # Validate RGB values are in valid range (0-255)
          if all(0 <= v <= 255 for v in values):
            return tuple(values)
      except ValueError:
        pass

    # Fallback to white if parsing fails
    return (255, 255, 255)

  def preview_watermark(
      self,
      image_size: Tuple[int, int],
      text: str
  ) -> dict:
    """
    Get watermark position and size info without rendering.

    Args:
        image_size: (width, height) of the image
        text: Text to render as watermark

    Returns:
        Dictionary with position and size information
    """
    # Create a temporary image for text measurement
    temp_image = Image.new('RGB', (100, 100))
    draw = ImageDraw.Draw(temp_image)
    font = self._get_font()

    # Get text size
    text_bbox = self._get_text_bbox(draw, text, font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate position
    position = self._calculate_position(image_size, (text_width, text_height))

    return {
        "position": position,
        "text_size": (text_width, text_height),
        "text": text,
        "font_size": self.config.font_size,
        "color": self.config.color,
        "watermark_position": self.config.position.value
    }
