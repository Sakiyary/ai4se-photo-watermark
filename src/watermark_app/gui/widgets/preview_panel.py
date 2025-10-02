"""
水印工具 - 预览面板组件

用于显示图片预览和水印效果
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from pathlib import Path


class PreviewPanel:
  """预览面板组件"""

  def __init__(self, parent):
    """初始化预览面板

    Args:
        parent: 父组件
    """
    self.parent = parent
    self.original_image = None
    self.preview_image = None
    self.photo = None
    self.canvas = None
    self.current_watermark = None

    self._setup_ui()

  def _setup_ui(self):
    """设置用户界面"""
    # 创建标题框架
    title_frame = ttk.Frame(self.parent)
    title_frame.pack(fill=tk.X, pady=(0, 5))

    title_label = ttk.Label(title_frame, text="预览", font=('Arial', 12, 'bold'))
    title_label.pack(side=tk.LEFT)

    # 创建工具栏
    toolbar_frame = ttk.Frame(title_frame)
    toolbar_frame.pack(side=tk.RIGHT)

    # 缩放级别显示
    self.zoom_label = ttk.Label(toolbar_frame, text="100%", width=6)
    self.zoom_label.pack(side=tk.LEFT, padx=2)

    # 缩放按钮
    self.zoom_in_btn = ttk.Button(
        toolbar_frame, text="放大", command=self._zoom_in, width=6)
    self.zoom_in_btn.pack(side=tk.LEFT, padx=2)

    self.zoom_out_btn = ttk.Button(
        toolbar_frame, text="缩小", command=self._zoom_out, width=6)
    self.zoom_out_btn.pack(side=tk.LEFT, padx=2)

    self.fit_btn = ttk.Button(toolbar_frame, text="适应",
                              command=self._fit_to_window, width=6)
    self.fit_btn.pack(side=tk.LEFT, padx=2)

    # 原始大小按钮
    self.actual_size_btn = ttk.Button(
        toolbar_frame, text="原始", command=self._actual_size, width=6)
    self.actual_size_btn.pack(side=tk.LEFT, padx=2)

    # 创建预览区域框架
    preview_frame = ttk.Frame(self.parent, relief='sunken', borderwidth=2)
    preview_frame.pack(fill=tk.BOTH, expand=True)

    # 创建画布和滚动条
    self.canvas = tk.Canvas(preview_frame, bg='white')

    h_scrollbar = ttk.Scrollbar(
        preview_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
    v_scrollbar = ttk.Scrollbar(
        preview_frame, orient=tk.VERTICAL, command=self.canvas.yview)

    self.canvas.configure(xscrollcommand=h_scrollbar.set,
                          yscrollcommand=v_scrollbar.set)

    # 布局
    self.canvas.grid(row=0, column=0, sticky='nsew')
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')

    # 配置网格权重
    preview_frame.grid_rowconfigure(0, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)

    # 缩放相关
    self.zoom_level = 1.0
    self.min_zoom = 0.1
    self.max_zoom = 5.0

    # 绑定事件
    self.canvas.bind('<Configure>', self._on_canvas_configure)
    self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)

    # 显示默认消息
    self._show_default_message()

  def _show_default_message(self):
    """显示默认消息"""
    self.canvas.delete("all")
    self.canvas.create_text(
        200, 150,
        text="请选择图片文件进行预览",
        font=('Arial', 14),
        fill='gray'
    )

  def load_image(self, image_path):
    """加载图片

    Args:
        image_path: 图片文件路径
    """
    try:
      # 加载图片
      self.original_image = Image.open(image_path)
      self.zoom_level = 1.0

      # 更新预览
      self._update_preview()

    except Exception as e:
      print(f"加载图片失败: {e}")
      self._show_error_message(f"无法加载图片: {Path(image_path).name}")

  def _show_error_message(self, message):
    """显示错误消息"""
    self.canvas.delete("all")
    self.canvas.create_text(
        200, 150,
        text=message,
        font=('Arial', 12),
        fill='red'
    )

  def update_watermark(self, watermark_config):
    """更新水印

    Args:
        watermark_config: 水印配置字典
    """
    self.current_watermark = watermark_config
    if self.original_image:
      self._update_preview()

  def _update_preview(self):
    """更新预览显示"""
    if not self.original_image:
      return

    try:
      # 复制原图
      image = self.original_image.copy()

      # 应用水印
      if self.current_watermark:
        image = self._apply_watermark(image, self.current_watermark)

      # 缩放图片
      if self.zoom_level != 1.0:
        new_width = int(image.width * self.zoom_level)
        new_height = int(image.height * self.zoom_level)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

      # 转换为PhotoImage
      self.photo = ImageTk.PhotoImage(image)

      # 更新画布
      self.canvas.delete("all")
      self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

      # 更新滚动区域
      self.canvas.configure(scrollregion=self.canvas.bbox("all"))

      # 更新缩放标签
      self._update_zoom_label()

    except Exception as e:
      print(f"更新预览失败: {e}")

  def _apply_watermark(self, image, config):
    """应用水印到图片

    Args:
        image: PIL图片对象
        config: 水印配置

    Returns:
        应用水印后的图片
    """
    try:
      # 创建可绘制的图片副本
      watermarked = image.copy()
      draw = ImageDraw.Draw(watermarked)

      # 获取水印文本
      text = config.get('text', 'Sample Watermark')
      if not text.strip():
        return watermarked

      # 字体设置
      font_size = config.get('font_size', 24)
      try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", font_size)
      except:
        # 使用默认字体
        font = ImageFont.load_default()

      # 获取文本尺寸
      bbox = draw.textbbox((0, 0), text, font=font)
      text_width = bbox[2] - bbox[0]
      text_height = bbox[3] - bbox[1]

      # 计算位置
      position = config.get('position', 'bottom-right')
      offset_x = config.get('offset_x', 10)
      offset_y = config.get('offset_y', 10)

      x, y = self._calculate_position(
          position, image.size, (text_width, text_height), offset_x, offset_y
      )

      # 颜色和透明度
      color = config.get('color', '#FFFFFF')
      opacity = config.get('opacity', 128)

      # 转换颜色
      if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        text_color = (r, g, b, opacity)
      else:
        text_color = (255, 255, 255, opacity)

      # 创建透明层用于绘制水印
      overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
      overlay_draw = ImageDraw.Draw(overlay)

      # 绘制文本
      overlay_draw.text((x, y), text, font=font, fill=text_color)

      # 合并图层
      watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay)
      watermarked = watermarked.convert('RGB')

      return watermarked

    except Exception as e:
      print(f"应用水印失败: {e}")
      return image

  def _calculate_position(self, position, image_size, text_size, offset_x, offset_y):
    """计算水印位置

    Args:
        position: 位置名称
        image_size: 图片尺寸 (width, height)
        text_size: 文本尺寸 (width, height)
        offset_x: X偏移
        offset_y: Y偏移

    Returns:
        (x, y) 坐标
    """
    img_w, img_h = image_size
    text_w, text_h = text_size

    position_map = {
        'top-left': (offset_x, offset_y),
        'top-center': ((img_w - text_w) // 2, offset_y),
        'top-right': (img_w - text_w - offset_x, offset_y),
        'left-center': (offset_x, (img_h - text_h) // 2),
        'center': ((img_w - text_w) // 2, (img_h - text_h) // 2),
        'right-center': (img_w - text_w - offset_x, (img_h - text_h) // 2),
        'bottom-left': (offset_x, img_h - text_h - offset_y),
        'bottom-center': ((img_w - text_w) // 2, img_h - text_h - offset_y),
        'bottom-right': (img_w - text_w - offset_x, img_h - text_h - offset_y),
    }

    return position_map.get(position, position_map['bottom-right'])

  def _zoom_in(self):
    """放大"""
    if self.zoom_level < self.max_zoom:
      self.zoom_level = min(self.zoom_level * 1.2, self.max_zoom)
      self._update_preview()

  def _zoom_out(self):
    """缩小"""
    if self.zoom_level > self.min_zoom:
      self.zoom_level = max(self.zoom_level / 1.2, self.min_zoom)
      self._update_preview()

  def _fit_to_window(self):
    """适应窗口大小"""
    if not self.original_image:
      return

    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()

    if canvas_width > 1 and canvas_height > 1:
      img_width = self.original_image.width
      img_height = self.original_image.height

      # 计算缩放比例，允许放大小图片以适应窗口
      zoom_x = canvas_width / img_width
      zoom_y = canvas_height / img_height

      # 选择较小的缩放比例以确保图片完全显示在窗口内
      self.zoom_level = min(zoom_x, zoom_y)
      # 限制最大缩放比例为5倍
      self.zoom_level = min(self.zoom_level, self.max_zoom)

      self._update_preview()

  def _actual_size(self):
    """显示原始大小"""
    self.zoom_level = 1.0
    self._update_preview()

  def _update_zoom_label(self):
    """更新缩放标签"""
    zoom_percent = int(self.zoom_level * 100)
    self.zoom_label.config(text=f"{zoom_percent}%")

  def _on_canvas_configure(self, event):
    """画布配置变更事件"""
    pass

  def _on_mouse_wheel(self, event):
    """鼠标滚轮事件"""
    if event.delta > 0:
      self._zoom_in()
    else:
      self._zoom_out()

  def clear(self):
    """清除预览"""
    self.original_image = None
    self.preview_image = None
    self.photo = None
    self.current_watermark = None
    self._show_default_message()

  def cleanup(self):
    """清理资源"""
    self.clear()
