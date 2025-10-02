"""
水印工具 - 水印设置面板组件 (增强版)

用于配置水印的各种属性（文本、字体、颜色、位置等），支持模板、预设、实时预览
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
from pathlib import Path
import json
import os


class WatermarkPanel:
  """水印设置面板组件 (增强版)"""

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

    # 增强功能变量
    self.rotation_var = tk.IntVar(value=0)  # 旋转角度
    self.shadow_var = tk.BooleanVar(value=False)  # 阴影效果
    self.outline_var = tk.BooleanVar(value=False)  # 描边效果
    self.outline_color_var = tk.StringVar(value="#000000")  # 描边颜色
    self.outline_width_var = tk.IntVar(value=1)  # 描边宽度

    # 模板相关
    self.templates_dir = Path("templates")
    self.templates_dir.mkdir(exist_ok=True)
    self.current_template = None

    self._setup_ui()
    self._bind_events()
    self._load_preset_templates()

  def _setup_ui(self):
    """设置用户界面 (优化布局版)"""
    # 主容器，使用两列布局
    main_frame = ttk.Frame(self.parent)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 创建两列布局
    left_column = ttk.Frame(main_frame)
    left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    right_column = ttk.Frame(main_frame)
    right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

    # 模板选择（跨列）
    template_select_frame = ttk.LabelFrame(main_frame, text="快速模板", padding=5)
    template_select_frame.pack(fill=tk.X, pady=(0, 10))

    template_content = ttk.Frame(template_select_frame)
    template_content.pack(fill=tk.X)

    self.template_var = tk.StringVar()
    self.template_combo = ttk.Combobox(
        template_content,
        textvariable=self.template_var,
        state="readonly",
        width=15
    )
    self.template_combo.pack(side=tk.LEFT, padx=(0, 5))
    self.template_combo.bind('<<ComboboxSelected>>', self._on_template_selected)

    ttk.Button(
        template_content,
        text="应用",
        command=self._apply_template,
        width=6
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        template_content,
        text="保存",
        command=self._save_template,
        width=6
    ).pack(side=tk.LEFT, padx=2)

    ttk.Button(
        template_content,
        text="重置",
        command=self.reset_to_defaults,
        width=6
    ).pack(side=tk.RIGHT)    # 左列：文本设置
    text_frame = ttk.LabelFrame(left_column, text="文本设置", padding=5)
    text_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(text_frame, text="水印文本:").pack(anchor=tk.W)

    text_input_frame = ttk.Frame(text_frame)
    text_input_frame.pack(fill=tk.X, pady=(2, 0))

    self.text_entry = ttk.Entry(text_input_frame, textvariable=self.text_var)
    self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # 快速文本按钮
    quick_text_btn = ttk.Button(
        text_input_frame, text="📝", width=3,
        command=self._show_quick_text_menu
    )
    quick_text_btn.pack(side=tk.RIGHT, padx=(5, 0))    # 左列：字体设置
    font_frame = ttk.LabelFrame(left_column, text="字体设置", padding=5)
    font_frame.pack(fill=tk.X, pady=(0, 10))

    # 字体大小
    size_frame = ttk.Frame(font_frame)
    size_frame.pack(fill=tk.X, pady=(0, 5))

    ttk.Label(size_frame, text="大小:").pack(side=tk.LEFT)
    self.size_scale = ttk.Scale(
        size_frame,
        from_=8,
        to=128,
        variable=self.font_size_var,
        orient=tk.HORIZONTAL
    )
    self.size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

    self.size_label = ttk.Label(size_frame, text="24", width=4)
    self.size_label.pack(side=tk.RIGHT)

    # 旋转角度
    rotation_frame = ttk.Frame(font_frame)
    rotation_frame.pack(fill=tk.X)

    ttk.Label(rotation_frame, text="旋转:").pack(side=tk.LEFT)
    self.rotation_scale = ttk.Scale(
        rotation_frame,
        from_=-180,
        to=180,
        variable=self.rotation_var,
        orient=tk.HORIZONTAL
    )
    self.rotation_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

    self.rotation_label = ttk.Label(rotation_frame, text="0°", width=5)
    self.rotation_label.pack(side=tk.RIGHT)    # 右列：颜色设置
    color_frame = ttk.LabelFrame(right_column, text="颜色设置", padding=5)
    color_frame.pack(fill=tk.X, pady=(0, 10))

    # 主颜色
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

    # 快速颜色选择
    quick_colors = ["#FFFFFF", "#000000", "#FF0000",
                    "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
    color_preset_frame = ttk.Frame(color_frame)
    color_preset_frame.pack(fill=tk.X, pady=2)

    ttk.Label(color_preset_frame, text="快速选择:").pack(side=tk.LEFT)
    for color in quick_colors:
      btn = tk.Button(
          color_preset_frame,
          bg=color,
          width=2,
          height=1,
          command=lambda c=color: self._set_quick_color(c)
      )
      btn.pack(side=tk.LEFT, padx=1)

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

    # 效果设置 (新增)
    effects_frame = ttk.LabelFrame(main_frame, text="效果设置", padding=5)
    effects_frame.pack(fill=tk.X, pady=5)

    # 阴影效果
    shadow_frame = ttk.Frame(effects_frame)
    shadow_frame.pack(fill=tk.X, pady=2)

    self.shadow_check = ttk.Checkbutton(
        shadow_frame, text="阴影效果", variable=self.shadow_var
    )
    self.shadow_check.pack(side=tk.LEFT)

    # 描边效果
    outline_frame = ttk.Frame(effects_frame)
    outline_frame.pack(fill=tk.X, pady=2)

    self.outline_check = ttk.Checkbutton(
        outline_frame, text="描边效果", variable=self.outline_var
    )
    self.outline_check.pack(side=tk.LEFT)

    # 描边设置
    outline_settings_frame = ttk.Frame(effects_frame)
    outline_settings_frame.pack(fill=tk.X, pady=2)

    ttk.Label(outline_settings_frame, text="描边颜色:").pack(side=tk.LEFT)

    self.outline_color_button = tk.Button(
        outline_settings_frame,
        text="   ",
        bg="#000000",
        width=3,
        command=self._choose_outline_color
    )
    self.outline_color_button.pack(side=tk.LEFT, padx=(5, 0))

    ttk.Label(outline_settings_frame, text="宽度:").pack(
        side=tk.LEFT, padx=(10, 0))
    self.outline_width_spinbox = ttk.Spinbox(
        outline_settings_frame,
        from_=1,
        to=10,
        textvariable=self.outline_width_var,
        width=5
    )
    self.outline_width_spinbox.pack(side=tk.LEFT, padx=(5, 0))

    # 右列：位置设置
    position_frame = ttk.LabelFrame(right_column, text="位置设置", padding=5)
    position_frame.pack(fill=tk.X, pady=(0, 10))

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

    # 新增变量的事件绑定
    self.rotation_var.trace_add('write', self._on_change)
    self.shadow_var.trace_add('write', self._on_change)
    self.outline_var.trace_add('write', self._on_change)
    self.outline_color_var.trace_add('write', self._on_change)
    self.outline_width_var.trace_add('write', self._on_change)

    # 绑定滑块变更事件更新标签
    self.font_size_var.trace_add('write', self._update_size_label)
    self.opacity_var.trace_add('write', self._update_opacity_label)
    self.rotation_var.trace_add('write', self._update_rotation_label)

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

  def _update_rotation_label(self, *args):
    """更新旋转角度标签"""
    self.rotation_label.config(text=f"{self.rotation_var.get()}°")

  def _choose_color(self):
    """选择颜色"""
    color = colorchooser.askcolor(
        color=self.color_var.get(),
        title="选择水印颜色"
    )

    if color[1]:  # 用户选择了颜色
      hex_color = color[1]
      self._set_quick_color(hex_color)

  def _set_quick_color(self, color):
    """设置快速颜色"""
    self.color_var.set(color)
    self.color_button.config(bg=color)
    self.color_label.config(text=color)

  def _choose_outline_color(self):
    """选择描边颜色"""
    color = colorchooser.askcolor(
        color=self.outline_color_var.get(),
        title="选择描边颜色"
    )

    if color[1]:  # 用户选择了颜色
      hex_color = color[1]
      self.outline_color_var.set(hex_color)
      self.outline_color_button.config(bg=hex_color)

  def _show_quick_text_menu(self):
    """显示快速文本菜单"""
    menu = tk.Menu(self.parent, tearoff=0)

    # 预设文本选项
    quick_texts = [
        "版权所有 © 2024",
        "保密文件",
        "样本",
        "草稿",
        "机密",
        "内部使用",
        "未经授权禁止复制"
    ]

    for text in quick_texts:
      menu.add_command(
          label=text,
          command=lambda t=text: self.text_var.set(t)
      )

    menu.add_separator()
    menu.add_command(label="清空", command=lambda: self.text_var.set(""))

    # 显示菜单
    try:
      menu.post(self.text_entry.winfo_rootx(),
                self.text_entry.winfo_rooty() + 25)
    finally:
      menu.grab_release()

  def _load_preset_templates(self):
    """加载预设模板"""
    # 创建预设模板
    presets = {
        "版权水印": {
            "text": "© 2024 版权所有",
            "font_size": 20,
            "color": "#FFFFFF",
            "opacity": 180,
            "position": "bottom-right",
            "rotation": 0,
            "shadow": True,
            "outline": False
        },
        "机密文档": {
            "text": "机密文档",
            "font_size": 48,
            "color": "#FF0000",
            "opacity": 100,
            "position": "center",
            "rotation": -45,
            "shadow": False,
            "outline": True,
            "outline_color": "#000000"
        },
        "草稿水印": {
            "text": "DRAFT",
            "font_size": 64,
            "color": "#808080",
            "opacity": 80,
            "position": "center",
            "rotation": -30,
            "shadow": False,
            "outline": False
        },
        "品牌标识": {
            "text": "Your Brand",
            "font_size": 32,
            "color": "#0066CC",
            "opacity": 200,
            "position": "top-right",
            "rotation": 0,
            "shadow": True,
            "outline": False
        }
    }

    # 保存预设模板到文件
    for name, config in presets.items():
      template_file = self.templates_dir / f"{name}.json"
      if not template_file.exists():
        try:
          with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
          print(f"保存预设模板失败: {e}")

    # 更新模板列表
    self._refresh_template_list()

  def _refresh_template_list(self):
    """刷新模板列表"""
    templates = []

    # 加载所有模板文件
    if self.templates_dir.exists():
      for template_file in self.templates_dir.glob("*.json"):
        templates.append(template_file.stem)

    self.template_combo['values'] = templates

  def _on_template_selected(self, event):
    """模板选择事件"""
    pass  # 用户选择了模板，但需要点击应用按钮才生效

  def _apply_template(self):
    """应用选中的模板"""
    template_name = self.template_var.get()
    if not template_name:
      return

    template_file = self.templates_dir / f"{template_name}.json"

    try:
      with open(template_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

      self.set_config(config)
      self.current_template = template_name
      messagebox.showinfo("模板", f"已应用模板: {template_name}")

    except Exception as e:
      messagebox.showerror("错误", f"加载模板失败: {e}")

  def _save_template(self):
    """保存模板"""
    # 弹出对话框获取模板名称
    from tkinter.simpledialog import askstring

    template_name = askstring("保存模板", "请输入模板名称:")
    if not template_name:
      return

    # 获取当前配置
    config = self.get_config()
    template_file = self.templates_dir / f"{template_name}.json"

    try:
      with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

      self._refresh_template_list()
      messagebox.showinfo("模板", f"模板 '{template_name}' 保存成功！")

    except Exception as e:
      messagebox.showerror("错误", f"保存模板失败: {e}")

  def _load_template(self):
    """加载模板"""
    template_file = filedialog.askopenfilename(
        title="选择模板文件",
        initialdir=self.templates_dir,
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
    )

    if template_file:
      try:
        with open(template_file, 'r', encoding='utf-8') as f:
          config = json.load(f)

        self.set_config(config)
        messagebox.showinfo("模板", "模板加载成功！")

      except Exception as e:
        messagebox.showerror("错误", f"加载模板失败: {e}")

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
        'rotation': self.rotation_var.get(),
        'shadow': self.shadow_var.get(),
        'outline': self.outline_var.get(),
        'outline_color': self.outline_color_var.get(),
        'outline_width': self.outline_width_var.get(),
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
    if 'rotation' in config:
      self.rotation_var.set(config['rotation'])
    if 'shadow' in config:
      self.shadow_var.set(config['shadow'])
    if 'outline' in config:
      self.outline_var.set(config['outline'])
    if 'outline_color' in config:
      color = config['outline_color']
      self.outline_color_var.set(color)
      self.outline_color_button.config(bg=color)
    if 'outline_width' in config:
      self.outline_width_var.set(config['outline_width'])

  def reset_to_defaults(self):
    """重置为默认值"""
    self.text_var.set("Sample Watermark")
    self.font_size_var.set(24)
    self.color_var.set("#FFFFFF")
    self.opacity_var.set(128)
    self.position_var.set("bottom-right")
    self.offset_x_var.set(10)
    self.offset_y_var.set(10)
    self.rotation_var.set(0)
    self.shadow_var.set(False)
    self.outline_var.set(False)
    self.outline_color_var.set("#000000")
    self.outline_width_var.set(1)

    # 更新颜色按钮
    self.color_button.config(bg="#FFFFFF")
    self.color_label.config(text="#FFFFFF")
    self.outline_color_button.config(bg="#000000")

    # 清除模板选择
    self.template_var.set("")
    self.current_template = None

  def export_config(self):
    """导出当前配置"""
    config = self.get_config()

    file_path = filedialog.asksaveasfilename(
        title="导出水印配置",
        defaultextension=".json",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
    )

    if file_path:
      try:
        with open(file_path, 'w', encoding='utf-8') as f:
          json.dump(config, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("导出", "配置导出成功！")
      except Exception as e:
        messagebox.showerror("错误", f"导出配置失败: {e}")

  def import_config(self):
    """导入配置"""
    file_path = filedialog.askopenfilename(
        title="导入水印配置",
        filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
    )

    if file_path:
      try:
        with open(file_path, 'r', encoding='utf-8') as f:
          config = json.load(f)

        self.set_config(config)
        messagebox.showinfo("导入", "配置导入成功！")
      except Exception as e:
        messagebox.showerror("错误", f"导入配置失败: {e}")

  def get_template_names(self):
    """获取所有模板名称列表"""
    templates = []
    if self.templates_dir.exists():
      for template_file in self.templates_dir.glob("*.json"):
        templates.append(template_file.stem)
    return templates
