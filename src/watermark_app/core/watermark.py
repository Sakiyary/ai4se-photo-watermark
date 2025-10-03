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
from ..utils.font_mapper import get_font_path

logger = logging.getLogger(__name__)


class WatermarkProcessor:
  """水印处理器类"""

  def __init__(self):
    """初始化水印处理器"""
    self.logger = logging.getLogger(__name__)

  def _load_font(self, font_name_or_path: Optional[str], font_size: int, bold: bool = False, italic: bool = False) -> ImageFont.ImageFont:
    """智能字体加载，支持粗体和斜体"""

    self.logger.info(
        f"加载字体: {font_name_or_path}, 大小: {font_size}, 粗体: {bold}, 斜体: {italic}")

    try:
      font_path = None

      # 1. 如果直接提供了文件路径
      if font_name_or_path and os.path.exists(font_name_or_path):
        font_path = font_name_or_path
        self.logger.info(f"使用提供的字体文件: {font_path}")

      # 2. 使用字体映射器查找字体文件（包括变体支持）
      elif font_name_or_path:
        font_path = get_font_path(font_name_or_path, bold, italic)
        if font_path:
          self.logger.info(f"字体映射成功: {font_name_or_path} -> {font_path}")
        else:
          # 3. 尝试直接使用字体名称
          self.logger.info(f"字体映射失败，尝试直接使用字体名称: {font_name_or_path}")
          font_path = font_name_or_path

      # 4. 加载字体
      if font_path:
        try:
          font = ImageFont.truetype(font_path, font_size)
          self.logger.info(f"成功加载字体: {font_path}")
          return font

        except Exception as e:
          self.logger.warning(f"加载字体失败 {font_path}: {e}")

      # 5. 使用系统默认字体
      import platform
      system = platform.system()

      fallback_fonts = []
      if system == "Windows":
        fallback_fonts = ["C:/Windows/Fonts/msyh.ttc",
                          "C:/Windows/Fonts/arial.ttf"]
      elif system == "Darwin":
        fallback_fonts = ["/System/Library/Fonts/Helvetica.ttc",
                          "/System/Library/Fonts/Arial.ttf"]
      else:
        fallback_fonts = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

      for fallback in fallback_fonts:
        try:
          if os.path.exists(fallback):
            font = ImageFont.truetype(fallback, font_size)
            self.logger.info(f"使用备用字体: {fallback}")
            return font
        except Exception:
          continue

      # 6. 最后的备用方案
      self.logger.warning("使用默认字体")
      return ImageFont.load_default()

    except Exception as e:
      self.logger.error(f"字体加载异常: {e}")
      return ImageFont.load_default()

  def create_text_watermark(self, text: str, font_path: Optional[str] = None,
                            font_size: int = 36, color: Tuple[int, int, int, int] = (255, 255, 255, 128),
                            shadow: bool = False, shadow_offset: Tuple[int, int] = (2, 2),
                            shadow_color: Tuple[int, int,
                                                int, int] = (0, 0, 0, 64),
                            stroke_width: int = 0, stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                            bold: bool = False, italic: bool = False) -> Optional[Image.Image]:
    """
    创建文本水印

    Args:
        text: 水印文本
        font_path: 字体文件路径或名称
        font_size: 字体大小
        color: 文本颜色 (R, G, B, A)
        shadow: 是否添加阴影
        shadow_offset: 阴影偏移
        shadow_color: 阴影颜色
        stroke_width: 描边宽度
        stroke_color: 描边颜色
        bold: 是否粗体
        italic: 是否斜体

    Returns:
        文本水印图像
    """
    try:
      # 加载字体（跨平台支持，包括粗体斜体）
      font = self._load_font(font_path, font_size, bold, italic)

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
        self._draw_text_with_effects((shadow_x, shadow_y), text, font, shadow_color,
                                     stroke_width, shadow_color, draw, bold, italic)

      # 绘制主文本
      self._draw_text_with_effects((text_x, text_y), text, font, color,
                                   stroke_width, stroke_color, draw, bold, italic)

      self.logger.info(f"成功创建文本水印: '{text}', 尺寸: {watermark_img.size}")
      return watermark_img

    except Exception as e:
      self.logger.error(f"创建文本水印失败: {str(e)}")
      return None

  def _draw_text_with_effects(self, position: Tuple[int, int], text: str, font: ImageFont.ImageFont,
                              color: Tuple[int, int, int, int], stroke_width: int,
                              stroke_color: Tuple[int, int, int, int], draw: ImageDraw.ImageDraw,
                              bold: bool, italic: bool):
    """绘制带效果的文本（支持算法模拟的粗体和斜体）"""
    try:
      x, y = position

      # 检查是否需要算法模拟效果
      needs_simulated_bold = bold and self._needs_simulated_effect(
          font, bold=True)
      needs_simulated_italic = italic and self._needs_simulated_effect(
          font, italic=True)

      if needs_simulated_bold or needs_simulated_italic:
        # 使用算法模拟效果
        self._draw_simulated_text(draw, (x, y), text, font, color, stroke_width,
                                  stroke_color, needs_simulated_bold, needs_simulated_italic)
      else:
        # 普通绘制
        draw.text((x, y), text, font=font, fill=color,
                  stroke_width=stroke_width, stroke_fill=stroke_color)

    except Exception as e:
      self.logger.warning(f"绘制特效文本失败，使用普通绘制: {e}")
      draw.text(position, text, font=font, fill=color,
                stroke_width=stroke_width, stroke_fill=stroke_color)

  def _needs_simulated_effect(self, font: ImageFont.ImageFont, bold: bool = False, italic: bool = False) -> bool:
    """判断是否需要算法模拟字体效果"""
    try:
      # 通过字体文件名判断是否为中文字体或缺少变体的字体
      font_path = getattr(font, 'path', '')
      if not font_path:
        return True  # 如果无法获取路径，保守地认为需要模拟

      # 中文字体通常需要算法模拟斜体
      chinese_font_files = ['msyh', 'simsun',
                            'simhei', 'stfang', 'stkai', 'stsong']
      font_name_lower = font_path.lower()

      for chinese_font in chinese_font_files:
        if chinese_font in font_name_lower:
          # 对于中文字体，斜体总是需要模拟
          if italic:
            return True
          # 粗体只在没有对应粗体文件时需要模拟
          if bold and 'bd' not in font_name_lower and 'bold' not in font_name_lower:
            return True

      return False

    except Exception:
      return True  # 出错时保守地认为需要模拟

  def _draw_simulated_text(self, draw: ImageDraw.ImageDraw, position: Tuple[int, int], text: str,
                           font: ImageFont.ImageFont, color: Tuple[int, int, int, int],
                           stroke_width: int, stroke_color: Tuple[int, int, int, int],
                           simulate_bold: bool, simulate_italic: bool):
    """绘制算法模拟的粗体和斜体文本"""
    try:
      x, y = position

      if simulate_bold and simulate_italic:
        # 粗斜体：先绘制粗体，再应用斜体变换，避免裁切
        from PIL import Image, ImageDraw

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 计算斜体变换所需空间
        shear_factor = 0.2
        shear_offset = int(text_height * shear_factor)

        # 创建足够大的临时画布
        margin_left = abs(shear_offset) + 5
        margin_right = shear_offset + 5
        temp_width = text_width + margin_left + margin_right + 2  # 额外空间给粗体
        temp_height = text_height + 10

        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        # 绘制粗体效果，位置偏移预留变换空间
        text_x = margin_left - bbox[0]
        text_y = 5 - bbox[1]
        for offset_x in range(2):  # 粗体效果
          temp_draw.text((text_x + offset_x, text_y), text, font=font, fill=color,
                         stroke_width=stroke_width, stroke_fill=stroke_color)

        # 应用斜体变换
        try:
          bold_italic_img = temp_img.transform(
              temp_img.size,
              Image.AFFINE,
              (1, shear_factor, 0, 0, 1, 0),
              Image.BILINEAR,
              fillcolor=(0, 0, 0, 0)
          )

          # 计算粘贴位置，微调补偿偏移（粗斜体）
          paste_x = max(0, x - int(margin_left * 0.9))  # 减少左补偿
          paste_y = max(0, y - 7)  # 减少上补偿

          # 合成到主画布
          main_img = draw._image
          actual_width = min(temp_width, main_img.width - paste_x)
          actual_height = min(temp_height, main_img.height - paste_y)

          if actual_width > 0 and actual_height > 0:
            if actual_width == temp_width and actual_height == temp_height:
              main_img.alpha_composite(bold_italic_img, (paste_x, paste_y))
            else:
              cropped_img = bold_italic_img.crop(
                  (0, 0, actual_width, actual_height))
              main_img.alpha_composite(cropped_img, (paste_x, paste_y))

        except Exception as e:
          # 备用方案：简单的粗体+偏移
          self.logger.debug(f"粗斜体变换失败，使用备用方案: {e}")
          italic_offset = int(text_height * 0.15)
          for offset_x in range(2):
            draw.text((x + offset_x + italic_offset, y), text, font=font, fill=color,
                      stroke_width=stroke_width, stroke_fill=stroke_color)
      elif simulate_bold:
        # 粗体：适度的多次绘制模拟粗体效果
        for offset_x in range(2):  # 减少到2次
          for offset_y in range(1):  # 减少到1次
            draw.text((x + offset_x, y + offset_y), text, font=font, fill=color,
                      stroke_width=stroke_width, stroke_fill=stroke_color)
      elif simulate_italic:
        # 斜体：通过PIL的transform实现真正的斜体变换，避免裁切
        from PIL import Image, ImageDraw

        # 获取文本边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 计算斜体变换所需的额外空间
        shear_factor = 0.2  # 斜体倾斜度
        shear_offset = int(text_height * shear_factor)  # 变换会产生的水平偏移

        # 创建足够大的临时画布，预留变换空间
        margin_left = abs(shear_offset) + 5  # 左侧边距防止负偏移裁切
        margin_right = shear_offset + 5      # 右侧边距
        temp_width = text_width + margin_left + margin_right
        temp_height = text_height + 10  # 额外的垂直空间

        # 创建临时透明画布
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)

        # 在临时画布上绘制正常文本，位置偏移以预留变换空间
        text_x = margin_left - bbox[0]
        text_y = 5 - bbox[1]
        temp_draw.text((text_x, text_y), text, font=font, fill=color,
                       stroke_width=stroke_width, stroke_fill=stroke_color)

        # 应用斜体剪切变换
        try:
          italic_img = temp_img.transform(
              temp_img.size,
              Image.AFFINE,
              (1, shear_factor, 0, 0, 1, 0),
              Image.BILINEAR,
              fillcolor=(0, 0, 0, 0)
          )

          # 计算在主画布上的粘贴位置，微调补偿偏移
          # 调整这两个参数来控制斜体位置：
          # - 减少 margin_left 可以让斜体更靠左
          # - 增加 y 的补偿可以让斜体更靠上
          paste_x = max(0, x - int(margin_left * 0.7))  # 减少左补偿，避免过度左移
          paste_y = max(0, y - 3)  # 减少上补偿，避免过度上移

          # 将斜体图像合成到主画布上
          main_img = draw._image

          # 检查并调整粘贴区域以避免越界
          actual_width = min(temp_width, main_img.width - paste_x)
          actual_height = min(temp_height, main_img.height - paste_y)

          if actual_width > 0 and actual_height > 0:
            if actual_width == temp_width and actual_height == temp_height:
              # 完整粘贴
              main_img.alpha_composite(italic_img, (paste_x, paste_y))
            else:
              # 需要裁剪
              cropped_img = italic_img.crop((0, 0, actual_width, actual_height))
              main_img.alpha_composite(cropped_img, (paste_x, paste_y))

        except Exception as e:
          # 如果变换失败，使用简单的偏移作为备用方案
          self.logger.debug(f"斜体变换失败，使用备用方案: {e}")
          italic_offset = int(text_height * 0.15)
          draw.text((x + italic_offset, y), text, font=font, fill=color,
                    stroke_width=stroke_width, stroke_fill=stroke_color)

    except Exception as e:
      self.logger.warning(f"算法模拟字体效果失败，使用普通绘制: {e}")
      draw.text(position, text, font=font, fill=color,
                stroke_width=stroke_width, stroke_fill=stroke_color)

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
