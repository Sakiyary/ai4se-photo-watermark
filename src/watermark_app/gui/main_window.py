"""
水印工具 - 主窗口

应用程序的主要用户界面，包含文件列表、预览区域、水印设置等组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from PIL import Image, ImageDraw, ImageFont

from .widgets.file_list import FileListWidget
from .widgets.preview_panel import PreviewPanel
from .widgets.watermark_panel import WatermarkPanel
from .widgets.export_dialog import ExportDialog


class MainWindow:
  """主窗口类"""

  def __init__(self, root, settings):
    """初始化主窗口

    Args:
        root: Tkinter根窗口
        settings: 应用程序设置对象
    """
    self.root = root
    self.settings = settings

    # 窗口组件
    self.file_list = None
    self.preview_panel = None
    self.watermark_panel = None

    # 数据
    self.current_images = []
    self.current_image_index = 0

    # 初始化界面
    self._setup_ui()
    self._setup_bindings()

  def _setup_ui(self):
    """设置用户界面布局"""
    # 创建主框架
    main_frame = ttk.Frame(self.root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 创建水平分割的PanedWindow
    h_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
    h_paned.pack(fill=tk.BOTH, expand=True)

    # 左侧面板 - 文件列表和水印设置
    left_frame = ttk.Frame(h_paned, width=350)
    h_paned.add(left_frame, weight=1)

    # 右侧面板 - 预览区域和导出设置
    right_frame = ttk.Frame(h_paned)
    h_paned.add(right_frame, weight=2)

    # 创建右侧的垂直布局
    right_main_frame = ttk.Frame(right_frame)
    right_main_frame.pack(fill=tk.BOTH, expand=True)

    # 预览区域（上部）
    preview_container = ttk.Frame(right_main_frame)
    preview_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    # 导出设置区域（下部）
    export_frame = ttk.LabelFrame(right_main_frame, text="导出设置", padding=5)
    export_frame.pack(fill=tk.X, side=tk.BOTTOM)

    # 创建左侧垂直分割
    v_paned = ttk.PanedWindow(left_frame, orient=tk.VERTICAL)
    v_paned.pack(fill=tk.BOTH, expand=True)

    # 文件列表区域
    file_frame = ttk.LabelFrame(v_paned, text="图片文件", padding=5)
    v_paned.add(file_frame, weight=1)

    # 水印设置区域
    watermark_frame = ttk.LabelFrame(v_paned, text="水印设置", padding=5)
    v_paned.add(watermark_frame, weight=1)

    # 创建组件
    self.file_list = FileListWidget(file_frame, self._on_image_selected)
    self.preview_panel = PreviewPanel(preview_container)
    self.watermark_panel = WatermarkPanel(
        watermark_frame, self._on_watermark_changed)

    # 创建导出设置组件
    self._setup_export_panel(export_frame)

    # 连接文件列表的按钮事件
    self.file_list.add_files_btn.config(command=self._add_images)
    self.file_list.add_folder_btn.config(command=self._add_folder)

    # 创建菜单栏
    self._create_menu()

    # 创建状态栏
    self._create_status_bar()

  def _create_menu(self):
    """创建菜单栏"""
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)

    # 文件菜单
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="文件", menu=file_menu)
    file_menu.add_command(
        label="添加图片...", command=self._add_images, accelerator="Ctrl+O")
    file_menu.add_command(
        label="添加文件夹...", command=self._add_folder, accelerator="Ctrl+Shift+O")
    file_menu.add_separator()
    file_menu.add_command(
        label="导出图片...", command=self._export_images, accelerator="Ctrl+E")
    file_menu.add_separator()
    file_menu.add_command(
        label="退出", command=self.root.quit, accelerator="Ctrl+Q")

    # 编辑菜单
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="编辑", menu=edit_menu)
    edit_menu.add_command(label="清除所有图片", command=self._clear_images)
    edit_menu.add_separator()
    edit_menu.add_command(label="设置...", command=self._show_settings)

    # 帮助菜单
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="帮助", menu=help_menu)
    help_menu.add_command(label="使用说明", command=self._show_help)
    help_menu.add_command(label="关于", command=self._show_about)

  def _setup_export_panel(self, parent):
    """设置导出面板"""
    # 创建两列布局
    export_content = ttk.Frame(parent)
    export_content.pack(fill=tk.X)

    # 左侧：导出设置
    left_export = ttk.Frame(export_content)
    left_export.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    # 输出格式设置
    format_frame = ttk.Frame(left_export)
    format_frame.pack(fill=tk.X, pady=(0, 5))

    ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
    self.export_format_var = tk.StringVar(value="original")
    format_combo = ttk.Combobox(format_frame, textvariable=self.export_format_var,
                                values=["original", "jpeg", "png"], width=10, state="readonly")
    format_combo.pack(side=tk.LEFT, padx=(5, 0))

    # 质量设置
    quality_frame = ttk.Frame(left_export)
    quality_frame.pack(fill=tk.X, pady=(0, 5))

    ttk.Label(quality_frame, text="JPEG质量:").pack(side=tk.LEFT)
    self.jpeg_quality_var = tk.IntVar(value=95)
    quality_scale = ttk.Scale(quality_frame, from_=60, to=100,
                              variable=self.jpeg_quality_var, orient=tk.HORIZONTAL, length=100)
    quality_scale.pack(side=tk.LEFT, padx=(5, 5))

    self.quality_label = ttk.Label(quality_frame, text="95")
    self.quality_label.pack(side=tk.LEFT)

    # 文件命名设置
    naming_frame = ttk.Frame(left_export)
    naming_frame.pack(fill=tk.X)

    ttk.Label(naming_frame, text="文件名:").pack(side=tk.LEFT)
    self.naming_var = tk.StringVar(value="suffix")
    naming_combo = ttk.Combobox(naming_frame, textvariable=self.naming_var,
                                values=["original", "prefix", "suffix"], width=10, state="readonly")
    naming_combo.pack(side=tk.LEFT, padx=(5, 5))

    self.naming_text_var = tk.StringVar(value="_watermarked")
    naming_entry = ttk.Entry(
        naming_frame, textvariable=self.naming_text_var, width=12)
    naming_entry.pack(side=tk.LEFT)

    # 右侧：导出按钮
    right_export = ttk.Frame(export_content)
    right_export.pack(side=tk.RIGHT)

    self.export_btn = ttk.Button(right_export, text="导出图片",
                                 command=self._export_images, width=12)
    self.export_btn.pack(pady=10)

    # 绑定事件
    self.jpeg_quality_var.trace_add('write', self._update_quality_label)

  def _update_quality_label(self, *args):
    """更新质量标签"""
    self.quality_label.config(text=str(self.jpeg_quality_var.get()))

  def _start_export_process(self, image_files, watermark_config, export_config):
    """开始导出处理"""
    # 创建进度对话框
    progress_dialog = tk.Toplevel(self.root)
    progress_dialog.title("导出进度")
    progress_dialog.geometry("400x150")
    progress_dialog.resizable(False, False)
    progress_dialog.transient(self.root)
    progress_dialog.grab_set()

    # 居中显示
    progress_dialog.update_idletasks()
    x = (progress_dialog.winfo_screenwidth() // 2) - \
        (progress_dialog.winfo_width() // 2)
    y = (progress_dialog.winfo_screenheight() // 2) - \
        (progress_dialog.winfo_height() // 2)
    progress_dialog.geometry(f"+{x}+{y}")

    # 进度界面
    main_frame = ttk.Frame(progress_dialog, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    status_label = ttk.Label(main_frame, text=f"准备处理 {len(image_files)} 个文件...")
    status_label.pack(pady=(0, 10))

    progress = ttk.Progressbar(
        main_frame, mode='determinate', maximum=len(image_files))
    progress.pack(fill=tk.X, pady=(0, 10))

    # 取消按钮
    cancel_var = tk.BooleanVar()
    cancel_btn = ttk.Button(main_frame, text="取消",
                            command=lambda: cancel_var.set(True))
    cancel_btn.pack()

    # 在后台线程中处理
    def process_export():
      try:
        processed = 0
        errors = []

        for i, image_file in enumerate(image_files):
          if cancel_var.get():
            break

          try:
            # 更新状态
            progress_dialog.after(0, lambda f=Path(image_file).name:
                                  status_label.config(text=f"正在处理: {f}"))

            # 处理单个图片
            self._process_single_image(
                image_file, watermark_config, export_config)
            processed += 1

            # 更新进度
            progress_dialog.after(
                0, lambda p=processed: progress.config(value=p))

          except Exception as e:
            errors.append(f"{Path(image_file).name}: {str(e)}")

        # 处理完成
        if cancel_var.get():
          progress_dialog.after(0, lambda: status_label.config(text="已取消"))
        else:
          success_msg = f"处理完成！成功: {processed}, 失败: {len(errors)}"
          progress_dialog.after(
              0, lambda: status_label.config(text=success_msg))

          if errors:
            error_msg = "以下文件处理失败:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
              error_msg += f"\n... 还有 {len(errors) - 10} 个错误"
            progress_dialog.after(
                0, lambda: messagebox.showwarning("处理警告", error_msg))

          # 3秒后自动关闭
          progress_dialog.after(3000, progress_dialog.destroy)

      except Exception as e:
        progress_dialog.after(
            0, lambda: messagebox.showerror("错误", f"导出失败: {e}"))
        progress_dialog.after(0, progress_dialog.destroy)

    # 启动后台线程
    threading.Thread(target=process_export, daemon=True).start()

  def _process_single_image(self, image_file, watermark_config, export_config):
    """处理单个图片"""
    from PIL import Image, ImageDraw, ImageFont

    # 打开图片
    with Image.open(image_file) as image:
      # 应用水印
      watermarked = self._apply_watermark_to_image(image, watermark_config)

      # 生成输出文件名
      output_file = self._generate_output_filename(image_file, export_config)

      # 保存图片
      if export_config['format'] == "jpeg":
        # 转换为RGB模式并保存为JPEG
        if watermarked.mode in ('RGBA', 'P'):
          rgb_image = Image.new('RGB', watermarked.size, (255, 255, 255))
          if watermarked.mode == 'RGBA':
            rgb_image.paste(watermarked, mask=watermarked.split()[3])
          else:
            rgb_image.paste(watermarked)
          watermarked = rgb_image
        watermarked.save(output_file, "JPEG", quality=export_config['quality'])
      elif export_config['format'] == "png":
        watermarked.save(output_file, "PNG")
      else:  # 原格式
        original_format = image.format or 'JPEG'
        if original_format == 'JPEG' and watermarked.mode in ('RGBA', 'P'):
          rgb_image = Image.new('RGB', watermarked.size, (255, 255, 255))
          if watermarked.mode == 'RGBA':
            rgb_image.paste(watermarked, mask=watermarked.split()[3])
          else:
            rgb_image.paste(watermarked)
          watermarked = rgb_image

        save_kwargs = {}
        if original_format == 'JPEG':
          save_kwargs['quality'] = 95
        watermarked.save(output_file, original_format, **save_kwargs)

  def _apply_watermark_to_image(self, image, config):
    """对图片应用水印"""
    watermarked = image.copy()

    if not config.get('text', '').strip():
      return watermarked

    try:
      draw = ImageDraw.Draw(watermarked)
      text = config['text']
      font_size = config.get('font_size', 24)

      try:
        font = ImageFont.truetype("arial.ttf", font_size)
      except:
        font = ImageFont.load_default()

      # 计算位置
      bbox = draw.textbbox((0, 0), text, font=font)
      text_width = bbox[2] - bbox[0]
      text_height = bbox[3] - bbox[1]

      position = config.get('position', 'bottom-right')
      offset_x = config.get('offset_x', 10)
      offset_y = config.get('offset_y', 10)

      x, y = self._calculate_watermark_position(
          position, image.size, (text_width, text_height), offset_x, offset_y)

      # 应用水印
      color = config.get('color', '#FFFFFF')
      opacity = config.get('opacity', 128)

      if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        text_color = (r, g, b, opacity)
      else:
        text_color = (255, 255, 255, opacity)

      overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
      overlay_draw = ImageDraw.Draw(overlay)
      overlay_draw.text((x, y), text, font=font, fill=text_color)

      watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay)
      watermarked = watermarked.convert('RGB')

    except Exception as e:
      print(f"应用水印失败: {e}")

    return watermarked

  def _calculate_watermark_position(self, position, image_size, text_size, offset_x, offset_y):
    """计算水印位置"""
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

  def _generate_output_filename(self, input_file, export_config):
    """生成输出文件名"""
    input_path = Path(input_file)
    base_name = input_path.stem

    # 根据命名规则生成新名称
    if export_config['naming'] == "prefix":
      new_name = export_config['naming_text'] + base_name
    elif export_config['naming'] == "suffix":
      new_name = base_name + export_config['naming_text']
    else:  # original
      new_name = base_name

    # 确定扩展名
    if export_config['format'] == "jpeg":
      extension = ".jpg"
    elif export_config['format'] == "png":
      extension = ".png"
    else:  # original
      extension = input_path.suffix

    # 生成完整路径
    output_file = Path(export_config['output_dir']) / f"{new_name}{extension}"

    # 避免文件名冲突
    counter = 1
    while output_file.exists():
      output_file = Path(export_config['output_dir']) / \
          f"{new_name}_{counter}{extension}"
      counter += 1

    return output_file

  def _create_status_bar(self):
    """创建状态栏"""
    self.status_bar = ttk.Frame(self.root)
    self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    self.status_label = ttk.Label(self.status_bar, text="就绪")
    self.status_label.pack(side=tk.LEFT, padx=5, pady=2)

  def _setup_bindings(self):
    """设置快捷键绑定"""
    self.root.bind('<Control-o>', lambda e: self._add_images())
    self.root.bind('<Control-O>', lambda e: self._add_folder())
    self.root.bind('<Control-e>', lambda e: self._export_images())
    self.root.bind('<Control-q>', lambda e: self.root.quit())

  def _on_image_selected(self, index):
    """图片选择事件处理"""
    if 0 <= index < len(self.current_images):
      self.current_image_index = index
      image_path = self.current_images[index]

      # 更新预览
      self.preview_panel.load_image(image_path)
      self._update_preview()

      # 更新状态栏
      self.status_label.config(
          text=f"当前: {Path(image_path).name} ({index + 1}/{len(self.current_images)})")

  def _on_watermark_changed(self, watermark_config):
    """水印设置变更事件处理"""
    # 更新预览
    self._update_preview()

  def _update_preview(self):
    """更新预览显示"""
    if hasattr(self, 'watermark_panel') and self.watermark_panel:
      watermark_config = self.watermark_panel.get_config()
      if hasattr(self, 'preview_panel') and self.preview_panel:
        self.preview_panel.update_watermark(watermark_config)

  def _add_images(self):
    """添加图片文件"""
    file_types = [
        ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
        ("JPEG文件", "*.jpg *.jpeg"),
        ("PNG文件", "*.png"),
        ("所有文件", "*.*")
    ]

    files = filedialog.askopenfilenames(
        title="选择图片文件",
        filetypes=file_types
    )

    if files:
      self.file_list.add_files(files)
      self._update_image_list()

  def _add_folder(self):
    """添加文件夹"""
    folder = filedialog.askdirectory(title="选择图片文件夹")
    if folder:
      # 扫描文件夹中的图片文件
      supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
      folder_path = Path(folder)

      image_files = []
      for ext in supported_extensions:
        image_files.extend(folder_path.glob(f"*{ext}"))
        image_files.extend(folder_path.glob(f"*{ext.upper()}"))

      if image_files:
        self.file_list.add_files([str(f) for f in image_files])
        self._update_image_list()
      else:
        messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")

  def _update_image_list(self):
    """更新图片列表"""
    self.current_images = self.file_list.get_files()
    if self.current_images and self.current_image_index < len(self.current_images):
      self._on_image_selected(self.current_image_index)

  def _clear_images(self):
    """清除所有图片"""
    if messagebox.askyesno("确认", "确定要清除所有图片吗？"):
      self.file_list.clear()
      self.current_images = []
      self.current_image_index = 0
      if hasattr(self, 'preview_panel'):
        self.preview_panel.clear()
      self.status_label.config(text="就绪")

  def _export_images(self):
    """导出图片"""
    if not self.current_images:
      messagebox.showwarning("警告", "请先添加要处理的图片")
      return

    # 选择输出目录
    output_dir = filedialog.askdirectory(
        title="选择输出目录",
        initialdir=str(
            Path(self.current_images[0]).parent) if self.current_images else None
    )

    if not output_dir:
      return

    # 获取设置
    watermark_config = self.watermark_panel.get_config()
    export_config = {
        'output_dir': output_dir,
        'format': self.export_format_var.get(),
        'quality': self.jpeg_quality_var.get(),
        'naming': self.naming_var.get(),
        'naming_text': self.naming_text_var.get()
    }

    # 开始导出处理
    self._start_export_process(
        self.current_images, watermark_config, export_config)

  def _show_settings(self):
    """显示设置对话框"""
    messagebox.showinfo("设置", "设置功能即将推出...")

  def _show_help(self):
    """显示帮助"""
    help_text = """
水印工具使用说明：

1. 添加图片：点击"文件"菜单中的"添加图片"或"添加文件夹"
2. 设置水印：在左下角的"水印设置"面板中配置文本、大小、位置等
3. 预览效果：在右侧预览区域查看水印效果
4. 导出图片：点击"文件"菜单中的"导出图片"

支持的图片格式：JPEG, PNG, BMP, TIFF

快捷键：
- Ctrl+O：添加图片
- Ctrl+Shift+O：添加文件夹  
- Ctrl+E：导出图片
- Ctrl+Q：退出程序
        """
    messagebox.showinfo("使用说明", help_text)

  def _show_about(self):
    """显示关于对话框"""
    about_text = """水印工具 v2.0.0

跨平台桌面水印应用程序

功能特性：
• 支持文本和图片水印
• 批量处理
• 实时预览
• 跨平台兼容

作者：Sakiyary
许可：MIT License"""
    messagebox.showinfo("关于", about_text)

  def cleanup(self):
    """清理资源"""
    try:
      if hasattr(self, 'preview_panel') and self.preview_panel:
        self.preview_panel.cleanup()
    except Exception as e:
      print(f"清理资源时发生错误: {e}")
