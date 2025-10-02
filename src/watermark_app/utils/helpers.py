"""
水印工具 - 辅助函数

提供各种实用的辅助功能
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Any
from PIL import Image
import hashlib


def get_app_data_dir() -> Path:
  """获取应用数据目录

  Returns:
      Path: 应用数据目录路径
  """
  if sys.platform == "win32":
    base_dir = Path(os.environ.get('APPDATA', Path.home()))
  elif sys.platform == "darwin":  # macOS
    base_dir = Path.home() / "Library" / "Application Support"
  else:  # Linux and others
    base_dir = Path.home() / ".config"

  return base_dir / "WatermarkTool"


def ensure_directory_exists(directory: Path) -> bool:
  """确保目录存在，如果不存在则创建

  Args:
      directory: 目录路径

  Returns:
      bool: 是否成功创建或已存在
  """
  try:
    directory.mkdir(parents=True, exist_ok=True)
    return True
  except Exception as e:
    print(f"创建目录失败: {e}")
    return False


def format_file_size(size_bytes: int) -> str:
  """格式化文件大小为人类可读格式

  Args:
      size_bytes: 字节数

  Returns:
      str: 格式化的文件大小
  """
  if size_bytes == 0:
    return "0 B"

  size_names = ["B", "KB", "MB", "GB", "TB"]
  i = 0

  while size_bytes >= 1024 and i < len(size_names) - 1:
    size_bytes /= 1024.0
    i += 1

  if i == 0:
    return f"{int(size_bytes)} {size_names[i]}"
  else:
    return f"{size_bytes:.1f} {size_names[i]}"


def get_image_info(image_path: str) -> Optional[dict]:
  """获取图片信息

  Args:
      image_path: 图片路径

  Returns:
      dict: 图片信息字典，失败时返回None
  """
  try:
    with Image.open(image_path) as img:
      file_path = Path(image_path)
      file_size = file_path.stat().st_size

      return {
          'filename': file_path.name,
          'filepath': str(file_path),
          'format': img.format,
          'mode': img.mode,
          'width': img.width,
          'height': img.height,
          'size': f"{img.width}x{img.height}",
          'file_size': file_size,
          'file_size_formatted': format_file_size(file_size),
          'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
      }
  except Exception as e:
    print(f"获取图片信息失败: {e}")
    return None


def generate_unique_filename(directory: Path, base_name: str, extension: str) -> str:
  """生成唯一的文件名，避免重名冲突

  Args:
      directory: 目标目录
      base_name: 基础文件名
      extension: 文件扩展名

  Returns:
      str: 唯一的文件名
  """
  counter = 1
  filename = f"{base_name}{extension}"

  while (directory / filename).exists():
    filename = f"{base_name}_{counter}{extension}"
    counter += 1

  return filename


def calculate_file_hash(file_path: str) -> Optional[str]:
  """计算文件的MD5哈希值

  Args:
      file_path: 文件路径

  Returns:
      str: MD5哈希值，失败时返回None
  """
  try:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()
  except Exception as e:
    print(f"计算文件哈希失败: {e}")
    return None


def find_duplicates(file_paths: List[str]) -> List[List[str]]:
  """查找重复文件

  Args:
      file_paths: 文件路径列表

  Returns:
      List[List[str]]: 重复文件组列表
  """
  hash_to_files = {}

  for file_path in file_paths:
    file_hash = calculate_file_hash(file_path)
    if file_hash:
      if file_hash not in hash_to_files:
        hash_to_files[file_hash] = []
      hash_to_files[file_hash].append(file_path)

  # 返回包含重复文件的组
  duplicates = []
  for files in hash_to_files.values():
    if len(files) > 1:
      duplicates.append(files)

  return duplicates


def rgb_to_hex(r: int, g: int, b: int) -> str:
  """将RGB颜色转换为十六进制格式

  Args:
      r: 红色分量 (0-255)
      g: 绿色分量 (0-255)
      b: 蓝色分量 (0-255)

  Returns:
      str: 十六进制颜色字符串
  """
  return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
  """将十六进制颜色转换为RGB

  Args:
      hex_color: 十六进制颜色字符串

  Returns:
      Tuple[int, int, int]: RGB颜色元组
  """
  hex_color = hex_color.lstrip('#')

  if len(hex_color) != 6:
    raise ValueError("无效的十六进制颜色格式")

  try:
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b
  except ValueError:
    raise ValueError("无效的十六进制颜色格式")


def clamp(value: float, min_val: float, max_val: float) -> float:
  """将值限制在指定范围内

  Args:
      value: 输入值
      min_val: 最小值
      max_val: 最大值

  Returns:
      float: 限制后的值
  """
  return max(min_val, min(value, max_val))


def scale_to_fit(original_size: Tuple[int, int], target_size: Tuple[int, int],
                 keep_aspect: bool = True) -> Tuple[int, int]:
  """计算缩放后的尺寸以适应目标区域

  Args:
      original_size: 原始尺寸 (width, height)
      target_size: 目标尺寸 (width, height) 
      keep_aspect: 是否保持宽高比

  Returns:
      Tuple[int, int]: 缩放后的尺寸
  """
  orig_w, orig_h = original_size
  target_w, target_h = target_size

  if not keep_aspect:
    return target_w, target_h

  # 计算缩放比例
  scale_w = target_w / orig_w
  scale_h = target_h / orig_h
  scale = min(scale_w, scale_h)

  # 应用缩放比例
  new_w = int(orig_w * scale)
  new_h = int(orig_h * scale)

  return new_w, new_h


def get_system_fonts() -> List[str]:
  """获取系统可用字体列表

  Returns:
      List[str]: 字体名称列表
  """
  # 这是一个简化版本，实际实现可能需要更复杂的字体检测
  common_fonts = [
      "Arial",
      "Times New Roman",
      "Calibri",
      "Verdana",
      "Georgia",
      "Tahoma",
      "Trebuchet MS",
      "Comic Sans MS",
      "Impact",
      "Lucida Console"
  ]

  # 在实际应用中，可能需要检测系统实际可用的字体
  return common_fonts


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
  """截断文本并添加后缀

  Args:
      text: 原始文本
      max_length: 最大长度
      suffix: 截断后缀

  Returns:
      str: 截断后的文本
  """
  if len(text) <= max_length:
    return text

  if len(suffix) >= max_length:
    return text[:max_length]

  return text[:max_length - len(suffix)] + suffix


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
  """安全除法，避免除零错误

  Args:
      numerator: 分子
      denominator: 分母
      default: 除零时的默认值

  Returns:
      float: 除法结果
  """
  try:
    if denominator == 0:
      return default
    return numerator / denominator
  except (TypeError, ValueError):
    return default


def deep_merge_dict(dict1: dict, dict2: dict) -> dict:
  """深度合并两个字典

  Args:
      dict1: 第一个字典
      dict2: 第二个字典

  Returns:
      dict: 合并后的字典
  """
  result = dict1.copy()

  for key, value in dict2.items():
    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
      result[key] = deep_merge_dict(result[key], value)
    else:
      result[key] = value

  return result
