#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os
from typing import Optional, List
from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD

from ..core import ImageProcessor, WatermarkProcessor, FileManager, ConfigManager, ImageExporter
from ..utils.constants import *
from ..utils.helpers import center_window, get_system_fonts
from .widgets.image_list_panel import ImageListPanel
from .widgets.preview_panel import PreviewPanel
from .widgets.watermark_control_panel import WatermarkControlPanel
from .widgets.position_control_panel import PositionControlPanel
from .dialogs.progress_dialog import ProgressDialog

logger = logging.getLogger(__name__)


class MainWindow:
  """主窗口类"""

  def __init__(self, root: tk.Tk):
    """
    初始化主窗口

    Args:
        root: Tkinter根窗口
    """
    self.root = TkinterDnD.Tk() if not isinstance(root, TkinterDnD.Tk) else root
    self.logger = logging.getLogger(__name__)

    # 核心组件
    self.image_processor = ImageProcessor()
    self.watermark_processor = WatermarkProcessor()
    self.file_manager = FileManager()
    self.config_manager = ConfigManager()
    self.image_exporter = ImageExporter()

    # 界面组件
    self.image_list_panel = None
    self.preview_panel = None
    self.watermark_control_panel = None
    self.position_control_panel = None

    # 状态变量
    self.current_image_index = -1
    self.current_image = None
    self.current_preview_image = None

    # 初始化界面
    self._setup_window()
    self._create_menu()
    self._create_toolbar()
    self._create_main_layout()
    self._bind_events()

    # 加载配置
    self._load_config()

    self.logger.info("主窗口初始化完成")

  def _setup_window(self):
    """设置窗口属性"""
    try:
      # 窗口标题和图标
      self.root.title(f"{APP_NAME} v{APP_VERSION}")

      # 窗口大小和位置
      window_size = self.config_manager.get_config(
          'app.window_size') or DEFAULT_WINDOW_SIZE
      window_pos = self.config_manager.get_config(
          'app.window_position') or DEFAULT_WINDOW_POSITION

      self.root.geometry(
          f"{window_size[0]}x{window_size[1]}+{window_pos[0]}+{window_pos[1]}")
      self.root.minsize(*MIN_WINDOW_SIZE)

      # 居中显示
      center_window(self.root, window_size[0], window_size[1])

      # 窗口关闭事件
      self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

      # 设置键盘快捷键
      self._setup_keyboard_shortcuts()

    except Exception as e:
      self.logger.error(f"设置窗口属性失败: {str(e)}")

  def _create_menu(self):
    """创建菜单栏"""
    try:
      menubar = tk.Menu(self.root)
      self.root.config(menu=menubar)

      # 文件菜单
      file_menu = tk.Menu(menubar, tearoff=0)
      menubar.add_cascade(label="文件", menu=file_menu)
      file_menu.add_command(
          label="导入图片...", command=self._import_images, accelerator="Ctrl+O")
      file_menu.add_command(
          label="导入文件夹...", command=self._import_folder, accelerator="Ctrl+Shift+O")
      file_menu.add_separator()
      file_menu.add_command(
          label="导出当前图片...", command=self._export_current_image, accelerator="Ctrl+S")
      file_menu.add_command(
          label="批量导出...", command=self._export_all_images, accelerator="Ctrl+Shift+S")
      file_menu.add_separator()
      file_menu.add_command(
          label="退出", command=self._on_window_close, accelerator="Ctrl+Q")

      # 编辑菜单
      edit_menu = tk.Menu(menubar, tearoff=0)
      menubar.add_cascade(label="编辑", menu=edit_menu)
      edit_menu.add_command(
          label="清空列表", command=self._on_clear_list, accelerator="Ctrl+Delete")
      edit_menu.add_separator()
      edit_menu.add_command(
          label="上一张图片", command=lambda: self._on_image_switch('prev'), accelerator="←")
      edit_menu.add_command(
          label="下一张图片", command=lambda: self._on_image_switch('next'), accelerator="→")
      edit_menu.add_separator()
      edit_menu.add_command(
          label="复制水印设置", command=self._copy_watermark_settings)
      edit_menu.add_command(
          label="粘贴水印设置", command=self._paste_watermark_settings)

      # 水印菜单
      watermark_menu = tk.Menu(menubar, tearoff=0)
      menubar.add_cascade(label="水印", menu=watermark_menu)
      watermark_menu.add_command(
          label="保存为模板...", command=self._save_watermark_template)
      watermark_menu.add_command(
          label="加载模板...", command=self._load_watermark_template)
      watermark_menu.add_command(
          label="管理模板...", command=self._manage_templates)

      # 帮助菜单
      help_menu = tk.Menu(menubar, tearoff=0)
      menubar.add_cascade(label="帮助", menu=help_menu)
      help_menu.add_command(label="使用说明", command=self._show_help)
      help_menu.add_command(label="关于", command=self._show_about)

    except Exception as e:
      self.logger.error(f"创建菜单失败: {str(e)}")

  def _create_toolbar(self):
    """创建工具栏"""
    try:
      self.toolbar = ttk.Frame(self.root)
      self.toolbar.pack(fill=tk.X, padx=5, pady=2)

      # 导入按钮
      ttk.Button(self.toolbar, text="导入图片",
                 command=self._import_images).pack(side=tk.LEFT, padx=2)
      ttk.Button(self.toolbar, text="导入文件夹",
                 command=self._import_folder).pack(side=tk.LEFT, padx=2)

      # 分隔符
      ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
          side=tk.LEFT, fill=tk.Y, padx=5)

      # 导出按钮
      ttk.Button(self.toolbar, text="导出当前",
                 command=self._export_current_image).pack(side=tk.LEFT, padx=2)
      ttk.Button(self.toolbar, text="批量导出",
                 command=self._export_all_images).pack(side=tk.LEFT, padx=2)

      # 分隔符
      ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
          side=tk.LEFT, fill=tk.Y, padx=5)

      # 模板按钮
      ttk.Button(self.toolbar, text="保存模板",
                 command=self._save_watermark_template).pack(side=tk.LEFT, padx=2)
      ttk.Button(self.toolbar, text="加载模板",
                 command=self._load_watermark_template).pack(side=tk.LEFT, padx=2)

    except Exception as e:
      self.logger.error(f"创建工具栏失败: {str(e)}")

  def _create_main_layout(self):
    """创建主布局"""
    try:
      # 主容器
      self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
      self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

      # 左侧面板（图片列表）
      self.left_frame = ttk.Frame(self.main_container)
      self.main_container.add(self.left_frame, weight=1)

      # 中间面板（预览区域）
      self.center_frame = ttk.Frame(self.main_container)
      self.main_container.add(self.center_frame, weight=3)

      # 右侧面板（控制面板）
      self.right_frame = ttk.Frame(self.main_container)
      self.main_container.add(self.right_frame, weight=2)

      # 创建各个面板
      self._create_panels()

    except Exception as e:
      self.logger.error(f"创建主布局失败: {str(e)}")

  def _create_panels(self):
    """创建各个功能面板"""
    try:
      # 图片列表面板
      self.image_list_panel = ImageListPanel(
          self.left_frame,
          on_selection_change=self._on_image_selection_change,
          on_remove_image=self._on_remove_image,
          on_clear_list=self._clear_image_list
      )

      # 预览面板
      self.preview_panel = PreviewPanel(
          self.center_frame,
          on_position_change=self._on_watermark_position_change,
          on_image_switch=self._on_image_switch
      )

      # 右侧控制面板容器
      control_notebook = ttk.Notebook(self.right_frame)
      control_notebook.pack(fill=tk.BOTH, expand=True)

      # 水印控制面板
      watermark_frame = ttk.Frame(control_notebook)
      control_notebook.add(watermark_frame, text="水印设置")
      self.watermark_control_panel = WatermarkControlPanel(
          watermark_frame,
          on_watermark_change=self._on_watermark_change
      )

      # 位置控制面板
      position_frame = ttk.Frame(control_notebook)
      control_notebook.add(position_frame, text="位置控制")
      self.position_control_panel = PositionControlPanel(
          position_frame,
          on_position_change=self._on_watermark_position_change
      )

    except Exception as e:
      self.logger.error(f"创建功能面板失败: {str(e)}")

  def _bind_events(self):
    """绑定事件"""
    try:
      # 键盘快捷键
      self.root.bind('<Control-o>', lambda e: self._import_images())
      self.root.bind('<Control-O>', lambda e: self._import_folder())
      self.root.bind('<Control-s>', lambda e: self._export_current_image())
      self.root.bind('<Control-S>', lambda e: self._export_all_images())
      self.root.bind('<Control-q>', lambda e: self._on_window_close())

      # 拖拽支持
      self._setup_drag_drop()

    except Exception as e:
      self.logger.error(f"绑定事件失败: {str(e)}")

  def _setup_drag_drop(self):
    """设置拖拽支持"""
    try:
      # 注册拖拽目标
      self.root.drop_target_register(DND_FILES)
      self.root.dnd_bind('<<Drop>>', self._on_drop_files)

      # 也为左侧图片列表面板设置拖拽
      if self.image_list_panel and hasattr(self.image_list_panel, 'tree'):
        self.image_list_panel.tree.drop_target_register(DND_FILES)
        self.image_list_panel.tree.dnd_bind('<<Drop>>', self._on_drop_files)

    except Exception as e:
      self.logger.error(f"设置拖拽功能失败: {str(e)}")

  def _load_config(self):
    """加载配置"""
    try:
      # 应用水印配置到控制面板
      watermark_config = self.config_manager.get_watermark_config()

      if self.watermark_control_panel:
        self.watermark_control_panel.load_config(watermark_config)

      if self.position_control_panel:
        self.position_control_panel.load_config(
            watermark_config.get('position', {}))

    except Exception as e:
      self.logger.error(f"加载配置失败: {str(e)}")

  def _save_config(self):
    """保存配置"""
    try:
      # 保存窗口状态
      geometry = self.root.geometry()
      size_pos = geometry.split('+')
      size = size_pos[0].split('x')

      self.config_manager.set_config(
          'app.window_size', [int(size[0]), int(size[1])])
      if len(size_pos) > 2:
        self.config_manager.set_config(
            'app.window_position', [int(size_pos[1]), int(size_pos[2])])

      # 保存水印配置
      if self.watermark_control_panel and self.position_control_panel:
        watermark_config = self.watermark_control_panel.get_config()
        position_config = self.position_control_panel.get_config()
        watermark_config['position'] = position_config

        self.config_manager.set_watermark_config(watermark_config)

      # 保存到文件
      self.config_manager.save_config()

    except Exception as e:
      self.logger.error(f"保存配置失败: {str(e)}")

  # 事件处理方法
  def _on_image_selection_change(self, index: int):
    """图片选择改变事件"""
    try:
      self.current_image_index = index
      if index >= 0:
        file_info = self.file_manager.get_file_by_index(index)
        if file_info:
          # 加载图像
          image = self.image_processor.load_image(file_info['path'])
          if image:
            self.current_image = image
            self._update_preview()
            self._update_navigation_buttons()
            return

      # 清空预览
      self.current_image = None
      self.current_image_index = -1
      if self.preview_panel:
        self.preview_panel.clear_preview()
        self._update_navigation_buttons()

    except Exception as e:
      self.logger.error(f"处理图片选择事件失败: {str(e)}")

  def _on_image_switch(self, direction: str):
    """图片切换事件"""
    try:
      file_list = self.file_manager.get_file_list()
      if not file_list or self.current_image_index < 0:
        return

      if direction == 'prev' and self.current_image_index > 0:
        new_index = self.current_image_index - 1
      elif direction == 'next' and self.current_image_index < len(file_list) - 1:
        new_index = self.current_image_index + 1
      else:
        return

      # 更新图片列表选择
      if self.image_list_panel:
        self.image_list_panel.select_image(new_index)

    except Exception as e:
      self.logger.error(f"处理图片切换失败: {str(e)}")

  def _update_navigation_buttons(self):
    """更新导航按钮状态"""
    try:
      if not self.preview_panel:
        return

      file_list = self.file_manager.get_file_list()
      has_prev = self.current_image_index > 0
      has_next = self.current_image_index >= 0 and self.current_image_index < len(
          file_list) - 1

      self.preview_panel.update_navigation_buttons(has_prev, has_next)

    except Exception as e:
      self.logger.error(f"更新导航按钮状态失败: {str(e)}")

  def _on_remove_image(self, index: int):
    """移除图片事件"""
    try:
      success = self.file_manager.remove_file_by_index(index)
      if success:
        # 更新图片列表
        if self.image_list_panel:
          self.image_list_panel.refresh_list(self.file_manager.get_file_list())

        # 如果移除的是当前选中的图片
        if index == self.current_image_index:
          self.current_image = None
          self.current_image_index = -1
          if self.preview_panel:
            self.preview_panel.clear_preview()
            self._update_navigation_buttons()
        elif index < self.current_image_index:
          self.current_image_index -= 1

    except Exception as e:
      self.logger.error(f"移除图片失败: {str(e)}")

  def _on_watermark_change(self):
    """水印设置改变事件"""
    self._update_preview()

  def _on_watermark_position_change(self, position=None):
    """水印位置改变事件"""
    if position and self.position_control_panel:
      self.position_control_panel.update_position(position)
    self._update_preview()

  def _update_preview(self):
    """更新预览"""
    try:
      if not self.current_image or not self.preview_panel:
        return

      # 获取水印配置
      watermark_config = {}
      position_config = {}

      if self.watermark_control_panel:
        watermark_config = self.watermark_control_panel.get_config()
      if self.position_control_panel:
        position_config = self.position_control_panel.get_config()

      # 生成水印预览
      preview_image = self._apply_watermark_to_image(
          self.current_image, watermark_config, position_config)

      if preview_image:
        self.current_preview_image = preview_image

        # 生成图片信息
        image_info = self._get_current_image_info()
        self.preview_panel.update_preview(preview_image, image_info)

    except Exception as e:
      self.logger.error(f"更新预览失败: {str(e)}")

  def _get_current_image_info(self) -> str:
    """
    获取当前图片信息字符串

    Returns:
        图片信息字符串
    """
    try:
      if self.current_image_index < 0:
        return ""

      file_info = self.file_manager.get_file_by_index(self.current_image_index)
      if not file_info:
        return ""

      file_list = self.file_manager.get_file_list()
      current_pos = self.current_image_index + 1
      total_count = len(file_list)

      width = self.current_image.width if self.current_image else 0
      height = self.current_image.height if self.current_image else 0

      return f"{current_pos}/{total_count} | {width}×{height}像素 | {file_info.get('name', '')}"

    except Exception as e:
      self.logger.error(f"获取图片信息失败: {str(e)}")
      return ""

  def _apply_watermark_to_image(self, image, watermark_config, position_config):
    """应用水印到图像"""
    try:
      if not image:
        return image

      # 如果没有水印配置，直接返回原图
      if not watermark_config or watermark_config.get('type') not in ['text', 'image']:
        return image

      # 创建图像副本避免修改原图
      result_image = image.copy()

      # 根据水印类型生成水印
      watermark = None

      if watermark_config.get('type') == 'text':
        # 文本水印
        text_config = watermark_config.get('text', {})
        text_content = text_config.get('content', '水印文本')
        font_size = text_config.get('font_size', 36)
        opacity = text_config.get('opacity', 0.8)

        # 计算透明度（0-255）
        alpha = int(opacity * 255)
        color = (255, 255, 255, alpha)  # 白色文本
        shadow_color = (0, 0, 0, alpha // 2)  # 半透明阴影

        watermark = self.watermark_processor.create_text_watermark(
            text=text_content,
            font_size=font_size,
            color=color,
            shadow=True,
            shadow_offset=(2, 2),
            shadow_color=shadow_color
        )

      elif watermark_config.get('type') == 'image':
        # 图片水印
        image_config = watermark_config.get('image', {})
        image_path = image_config.get('path', '')
        opacity = image_config.get('opacity', 1.0)

        if image_path and os.path.exists(image_path):
          # 计算水印尺寸（不超过原图的1/4）
          max_size = (result_image.width // 4, result_image.height // 4)
          watermark = self.watermark_processor.load_image_watermark(
              image_path, size=max_size, opacity=opacity
          )

      # 如果成功生成水印，应用到图像上
      if watermark:
        # 计算水印位置
        position = self._calculate_watermark_position(
            result_image.size, watermark.size, position_config
        )

        # 应用水印
        result_image = self.watermark_processor.apply_watermark(
            result_image, watermark, position
        )

      return result_image

    except Exception as e:
      self.logger.error(f"应用水印失败: {str(e)}")
      return image

  def _calculate_watermark_position(self, image_size, watermark_size, position_config):
    """
    计算水印位置

    Args:
        image_size: 图像尺寸 (width, height)
        watermark_size: 水印尺寸 (width, height)
        position_config: 位置配置

    Returns:
        水印位置 (x, y)
    """
    try:
      img_width, img_height = image_size
      wm_width, wm_height = watermark_size

      # 边距
      margin = 20

      # 获取位置配置
      position = position_config.get('position', 'bottom_right')

      # 根据位置计算坐标
      position_map = {
          'top_left': (margin, margin),
          'top_center': ((img_width - wm_width) // 2, margin),
          'top_right': (img_width - wm_width - margin, margin),
          'middle_left': (margin, (img_height - wm_height) // 2),
          'center': ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
          'middle_right': (img_width - wm_width - margin, (img_height - wm_height) // 2),
          'bottom_left': (margin, img_height - wm_height - margin),
          'bottom_center': ((img_width - wm_width) // 2, img_height - wm_height - margin),
          'bottom_right': (img_width - wm_width - margin, img_height - wm_height - margin)
      }

      return position_map.get(position, position_map['bottom_right'])

    except Exception as e:
      self.logger.error(f"计算水印位置失败: {str(e)}")
      return (20, 20)

  def _on_drop_files(self, event):
    """处理拖拽文件事件"""
    try:
      files = self.root.tk.splitlist(event.data)
      if files:
        self._process_dropped_files(files)
    except Exception as e:
      self.logger.error(f"处理拖拽文件失败: {str(e)}")

  def _process_dropped_files(self, files):
    """处理拖拽的文件列表"""
    try:
      # 如果文件数量较少，直接处理不显示进度
      if len(files) <= 5:
        result = self._import_files_simple(files)
      else:
        # 使用进度对话框处理大量文件
        progress = ProgressDialog(self.root, "导入图片")
        result = progress.run_task(self._import_files_with_progress, files)

      imported_count, error_count, error_details = result

      # 更新UI
      if imported_count > 0:
        if self.image_list_panel:
          self.image_list_panel.refresh_list(self.file_manager.get_file_list())
        # 更新导航按钮
        self._update_navigation_buttons()

        # 显示结果消息
        message = f"成功导入 {imported_count} 张图片"
        if error_count > 0:
          message += f"，{error_count} 个文件导入失败"
          if error_details:
            # 只显示前5个错误
            message += f"\n\n错误详情:\n{chr(10).join(error_details[:5])}"
        messagebox.showinfo("导入完成", message)
      elif error_count > 0:
        error_msg = f"导入失败，{error_count} 个文件格式不支持或无法访问"
        if error_details:
          error_msg += f"\n\n错误详情:\n{chr(10).join(error_details[:5])}"
        messagebox.showerror("导入失败", error_msg)

    except Exception as e:
      self.logger.error(f"处理拖拽文件失败: {str(e)}")
      messagebox.showerror("错误", f"处理文件时出现错误: {str(e)}")

  def _import_files_simple(self, files):
    """简单文件导入（无进度显示）"""
    imported_count = 0
    error_count = 0
    error_details = []

    for file_path in files:
      file_path = str(file_path).strip('{}')  # 清理路径格式

      try:
        if os.path.isfile(file_path):
          # 单个文件
          if self.file_manager.is_supported_format(file_path):
            success = self.file_manager.add_file(file_path)
            if success:
              imported_count += 1
            else:
              error_count += 1
              error_details.append(f"添加文件失败: {os.path.basename(file_path)}")
          else:
            error_count += 1
            error_details.append(f"不支持的格式: {os.path.basename(file_path)}")

        elif os.path.isdir(file_path):
          # 文件夹
          folder_files = self.file_manager.scan_folder_for_images(file_path)
          for img_path in folder_files:
            success = self.file_manager.add_file(img_path)
            if success:
              imported_count += 1
            else:
              error_count += 1
              error_details.append(f"添加文件失败: {os.path.basename(img_path)}")
      except Exception as e:
        error_count += 1
        error_details.append(
            f"处理文件错误: {os.path.basename(file_path)} - {str(e)}")

    return imported_count, error_count, error_details

  def _import_files_with_progress(self, progress_dialog, files):
    """带进度显示的文件导入"""
    imported_count = 0
    error_count = 0
    error_details = []

    # 第一步：扫描所有文件
    progress_dialog.update_progress(0, "正在扫描文件...")
    all_files = []

    for i, file_path in enumerate(files):
      if progress_dialog.is_cancelled():
        break

      file_path = str(file_path).strip('{}')

      if os.path.isfile(file_path):
        all_files.append(file_path)
      elif os.path.isdir(file_path):
        folder_files = self.file_manager.scan_folder_for_images(file_path)
        all_files.extend(folder_files)

      progress = (i + 1) / len(files) * 20  # 扫描阶段占总进度的20%
      progress_dialog.update_progress(
          progress, f"正在扫描文件... ({i+1}/{len(files)})")

    if progress_dialog.is_cancelled():
      return 0, 0, []

    # 第二步：导入文件
    total_files = len(all_files)
    for i, file_path in enumerate(all_files):
      if progress_dialog.is_cancelled():
        break

      try:
        if self.file_manager.is_supported_format(file_path):
          success = self.file_manager.add_file(file_path)
          if success:
            imported_count += 1
          else:
            error_count += 1
            error_details.append(f"添加文件失败: {os.path.basename(file_path)}")
        else:
          error_count += 1
          error_details.append(f"不支持的格式: {os.path.basename(file_path)}")
      except Exception as e:
        error_count += 1
        error_details.append(
            f"处理文件错误: {os.path.basename(file_path)} - {str(e)}")

      # 更新进度
      progress = 20 + (i + 1) / total_files * 80  # 导入阶段占总进度的80%
      progress_dialog.update_progress(
          progress, f"正在导入图片... ({i+1}/{total_files})")

    return imported_count, error_count, error_details

  # 文件操作方法
  def _import_images(self):
    """导入图片"""
    try:
      file_paths = filedialog.askopenfilenames(
          title="选择图片文件",
          filetypes=[
              ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
              ("JPEG文件", "*.jpg *.jpeg"),
              ("PNG文件", "*.png"),
              ("BMP文件", "*.bmp"),
              ("TIFF文件", "*.tiff"),
              ("所有文件", "*.*")
          ]
      )

      if file_paths:
        self._process_dropped_files(file_paths)

    except Exception as e:
      self.logger.error(f"导入图片失败: {str(e)}")
      messagebox.showerror("错误", f"导入图片时出现错误: {str(e)}")

  def _import_folder(self):
    """导入文件夹"""
    try:
      folder_path = filedialog.askdirectory(
          title="选择包含图片的文件夹"
      )

      if folder_path:
        self._process_dropped_files([folder_path])

    except Exception as e:
      self.logger.error(f"导入文件夹失败: {str(e)}")
      messagebox.showerror("错误", f"导入文件夹时出现错误: {str(e)}")

  def _export_current_image(self):
    """导出当前图片"""
    pass

  def _export_all_images(self):
    """批量导出"""
    pass

  # 其他方法（后续实现）

  def _copy_watermark_settings(self):
    pass

  def _paste_watermark_settings(self):
    pass

  def _save_watermark_template(self):
    pass

  def _load_watermark_template(self):
    pass

  def _manage_templates(self):
    pass

  def _show_help(self):
    pass

  def _show_about(self):
    pass

  def _setup_keyboard_shortcuts(self):
    """设置键盘快捷键"""
    try:
      # 文件操作快捷键
      self.root.bind('<Control-o>', lambda e: self._import_images())
      self.root.bind('<Control-O>', lambda e: self._import_folder())
      self.root.bind('<Control-s>', lambda e: self._export_current_image())
      self.root.bind('<Control-S>', lambda e: self._export_all_images())
      self.root.bind('<Control-q>', lambda e: self._on_window_close())

      # 编辑操作快捷键
      self.root.bind('<Control-Delete>', lambda e: self._clear_image_list())
      self.root.bind('<Delete>', lambda e: self._remove_selected_image())

      # 导航快捷键
      self.root.bind('<Left>', lambda e: self._on_image_switch('prev'))
      self.root.bind('<Right>', lambda e: self._on_image_switch('next'))
      self.root.bind('<Up>', lambda e: self._on_image_switch('prev'))
      self.root.bind('<Down>', lambda e: self._on_image_switch('next'))

      # 视图操作快捷键
      self.root.bind('<Control-plus>', lambda e: self._zoom_in())
      self.root.bind('<Control-equal>',
                     lambda e: self._zoom_in())  # = 键不需要Shift
      self.root.bind('<Control-KeyPress-equal>', lambda e: self._zoom_in())
      self.root.bind('<Control-minus>', lambda e: self._zoom_out())
      self.root.bind('<Control-0>', lambda e: self._fit_to_window())
      self.root.bind('<Control-1>', lambda e: self._actual_size())

      # 鼠标滚轮缩放（需要Ctrl键）
      self.root.bind('<Control-MouseWheel>', self._on_ctrl_mouse_wheel)

      # ESC 键清除选择
      self.root.bind('<Escape>', lambda e: self._clear_selection())

      # F5 刷新
      self.root.bind('<F5>', lambda e: self._refresh_current_image())

      self.logger.info("键盘快捷键设置完成")

    except Exception as e:
      self.logger.error(f"设置键盘快捷键失败: {str(e)}")

  def _clear_selection(self):
    """清除当前选择"""
    try:
      if self.image_list_panel:
        self.image_list_panel.select_image(-1)
    except Exception as e:
      self.logger.error(f"清除选择失败: {str(e)}")

  def _refresh_current_image(self):
    """刷新当前图像"""
    try:
      if self.current_image_index >= 0:
        self._on_image_selection_change(self.current_image_index)
    except Exception as e:
      self.logger.error(f"刷新当前图像失败: {str(e)}")

  def _zoom_in(self):
    """放大预览"""
    try:
      if self.preview_panel and hasattr(self.preview_panel, '_zoom_in'):
        self.preview_panel._zoom_in()
    except Exception as e:
      self.logger.error(f"放大失败: {str(e)}")

  def _zoom_out(self):
    """缩小预览"""
    try:
      if self.preview_panel and hasattr(self.preview_panel, '_zoom_out'):
        self.preview_panel._zoom_out()
    except Exception as e:
      self.logger.error(f"缩小失败: {str(e)}")

  def _fit_to_window(self):
    """适应窗口"""
    try:
      if self.preview_panel and hasattr(self.preview_panel, '_fit_to_window'):
        self.preview_panel._fit_to_window()
    except Exception as e:
      self.logger.error(f"适应窗口失败: {str(e)}")

  def _actual_size(self):
    """实际大小"""
    try:
      if self.preview_panel and hasattr(self.preview_panel, '_actual_size'):
        self.preview_panel._actual_size()
    except Exception as e:
      self.logger.error(f"实际大小失败: {str(e)}")

  def _on_ctrl_mouse_wheel(self, event):
    """处理Ctrl+鼠标滚轮缩放"""
    try:
      if event.delta > 0:
        self._zoom_in()
      else:
        self._zoom_out()
    except Exception as e:
      self.logger.error(f"处理鼠标滚轮缩放失败: {str(e)}")

  def _remove_selected_image(self):
    """删除选中的图片"""
    try:
      if self.current_image_index >= 0:
        self._on_remove_image(self.current_image_index)
    except Exception as e:
      self.logger.error(f"删除选中图片失败: {str(e)}")

  def _clear_image_list(self):
    """清空图片列表"""
    try:
      if self.file_manager.get_file_count() == 0:
        messagebox.showinfo("提示", "列表为空，无需清空。")
        return

      result = messagebox.askyesno(
          "确认清空",
          "确定要清空所有图片吗？此操作不可撤销。"
      )

      if result:
        # 清空文件管理器
        self.file_manager.clear_all()

        # 清空图片列表面板
        if self.image_list_panel:
          self.image_list_panel.refresh_list([])

        # 清空预览
        self.current_image = None
        self.current_image_index = -1
        self.current_preview_image = None
        if self.preview_panel:
          self.preview_panel.clear_preview()

        self.logger.info("已清空图片列表")
        messagebox.showinfo("完成", "已成功清空所有图片。")

    except Exception as e:
      self.logger.error(f"清空图片列表失败: {str(e)}")
      messagebox.showerror("错误", f"清空图片列表时出现错误: {str(e)}")

  def _on_clear_list(self):
    """统一调用_clear_image_list方法"""
    self._clear_image_list()

  def _on_window_close(self):
    """窗口关闭事件"""
    try:
      # 清理资源
      if self.image_list_panel and hasattr(self.image_list_panel, 'destroy'):
        self.image_list_panel.destroy()

      self._save_config()
      self.root.destroy()
    except Exception as e:
      self.logger.error(f"关闭窗口失败: {str(e)}")
      self.root.destroy()
