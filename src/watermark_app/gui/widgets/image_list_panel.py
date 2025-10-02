#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片列表面板组件
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any, Callable, Optional
from PIL import Image, ImageTk
import os
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class ImageListPanel:
  """图片列表面板"""

  def __init__(self, parent: tk.Widget,
               on_selection_change: Optional[Callable[[int], None]] = None,
               on_remove_image: Optional[Callable[[int], None]] = None,
               on_clear_list: Optional[Callable[[], None]] = None):
    """
    初始化图片列表面板

    Args:
        parent: 父容器
        on_selection_change: 选择改变回调
        on_remove_image: 移除图片回调
        on_clear_list: 清空列表回调
    """
    self.parent = parent
    self.on_selection_change = on_selection_change
    self.on_remove_image = on_remove_image
    self.on_clear_list = on_clear_list
    self.logger = logging.getLogger(__name__)

    # 数据
    self.image_list = []
    self.selected_index = -1

    # 缩略图缓存
    self.thumbnail_cache = {}
    self.thumbnail_size = (50, 50)
    self.loading_image = None
    self.error_image = None

    # 线程池用于异步加载缩略图
    self.thumbnail_executor = ThreadPoolExecutor(
        max_workers=2, thread_name_prefix="thumbnail")

    # 创建界面
    self._create_widgets()
    self._create_placeholder_images()

  def _create_widgets(self):
    """创建界面组件"""
    try:
      # 主容器
      main_frame = ttk.Frame(self.parent)
      main_frame.pack(fill=tk.BOTH, expand=True)

      # 标题
      title_label = ttk.Label(main_frame, text="图片列表",
                              font=('Arial', 12, 'bold'))
      title_label.pack(pady=5)

      # 列表框架
      list_frame = ttk.Frame(main_frame)
      list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

      # 创建Treeview
      columns = ('name', 'size', 'format', 'status')
      self.tree = ttk.Treeview(
          list_frame, columns=columns, show='tree headings', height=10)

      # 设置列标题
      self.tree.heading('#0', text='缩略图')
      self.tree.heading('name', text='文件名')
      self.tree.heading('size', text='大小')
      self.tree.heading('format', text='格式')
      self.tree.heading('status', text='状态')

      # 设置列宽
      self.tree.column('#0', width=70, minwidth=70, anchor='center')
      self.tree.column('name', width=180, minwidth=120)
      self.tree.column('size', width=80, minwidth=60)
      self.tree.column('format', width=60, minwidth=40)
      self.tree.column('status', width=80, minwidth=60)

      # 设置行高适配缩略图（减小到适合的高度）
      style = ttk.Style()
      style.configure("Treeview", rowheight=60)      # 滚动条
      scrollbar = ttk.Scrollbar(
          list_frame, orient=tk.VERTICAL, command=self.tree.yview)
      self.tree.configure(yscrollcommand=scrollbar.set)

      # 打包
      self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
      scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

      # 按钮框架
      button_frame = ttk.Frame(main_frame)
      button_frame.pack(fill=tk.X, padx=5, pady=(5, 10))

      # 按钮（使用更明显的布局）
      self.remove_button = ttk.Button(button_frame, text="移除选中",
                                      command=self._remove_selected)
      self.remove_button.pack(side=tk.LEFT, padx=(0, 5))

      self.clear_button = ttk.Button(button_frame, text="清空列表",
                                     command=self._clear_all)
      self.clear_button.pack(side=tk.LEFT, padx=(5, 0))

      # 添加状态标签
      self.status_label = ttk.Label(button_frame, text="", foreground="gray")
      self.status_label.pack(side=tk.RIGHT, padx=(10, 0))

      # 绑定事件
      self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
      self.tree.bind('<Double-1>', self._on_double_click)

    except Exception as e:
      self.logger.error(f"创建图片列表界面失败: {str(e)}")

  def _create_placeholder_images(self):
    """创建占位图像"""
    try:
      # 创建加载中图像
      loading_img = Image.new('RGB', self.thumbnail_size, '#E0E0E0')
      self.loading_image = ImageTk.PhotoImage(loading_img)

      # 创建错误图像
      error_img = Image.new('RGB', self.thumbnail_size, '#FFE0E0')
      self.error_image = ImageTk.PhotoImage(error_img)

    except Exception as e:
      self.logger.error(f"创建占位图像失败: {str(e)}")

  def _generate_thumbnail(self, image_path: str, item_id: str):
    """
    异步生成缩略图

    Args:
        image_path: 图像文件路径
        item_id: TreeView项目ID
    """
    def load_thumbnail():
      try:
        if image_path in self.thumbnail_cache:
          cached_photo = self.thumbnail_cache[image_path]
          self.parent.after(0, lambda p=cached_photo,
                            iid=item_id: self._update_thumbnail(iid, p))
          return

        # 加载和缩放图像
        with Image.open(image_path) as img:
          # 转换为RGB模式以确保兼容性
          if img.mode != 'RGB':
            img = img.convert('RGB')

          # 生成缩略图
          img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)

          # 创建固定尺寸的背景
          thumb_img = Image.new('RGB', self.thumbnail_size, '#FFFFFF')

          # 居中放置缩略图
          offset = ((self.thumbnail_size[0] - img.size[0]) // 2,
                    (self.thumbnail_size[1] - img.size[1]) // 2)
          thumb_img.paste(img, offset)

          # 转换为Tkinter图像
          photo = ImageTk.PhotoImage(thumb_img)
          self.thumbnail_cache[image_path] = photo

          # 在主线程中更新UI
          self.parent.after(0, lambda p=photo,
                            iid=item_id: self._update_thumbnail(iid, p))

      except Exception as e:
        self.logger.error(f"生成缩略图失败 {image_path}: {str(e)}")
        # 在主线程中设置错误图像
        self.parent.after(
            0, lambda iid=item_id: self._update_thumbnail(iid, self.error_image))

    # 提交到线程池
    self.thumbnail_executor.submit(load_thumbnail)

  def _update_thumbnail(self, item_id: str, photo):
    """
    更新TreeView项目的缩略图

    Args:
        item_id: TreeView项目ID
        photo: PhotoImage对象
    """
    try:
      if self.tree.exists(item_id) and photo:
        self.tree.item(item_id, image=photo)
    except Exception as e:
      self.logger.error(f"更新缩略图失败: {str(e)}")

  def refresh_list(self, image_list: List[Dict[str, Any]]):
    """
    刷新图片列表

    Args:
        image_list: 图片信息列表
    """
    try:
      # 清空现有项目
      for item in self.tree.get_children():
        self.tree.delete(item)

      self.image_list = image_list

      # 添加新项目
      for i, image_info in enumerate(image_list):
        name = image_info.get('name', 'Unknown')
        size = self._format_file_size(image_info.get('size', 0))
        format_ext = image_info.get('extension', '').upper()
        status = image_info.get('status', '就绪')
        image_path = image_info.get('path')

        # 检查缓存中是否已有缩略图
        initial_image = self.loading_image
        if image_path in self.thumbnail_cache:
          initial_image = self.thumbnail_cache[image_path]

        # 插入项目
        item_id = self.tree.insert('', tk.END,
                                   text='',
                                   image=initial_image,
                                   values=(name, size, format_ext, status),
                                   tags=(str(i),))

        # 异步加载真实缩略图（如果需要）
        if image_path and os.path.exists(image_path):
          self._generate_thumbnail(image_path, item_id)

      self.logger.info(f"刷新图片列表完成，共 {len(image_list)} 个文件")
      self._update_status_label()

    except Exception as e:
      self.logger.error(f"刷新图片列表失败: {str(e)}")

  def add_images(self, image_list: List[Dict[str, Any]]):
    """
    添加图片到列表

    Args:
        image_list: 要添加的图片信息列表
    """
    try:
      start_index = len(self.image_list)

      for i, image_info in enumerate(image_list):
        name = image_info.get('name', 'Unknown')
        size = self._format_file_size(image_info.get('size', 0))
        format_ext = image_info.get('extension', '').upper()
        status = image_info.get('status', '就绪')

        # 插入项目，使用加载中图像作为初始缩略图
        item_id = self.tree.insert('', tk.END,
                                   text='',
                                   image=self.loading_image,
                                   values=(name, size, format_ext, status),
                                   tags=(str(start_index + i),))

        # 异步加载真实缩略图
        image_path = image_info.get('path')
        if image_path and os.path.exists(image_path):
          self._generate_thumbnail(image_path, item_id)

        self.image_list.append(image_info)

      self.logger.info(f"添加 {len(image_list)} 个图片到列表")
      self._update_status_label()

    except Exception as e:
      self.logger.error(f"添加图片到列表失败: {str(e)}")

  def get_selected_index(self) -> int:
    """
    获取当前选中的索引

    Returns:
        选中的索引，-1表示未选中
    """
    return self.selected_index

  def select_image(self, index: int):
    """
    选中指定索引的图片

    Args:
        index: 图片索引
    """
    try:
      if 0 <= index < len(self.image_list):
        # 清除当前选择
        for item in self.tree.selection():
          self.tree.selection_remove(item)

        # 选中新项目
        items = self.tree.get_children()
        if index < len(items):
          self.tree.selection_set(items[index])
          self.tree.focus(items[index])
          self.tree.see(items[index])

    except Exception as e:
      self.logger.error(f"选中图片失败: {str(e)}")

  def _on_tree_select(self, event):
    """树形视图选择事件"""
    try:
      selection = self.tree.selection()
      if selection:
        item = selection[0]
        # 获取索引
        index = int(self.tree.item(item)['tags'][0])
        if index != self.selected_index:
          self.selected_index = index
          if self.on_selection_change:
            self.on_selection_change(index)
      else:
        if self.selected_index != -1:
          self.selected_index = -1
          if self.on_selection_change:
            self.on_selection_change(-1)

    except Exception as e:
      self.logger.error(f"处理选择事件失败: {str(e)}")

  def _on_double_click(self, event):
    """双击事件"""
    # 双击时可以实现特殊功能，比如放大预览
    pass

  def _remove_selected(self):
    """移除选中的图片"""
    try:
      if self.selected_index >= 0:
        if self.on_remove_image:
          self.on_remove_image(self.selected_index)

    except Exception as e:
      self.logger.error(f"移除选中图片失败: {str(e)}")

  def _clear_all(self):
    """清空所有图片"""
    try:
      # 调用主窗口的清空方法
      if self.on_clear_list:
        self.on_clear_list()
      else:
        # 如果没有回调，执行本地清空（向后兼容）
        for item in self.tree.get_children():
          self.tree.delete(item)
        self.image_list.clear()
        self.selected_index = -1
        if self.on_selection_change:
          self.on_selection_change(-1)
        self._update_status_label()
        self.logger.info("已清空图片列表")

    except Exception as e:
      self.logger.error(f"清空图片列表失败: {str(e)}")

  def update_image_status(self, index: int, status: str):
    """
    更新指定图像的状态

    Args:
        index: 图像索引
        status: 新状态
    """
    try:
      if 0 <= index < len(self.image_list):
        # 更新数据
        self.image_list[index]['status'] = status

        # 更新TreeView显示
        items = self.tree.get_children()
        if index < len(items):
          item_id = items[index]
          current_values = list(self.tree.item(item_id)['values'])
          if len(current_values) >= 4:
            current_values[3] = status  # 状态列（现在是第4列，索引3）
            self.tree.item(item_id, values=current_values)

    except Exception as e:
      self.logger.error(f"更新图像状态失败: {str(e)}")

  def get_image_info(self, index: int) -> Dict[str, Any]:
    """
    获取指定索引的图像信息

    Args:
        index: 图像索引

    Returns:
        图像信息字典
    """
    if 0 <= index < len(self.image_list):
      return self.image_list[index].copy()
    return {}

  def _update_status_label(self):
    """更新状态标签"""
    try:
      count = len(self.image_list)
      if count == 0:
        status_text = "无图片"
      else:
        status_text = f"共 {count} 张图片"

      if hasattr(self, 'status_label'):
        self.status_label.config(text=status_text)

    except Exception as e:
      self.logger.error(f"更新状态标签失败: {str(e)}")

  def destroy(self):
    """清理资源"""
    try:
      # 关闭线程池
      self.thumbnail_executor.shutdown(wait=False)

      # 清理缓存
      self.thumbnail_cache.clear()

    except Exception as e:
      self.logger.error(f"清理资源失败: {str(e)}")

  def _format_file_size(self, size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        格式化的大小字符串
    """
    try:
      if size_bytes == 0:
        return "0 B"

      size_names = ["B", "KB", "MB", "GB"]
      i = 0
      while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

      return f"{size_bytes:.1f} {size_names[i]}"
    except Exception:
      return "Unknown"
