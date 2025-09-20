"""Input validation utilities."""

import os
import re
from pathlib import Path
from typing import Union, List, Tuple

from ..exceptions import InvalidConfigError
from ..core.watermark import WatermarkPosition


def validate_font_size(font_size: int) -> int:
  """
  Validate font size parameter.

  Args:
      font_size: Font size to validate

  Returns:
      Validated font size

  Raises:
      InvalidConfigError: If font size is invalid
  """
  if not isinstance(font_size, int):
    try:
      font_size = int(font_size)
    except (ValueError, TypeError):
      raise InvalidConfigError("Font size must be an integer")

  if font_size <= 0:
    raise InvalidConfigError("Font size must be positive")

  if font_size > 500:
    raise InvalidConfigError("Font size too large (max 500)")

  return font_size


def validate_color(color: str) -> str:
  """
  Validate color parameter.

  Args:
      color: Color string to validate

  Returns:
      Validated color string

  Raises:
      InvalidConfigError: If color is invalid
  """
  if not isinstance(color, str):
    raise InvalidConfigError("Color must be a string")

  color = color.strip().lower()

  # Check named colors
  named_colors = {
      "white", "black", "red", "green", "blue", "yellow",
      "cyan", "magenta", "gray", "grey"
  }

  if color in named_colors:
    return color

  # Check hex colors
  if color.startswith("#"):
    hex_pattern = re.compile(r'^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$')
    if hex_pattern.match(color):
      return color
    else:
      raise InvalidConfigError(f"Invalid hex color format: {color}")

  # Check RGB/RGBA format
  rgb_pattern = re.compile(
      r'^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(,\s*\d+\s*)?\)$')
  if rgb_pattern.match(color):
    return color

  raise InvalidConfigError(f"Invalid color format: {color}")


def validate_position(position: Union[str, WatermarkPosition]) -> WatermarkPosition:
  """
  Validate watermark position parameter.

  Args:
      position: Position to validate

  Returns:
      Validated WatermarkPosition enum

  Raises:
      InvalidConfigError: If position is invalid
  """
  if isinstance(position, WatermarkPosition):
    return position

  if isinstance(position, str):
    # Try to match string to enum value
    position = position.lower().replace('_', '-')

    for pos in WatermarkPosition:
      if pos.value == position:
        return pos

    # List valid positions for error message
    valid_positions = [pos.value for pos in WatermarkPosition]
    raise InvalidConfigError(
        f"Invalid position '{position}'. Valid positions: {valid_positions}"
    )

  raise InvalidConfigError("Position must be string or WatermarkPosition enum")


def validate_file_path(file_path: Union[str, Path]) -> Path:
  """
  Validate file path parameter.

  Args:
      file_path: File path to validate

  Returns:
      Validated Path object

  Raises:
      InvalidConfigError: If path is invalid
  """
  try:
    path = Path(file_path)
  except Exception:
    raise InvalidConfigError(f"Invalid file path: {file_path}")

  if not path.exists():
    raise InvalidConfigError(f"File does not exist: {file_path}")

  return path


def validate_output_directory(dir_path: Union[str, Path]) -> Path:
  """
  Validate output directory parameter.

  Args:
      dir_path: Directory path to validate

  Returns:
      Validated Path object

  Raises:
      InvalidConfigError: If directory is invalid
  """
  try:
    path = Path(dir_path)
  except Exception:
    raise InvalidConfigError(f"Invalid directory path: {dir_path}")

  # Check if parent directory exists and is writable
  parent = path.parent
  if not parent.exists():
    raise InvalidConfigError(f"Parent directory does not exist: {parent}")

  if not os.access(parent, os.W_OK):
    raise InvalidConfigError(f"No write permission for directory: {parent}")

  return path


def validate_opacity(opacity: Union[int, float]) -> int:
  """
  Validate opacity parameter.

  Args:
      opacity: Opacity value to validate (0-255 or 0.0-1.0)

  Returns:
      Validated opacity as integer (0-255)

  Raises:
      InvalidConfigError: If opacity is invalid
  """
  try:
    opacity = float(opacity)
  except (ValueError, TypeError):
    raise InvalidConfigError("Opacity must be a number")

  # Convert percentage (0.0-1.0) to 0-255 range
  if 0.0 <= opacity <= 1.0:
    opacity = int(opacity * 255)
  elif 0 <= opacity <= 255:
    opacity = int(opacity)
  else:
    raise InvalidConfigError("Opacity must be between 0-255 or 0.0-1.0")

  return opacity


def validate_margin(margin: int) -> int:
  """
  Validate margin parameter.

  Args:
      margin: Margin value to validate

  Returns:
      Validated margin

  Raises:
      InvalidConfigError: If margin is invalid
  """
  if not isinstance(margin, int):
    try:
      margin = int(margin)
    except (ValueError, TypeError):
      raise InvalidConfigError("Margin must be an integer")

  if margin < 0:
    raise InvalidConfigError("Margin must be non-negative")

  if margin > 1000:
    raise InvalidConfigError("Margin too large (max 1000)")

  return margin


def validate_quality(quality: int) -> int:
  """
  Validate JPEG quality parameter.

  Args:
      quality: Quality value to validate (1-100)

  Returns:
      Validated quality

  Raises:
      InvalidConfigError: If quality is invalid
  """
  if not isinstance(quality, int):
    try:
      quality = int(quality)
    except (ValueError, TypeError):
      raise InvalidConfigError("Quality must be an integer")

  if not (1 <= quality <= 100):
    raise InvalidConfigError("Quality must be between 1 and 100")

  return quality
