"""
水印工具 - 输入验证工具

提供各种输入验证和数据校验功能
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from .constants import SUPPORTED_IMAGE_FORMATS, MAX_IMAGE_SIZE_MB


def is_valid_image_file(file_path: str) -> bool:
  """验证是否为有效的图片文件

  Args:
      file_path: 文件路径

  Returns:
      bool: 是否为有效图片文件
  """
  try:
    path = Path(file_path)

    # 检查文件是否存在
    if not path.exists() or not path.is_file():
      return False

    # 检查文件扩展名
    extension = path.suffix.lower()
    if extension not in SUPPORTED_IMAGE_FORMATS:
      return False

    # 检查文件大小
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_IMAGE_SIZE_MB:
      return False

    return True

  except Exception:
    return False


def validate_image_files(file_paths: List[str]) -> Tuple[List[str], List[str]]:
  """批量验证图片文件

  Args:
      file_paths: 文件路径列表

  Returns:
      Tuple[List[str], List[str]]: (有效文件列表, 无效文件列表)
  """
  valid_files = []
  invalid_files = []

  for file_path in file_paths:
    if is_valid_image_file(file_path):
      valid_files.append(file_path)
    else:
      invalid_files.append(file_path)

  return valid_files, invalid_files


def is_valid_hex_color(color: str) -> bool:
  """验证十六进制颜色值

  Args:
      color: 颜色字符串

  Returns:
      bool: 是否为有效的十六进制颜色
  """
  if not color or not isinstance(color, str):
    return False

  # 匹配 #RRGGBB 格式
  pattern = r'^#[0-9A-Fa-f]{6}$'
  return bool(re.match(pattern, color))


def validate_font_size(font_size: int) -> bool:
  """验证字体大小

  Args:
      font_size: 字体大小

  Returns:
      bool: 是否为有效的字体大小
  """
  return isinstance(font_size, int) and 8 <= font_size <= 500


def validate_opacity(opacity: int) -> bool:
  """验证透明度值

  Args:
      opacity: 透明度值

  Returns:
      bool: 是否为有效的透明度值
  """
  return isinstance(opacity, int) and 0 <= opacity <= 255


def validate_offset(offset: int) -> bool:
  """验证偏移量

  Args:
      offset: 偏移量

  Returns:
      bool: 是否为有效的偏移量
  """
  return isinstance(offset, int) and 0 <= offset <= 1000


def validate_watermark_text(text: str) -> Tuple[bool, str]:
  """验证水印文本

  Args:
      text: 水印文本

  Returns:
      Tuple[bool, str]: (是否有效, 错误消息)
  """
  if not isinstance(text, str):
    return False, "文本必须是字符串类型"

  # 允许空文本（表示不添加水印）
  if len(text) == 0:
    return True, ""

  # 检查文本长度
  if len(text) > 500:
    return False, "文本长度不能超过500个字符"

  # 检查是否包含不可打印字符（除了换行符）
  if any(ord(c) < 32 and c != '\n' for c in text):
    return False, "文本包含不可打印字符"

  return True, ""


def validate_directory_path(path: str) -> Tuple[bool, str]:
  """验证目录路径

  Args:
      path: 目录路径

  Returns:
      Tuple[bool, str]: (是否有效, 错误消息)
  """
  if not path or not isinstance(path, str):
    return False, "路径不能为空"

  try:
    path_obj = Path(path)

    # 检查路径格式是否有效
    if not str(path_obj).strip():
      return False, "路径格式无效"

    # 检查父目录是否存在（用于创建新目录）
    if path_obj.exists():
      if not path_obj.is_dir():
        return False, "路径存在但不是目录"
    else:
      # 检查是否可以创建目录
      parent = path_obj.parent
      if not parent.exists():
        return False, "父目录不存在"

    return True, ""

  except Exception as e:
    return False, f"路径验证失败: {str(e)}"


def validate_filename(filename: str) -> Tuple[bool, str]:
  """验证文件名

  Args:
      filename: 文件名

  Returns:
      Tuple[bool, str]: (是否有效, 错误消息)
  """
  if not filename or not isinstance(filename, str):
    return False, "文件名不能为空"

  # 检查长度
  if len(filename) > 255:
    return False, "文件名过长"

  # 检查非法字符
  invalid_chars = r'<>:"/\\|?*'
  for char in invalid_chars:
    if char in filename:
      return False, f"文件名包含非法字符: {char}"

  # 检查保留名称（Windows）
  reserved_names = {
      'CON', 'PRN', 'AUX', 'NUL',
      'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
      'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
  }

  base_name = filename.upper().split('.')[0]
  if base_name in reserved_names:
    return False, f"文件名 '{filename}' 是系统保留名称"

  return True, ""


def sanitize_filename(filename: str) -> str:
  """清理文件名，移除或替换非法字符

  Args:
      filename: 原始文件名

  Returns:
      str: 清理后的文件名
  """
  if not filename:
    return "untitled"

  # 替换非法字符
  invalid_chars = r'<>:"/\\|?*'
  sanitized = filename
  for char in invalid_chars:
    sanitized = sanitized.replace(char, '_')

  # 移除前导和尾随空格/点号
  sanitized = sanitized.strip('. ')

  # 确保不为空
  if not sanitized:
    sanitized = "untitled"

  # 截断长度
  if len(sanitized) > 200:
    name_part, ext_part = splitext_safe(sanitized)
    max_name_len = 200 - len(ext_part)
    sanitized = name_part[:max_name_len] + ext_part

  return sanitized


def splitext_safe(filename: str) -> Tuple[str, str]:
  """安全地分割文件名和扩展名

  Args:
      filename: 文件名

  Returns:
      Tuple[str, str]: (文件名主体, 扩展名)
  """
  if '.' in filename:
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
      return parts[0], '.' + parts[1]

  return filename, ''


def validate_jpeg_quality(quality: int) -> bool:
  """验证JPEG质量值

  Args:
      quality: 质量值

  Returns:
      bool: 是否为有效的质量值
  """
  return isinstance(quality, int) and 1 <= quality <= 100
