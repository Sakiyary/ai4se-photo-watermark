"""
水印工具 - 文件列表组件

用于显示和管理导入的图片文件列表
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os


class FileListWidget:
  """文件列表组件"""

  def __init__(self, parent, selection_callback=None):
    """初始化文件列表组件

    Args:
        parent: 父组件
        selection_callback: 选择回调函数
    """
    self.parent = parent
    self.selection_callback = selection_callback
    self.files = []

    self._setup_ui()

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

    # 创建列表框架
    list_frame = ttk.Frame(self.parent)
    list_frame.pack(fill=tk.BOTH, expand=True)

    # 创建树形视图
    columns = ('name', 'size', 'path')
    self.tree = ttk.Treeview(list_frame, columns=columns,
                             show='tree headings', height=8)

    # 设置列
    self.tree.heading('#0', text='')
    self.tree.heading('name', text='文件名')
    self.tree.heading('size', text='大小')
    self.tree.heading('path', text='路径')

    # 设置列宽
    self.tree.column('#0', width=30, minwidth=30)
    self.tree.column('name', width=150, minwidth=100)
    self.tree.column('size', width=80, minwidth=60)
    self.tree.column('path', width=200, minwidth=100)

    # 添加滚动条
    scrollbar = ttk.Scrollbar(
        list_frame, orient=tk.VERTICAL, command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)

    # 布局
    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 绑定选择事件
    self.tree.bind('<<TreeviewSelect>>', self._on_selection_changed)

    # 支持拖拽（基础版本）
    self.tree.bind('<Button-1>', self._on_click)

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
    self.clear()

  def _on_selection_changed(self, event):
    """选择变更事件"""
    selection = self.tree.selection()
    if selection and self.selection_callback:
      # 获取选中项的索引
      item = selection[0]
      index = self.tree.index(item)
      self.selection_callback(index)

  def _on_click(self, event):
    """点击事件"""
    # 用于后续实现拖拽功能
    pass

  def add_files(self, file_paths):
    """添加文件到列表

    Args:
        file_paths: 文件路径列表
    """
    for file_path in file_paths:
      if file_path not in self.files:
        self.files.append(file_path)
        self._add_file_to_tree(file_path)

  def _add_file_to_tree(self, file_path):
    """将文件添加到树形视图"""
    try:
      path = Path(file_path)
      if path.exists() and path.is_file():
        # 获取文件信息
        name = path.name
        size = self._format_file_size(path.stat().st_size)
        dir_path = str(path.parent)

        # 添加到树形视图
        self.tree.insert('', tk.END, values=(name, size, dir_path))

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

    return f"{size_bytes:.1f} {size_names[i]}"

  def clear(self):
    """清除所有文件"""
    self.files.clear()
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

  def remove_selected(self):
    """移除选中的文件"""
    selection = self.tree.selection()
    if selection:
      item = selection[0]
      index = self.tree.index(item)

      # 从列表中移除
      if 0 <= index < len(self.files):
        self.files.pop(index)

      # 从树形视图中移除
      self.tree.delete(item)
