"""
水印工具 - 水印设置面板组件

用于配置水印的各种属性（文本、字体、颜色、位置等）
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from pathlib import Path


class WatermarkPanel:
  """水印设置面板组件"""

  def __init__(self, parent, change_callback=None):
    """初始化水印设置面板

    Args:
        parent: 父组件
        change_callback: 设置变更回调函数
    """
    self.parent = parent
    self.change_callback = change_callback

    # 控件变量
    self.text_var = tk.StringVar(value="Sample Watermark")
    self.font_size_var = tk.IntVar(value=24)
    self.color_var = tk.StringVar(value="#FFFFFF")
    self.opacity_var = tk.IntVar(value=128)
    self.position_var = tk.StringVar(value="bottom-right")
    self.offset_x_var = tk.IntVar(value=10)
    self.offset_y_var = tk.IntVar(value=10)

    self._setup_ui()
    self._bind_events()

  def _setup_ui(self):
    """设置用户界面"""
    # 创建滚动框架
    canvas = tk.Canvas(self.parent)
    scrollbar = ttk.Scrollbar(
        self.parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 布局
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 使用滚动框架作为主容器
    main_frame = scrollable_frame

    # 文本设置
    text_frame = ttk.LabelFrame(main_frame, text="文本设置", padding=5)
    text_frame.pack(fill=tk.X, pady=5)

    ttk.Label(text_frame, text="水印文本:").pack(anchor=tk.W)
    self.text_entry = ttk.Entry(text_frame, textvariable=self.text_var)
    self.text_entry.pack(fill=tk.X, pady=2)

    # 字体设置
    font_frame = ttk.LabelFrame(main_frame, text="字体设置", padding=5)
    font_frame.pack(fill=tk.X, pady=5)

    # 字体大小
    size_frame = ttk.Frame(font_frame)
    size_frame.pack(fill=tk.X, pady=2)

    ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
    self.size_scale = ttk.Scale(
        size_frame,
        from_=8,
        to=128,
        variable=self.font_size_var,
        orient=tk.HORIZONTAL
    )
    self.size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    self.size_label = ttk.Label(size_frame, text="24", width=4)
    self.size_label.pack(side=tk.RIGHT, padx=(5, 0))

    # 颜色设置
    color_frame = ttk.LabelFrame(main_frame, text="颜色设置", padding=5)
    color_frame.pack(fill=tk.X, pady=5)

    color_select_frame = ttk.Frame(color_frame)
    color_select_frame.pack(fill=tk.X, pady=2)

    ttk.Label(color_select_frame, text="文本颜色:").pack(side=tk.LEFT)

    self.color_button = tk.Button(
        color_select_frame,
        text="   ",
        bg="#FFFFFF",
        width=4,
        command=self._choose_color
    )
    self.color_button.pack(side=tk.LEFT, padx=(5, 0))

    self.color_label = ttk.Label(color_select_frame, text="#FFFFFF")
    self.color_label.pack(side=tk.LEFT, padx=(5, 0))

    # 透明度
    opacity_frame = ttk.Frame(color_frame)
    opacity_frame.pack(fill=tk.X, pady=2)

    ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
    self.opacity_scale = ttk.Scale(
        opacity_frame,
        from_=0,
        to=255,
        variable=self.opacity_var,
        orient=tk.HORIZONTAL
    )
    self.opacity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    self.opacity_label = ttk.Label(opacity_frame, text="128", width=4)
    self.opacity_label.pack(side=tk.RIGHT, padx=(5, 0))

    # 位置设置
    position_frame = ttk.LabelFrame(main_frame, text="位置设置", padding=5)
    position_frame.pack(fill=tk.X, pady=5)

    ttk.Label(position_frame, text="预设位置:").pack(anchor=tk.W)

    # 位置选择网格
    pos_grid = ttk.Frame(position_frame)
    pos_grid.pack(fill=tk.X, pady=5)

    positions = [
        ["top-left", "top-center", "top-right"],
        ["left-center", "center", "right-center"],
        ["bottom-left", "bottom-center", "bottom-right"]
    ]

    position_names = {
        "top-left": "左上", "top-center": "上中", "top-right": "右上",
        "left-center": "左中", "center": "正中", "right-center": "右中",
        "bottom-left": "左下", "bottom-center": "下中", "bottom-right": "右下"
    }

    self.position_buttons = {}
    for i, row in enumerate(positions):
      row_frame = ttk.Frame(pos_grid)
      row_frame.pack(fill=tk.X, pady=1)

      for j, pos in enumerate(row):
        btn = ttk.Radiobutton(
            row_frame,
            text=position_names[pos],
            value=pos,
            variable=self.position_var,
            width=8
        )
        btn.pack(side=tk.LEFT, padx=2)
        self.position_buttons[pos] = btn

    # 偏移设置
    offset_frame = ttk.Frame(position_frame)
    offset_frame.pack(fill=tk.X, pady=5)

    # X偏移
    x_frame = ttk.Frame(offset_frame)
    x_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    ttk.Label(x_frame, text="X偏移:").pack(anchor=tk.W)
    self.offset_x_spinbox = ttk.Spinbox(
        x_frame,
        from_=0,
        to=200,
        textvariable=self.offset_x_var,
        width=8
    )
    self.offset_x_spinbox.pack(anchor=tk.W)

    # Y偏移
    y_frame = ttk.Frame(offset_frame)
    y_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

    ttk.Label(y_frame, text="Y偏移:").pack(anchor=tk.W)
    self.offset_y_spinbox = ttk.Spinbox(
        y_frame,
        from_=0,
        to=200,
        textvariable=self.offset_y_var,
        width=8
    )
    self.offset_y_spinbox.pack(anchor=tk.W)

    # 模板操作
    template_frame = ttk.LabelFrame(main_frame, text="模板操作", padding=5)
    template_frame.pack(fill=tk.X, pady=5)

    template_btn_frame = ttk.Frame(template_frame)
    template_btn_frame.pack(fill=tk.X)

    self.save_template_btn = ttk.Button(
        template_btn_frame,
        text="保存模板",
        command=self._save_template
    )
    self.save_template_btn.pack(side=tk.LEFT, padx=(0, 5))

    self.load_template_btn = ttk.Button(
        template_btn_frame,
        text="加载模板",
        command=self._load_template
    )
    self.load_template_btn.pack(side=tk.LEFT)

  def _bind_events(self):
    """绑定事件"""
    # 绑定所有变量的变更事件
    self.text_var.trace_add('write', self._on_change)
    self.font_size_var.trace_add('write', self._on_change)
    self.color_var.trace_add('write', self._on_change)
    self.opacity_var.trace_add('write', self._on_change)
    self.position_var.trace_add('write', self._on_change)
    self.offset_x_var.trace_add('write', self._on_change)
    self.offset_y_var.trace_add('write', self._on_change)

    # 绑定滑块变更事件更新标签
    self.font_size_var.trace_add('write', self._update_size_label)
    self.opacity_var.trace_add('write', self._update_opacity_label)

  def _on_change(self, *args):
    """设置变更事件处理"""
    if self.change_callback:
      config = self.get_config()
      self.change_callback(config)

  def _update_size_label(self, *args):
    """更新字体大小标签"""
    self.size_label.config(text=str(self.font_size_var.get()))

  def _update_opacity_label(self, *args):
    """更新透明度标签"""
    self.opacity_label.config(text=str(self.opacity_var.get()))

  def _choose_color(self):
    """选择颜色"""
    color = colorchooser.askcolor(
        color=self.color_var.get(),
        title="选择水印颜色"
    )

    if color[1]:  # 用户选择了颜色
      hex_color = color[1]
      self.color_var.set(hex_color)
      self.color_button.config(bg=hex_color)
      self.color_label.config(text=hex_color)

  def _save_template(self):
    """保存模板"""
    # TODO: 实现模板保存功能
    tk.messagebox.showinfo("模板", "模板保存功能即将推出...")

  def _load_template(self):
    """加载模板"""
    # TODO: 实现模板加载功能
    tk.messagebox.showinfo("模板", "模板加载功能即将推出...")

  def get_config(self):
    """获取当前水印配置

    Returns:
        dict: 水印配置字典
    """
    return {
        'text': self.text_var.get(),
        'font_size': self.font_size_var.get(),
        'color': self.color_var.get(),
        'opacity': self.opacity_var.get(),
        'position': self.position_var.get(),
        'offset_x': self.offset_x_var.get(),
        'offset_y': self.offset_y_var.get(),
    }

  def set_config(self, config):
    """设置水印配置

    Args:
        config: 水印配置字典
    """
    if 'text' in config:
      self.text_var.set(config['text'])
    if 'font_size' in config:
      self.font_size_var.set(config['font_size'])
    if 'color' in config:
      color = config['color']
      self.color_var.set(color)
      self.color_button.config(bg=color)
      self.color_label.config(text=color)
    if 'opacity' in config:
      self.opacity_var.set(config['opacity'])
    if 'position' in config:
      self.position_var.set(config['position'])
    if 'offset_x' in config:
      self.offset_x_var.set(config['offset_x'])
    if 'offset_y' in config:
      self.offset_y_var.set(config['offset_y'])

  def reset_to_defaults(self):
    """重置为默认值"""
    self.text_var.set("Sample Watermark")
    self.font_size_var.set(24)
    self.color_var.set("#FFFFFF")
    self.opacity_var.set(128)
    self.position_var.set("bottom-right")
    self.offset_x_var.set(10)
    self.offset_y_var.set(10)

    # 更新颜色按钮
    self.color_button.config(bg="#FFFFFF")
    self.color_label.config(text="#FFFFFF")
