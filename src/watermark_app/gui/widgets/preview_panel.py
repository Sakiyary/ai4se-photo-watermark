#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预览面板组件
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Callable, Tuple
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class PreviewPanel:
  """预览面板"""

  def __init__(self, parent: tk.Widget,
               on_position_change: Optional[Callable[[
                   Tuple[int, int]], None]] = None,
               on_image_switch: Optional[Callable[[str], None]] = None):
    """
    初始化预览面板

    Args:
        parent: 父容器
        on_position_change: 位置改变回调
        on_image_switch: 图片切换回调 (direction: 'prev' | 'next')
    """
    self.parent = parent
    self.on_position_change = on_position_change
    self.on_image_switch = on_image_switch
    self.logger = logging.getLogger(__name__)

    # 状态变量
    self.current_image = None
    self.display_image = None
    self.canvas_image = None
    self.scale_factor = 1.0
    self.image_position = (0, 0)

    # 图片信息显示
    self.image_info = ""

    # 拖拽状态
    self.drag_start_x = 0
    self.drag_start_y = 0
    self.is_dragging = False

    # 创建界面
    self._create_widgets()

  def _create_widgets(self):
    """创建界面组件"""
    try:
      # 主容器
      main_frame = ttk.Frame(self.parent)
      main_frame.pack(fill=tk.BOTH, expand=True)

      # 标题
      title_label = ttk.Label(main_frame, text="预览", font=('Arial', 12, 'bold'))
      title_label.pack(pady=5)

      # 工具栏容器（分为两行）
      toolbar_container = ttk.Frame(main_frame)
      toolbar_container.pack(fill=tk.X, padx=5, pady=2)

      # 第一行：控制按钮
      control_toolbar = ttk.Frame(toolbar_container)
      control_toolbar.pack(fill=tk.X, pady=(0, 3))

      # 图片切换按钮
      nav_frame = ttk.Frame(control_toolbar)
      nav_frame.pack(side=tk.LEFT)

      self.prev_button = ttk.Button(nav_frame, text="◀ 上一张",
                                    command=self._prev_image, width=10)
      self.prev_button.pack(side=tk.LEFT, padx=2)

      self.next_button = ttk.Button(nav_frame, text="下一张 ▶",
                                    command=self._next_image, width=10)
      self.next_button.pack(side=tk.LEFT, padx=2)

      # 分隔符
      ttk.Separator(control_toolbar, orient=tk.VERTICAL).pack(
          side=tk.LEFT, fill=tk.Y, padx=10)

      # 缩放按钮
      zoom_frame = ttk.Frame(control_toolbar)
      zoom_frame.pack(side=tk.LEFT)

      ttk.Button(zoom_frame, text="放大", command=self._zoom_in,
                 width=8).pack(side=tk.LEFT, padx=2)
      ttk.Button(zoom_frame, text="缩小", command=self._zoom_out,
                 width=8).pack(side=tk.LEFT, padx=2)
      ttk.Button(zoom_frame, text="适应", command=self._fit_to_window,
                 width=8).pack(side=tk.LEFT, padx=2)
      ttk.Button(zoom_frame, text="原始", command=self._actual_size,
                 width=8).pack(side=tk.LEFT, padx=2)

      # 缩放比例显示（放在控制按钮行的右侧）
      self.scale_label = ttk.Label(
          control_toolbar, text="100%", font=('Arial', 10, 'bold'))
      self.scale_label.pack(side=tk.RIGHT, padx=5)

      # 第二行：信息显示
      info_toolbar = ttk.Frame(toolbar_container)
      info_toolbar.pack(fill=tk.X)

      # 图片信息显示
      self.info_label = ttk.Label(
          info_toolbar, text="", foreground='gray', anchor=tk.W)
      self.info_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

      # 画布容器
      canvas_frame = ttk.Frame(main_frame)
      canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

      # 创建画布和滚动条
      self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=1,
                              highlightbackground='gray')

      v_scrollbar = ttk.Scrollbar(
          canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
      h_scrollbar = ttk.Scrollbar(
          canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

      self.canvas.configure(yscrollcommand=v_scrollbar.set,
                            xscrollcommand=h_scrollbar.set)

      # 布局
      self.canvas.grid(row=0, column=0, sticky='nsew')
      v_scrollbar.grid(row=0, column=1, sticky='ns')
      h_scrollbar.grid(row=1, column=0, sticky='ew')

      canvas_frame.grid_rowconfigure(0, weight=1)
      canvas_frame.grid_columnconfigure(0, weight=1)

      # 绑定事件
      self.canvas.bind('<Button-1>', self._on_canvas_click)
      self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
      self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
      self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
      self.canvas.bind('<Configure>', self._on_canvas_configure)

      # 显示提示文本
      self._show_placeholder()

    except Exception as e:
      self.logger.error(f"创建预览界面失败: {str(e)}")

  def update_preview(self, image: Image.Image, image_info: str = ""):
    """
    更新预览图像

    Args:
        image: PIL图像对象
        image_info: 图像信息字符串
    """
    try:
      if not image:
        self.clear_preview()
        return

      self.current_image = image
      self.image_info = image_info

      # 默认使用适应窗口大小
      self._fit_to_window()
      self._update_info_label()

    except Exception as e:
      self.logger.error(f"更新预览失败: {str(e)}")

  def clear_preview(self):
    """清空预览"""
    try:
      self.current_image = None
      self.display_image = None
      self.canvas_image = None
      self.scale_factor = 1.0
      self.image_info = ""

      self.canvas.delete("all")
      self._show_placeholder()
      self._update_scale_label()
      self._update_info_label()

    except Exception as e:
      self.logger.error(f"清空预览失败: {str(e)}")

  def _display_image(self):
    """显示图像"""
    try:
      if not self.current_image:
        return

      # 计算显示尺寸
      display_width = int(self.current_image.width * self.scale_factor)
      display_height = int(self.current_image.height * self.scale_factor)

      # 调整图像大小
      if self.scale_factor != 1.0:
        self.display_image = self.current_image.resize(
            (display_width, display_height), Image.Resampling.LANCZOS)
      else:
        self.display_image = self.current_image

      # 转换为Tkinter可用格式
      self.canvas_image = ImageTk.PhotoImage(self.display_image)

      # 清空画布
      self.canvas.delete("all")

      # 计算居中位置
      canvas_width = self.canvas.winfo_width()
      canvas_height = self.canvas.winfo_height()

      if canvas_width <= 1 or canvas_height <= 1:
        # 画布尚未显示，使用默认值
        canvas_width = 800
        canvas_height = 600

      x = max(display_width // 2, canvas_width // 2)
      y = max(display_height // 2, canvas_height // 2)

      # 显示图像
      self.canvas.create_image(
          x, y, image=self.canvas_image, anchor=tk.CENTER, tags="image")

      # 更新画布滚动区域
      self.canvas.configure(scrollregion=(0, 0, max(display_width, canvas_width),
                                          max(display_height, canvas_height)))

      # 更新缩放标签和信息标签
      self._update_scale_label()
      self._update_info_label()

    except Exception as e:
      self.logger.error(f"显示图像失败: {str(e)}")

  def _show_placeholder(self):
    """显示占位符文本"""
    try:
      self.canvas.delete("all")
      canvas_width = self.canvas.winfo_width()
      canvas_height = self.canvas.winfo_height()

      if canvas_width <= 1:
        canvas_width = 400
      if canvas_height <= 1:
        canvas_height = 300

      self.canvas.create_text(canvas_width // 2, canvas_height // 2,
                              text="请选择图片进行预览",
                              font=('Arial', 14), fill='gray',
                              anchor=tk.CENTER)
    except Exception as e:
      self.logger.error(f"显示占位符失败: {str(e)}")

  def _zoom_in(self):
    """放大"""
    try:
      if self.current_image:
        self.scale_factor = min(5.0, self.scale_factor * 1.2)
        self._display_image()
    except Exception as e:
      self.logger.error(f"放大失败: {str(e)}")

  def _zoom_out(self):
    """缩小"""
    try:
      if self.current_image:
        self.scale_factor = max(0.1, self.scale_factor / 1.2)
        self._display_image()
    except Exception as e:
      self.logger.error(f"缩小失败: {str(e)}")

  def _fit_to_window(self):
    """适应窗口"""
    try:
      if not self.current_image:
        return

      canvas_width = self.canvas.winfo_width()
      canvas_height = self.canvas.winfo_height()

      if canvas_width <= 1 or canvas_height <= 1:
        return

      # 计算缩放比例
      width_ratio = canvas_width / self.current_image.width
      height_ratio = canvas_height / self.current_image.height
      self.scale_factor = min(width_ratio, height_ratio, 1.0)  # 不放大

      self._display_image()

    except Exception as e:
      self.logger.error(f"适应窗口失败: {str(e)}")

  def _actual_size(self):
    """实际大小"""
    try:
      if self.current_image:
        self.scale_factor = 1.0
        self._display_image()
    except Exception as e:
      self.logger.error(f"实际大小失败: {str(e)}")

  def _prev_image(self):
    """切换到上一张图片"""
    try:
      if self.on_image_switch:
        self.on_image_switch('prev')
    except Exception as e:
      self.logger.error(f"切换到上一张图片失败: {str(e)}")

  def _next_image(self):
    """切换到下一张图片"""
    try:
      if self.on_image_switch:
        self.on_image_switch('next')
    except Exception as e:
      self.logger.error(f"切换到下一张图片失败: {str(e)}")

  def update_navigation_buttons(self, has_prev: bool, has_next: bool):
    """
    更新导航按钮状态

    Args:
        has_prev: 是否有上一张图片
        has_next: 是否有下一张图片
    """
    try:
      self.prev_button.config(state=tk.NORMAL if has_prev else tk.DISABLED)
      self.next_button.config(state=tk.NORMAL if has_next else tk.DISABLED)
    except Exception as e:
      self.logger.error(f"更新导航按钮状态失败: {str(e)}")

  def _update_scale_label(self):
    """更新缩放标签"""
    try:
      percentage = int(self.scale_factor * 100)
      self.scale_label.config(text=f"{percentage}%")
    except Exception as e:
      self.logger.error(f"更新缩放标签失败: {str(e)}")

  def _update_info_label(self):
    """更新信息标签"""
    try:
      self.info_label.config(text=self.image_info)
    except Exception as e:
      self.logger.error(f"更新信息标签失败: {str(e)}")

  def _on_canvas_click(self, event):
    """画布点击事件"""
    try:
      self.drag_start_x = event.x
      self.drag_start_y = event.y
      self.is_dragging = False
    except Exception as e:
      self.logger.error(f"处理画布点击失败: {str(e)}")

  def _on_canvas_drag(self, event):
    """画布拖拽事件"""
    try:
      if not self.is_dragging:
        # 检查是否开始拖拽
        dx = abs(event.x - self.drag_start_x)
        dy = abs(event.y - self.drag_start_y)
        if dx > 3 or dy > 3:  # 阈值
          self.is_dragging = True

      if self.is_dragging and self.on_position_change:
        # 计算水印位置（简化版）
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # 转换为图像坐标
        if self.current_image and self.scale_factor > 0:
          img_x = int(canvas_x / self.scale_factor)
          img_y = int(canvas_y / self.scale_factor)

          # 限制在图像范围内
          img_x = max(0, min(img_x, self.current_image.width))
          img_y = max(0, min(img_y, self.current_image.height))

          self.on_position_change((img_x, img_y))

    except Exception as e:
      self.logger.error(f"处理画布拖拽失败: {str(e)}")

  def _on_canvas_release(self, event):
    """画布释放事件"""
    try:
      self.is_dragging = False
    except Exception as e:
      self.logger.error(f"处理画布释放失败: {str(e)}")

  def _on_mouse_wheel(self, event):
    """鼠标滚轮事件"""
    try:
      if self.current_image:
        if event.delta > 0:
          self._zoom_in()
        else:
          self._zoom_out()
    except Exception as e:
      self.logger.error(f"处理鼠标滚轮失败: {str(e)}")

  def _on_canvas_configure(self, event):
    """画布配置改变事件"""
    try:
      if not self.current_image:
        self._show_placeholder()
    except Exception as e:
      self.logger.error(f"处理画布配置改变失败: {str(e)}")
