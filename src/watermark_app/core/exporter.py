#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像导出核心模块
负责处理水印后图像的导出和保存
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from PIL import Image
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ImageExporter:
  """图像导出器类"""

  # 支持的输出格式
  SUPPORTED_FORMATS = {
      'jpeg': {
          'extension': '.jpg',
          'mode': 'RGB',
          'has_quality': True
      },
      'jpg': {
          'extension': '.jpg',
          'mode': 'RGB',
          'has_quality': True
      },
      'png': {
          'extension': '.png',
          'mode': 'RGBA',
          'has_quality': False
      },
      'bmp': {
          'extension': '.bmp',
          'mode': 'RGB',
          'has_quality': False
      },
      'tiff': {
          'extension': '.tiff',
          'mode': 'RGB',
          'has_quality': False
      },
      'tif': {
          'extension': '.tif',
          'mode': 'RGB',
          'has_quality': False
      }
  }

  def __init__(self):
    """初始化图像导出器"""
    self.logger = logging.getLogger(__name__)

  def _get_unique_filename(self, output_path: str) -> str:
    """
    获取唯一的文件名,如果文件已存在则添加 (1), (2) 等后缀

    Args:
        output_path: 原始输出路径

    Returns:
        唯一的文件路径
    """
    if not os.path.exists(output_path):
      return output_path

    # 分离路径、文件名和扩展名
    path_obj = Path(output_path)
    directory = path_obj.parent
    stem = path_obj.stem
    extension = path_obj.suffix

    # 从 1 开始尝试添加后缀
    counter = 1
    while True:
      new_filename = f"{stem} ({counter}){extension}"
      new_path = directory / new_filename
      if not os.path.exists(new_path):
        return str(new_path)
      counter += 1

  def export_image(self, image: Image.Image, output_path: str,
                   format_type: str = 'png', quality: int = 85,
                   resize_config: Optional[Dict[str, Any]] = None) -> bool:
    """
    导出图像

    Args:
        image: 要导出的PIL图像
        output_path: 输出文件路径
        format_type: 输出格式 ('png', 'jpeg', 'jpg')
        quality: JPEG质量 (1-100)
        resize_config: 尺寸调整配置

    Returns:
        bool: 是否成功导出
    """
    try:
      # 验证格式
      format_type = format_type.lower()
      if format_type not in self.SUPPORTED_FORMATS:
        self.logger.error(f"不支持的输出格式: {format_type}")
        return False

      format_info = self.SUPPORTED_FORMATS[format_type]

      # 确保输出路径使用正确的扩展名
      path_obj = Path(output_path)
      correct_extension = format_info['extension']
      # 如果扩展名不正确，替换为正确的扩展名
      if path_obj.suffix.lower() != correct_extension:
        output_path = str(path_obj.with_suffix(correct_extension))

      # 复制图像以避免修改原图
      export_image = image.copy()

      # 调整尺寸
      if resize_config and resize_config.get('enabled', False):
        export_image = self._resize_image(export_image, resize_config)

      # 转换图像模式
      target_mode = format_info['mode']
      if export_image.mode != target_mode:
        if target_mode == 'RGB' and export_image.mode == 'RGBA':
          # RGBA转RGB，使用白色背景
          background = Image.new('RGB', export_image.size, (255, 255, 255))
          background.paste(export_image, mask=export_image.split()[-1])
          export_image = background
        else:
          export_image = export_image.convert(target_mode)

      # 确保输出目录存在
      output_dir = os.path.dirname(output_path)
      if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

      # 检查文件名冲突并获取唯一文件名
      output_path = self._get_unique_filename(output_path)

      # 保存图像
      save_kwargs = {}
      if format_info['has_quality']:
        actual_quality = max(1, min(100, quality))
        save_kwargs['quality'] = actual_quality

        # 根据质量设置压缩策略
        if actual_quality >= 95:
          # 超高质量: 无子采样
          save_kwargs['subsampling'] = 0  # 4:4:4 无子采样,最高质量
        elif actual_quality >= 85:
          # 高质量: 轻度子采样
          save_kwargs['subsampling'] = 1  # 4:2:2 轻度子采样
        else:
          # 中低质量: 标准子采样
          save_kwargs['subsampling'] = 2  # 4:2:0 标准子采样,更好的压缩

        self.logger.info(
            f"JPEG保存参数 - quality: {actual_quality}, subsampling: {save_kwargs['subsampling']}")

      if format_type == 'png':
        save_kwargs['optimize'] = True

      # 将格式代码转换为PIL识别的格式名称
      format_map = {
          'jpg': 'JPEG',
          'jpeg': 'JPEG',
          'png': 'PNG',
          'bmp': 'BMP',
          'tiff': 'TIFF',
          'tif': 'TIFF'
      }
      pil_format = format_map.get(format_type, format_type.upper())

      export_image.save(output_path, format=pil_format, **save_kwargs)

      self.logger.info(f"成功导出图像: {output_path}")
      return True

    except Exception as e:
      self.logger.error(f"导出图像失败 {output_path}: {str(e)}")
      return False

  def batch_export(self, images_with_paths: list, export_config: Dict[str, Any],
                   progress_callback=None) -> Dict[str, Any]:
    """
    批量导出图像

    Args:
        images_with_paths: 图像和路径的列表 [(image, output_path), ...]
        export_config: 导出配置
        progress_callback: 进度回调函数

    Returns:
        导出结果统计
    """
    results = {
        'total': len(images_with_paths),
        'success': 0,
        'failed': 0,
        'errors': []
    }

    try:
      for i, (image, output_path) in enumerate(images_with_paths):
        try:
          success = self.export_image(
              image=image,
              output_path=output_path,
              format_type=export_config.get('format', 'png'),
              quality=export_config.get('quality', 85),
              resize_config=export_config.get('resize', None)
          )

          if success:
            results['success'] += 1
          else:
            results['failed'] += 1
            results['errors'].append(f"导出失败: {output_path}")

        except Exception as e:
          results['failed'] += 1
          error_msg = f"导出异常 {output_path}: {str(e)}"
          results['errors'].append(error_msg)
          self.logger.error(error_msg)

        # 进度回调
        if progress_callback:
          progress = (i + 1) / len(images_with_paths) * 100
          progress_callback(progress, i + 1, len(images_with_paths))

      self.logger.info(
          f"批量导出完成: 成功 {results['success']}, 失败 {results['failed']}")
      return results

    except Exception as e:
      self.logger.error(f"批量导出异常: {str(e)}")
      results['errors'].append(f"批量导出异常: {str(e)}")
      return results

  def generate_output_filename(self, original_path: str, naming_config: Dict[str, Any],
                               output_format: str = 'png') -> str:
    """
    生成输出文件名

    Args:
        original_path: 原文件路径
        naming_config: 命名配置
        output_format: 输出格式

    Returns:
        生成的文件名
    """
    try:
      path_obj = Path(original_path)
      original_stem = path_obj.stem  # 不带扩展名的文件名

      # 获取新扩展名
      new_extension = self.SUPPORTED_FORMATS.get(
          output_format.lower(), {}).get('extension', '.png')

      naming_rule = naming_config.get('rule', 'suffix')

      if naming_rule == 'original':
        # 保留原文件名，只改扩展名
        new_filename = original_stem + new_extension
      elif naming_rule == 'prefix':
        # 添加前缀
        prefix = naming_config.get(
            'prefix', naming_config.get('naming_prefix', 'wm_'))
        new_filename = prefix + original_stem + new_extension
      elif naming_rule == 'suffix':
        # 添加后缀
        suffix = naming_config.get(
            'suffix', naming_config.get('naming_suffix', '_watermarked'))
        new_filename = original_stem + suffix + new_extension
      else:
        # 默认添加后缀（从config获取默认值）
        suffix = naming_config.get('naming_suffix', '_watermarked')
        new_filename = original_stem + suffix + new_extension

      return new_filename

    except Exception as e:
      self.logger.error(f"生成文件名失败: {str(e)}")
      # 返回默认文件名
      return f"watermarked_{int(time.time())}.png"

  def _resize_image(self, image: Image.Image, resize_config: Dict[str, Any]) -> Image.Image:
    """
    调整图像尺寸

    Args:
        image: 原图像
        resize_config: 尺寸配置

    Returns:
        调整后的图像
    """
    try:
      resize_type = resize_config.get('type', 'percentage')

      if resize_type == 'percentage':
        # 按百分比缩放
        percentage = resize_config.get('percentage', 100)
        if percentage != 100:
          new_width = int(image.width * percentage / 100)
          new_height = int(image.height * percentage / 100)
          return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

      elif resize_type == 'width':
        # 按宽度缩放，保持宽高比
        target_width = resize_config.get('width', image.width)
        if target_width != image.width:
          ratio = target_width / image.width
          new_height = int(image.height * ratio)
          return image.resize((target_width, new_height), Image.Resampling.LANCZOS)

      elif resize_type == 'height':
        # 按高度缩放，保持宽高比
        target_height = resize_config.get('height', image.height)
        if target_height != image.height:
          ratio = target_height / image.height
          new_width = int(image.width * ratio)
          return image.resize((new_width, target_height), Image.Resampling.LANCZOS)

      elif resize_type == 'fixed':
        # 固定尺寸
        target_width = resize_config.get('width', image.width)
        target_height = resize_config.get('height', image.height)
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

      return image

    except Exception as e:
      self.logger.error(f"调整图像尺寸失败: {str(e)}")
      return image

  def get_estimated_file_size(self, image: Image.Image, format_type: str = 'png',
                              quality: int = 85) -> int:
    """
    估算导出文件大小

    Args:
        image: 图像对象
        format_type: 输出格式
        quality: JPEG质量

    Returns:
        估算的文件大小（字节）
    """
    try:
      # 这是一个简单的估算方法
      width, height = image.size
      pixels = width * height

      if format_type.lower() in ['jpeg', 'jpg']:
        # JPEG估算：质量越高文件越大
        base_size = pixels * 0.5  # 基础大小
        quality_factor = quality / 100
        estimated_size = int(base_size * quality_factor)
      else:
        # PNG估算：基于像素和透明度
        if image.mode == 'RGBA':
          estimated_size = pixels * 4  # 4字节每像素
        else:
          estimated_size = pixels * 3  # 3字节每像素

        # PNG压缩因子
        estimated_size = int(estimated_size * 0.7)

      return max(1024, estimated_size)  # 最小1KB

    except Exception as e:
      self.logger.error(f"估算文件大小失败: {str(e)}")
      return 1024 * 100  # 默认100KB
