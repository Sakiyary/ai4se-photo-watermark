#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
位置控制面板组件（简化版）
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Callable, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class PositionControlPanel:
  """位置控制面板"""

  def __init__(self, parent: tk.Widget,
               on_position_change: Optional[Callable[[], None]] = None,
               config_manager=None):
    """
    初始化位置控制面板

    Args:
        parent: 父容器
        on_position_change: 位置改变回调
        config_manager: 配置管理器
    """
    self.parent = parent
    self.on_position_change = on_position_change
    self.config_manager = config_manager
    self.logger = logging.getLogger(__name__)

    # 位置按钮
    self.position_buttons = {}

    # 创建界面
    self._create_widgets()

  def _create_widgets(self):
    """创建界面组件"""
    try:
      # 主容器
      main_frame = ttk.Frame(self.parent)
      main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

      # 位置选择
      position_frame = ttk.LabelFrame(main_frame, text="水印位置")
      position_frame.pack(fill=tk.X, pady=5)

      # 九宫格位置
      grid_frame = ttk.Frame(position_frame)
      grid_frame.pack(pady=10)

      # 当前选中位置
      self.selected_position = tk.StringVar(value="bottom_right")

      # 创建九宫格按钮
      positions = [
          ("top_left", "左上", 0, 0),
          ("top_center", "上中", 0, 1),
          ("top_right", "右上", 0, 2),
          ("middle_left", "左中", 1, 0),
          ("center", "中心", 1, 1),
          ("middle_right", "右中", 1, 2),
          ("bottom_left", "左下", 2, 0),
          ("bottom_center", "下中", 2, 1),
          ("bottom_right", "右下", 2, 2)
      ]

      for pos_id, text, row, col in positions:
        btn = tk.Radiobutton(
            grid_frame,
            text=text,
            variable=self.selected_position,
            value=pos_id,
            command=self._on_position_change,
            indicatoron=False,
            width=8,
            height=2
        )
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        self.position_buttons[pos_id] = btn

      # 添加自定义位置选项
      custom_btn = tk.Radiobutton(
          position_frame,
          text="自定义位置",
          variable=self.selected_position,
          value="custom",
          command=self._on_position_change,
          indicatoron=False
      )
      custom_btn.pack(pady=5)
      self.position_buttons["custom"] = custom_btn

      # 自定义坐标输入
      custom_coord_frame = ttk.LabelFrame(position_frame, text="自定义坐标 (像素)")
      custom_coord_frame.pack(fill=tk.X, pady=5)

      # X 坐标
      x_frame = ttk.Frame(custom_coord_frame)
      x_frame.pack(fill=tk.X, pady=2)
      ttk.Label(x_frame, text="X:").pack(side=tk.LEFT)
      self.custom_x = tk.IntVar(value=20)
      x_spinbox = ttk.Spinbox(x_frame, from_=0, to=10000, width=10,
                              textvariable=self.custom_x, command=self._on_setting_change)
      x_spinbox.pack(side=tk.RIGHT)

      # Y 坐标
      y_frame = ttk.Frame(custom_coord_frame)
      y_frame.pack(fill=tk.X, pady=2)
      ttk.Label(y_frame, text="Y:").pack(side=tk.LEFT)
      self.custom_y = tk.IntVar(value=20)
      y_spinbox = ttk.Spinbox(y_frame, from_=0, to=10000, width=10,
                              textvariable=self.custom_y, command=self._on_setting_change)
      y_spinbox.pack(side=tk.RIGHT)

      # 重置位置按钮（放在位置选择框内）
      ttk.Button(position_frame, text="重置位置",
                 command=self._reset_position).pack(pady=5)

      # 边距设置
      margin_frame = ttk.LabelFrame(main_frame, text="边距设置")
      margin_frame.pack(fill=tk.X, pady=5)

      # 水平边距
      h_margin_frame = ttk.Frame(margin_frame)
      h_margin_frame.pack(fill=tk.X, pady=2)
      ttk.Label(h_margin_frame, text="水平边距:").pack(side=tk.LEFT)
      self.h_margin = tk.IntVar(value=20)
      h_spinbox = ttk.Spinbox(h_margin_frame, from_=0, to=200, width=10,
                              textvariable=self.h_margin, command=self._on_setting_change)
      h_spinbox.pack(side=tk.RIGHT)

      # 垂直边距
      v_margin_frame = ttk.Frame(margin_frame)
      v_margin_frame.pack(fill=tk.X, pady=2)
      ttk.Label(v_margin_frame, text="垂直边距:").pack(side=tk.LEFT)
      self.v_margin = tk.IntVar(value=20)
      v_spinbox = ttk.Spinbox(v_margin_frame, from_=0, to=200, width=10,
                              textvariable=self.v_margin, command=self._on_setting_change)
      v_spinbox.pack(side=tk.RIGHT)

      # 重置边距按钮（放在边距设置框内）
      ttk.Button(margin_frame, text="重置边距",
                 command=self._reset_margins).pack(pady=5)

      # 旋转设置
      rotation_frame = ttk.LabelFrame(main_frame, text="旋转设置")
      rotation_frame.pack(fill=tk.X, pady=5)

      rot_frame = ttk.Frame(rotation_frame)
      rot_frame.pack(fill=tk.X, pady=2)
      ttk.Label(rot_frame, text="旋转角度:").pack(side=tk.LEFT)
      self.rotation = tk.IntVar(value=0)
      rot_scale = ttk.Scale(rot_frame, from_=-180, to=180, orient=tk.HORIZONTAL,
                            variable=self.rotation, command=self._on_setting_change)
      rot_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

      # 显示角度值
      self.rotation_label = ttk.Label(rotation_frame, text="0°")
      self.rotation_label.pack()

      # 重置旋转按钮（放在旋转设置框内）
      ttk.Button(rotation_frame, text="重置旋转",
                 command=self._reset_rotation).pack(pady=5)

    except Exception as e:
      self.logger.error(f"加载位置配置失败: {str(e)}")

  def set_custom_position(self, x: int, y: int):
    """
    设置自定义位置

    Args:
        x: X坐标
        y: Y坐标
    """
    try:
      self.selected_position.set('custom')
      self.custom_x.set(x)
      self.custom_y.set(y)
      self.logger.info(f"设置自定义位置: ({x}, {y})")
    except Exception as e:
      self.logger.error(f"设置自定义位置失败: {str(e)}")

  def _on_position_change(self):
    """位置改变"""
    try:
      self._notify_change()
    except Exception as e:
      self.logger.error(f"处理位置改变失败: {str(e)}")

  def _on_setting_change(self, event=None):
    """设置改变"""
    try:
      # 更新旋转角度显示
      angle = self.rotation.get()
      self.rotation_label.config(text=f"{angle}°")

      self._notify_change()
    except Exception as e:
      self.logger.error(f"处理设置改变失败: {str(e)}")

  def _reset_position(self):
    """重置位置"""
    try:
      if self.config_manager:
        from ...core.config_manager import ConfigManager
        default_position = ConfigManager.DEFAULT_CONFIG['watermark']['position']['preset']
        self.selected_position.set(default_position)
      else:
        self.selected_position.set("bottom_right")

      # 重置自定义位置
      self.custom_x.set(20)
      self.custom_y.set(20)

      self._notify_change()
    except Exception as e:
      self.logger.error(f"重置位置失败: {str(e)}")

  def _reset_margins(self):
    """重置边距"""
    try:
      if self.config_manager:
        from ...core.config_manager import ConfigManager
        default_margins = ConfigManager.DEFAULT_CONFIG['watermark']['position']['margins']
        self.h_margin.set(default_margins.get('horizontal', 20))
        self.v_margin.set(default_margins.get('vertical', 20))
      else:
        self.h_margin.set(20)
        self.v_margin.set(20)
      self._notify_change()
    except Exception as e:
      self.logger.error(f"重置边距失败: {str(e)}")

  def _reset_rotation(self):
    """重置旋转"""
    try:
      if self.config_manager:
        from ...core.config_manager import ConfigManager
        default_rotation = int(
            ConfigManager.DEFAULT_CONFIG['watermark']['position']['rotation'])
        self.rotation.set(default_rotation)
        self.rotation_label.config(text=f"{default_rotation}°")
      else:
        self.rotation.set(0)
        self.rotation_label.config(text="0°")
      self._notify_change()
    except Exception as e:
      self.logger.error(f"重置旋转失败: {str(e)}")

  def _notify_change(self):
    """通知改变"""
    if self.on_position_change:
      self.on_position_change()

  def get_config(self) -> Dict[str, Any]:
    """获取当前配置"""
    try:
      return {
          'position': self.selected_position.get(),
          'margins': {
              'horizontal': self.h_margin.get(),
              'vertical': self.v_margin.get()
          },
          'rotation': self.rotation.get(),
          'custom_x': self.custom_x.get(),
          'custom_y': self.custom_y.get()
      }
    except Exception as e:
      self.logger.error(f"获取位置配置失败: {str(e)}")
      return {}

  def load_config(self, config: Dict[str, Any]):
    """载入配置"""
    try:
      if 'position' in config:
        self.selected_position.set(config['position'])

      if 'margins' in config:
        margins = config['margins']
        if isinstance(margins, dict):
          self.h_margin.set(margins.get('horizontal', 20))
          self.v_margin.set(margins.get('vertical', 20))

      if 'rotation' in config:
        rotation_value = int(config['rotation'])
        self.rotation.set(rotation_value)
        self.rotation_label.config(text=f"{rotation_value}°")

      if 'custom_x' in config:
        self.custom_x.set(config['custom_x'])

      if 'custom_y' in config:
        self.custom_y.set(config['custom_y'])

    except Exception as e:
      self.logger.error(f"加载位置配置失败: {str(e)}")

  def get_position_coordinates(self, image_size: Tuple[int, int],
                               watermark_size: Tuple[int, int]) -> Tuple[int, int]:
    """
    计算水印位置坐标

    Args:
        image_size: 图片尺寸 (width, height)
        watermark_size: 水印尺寸 (width, height)

    Returns:
        水印位置坐标 (x, y)
    """
    try:
      img_w, img_h = image_size
      wm_w, wm_h = watermark_size
      h_margin = self.h_margin.get()
      v_margin = self.v_margin.get()

      position = self.selected_position.get()

      # 计算基础位置
      if position.startswith("top"):
        y = v_margin
      elif position.startswith("middle"):
        y = (img_h - wm_h) // 2
      else:  # bottom
        y = img_h - wm_h - v_margin

      if position.endswith("left"):
        x = h_margin
      elif position.endswith("center"):
        x = (img_w - wm_w) // 2
      else:  # right
        x = img_w - wm_w - h_margin

      return (x, y)

    except Exception as e:
      self.logger.error(f"计算位置坐标失败: {str(e)}")
      return (0, 0)
