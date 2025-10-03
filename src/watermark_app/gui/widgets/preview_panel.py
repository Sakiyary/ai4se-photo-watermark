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

    # 水印拖拽相关
    self.watermark_bounds = None  # 水印边界 (x, y, width, height)
    self.is_dragging_watermark = False  # 是否正在拖拽水印
    self.watermark_drag_offset = (0, 0)  # 拖拽偏移
    self.show_alignment_guides = False  # 是否显示对齐线
    self.alignment_lines = []  # 对齐线列表
    self.preview_image = None  # 保存预览图像引用

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

  def update_preview(self, image: Image.Image, image_info: str = "", watermark_bounds: Tuple[int, int, int, int] = None):
    """
    更新预览图像

    Args:
        image: PIL图像对象
        image_info: 图像信息字符串
        watermark_bounds: 水印边界 (x, y, width, height) 在原图坐标系中
    """
    try:
      self.current_image = image
      self.preview_image = image  # 保存引用
      self.image_info = image_info
      self.watermark_bounds = watermark_bounds

      if image:
        # 每次加载新图片时都自动适应窗口
        self._fit_to_window()
        self._update_info_label()
        # 绘制水印边界框(如果有)
        if watermark_bounds:
          self._draw_watermark_bounds()
      else:
        self.clear_preview()

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
      self.is_dragging_watermark = False

      # 检查是否点击了水印
      if self._is_point_in_watermark(event.x, event.y):
        self.is_dragging_watermark = True
        # 计算拖拽偏移（鼠标相对于水印左上角的偏移）
        if self.watermark_bounds:
          canvas_x = self.canvas.canvasx(event.x)
          canvas_y = self.canvas.canvasy(event.y)
          offset_x, offset_y = self._get_image_offset()
          watermark_canvas_x = offset_x + \
              self.watermark_bounds[0] * self.scale_factor
          watermark_canvas_y = offset_y + \
              self.watermark_bounds[1] * self.scale_factor
          self.watermark_drag_offset = (
              canvas_x - watermark_canvas_x,
              canvas_y - watermark_canvas_y
          )
        self.logger.info("开始拖拽水印")
    except Exception as e:
      self.logger.error(f"处理画布点击失败: {str(e)}")

  def _on_canvas_drag(self, event):
    """画布拖拽事件"""
    try:
      if self.is_dragging_watermark:
        # 拖拽水印
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # 获取图像偏移
        offset_x, offset_y = self._get_image_offset()

        # 计算水印新位置（考虑拖拽偏移和图像偏移）
        new_watermark_x = canvas_x - self.watermark_drag_offset[0] - offset_x
        new_watermark_y = canvas_y - self.watermark_drag_offset[1] - offset_y

        # 转换为图像坐标
        if self.current_image and self.scale_factor > 0:
          img_x = int(new_watermark_x / self.scale_factor)
          img_y = int(new_watermark_y / self.scale_factor)

          # 限制在图像范围内
          if self.watermark_bounds:
            watermark_width = self.watermark_bounds[2]
            watermark_height = self.watermark_bounds[3]
            img_x = max(
                0, min(img_x, self.current_image.width - watermark_width))
            img_y = max(
                0, min(img_y, self.current_image.height - watermark_height))
          else:
            img_x = max(0, min(img_x, self.current_image.width))
            img_y = max(0, min(img_y, self.current_image.height))

          # 绘制辅助对齐线
          self._draw_alignment_guides(img_x, img_y)

          # 通知位置改变
          if self.on_position_change:
            self.on_position_change((img_x, img_y))
      else:
        # 原有的画布拖拽逻辑（暂时保留）
        if not self.is_dragging:
          dx = abs(event.x - self.drag_start_x)
          dy = abs(event.y - self.drag_start_y)
          if dx > 3 or dy > 3:
            self.is_dragging = True

    except Exception as e:
      self.logger.error(f"处理画布拖拽失败: {str(e)}")

  def _on_canvas_release(self, event):
    """画布释放事件"""
    try:
      if self.is_dragging_watermark:
        self.logger.info("完成水印拖拽")
        # 清除对齐线
        self._clear_alignment_guides()

      self.is_dragging = False
      self.is_dragging_watermark = False
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
      # 窗口大小改变时重新显示图像
      if self.current_image:
        self._display_image()
    except Exception as e:
      self.logger.error(f"处理画布配置改变失败: {str(e)}")

  def _get_image_offset(self) -> Tuple[int, int]:
    """获取图像在画布上的偏移量（用于居中显示）"""
    try:
      if not self.display_image:
        return (0, 0)

      canvas_width = self.canvas.winfo_width()
      canvas_height = self.canvas.winfo_height()

      if canvas_width <= 1 or canvas_height <= 1:
        canvas_width = 800
        canvas_height = 600

      display_width = int(self.current_image.width * self.scale_factor)
      display_height = int(self.current_image.height * self.scale_factor)

      # 计算居中位置时的偏移
      offset_x = max(0, (canvas_width - display_width) // 2)
      offset_y = max(0, (canvas_height - display_height) // 2)

      return (offset_x, offset_y)
    except Exception as e:
      self.logger.error(f"获取图像偏移失败: {str(e)}")
      return (0, 0)

  def _is_point_in_watermark(self, x: int, y: int) -> bool:
    """检查点是否在水印范围内"""
    try:
      if not self.watermark_bounds or not self.scale_factor:
        return False

      canvas_x = self.canvas.canvasx(x)
      canvas_y = self.canvas.canvasy(y)

      # 获取图像偏移
      offset_x, offset_y = self._get_image_offset()

      # 水印在画布上的位置和大小（考虑图像偏移）
      wm_x = offset_x + self.watermark_bounds[0] * self.scale_factor
      wm_y = offset_y + self.watermark_bounds[1] * self.scale_factor
      wm_width = self.watermark_bounds[2] * self.scale_factor
      wm_height = self.watermark_bounds[3] * self.scale_factor

      # 检查点是否在矩形内
      return (wm_x <= canvas_x <= wm_x + wm_width and
              wm_y <= canvas_y <= wm_y + wm_height)
    except Exception as e:
      self.logger.error(f"检查水印点击失败: {str(e)}")
      return False

  def _draw_watermark_bounds(self):
    """绘制水印边界框"""
    try:
      if not self.watermark_bounds or not self.scale_factor:
        return

      # 删除旧的边界框
      self.canvas.delete('watermark_bounds')

      # 获取图像偏移
      offset_x, offset_y = self._get_image_offset()

      # 计算边界框在画布上的位置（考虑图像偏移）
      x = offset_x + self.watermark_bounds[0] * self.scale_factor
      y = offset_y + self.watermark_bounds[1] * self.scale_factor
      width = self.watermark_bounds[2] * self.scale_factor
      height = self.watermark_bounds[3] * self.scale_factor

      # 绘制虚线边界框
      self.canvas.create_rectangle(
          x, y, x + width, y + height,
          outline='blue',
          width=2,
          dash=(5, 3),
          tags='watermark_bounds'
      )

      # 绘制四个角的控制点
      corner_size = 8
      corners = [
          (x, y),  # 左上
          (x + width, y),  # 右上
          (x, y + height),  # 左下
          (x + width, y + height)  # 右下
      ]
      for cx, cy in corners:
        self.canvas.create_rectangle(
            cx - corner_size/2, cy - corner_size/2,
            cx + corner_size/2, cy + corner_size/2,
            fill='blue',
            outline='white',
            tags='watermark_bounds'
        )
    except Exception as e:
      self.logger.error(f"绘制水印边界失败: {str(e)}")

  def _draw_alignment_guides(self, img_x: int, img_y: int):
    """绘制辅助对齐线"""
    try:
      # 清除旧的对齐线
      self._clear_alignment_guides()

      if not self.current_image or not self.watermark_bounds:
        return

      img_width = self.current_image.width
      img_height = self.current_image.height
      wm_width = self.watermark_bounds[2]
      wm_height = self.watermark_bounds[3]

      # 水印中心点
      wm_center_x = img_x + wm_width // 2
      wm_center_y = img_y + wm_height // 2

      # 图像中心点
      img_center_x = img_width // 2
      img_center_y = img_height // 2

      # 对齐阈值（像素）
      threshold = 10

      # 获取图像偏移
      offset_x, offset_y = self._get_image_offset()

      # 检查水平居中对齐
      if abs(wm_center_x - img_center_x) < threshold:
        # 绘制垂直中心线
        x = offset_x + img_center_x * self.scale_factor
        self.canvas.create_line(
            x, offset_y, x, offset_y + img_height * self.scale_factor,
            fill='red',
            width=1,
            dash=(3, 3),
            tags='alignment_guide'
        )

      # 检查垂直居中对齐
      if abs(wm_center_y - img_center_y) < threshold:
        # 绘制水平中心线
        y = offset_y + img_center_y * self.scale_factor
        self.canvas.create_line(
            offset_x, y, offset_x + img_width * self.scale_factor, y,
            fill='red',
            width=1,
            dash=(3, 3),
            tags='alignment_guide'
        )

      # 检查左边缘对齐
      if abs(img_x) < threshold:
        x = offset_x
        self.canvas.create_line(
            x, offset_y, x, offset_y + img_height * self.scale_factor,
            fill='orange',
            width=1,
            dash=(3, 3),
            tags='alignment_guide'
        )

      # 检查右边缘对齐
      if abs(img_x + wm_width - img_width) < threshold:
        x = offset_x + img_width * self.scale_factor
        self.canvas.create_line(
            x, offset_y, x, offset_y + img_height * self.scale_factor,
            fill='orange',
            width=1,
            dash=(3, 3),
            tags='alignment_guide'
        )

      # 检查上边缘对齐
      if abs(img_y) < threshold:
        y = offset_y
        self.canvas.create_line(
            offset_x, y, offset_x + img_width * self.scale_factor, y,
            fill='orange',
            width=1,
            dash=(3, 3),
            tags='alignment_guide'
        )

      # 检查下边缘对齐
      if abs(img_y + wm_height - img_height) < threshold:
        y = offset_y + img_height * self.scale_factor
        self.canvas.create_line(
            offset_x, y, offset_x + img_width * self.scale_factor, y,
            fill='orange',
            width=1,
            dash=(3, 3),
            tags='alignment_guide'
        )

    except Exception as e:
      self.logger.error(f"绘制对齐线失败: {str(e)}")

  def _clear_alignment_guides(self):
    """清除对齐线"""
    try:
      self.canvas.delete('alignment_guide')
    except Exception as e:
      self.logger.error(f"清除对齐线失败: {str(e)}")
