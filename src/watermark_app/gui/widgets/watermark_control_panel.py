#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印控制面板组件（简化版）
"""

import tkinter as tk
from tkinter import ttk, colorchooser, font
import logging
from typing import Optional, Callable, Dict, Any
import os
import sys
import platform
from pathlib import Path

logger = logging.getLogger(__name__)


class WatermarkControlPanel:
  """水印控制面板"""

  def __init__(self, parent: tk.Widget,
               on_watermark_change: Optional[Callable[[], None]] = None,
               config_manager=None):
    """
    初始化水印控制面板

    Args:
        parent: 父容器
        on_watermark_change: 水印改变回调
        config_manager: 配置管理器
    """
    self.parent = parent
    self.on_watermark_change = on_watermark_change
    self.config_manager = config_manager
    self.logger = logging.getLogger(__name__)

    # 创建界面
    self._create_widgets()

  def _create_widgets(self):
    """创建界面组件"""
    try:
      # 主容器
      main_frame = ttk.Frame(self.parent)
      main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

      # 水印类型选择
      type_frame = ttk.LabelFrame(main_frame, text="水印类型")
      type_frame.pack(fill=tk.X, pady=5)

      self.watermark_type = tk.StringVar(value="text")
      ttk.Radiobutton(type_frame, text="文本水印", variable=self.watermark_type,
                      value="text", command=self._on_type_change).pack(anchor=tk.W)
      ttk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type,
                      value="image", command=self._on_type_change).pack(anchor=tk.W)

      # 文本水印设置
      self.text_frame = ttk.LabelFrame(main_frame, text="文本设置")
      self.text_frame.pack(fill=tk.X, pady=5)

      # 文本内容
      ttk.Label(self.text_frame, text="文本内容:").pack(anchor=tk.W)
      self.text_entry = ttk.Entry(self.text_frame, width=30)
      self.text_entry.pack(fill=tk.X, pady=2)
      self.text_entry.insert(0, "水印文本")
      self.text_entry.bind('<KeyRelease>', self._on_text_change)

      # 字体大小
      size_frame = ttk.Frame(self.text_frame)
      size_frame.pack(fill=tk.X, pady=2)
      ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
      self.font_size = tk.IntVar(value=36)
      size_spinbox = ttk.Spinbox(size_frame, from_=12, to=200, width=10,
                                 textvariable=self.font_size, command=self._on_setting_change)
      size_spinbox.bind('<KeyRelease>', self._on_setting_change)
      size_spinbox.bind('<FocusOut>', self._on_setting_change)
      size_spinbox.pack(side=tk.RIGHT)

      # 字体选择
      font_frame = ttk.Frame(self.text_frame)
      font_frame.pack(fill=tk.X, pady=2)
      ttk.Label(font_frame, text="字体:").pack(side=tk.LEFT)
      self.font_family = tk.StringVar(value="微软雅黑")
      self.font_combo = ttk.Combobox(font_frame, textvariable=self.font_family,
                                     values=self._get_available_fonts(), width=15)
      self.font_combo.pack(side=tk.RIGHT)
      self.font_combo.bind('<<ComboboxSelected>>', self._on_setting_change)

      # 重置字体按钮
      reset_font_frame = ttk.Frame(self.text_frame)
      reset_font_frame.pack(fill=tk.X, pady=2)
      ttk.Button(reset_font_frame, text="重置字体设置",
                 command=self._reset_font_settings).pack()

      # 颜色选择
      color_frame = ttk.Frame(self.text_frame)
      color_frame.pack(fill=tk.X, pady=2)
      ttk.Label(color_frame, text="文字颜色:").pack(side=tk.LEFT)
      self.text_color = tk.StringVar(value="#FFFFFF")
      self.color_button = tk.Button(color_frame, text="选择颜色",
                                    command=self._choose_color, width=12,
                                    bg="white")
      self.color_button.pack(side=tk.RIGHT)

      # 透明度
      opacity_frame = ttk.Frame(self.text_frame)
      opacity_frame.pack(fill=tk.X, pady=2)
      ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
      self.opacity = tk.IntVar(value=80)
      opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                variable=self.opacity, command=self._on_setting_change)
      opacity_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

      # 阴影效果
      shadow_frame = ttk.Frame(self.text_frame)
      shadow_frame.pack(fill=tk.X, pady=2)
      self.shadow_enabled = tk.BooleanVar(value=True)
      shadow_check = ttk.Checkbutton(
          shadow_frame, text="开启阴影", variable=self.shadow_enabled, command=self._on_setting_change)
      shadow_check.pack(side=tk.LEFT)

      # 字体样式（粗体和斜体）
      style_frame = ttk.Frame(self.text_frame)
      style_frame.pack(fill=tk.X, pady=2)
      self.bold_enabled = tk.BooleanVar(value=False)
      bold_check = ttk.Checkbutton(
          style_frame, text="粗体", variable=self.bold_enabled, command=self._on_setting_change)
      bold_check.pack(side=tk.LEFT)

      self.italic_enabled = tk.BooleanVar(value=False)
      italic_check = ttk.Checkbutton(
          style_frame, text="斜体", variable=self.italic_enabled, command=self._on_setting_change)
      italic_check.pack(side=tk.LEFT, padx=(10, 0))

      # 描边设置
      stroke_frame = ttk.Frame(self.text_frame)
      stroke_frame.pack(fill=tk.X, pady=2)
      self.stroke_enabled = tk.BooleanVar(value=False)
      stroke_check = ttk.Checkbutton(
          stroke_frame, text="开启描边", variable=self.stroke_enabled, command=self._on_setting_change)
      stroke_check.pack(side=tk.LEFT)

      # 描边宽度
      ttk.Label(stroke_frame, text="宽度:").pack(side=tk.LEFT, padx=(10, 5))
      self.stroke_width = tk.IntVar(value=2)
      stroke_width_spinbox = ttk.Spinbox(stroke_frame, from_=1, to=10, width=5,
                                         textvariable=self.stroke_width, command=self._on_setting_change)
      stroke_width_spinbox.pack(side=tk.LEFT)
      stroke_width_spinbox.bind('<KeyRelease>', self._on_setting_change)
      stroke_width_spinbox.bind('<FocusOut>', self._on_setting_change)

      # 图片水印设置（初始隐藏）
      self.image_frame = ttk.LabelFrame(main_frame, text="图片设置")

      ttk.Label(self.image_frame, text="水印图片路径:").pack(anchor=tk.W)
      path_frame = ttk.Frame(self.image_frame)
      path_frame.pack(fill=tk.X, pady=2)
      self.image_path = tk.StringVar()
      ttk.Entry(path_frame, textvariable=self.image_path, state='readonly').pack(
          side=tk.LEFT, fill=tk.X, expand=True)
      ttk.Button(path_frame, text="浏览", command=self._browse_image).pack(
          side=tk.RIGHT, padx=2)

      # 图片水印尺寸控制
      size_frame = ttk.Frame(self.image_frame)
      size_frame.pack(fill=tk.X, pady=2)
      ttk.Label(size_frame, text="尺寸比例:").pack(side=tk.LEFT)
      self.image_scale = tk.IntVar(value=25)  # 默认25%
      scale_spinbox = ttk.Spinbox(size_frame, from_=10, to=100, width=10,
                                  textvariable=self.image_scale,
                                  command=self._on_setting_change)
      scale_spinbox.bind('<KeyRelease>', self._on_setting_change)
      scale_spinbox.bind('<FocusOut>', self._on_setting_change)
      scale_spinbox.pack(side=tk.RIGHT)
      ttk.Label(size_frame, text="%").pack(side=tk.RIGHT)

      # 图片水印透明度
      img_opacity_frame = ttk.Frame(self.image_frame)
      img_opacity_frame.pack(fill=tk.X, pady=2)
      ttk.Label(img_opacity_frame, text="透明度:").pack(side=tk.LEFT)
      self.image_opacity = tk.IntVar(value=90)
      img_opacity_scale = ttk.Scale(img_opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.image_opacity, command=self._on_setting_change)
      img_opacity_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

      # 初始显示文本设置
      self._on_type_change()

    except Exception as e:
      self.logger.error(f"创建水印控制界面失败: {str(e)}")

  def _on_type_change(self):
    """水印类型改变"""
    try:
      if self.watermark_type.get() == "text":
        self.text_frame.pack(fill=tk.X, pady=5)
        self.image_frame.pack_forget()
      else:
        self.text_frame.pack_forget()
        self.image_frame.pack(fill=tk.X, pady=5)

      self._notify_change()
    except Exception as e:
      self.logger.error(f"处理水印类型改变失败: {str(e)}")

  def _on_text_change(self, event=None):
    """文本改变"""
    self._notify_change()

  def _on_setting_change(self, event=None):
    """设置改变"""
    self._notify_change()

  def _get_available_fonts(self):
    """获取系统所有可用字体列表（跨平台）"""
    try:
      # 获取Tkinter的系统字体列表
      system_fonts = sorted(list(font.families()))

      # 过滤掉以@开头的字体（这些通常是特殊的旋转字体）
      filtered_fonts = [f for f in system_fonts if not f.startswith('@')]

      # 优先显示常用字体
      common_fonts = []

      # 根据平台设置优先字体
      if platform.system() == "Windows":
        priority_fonts = ['微软雅黑', '宋体', 'Arial', 'Times New Roman', 'Calibri']
      elif platform.system() == "Darwin":  # macOS
        priority_fonts = ['苹方-简', 'Helvetica', 'Times', 'Arial']
      else:  # Linux
        priority_fonts = ['Noto Sans CJK SC',
                          'DejaVu Sans', 'Liberation Sans', 'Arial']

      # 先添加优先字体
      for font_name in priority_fonts:
        if font_name in filtered_fonts:
          common_fonts.append(font_name)

      # 添加其他字体
      for font_name in filtered_fonts:
        if font_name not in common_fonts:
          common_fonts.append(font_name)

      return common_fonts if common_fonts else ['Arial', 'Helvetica', 'Sans']

    except Exception as e:
      self.logger.error(f"获取系统字体失败: {e}")
      # 返回基本的备用字体
      return ['Arial', 'Helvetica', 'Times New Roman', 'Courier New']

  def _choose_color(self):
    """选择颜色"""
    try:
      # 获取当前颜色作为初始颜色
      current_color = self.text_color.get()
      if current_color.startswith('#'):
        initial_color = current_color
      else:
        initial_color = '#FFFFFF'

      color = colorchooser.askcolor(initialcolor=initial_color)
      if color[1]:  # 用户选择了颜色
        self.text_color.set(color[1])
        self.color_button.config(bg=color[1])
        self._notify_change()
    except Exception as e:
      self.logger.error(f"选择颜色失败: {str(e)}")

  def _browse_image(self):
    """浏览图片"""
    from tkinter import filedialog
    try:
      file_path = filedialog.askopenfilename(
          title="选择水印图片",
          filetypes=[
              ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
              ("PNG文件", "*.png"),
              ("所有文件", "*.*")
          ]
      )
      if file_path:
        self.image_path.set(file_path)
        self._notify_change()
    except Exception as e:
      self.logger.error(f"浏览图片失败: {str(e)}")

  def _reset_font_settings(self):
    """重置字体设置"""
    try:
      # 从 config_manager 获取默认值
      if self.config_manager:
        from ...core.config_manager import ConfigManager
        default_text = ConfigManager.DEFAULT_CONFIG['watermark']['text']

        # 重置为默认值
        self.font_family.set(default_text.get('font_family', 'arial'))
        self.font_size.set(default_text.get('font_size', 36))

        # 处理颜色，从 RGBA 数组转换为十六进制
        color_rgba = default_text.get('color', [255, 255, 255, 128])
        color_hex = '#{:02x}{:02x}{:02x}'.format(
            color_rgba[0], color_rgba[1], color_rgba[2])
        opacity = int((color_rgba[3] / 255.0) *
                      100) if len(color_rgba) > 3 else 80

        self.text_color.set(color_hex)
        self.color_button.config(bg=color_hex)
        self.opacity.set(opacity)

        self.shadow_enabled.set(default_text.get('shadow', False))
        self.bold_enabled.set(default_text.get('bold', False))
        self.italic_enabled.set(default_text.get('italic', False))
        self.stroke_enabled.set(False)  # 默认配置中没有stroke_enabled，使用False
        self.stroke_width.set(default_text.get('stroke_width', 1))
      else:
        # 备用：如果没有 config_manager，使用硬编码默认值
        self.font_family.set("arial")
        self.font_size.set(36)
        self.text_color.set("#FFFFFF")
        self.color_button.config(bg="#FFFFFF")
        self.opacity.set(50)
        self.shadow_enabled.set(False)
        self.bold_enabled.set(False)
        self.italic_enabled.set(False)
        self.stroke_enabled.set(False)
        self.stroke_width.set(1)

      self._notify_change()
    except Exception as e:
      self.logger.error(f"重置字体设置失败: {str(e)}")

  def _notify_change(self):
    """通知改变"""
    if self.on_watermark_change:
      self.on_watermark_change()

  def get_config(self) -> Dict[str, Any]:
    """获取当前配置"""
    try:
      config = {
          'type': self.watermark_type.get(),
          'text': {
              'content': self.text_entry.get(),
              'font_family': self.font_family.get(),
              'font_size': self.font_size.get(),
              'color': self.text_color.get(),
              'opacity': self.opacity.get() / 100.0,
              'shadow_enabled': self.shadow_enabled.get(),
              'stroke_enabled': self.stroke_enabled.get(),
              'stroke_width': self.stroke_width.get(),
              'bold': self.bold_enabled.get(),
              'italic': self.italic_enabled.get()
          },
          'image': {
              'path': self.image_path.get(),
              'scale': self.image_scale.get() / 100.0,
              'opacity': self.image_opacity.get() / 100.0
          }
      }
      return config
    except Exception as e:
      self.logger.error(f"获取配置失败: {str(e)}")
      return {}

  def load_config(self, config: Dict[str, Any]):
    """载入配置"""
    try:
      if 'type' in config:
        self.watermark_type.set(config['type'])

      if 'text' in config:
        text_config = config['text']
        if 'content' in text_config:
          self.text_entry.delete(0, tk.END)
          self.text_entry.insert(0, text_config['content'])
        if 'font_family' in text_config:
          self.font_family.set(text_config['font_family'])
        if 'font_size' in text_config:
          self.font_size.set(text_config['font_size'])
        if 'color' in text_config:
          color_value = text_config['color']
          if isinstance(color_value, str) and color_value.startswith('#'):
            self.text_color.set(color_value)
            if hasattr(self, 'color_button'):
              self.color_button.config(bg=color_value)
          else:
            self.text_color.set('#FFFFFF')
            if hasattr(self, 'color_button'):
              self.color_button.config(bg='#FFFFFF')
        if 'opacity' in text_config:
          self.opacity.set(int(text_config['opacity'] * 100))
        if 'shadow_enabled' in text_config:
          self.shadow_enabled.set(text_config['shadow_enabled'])
        if 'stroke_enabled' in text_config:
          self.stroke_enabled.set(text_config['stroke_enabled'])
        if 'stroke_width' in text_config:
          self.stroke_width.set(text_config['stroke_width'])
        if 'bold' in text_config:
          self.bold_enabled.set(text_config['bold'])
        if 'italic' in text_config:
          self.italic_enabled.set(text_config['italic'])

      if 'image' in config:
        image_config = config['image']
        if 'path' in image_config:
          self.image_path.set(image_config['path'])
        if 'scale' in image_config:
          self.image_scale.set(int(image_config['scale'] * 100))
        if 'opacity' in image_config:
          self.image_opacity.set(int(image_config['opacity'] * 100))

      self._on_type_change()

    except Exception as e:
      self.logger.error(f"载入配置失败: {str(e)}")
