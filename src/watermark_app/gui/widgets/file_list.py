"""
水印工具 - 文件列表组件 (修复版)

用于显示和管理导入的图片文件列表，支持拖拽、缩略图、格式验证
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import sys
from PIL import Image, ImageTk
import threading


class FileListWidget:
  """文件列表组件 (修复版)"""

  def __init__(self, parent, selection_callback=None):
    """初始化文件列表组件

    Args:
        parent: 父组件
        selection_callback: 选择回调函数
    """
    self.parent = parent
    self.selection_callback = selection_callback
    self.files = []
    self.thumbnails = {}  # 缓存缩略图
    self.thumbnail_size = (32, 32)

    self._setup_ui()
    self._setup_drag_drop()

  def _setup_ui(self):
    """设置用户界面"""
    # 创建按钮框架
    button_frame = ttk.Frame(self.parent)
    button_frame.pack(fill=tk.X, pady=(0, 5))

    # 添加文件按钮
    self.add_files_btn = ttk.Button(
        button_frame,
        text="添加文件",
        command=self._add_files_clicked
    )
    self.add_files_btn.pack(side=tk.LEFT, padx=(0, 5))

    # 添加文件夹按钮
    self.add_folder_btn = ttk.Button(
        button_frame,
        text="添加文件夹",
        command=self._add_folder_clicked
    )
    self.add_folder_btn.pack(side=tk.LEFT, padx=(0, 5))

    # 清除按钮
    self.clear_btn = ttk.Button(
        button_frame,
        text="清除",
        command=self._clear_clicked
    )
    self.clear_btn.pack(side=tk.RIGHT)

    # 创建拖拽提示标签
    self.drag_label = ttk.Label(
        button_frame,
        text="💡 提示：支持右键菜单操作",
        font=('Arial', 8),
        foreground='gray'
    )
    self.drag_label.pack(side=tk.LEFT, padx=(10, 0))

    # 创建列表框架
    list_frame = ttk.Frame(self.parent)
    list_frame.pack(fill=tk.BOTH, expand=True)

    # 创建树形视图
    columns = ('name', 'size', 'format', 'dimensions')
    self.tree = ttk.Treeview(list_frame, columns=columns,
                             show='tree headings', height=8)

    # 设置列
    self.tree.heading('#0', text='🖼️')
    self.tree.heading('name', text='文件名')
    self.tree.heading('size', text='大小')
    self.tree.heading('format', text='格式')
    self.tree.heading('dimensions', text='尺寸')

    # 设置列宽
    self.tree.column('#0', width=40, minwidth=40)  # 用于显示缩略图
    self.tree.column('name', width=150, minwidth=100)
    self.tree.column('size', width=80, minwidth=60)
    self.tree.column('format', width=60, minwidth=50)
    self.tree.column('dimensions', width=100, minwidth=80)

    # 添加滚动条
    v_scrollbar = ttk.Scrollbar(
        list_frame, orient=tk.VERTICAL, command=self.tree.yview)
    h_scrollbar = ttk.Scrollbar(
        list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
    self.tree.configure(yscrollcommand=v_scrollbar.set,
                        xscrollcommand=h_scrollbar.set)

    # 布局
    self.tree.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')

    # 配置网格权重
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)

    # 绑定事件
    self.tree.bind('<<TreeviewSelect>>', self._on_selection_changed)
    self.tree.bind('<Double-1>', self._on_double_click)

    # 创建右键菜单
    self._create_context_menu()

  def _setup_drag_drop(self):
    """设置拖拽功能"""
    # 注意：这是一个简化版本的拖拽支持
    # 实际生产环境建议使用 tkinterdnd2 库实现完整的拖拽功能

    # 绑定基础拖拽事件
    self.tree.bind('<Button-1>', self._on_click)

  def _create_context_menu(self):
    """创建右键菜单"""
    self.context_menu = tk.Menu(self.tree, tearoff=0)
    self.context_menu.add_command(label="查看详情", command=self._show_file_info)
    self.context_menu.add_command(
        label="在文件管理器中显示", command=self._show_in_explorer)
    self.context_menu.add_separator()
    self.context_menu.add_command(label="移除选中项", command=self._remove_selected)
    self.context_menu.add_command(label="清除所有", command=self._clear_clicked)

    # 绑定右键事件
    self.tree.bind('<Button-3>', self._show_context_menu)  # Windows/Linux
    if sys.platform == 'darwin':  # macOS
      self.tree.bind('<Button-2>', self._show_context_menu)
      self.tree.bind('<Control-Button-1>', self._show_context_menu)

  def _show_context_menu(self, event):
    """显示右键菜单"""
    # 选中右键点击的项目
    item = self.tree.identify_row(event.y)
    if item:
      self.tree.selection_set(item)
      self.context_menu.post(event.x_root, event.y_root)

  def _show_file_info(self):
    """显示文件详情"""
    selection = self.tree.selection()
    if selection:
      index = self.tree.index(selection[0])
      if 0 <= index < len(self.files):
        file_path = self.files[index]
        info = self._get_file_info(file_path)
        if info:
          messagebox.showinfo("文件信息",
                              f"文件名: {info['name']}\n"
                              f"路径: {info['path']}\n"
                              f"大小: {info['size_formatted']}\n"
                              f"格式: {info['format']}\n"
                              f"尺寸: {info['dimensions']}\n"
                              f"颜色模式: {info['mode']}"
                              )

  def _show_in_explorer(self):
    """在文件管理器中显示"""
    selection = self.tree.selection()
    if selection:
      index = self.tree.index(selection[0])
      if 0 <= index < len(self.files):
        file_path = Path(self.files[index])
        if file_path.exists():
          try:
            # 跨平台文件管理器打开
            if os.name == 'nt':  # Windows
              os.startfile(str(file_path.parent))
            elif sys.platform == 'darwin':  # macOS
              os.system(f'open "{file_path.parent}"')
            else:  # Linux
              os.system(f'xdg-open "{file_path.parent}"')
          except Exception as e:
            messagebox.showerror("错误", f"无法打开文件管理器: {e}")

  def _get_file_info(self, file_path):
    """获取文件详细信息"""
    try:
      path = Path(file_path)
      if not path.exists():
        return None

      # 基本文件信息
      stat = path.stat()
      info = {
          'name': path.name,
          'path': str(path.parent),
          'size': stat.st_size,
          'size_formatted': self._format_file_size(stat.st_size)
      }

      # 图片信息
      try:
        with Image.open(file_path) as img:
          info.update({
              'format': img.format or 'Unknown',
              'mode': img.mode,
              'dimensions': f"{img.width}x{img.height}",
              'width': img.width,
              'height': img.height
          })
      except Exception:
        info.update({
            'format': 'Unknown',
            'mode': 'Unknown',
            'dimensions': 'Unknown',
            'width': 0,
            'height': 0
        })

      return info

    except Exception as e:
      print(f"获取文件信息失败: {e}")
      return None

  def _add_files_clicked(self):
    """添加文件按钮点击事件"""
    # 这个方法会被主窗口重写或连接到实际的文件选择逻辑
    pass

  def _add_folder_clicked(self):
    """添加文件夹按钮点击事件"""
    # 这个方法会被主窗口重写或连接到实际的文件夹选择逻辑
    pass

  def _clear_clicked(self):
    """清除按钮点击事件"""
    if self.files:
      if messagebox.askyesno("确认", "确定要清除所有文件吗？"):
        self.clear()

  def _on_selection_changed(self, event):
    """选择变更事件"""
    selection = self.tree.selection()
    if selection and self.selection_callback:
      # 获取选中项的索引
      item = selection[0]
      index = self.tree.index(item)
      self.selection_callback(index)

  def _on_double_click(self, event):
    """双击事件"""
    selection = self.tree.selection()
    if selection:
      self._show_file_info()

  def _on_click(self, event):
    """点击事件"""
    # 用于后续实现拖拽功能
    pass

  def add_files(self, file_paths, show_progress=True):
    """添加文件到列表（增强版）

    Args:
        file_paths: 文件路径列表
        show_progress: 是否显示进度
    """
    if not file_paths:
      return

    # 验证文件
    valid_files, invalid_files = self._validate_files(file_paths)

    # 显示无效文件警告
    if invalid_files:
      invalid_count = len(invalid_files)
      if invalid_count <= 5:
        # 少量无效文件，显示详细列表
        message = f"以下 {invalid_count} 个文件无效，将被跳过:\n"
        for f in invalid_files:
          message += f"• {Path(f).name}\n"
      else:
        # 大量无效文件，显示统计信息
        sample_files = invalid_files[:3]
        message = f"发现 {invalid_count} 个无效文件，示例:\n"
        for f in sample_files:
          message += f"• {Path(f).name}\n"
        message += f"... 还有 {invalid_count - 3} 个文件\n\n这些文件将被跳过。"

      messagebox.showwarning("文件验证", message)

    # 添加有效文件
    added_count = 0
    duplicate_count = 0

    for file_path in valid_files:
      if file_path not in self.files:
        self.files.append(file_path)
        self._add_file_to_tree(file_path)
        added_count += 1
      else:
        duplicate_count += 1

    # 显示添加结果
    if show_progress and (added_count > 0 or duplicate_count > 0):
      message = f"处理完成!\n"
      if added_count > 0:
        message += f"✅ 成功添加: {added_count} 个文件\n"
      if duplicate_count > 0:
        message += f"⚠️ 重复文件: {duplicate_count} 个\n"
      if invalid_files:
        message += f"❌ 无效文件: {len(invalid_files)} 个"

      messagebox.showinfo("添加结果", message)

  def _validate_files(self, file_paths):
    """验证文件列表"""
    valid_files = []
    invalid_files = []

    for file_path in file_paths:
      if self._is_valid_image_file(file_path):
        valid_files.append(file_path)
      else:
        invalid_files.append(file_path)

    return valid_files, invalid_files

  def _is_valid_image_file(self, file_path):
    """验证是否为有效的图片文件"""
    try:
      path = Path(file_path)

      # 检查文件是否存在
      if not path.exists() or not path.is_file():
        return False

      # 检查文件扩展名
      extension = path.suffix.lower()
      supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
      if extension not in supported_formats:
        return False

      # 检查文件大小（限制100MB）
      file_size_mb = path.stat().st_size / (1024 * 1024)
      if file_size_mb > 100:
        return False

      # 尝试打开图片验证格式
      try:
        with Image.open(file_path) as img:
          img.verify()
        return True
      except Exception:
        return False

    except Exception:
      return False

  def _add_file_to_tree(self, file_path):
    """将文件添加到树形视图（增强版）"""
    try:
      info = self._get_file_info(file_path)
      if info:
        # 添加到树形视图
        item = self.tree.insert('', tk.END, values=(
            info['name'],
            info['size_formatted'],
            info['format'],
            info['dimensions']
        ))

    except Exception as e:
      print(f"添加文件到列表时出错: {e}")

  def _format_file_size(self, size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
      return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
      size_bytes /= 1024.0
      i += 1

    if i == 0:
      return f"{int(size_bytes)} {size_names[i]}"
    else:
      return f"{size_bytes:.1f} {size_names[i]}"

  def clear(self):
    """清除所有文件"""
    self.files.clear()
    self.thumbnails.clear()
    # 删除所有树形视图项目
    for item in self.tree.get_children():
      self.tree.delete(item)

  def get_files(self):
    """获取文件列表"""
    return self.files.copy()

  def get_selected_index(self):
    """获取当前选中的文件索引"""
    selection = self.tree.selection()
    if selection:
      return self.tree.index(selection[0])
    return -1

  def select_file(self, index):
    """选中指定索引的文件"""
    if 0 <= index < len(self.files):
      items = self.tree.get_children()
      if index < len(items):
        self.tree.selection_set(items[index])
        self.tree.see(items[index])

  def _remove_selected(self):
    """移除选中的文件"""
    selection = self.tree.selection()
    if selection:
      if messagebox.askyesno("确认", "确定要移除选中的文件吗？"):
        item = selection[0]
        index = self.tree.index(item)

        # 从列表中移除
        if 0 <= index < len(self.files):
          removed_file = self.files.pop(index)
          # 清除缓存的缩略图
          if removed_file in self.thumbnails:
            del self.thumbnails[removed_file]

        # 从树形视图中移除
        self.tree.delete(item)

  def remove_file(self, file_path):
    """移除指定文件"""
    if file_path in self.files:
      index = self.files.index(file_path)
      self.files.remove(file_path)

      # 清除缓存
      if file_path in self.thumbnails:
        del self.thumbnails[file_path]

      # 从树形视图中移除
      items = self.tree.get_children()
      if index < len(items):
        self.tree.delete(items[index])

  def get_file_count(self):
    """获取文件数量"""
    return len(self.files)

  def get_total_size(self):
    """获取所有文件的总大小"""
    total_size = 0
    for file_path in self.files:
      try:
        total_size += Path(file_path).stat().st_size
      except Exception:
        continue
    return total_size

  def get_statistics(self):
    """获取文件统计信息"""
    if not self.files:
      return "无文件"

    total_size = self.get_total_size()
    return f"共 {len(self.files)} 个文件，总大小 {self._format_file_size(total_size)}"
