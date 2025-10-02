"""
水印工具 - 主窗口

应用程序的主要用户界面，包含文件列表、预览区域、水印设置等组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

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

    # 右侧面板 - 预览区域
    right_frame = ttk.Frame(h_paned)
    h_paned.add(right_frame, weight=2)

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
    self.preview_panel = PreviewPanel(right_frame)
    self.watermark_panel = WatermarkPanel(
        watermark_frame, self._on_watermark_changed)

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

    # 获取水印配置
    watermark_config = self.watermark_panel.get_config()

    # 显示导出对话框
    dialog = ExportDialog(self.root, self.current_images, watermark_config)
    self.root.wait_window(dialog.dialog)

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
