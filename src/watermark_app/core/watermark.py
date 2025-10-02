#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印处理核心模块
负责文本水印和图片水印的生成与应用
"""

import logging
from typing import Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

logger = logging.getLogger(__name__)


class WatermarkProcessor:
  """水印处理器类"""

  def __init__(self):
    """初始化水印处理器"""
    self.logger = logging.getLogger(__name__)

  def create_text_watermark(self, text: str, font_path: Optional[str] = None,
                            font_size: int = 36, color: Tuple[int, int, int, int] = (255, 255, 255, 128),
                            shadow: bool = False, shadow_offset: Tuple[int, int] = (2, 2),
                            shadow_color: Tuple[int, int,
                                                int, int] = (0, 0, 0, 64),
                            stroke_width: int = 0, stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> Optional[Image.Image]:
    """
    创建文本水印

    Args:
        text: 水印文本
        font_path: 字体文件路径
        font_size: 字体大小
        color: 文本颜色 (R, G, B, A)
        shadow: 是否添加阴影
        shadow_offset: 阴影偏移
        shadow_color: 阴影颜色
        stroke_width: 描边宽度
        stroke_color: 描边颜色

    Returns:
        文本水印图像
    """
    try:
      # 加载字体
      try:
        if font_path and os.path.exists(font_path):
          font = ImageFont.truetype(font_path, font_size)
        else:
          # 尝试使用系统默认字体
          font = ImageFont.load_default()
      except Exception:
        font = ImageFont.load_default()

      # 计算文本尺寸
      temp_img = Image.new('RGBA', (1, 1))
      temp_draw = ImageDraw.Draw(temp_img)

      # 获取文本边界框
      bbox = temp_draw.textbbox(
          (0, 0), text, font=font, stroke_width=stroke_width)
      text_width = bbox[2] - bbox[0]
      text_height = bbox[3] - bbox[1]

      # 考虑阴影的额外空间
      margin = max(abs(shadow_offset[0]), abs(
          shadow_offset[1])) + stroke_width if shadow else stroke_width
      canvas_width = text_width + margin * 2
      canvas_height = text_height + margin * 2

      # 创建透明画布
      watermark_img = Image.new(
          'RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
      draw = ImageDraw.Draw(watermark_img)

      # 计算文本位置
      text_x = margin - bbox[0]
      text_y = margin - bbox[1]

      # 绘制阴影
      if shadow:
        shadow_x = text_x + shadow_offset[0]
        shadow_y = text_y + shadow_offset[1]
        draw.text((shadow_x, shadow_y), text, font=font, fill=shadow_color,
                  stroke_width=stroke_width, stroke_fill=shadow_color)

      # 绘制主文本
      draw.text((text_x, text_y), text, font=font, fill=color,
                stroke_width=stroke_width, stroke_fill=stroke_color)

      self.logger.info(f"成功创建文本水印: '{text}', 尺寸: {watermark_img.size}")
      return watermark_img

    except Exception as e:
      self.logger.error(f"创建文本水印失败: {str(e)}")
      return None

  def load_image_watermark(self, watermark_path: str, size: Optional[Tuple[int, int]] = None,
                           opacity: float = 1.0) -> Optional[Image.Image]:
    """
    加载并处理图片水印

    Args:
        watermark_path: 水印图片路径
        size: 目标尺寸，None表示保持原尺寸
        opacity: 透明度 (0.0-1.0)

    Returns:
        处理后的水印图像
    """
    try:
      if not os.path.exists(watermark_path):
        self.logger.error(f"水印文件不存在: {watermark_path}")
        return None

      # 加载水印图像
      watermark = Image.open(watermark_path)

      # 确保图像有透明通道
      if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')

      # 调整尺寸
      if size:
        watermark = watermark.resize(size, Image.Resampling.LANCZOS)

      # 调整透明度
      if opacity < 1.0:
        # 创建透明度遮罩
        alpha = watermark.split()[-1]  # 获取alpha通道
        alpha = alpha.point(lambda p: int(p * opacity))
        watermark.putalpha(alpha)

      self.logger.info(f"成功加载图片水印: {watermark_path}, 尺寸: {watermark.size}")
      return watermark

    except Exception as e:
      self.logger.error(f"加载图片水印失败: {str(e)}")
      return None

  def rotate_watermark(self, watermark: Image.Image, angle: float) -> Image.Image:
    """
    旋转水印

    Args:
        watermark: 水印图像
        angle: 旋转角度（度）

    Returns:
        旋转后的水印图像
    """
    try:
      if angle == 0:
        return watermark

      # 旋转水印，保持透明背景
      rotated = watermark.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
      return rotated

    except Exception as e:
      self.logger.error(f"旋转水印失败: {str(e)}")
      return watermark

  def apply_watermark(self, base_image: Image.Image, watermark: Image.Image,
                      position: Tuple[int, int], opacity: float = 1.0) -> Image.Image:
    """
    将水印应用到基础图像上

    Args:
        base_image: 基础图像
        watermark: 水印图像
        position: 水印位置 (x, y)
        opacity: 水印整体透明度 (0.0-1.0)

    Returns:
        应用水印后的图像
    """
    try:
      # 复制基础图像
      result = base_image.copy()

      # 确保基础图像有透明通道
      if result.mode != 'RGBA':
        result = result.convert('RGBA')

      # 处理水印透明度
      watermark_copy = watermark.copy()
      if opacity < 1.0:
        alpha = watermark_copy.split()[-1]
        alpha = alpha.point(lambda p: int(p * opacity))
        watermark_copy.putalpha(alpha)

      # 计算粘贴位置，确保水印不超出图像边界
      x, y = position
      img_width, img_height = result.size
      wm_width, wm_height = watermark_copy.size

      # 调整位置确保水印完全在图像内
      x = max(0, min(x, img_width - wm_width))
      y = max(0, min(y, img_height - wm_height))

      # 应用水印
      result.paste(watermark_copy, (x, y), watermark_copy)

      self.logger.info(f"成功应用水印，位置: ({x}, {y})")
      return result

    except Exception as e:
      self.logger.error(f"应用水印失败: {str(e)}")
      return base_image

  def get_preset_positions(self, image_size: Tuple[int, int],
                           watermark_size: Tuple[int, int],
                           margin: int = 20) -> dict:
    """
    获取九宫格预设位置

    Args:
        image_size: 图像尺寸
        watermark_size: 水印尺寸
        margin: 边距

    Returns:
        位置字典
    """
    img_width, img_height = image_size
    wm_width, wm_height = watermark_size

    positions = {
        'top_left': (margin, margin),
        'top_center': ((img_width - wm_width) // 2, margin),
        'top_right': (img_width - wm_width - margin, margin),
        'middle_left': (margin, (img_height - wm_height) // 2),
        'center': ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
        'middle_right': (img_width - wm_width - margin, (img_height - wm_height) // 2),
        'bottom_left': (margin, img_height - wm_height - margin),
        'bottom_center': ((img_width - wm_width) // 2, img_height - wm_height - margin),
        'bottom_right': (img_width - wm_width - margin, img_height - wm_height - margin)
    }

    return positions
