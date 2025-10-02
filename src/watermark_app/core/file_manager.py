#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理核心模块
负责图片文件的导入、管理和验证
"""

import os
import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class FileManager:
  """文件管理器类"""

  # 支持的图片MIME类型
  SUPPORTED_MIME_TYPES = {
      'image/jpeg', 'image/jpg', 'image/png',
      'image/bmp', 'image/tiff', 'image/x-ms-bmp'
  }

  # 支持的文件扩展名
  SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

  def __init__(self):
    """初始化文件管理器"""
    self.logger = logging.getLogger(__name__)
    self.image_files: List[Dict[str, Any]] = []

  def is_supported_format(self, file_path: str) -> bool:
    """
    检查文件是否为支持的图片格式

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为支持的图片文件
    """
    return self.is_image_file(file_path)

  def is_supported_format(self, file_path: str) -> bool:
    """
    检查文件是否为支持的图片格式（别名方法）

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为支持的图片文件
    """
    return self.is_image_file(file_path)

  def is_image_file(self, file_path: str) -> bool:
    """
    检查文件是否为支持的图片格式

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否为支持的图片文件
    """
    try:
      # 检查文件扩展名
      ext = Path(file_path).suffix.lower()
      if ext not in self.SUPPORTED_EXTENSIONS:
        return False

      # 检查MIME类型
      mime_type, _ = mimetypes.guess_type(file_path)
      if mime_type and mime_type.lower() in self.SUPPORTED_MIME_TYPES:
        return True

      return ext in self.SUPPORTED_EXTENSIONS

    except Exception as e:
      self.logger.error(f"检查文件类型失败 {file_path}: {str(e)}")
      return False

  def add_file(self, file_path: str) -> bool:
    """
    添加单个图片文件

    Args:
        file_path: 图片文件路径

    Returns:
        bool: 是否成功添加
    """
    return self.add_single_file(file_path)

  def add_file(self, file_path: str) -> bool:
    """
    添加单个图片文件（别名方法）

    Args:
        file_path: 图片文件路径

    Returns:
        bool: 是否成功添加
    """
    return self.add_single_file(file_path)

  def add_single_file(self, file_path: str) -> bool:
    """
    添加单个图片文件

    Args:
        file_path: 图片文件路径

    Returns:
        bool: 是否成功添加
    """
    try:
      if not os.path.exists(file_path):
        self.logger.error(f"文件不存在: {file_path}")
        return False

      if not self.is_image_file(file_path):
        self.logger.error(f"不支持的文件格式: {file_path}")
        return False

      # 检查是否已存在
      abs_path = os.path.abspath(file_path)
      if any(img['path'] == abs_path for img in self.image_files):
        self.logger.warning(f"文件已存在于列表中: {file_path}")
        return False

      # 获取文件信息
      file_info = self._get_file_info(abs_path)
      self.image_files.append(file_info)

      self.logger.info(f"成功添加文件: {file_path}")
      return True

    except Exception as e:
      self.logger.error(f"添加文件失败 {file_path}: {str(e)}")
      return False

  def add_multiple_files(self, file_paths: List[str]) -> int:
    """
    添加多个图片文件

    Args:
        file_paths: 图片文件路径列表

    Returns:
        int: 成功添加的文件数量
    """
    success_count = 0
    for file_path in file_paths:
      if self.add_single_file(file_path):
        success_count += 1

    self.logger.info(f"批量添加文件完成，成功: {success_count}/{len(file_paths)}")
    return success_count

  def add_folder(self, folder_path: str, recursive: bool = True) -> int:
    """
    添加文件夹中的所有图片文件

    Args:
        folder_path: 文件夹路径
        recursive: 是否递归搜索子文件夹

    Returns:
        int: 成功添加的文件数量
    """
    try:
      if not os.path.exists(folder_path):
        self.logger.error(f"文件夹不存在: {folder_path}")
        return 0

      if not os.path.isdir(folder_path):
        self.logger.error(f"路径不是文件夹: {folder_path}")
        return 0

      image_paths = []

      if recursive:
        # 递归搜索
        for root, dirs, files in os.walk(folder_path):
          for file in files:
            file_path = os.path.join(root, file)
            if self.is_image_file(file_path):
              image_paths.append(file_path)
      else:
        # 只搜索当前文件夹
        for file in os.listdir(folder_path):
          file_path = os.path.join(folder_path, file)
          if os.path.isfile(file_path) and self.is_image_file(file_path):
            image_paths.append(file_path)

      success_count = self.add_multiple_files(image_paths)
      self.logger.info(f"文件夹导入完成: {folder_path}, 成功添加 {success_count} 个文件")
      return success_count

    except Exception as e:
      self.logger.error(f"导入文件夹失败 {folder_path}: {str(e)}")
      return 0

  def remove_file(self, file_path: str) -> bool:
    """
    从列表中移除文件

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否成功移除
    """
    try:
      abs_path = os.path.abspath(file_path)
      original_count = len(self.image_files)
      self.image_files = [
          img for img in self.image_files if img['path'] != abs_path]

      if len(self.image_files) < original_count:
        self.logger.info(f"成功移除文件: {file_path}")
        return True
      else:
        self.logger.warning(f"文件不在列表中: {file_path}")
        return False

    except Exception as e:
      self.logger.error(f"移除文件失败 {file_path}: {str(e)}")
      return False

  def remove_file_by_index(self, index: int) -> bool:
    """
    根据索引移除文件

    Args:
        index: 文件索引

    Returns:
        bool: 是否成功移除
    """
    try:
      if 0 <= index < len(self.image_files):
        removed_file = self.image_files.pop(index)
        self.logger.info(f"成功移除文件: {removed_file['name']}")
        return True
      else:
        self.logger.error(f"无效的索引: {index}")
        return False

    except Exception as e:
      self.logger.error(f"根据索引移除文件失败: {str(e)}")
      return False

  def clear_all(self):
    """清空所有文件"""
    count = len(self.image_files)
    self.image_files.clear()
    self.logger.info(f"已清空所有文件，共移除 {count} 个文件")

  def get_file_list(self) -> List[Dict[str, Any]]:
    """
    获取文件列表

    Returns:
        文件信息列表
    """
    return self.image_files.copy()

  def get_file_count(self) -> int:
    """
    获取文件数量

    Returns:
        文件数量
    """
    return len(self.image_files)

  def get_file_by_index(self, index: int) -> Optional[Dict[str, Any]]:
    """
    根据索引获取文件信息

    Args:
        index: 文件索引

    Returns:
        文件信息字典
    """
    try:
      if 0 <= index < len(self.image_files):
        return self.image_files[index]
      return None
    except Exception:
      return None

  def _get_file_info(self, file_path: str) -> Dict[str, Any]:
    """
    获取文件详细信息

    Args:
        file_path: 文件路径

    Returns:
        文件信息字典
    """
    try:
      file_stat = os.stat(file_path)
      path_obj = Path(file_path)

      return {
          'path': file_path,
          'name': path_obj.name,
          'size': file_stat.st_size,
          'extension': path_obj.suffix.lower(),
          'modified_time': file_stat.st_mtime,
          'created_time': file_stat.st_ctime
      }

    except Exception as e:
      self.logger.error(f"获取文件信息失败 {file_path}: {str(e)}")
      return {
          'path': file_path,
          'name': Path(file_path).name,
          'size': 0,
          'extension': Path(file_path).suffix.lower(),
          'modified_time': 0,
          'created_time': 0
      }

  def validate_output_directory(self, output_dir: str, source_files: List[str] = None) -> Tuple[bool, str]:
    """
    验证输出目录是否有效

    Args:
        output_dir: 输出目录路径
        source_files: 源文件列表，用于检查是否与原文件目录相同

    Returns:
        (是否有效, 错误信息)
    """
    try:
      # 检查目录是否存在
      if not os.path.exists(output_dir):
        try:
          os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
          return False, f"无法创建输出目录: {str(e)}"

      # 检查是否为目录
      if not os.path.isdir(output_dir):
        return False, "输出路径不是有效的目录"

      # 检查是否有写入权限
      if not os.access(output_dir, os.W_OK):
        return False, "输出目录没有写入权限"

      # 检查是否与源文件目录相同（防止覆盖）
      if source_files:
        output_dir_abs = os.path.abspath(output_dir)
        for source_file in source_files:
          source_dir = os.path.dirname(os.path.abspath(source_file))
          if source_dir == output_dir_abs:
            return False, "输出目录不能与源文件目录相同，以防止覆盖原文件"

      return True, ""

    except Exception as e:
      return False, f"验证输出目录失败: {str(e)}"

  def scan_folder_for_images(self, folder_path: str, recursive: bool = True) -> List[str]:
    """
    扫描文件夹中的图片文件

    Args:
        folder_path: 文件夹路径
        recursive: 是否递归搜索子文件夹

    Returns:
        List[str]: 图片文件路径列表
    """
    try:
      if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return []

      image_paths = []

      if recursive:
        # 递归搜索
        for root, dirs, files in os.walk(folder_path):
          for file in files:
            file_path = os.path.join(root, file)
            if self.is_image_file(file_path):
              image_paths.append(file_path)
      else:
        # 只搜索当前文件夹
        for file in os.listdir(folder_path):
          file_path = os.path.join(folder_path, file)
          if os.path.isfile(file_path) and self.is_image_file(file_path):
            image_paths.append(file_path)

      return image_paths

    except Exception as e:
      self.logger.error(f"扫描文件夹失败 {folder_path}: {str(e)}")
      return []
