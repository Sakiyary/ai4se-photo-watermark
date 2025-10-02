#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, List
from pathlib import Path

from ..core import ImageProcessor, WatermarkProcessor, FileManager, ConfigManager, ImageExporter
from ..utils.constants import *
from ..utils.helpers import center_window, get_system_fonts
from .widgets.image_list_panel import ImageListPanel
from .widgets.preview_panel import PreviewPanel
from .widgets.watermark_control_panel import WatermarkControlPanel
from .widgets.position_control_panel import PositionControlPanel

logger = logging.getLogger(__name__)

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
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
            window_size = self.config_manager.get_config('app.window_size') or DEFAULT_WINDOW_SIZE
            window_pos = self.config_manager.get_config('app.window_position') or DEFAULT_WINDOW_POSITION
            
            self.root.geometry(f"{window_size[0]}x{window_size[1]}+{window_pos[0]}+{window_pos[1]}")
            self.root.minsize(*MIN_WINDOW_SIZE)
            
            # 居中显示
            center_window(self.root, window_size[0], window_size[1])
            
            # 窗口关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
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
            file_menu.add_command(label="导入图片...", command=self._import_images, accelerator="Ctrl+O")
            file_menu.add_command(label="导入文件夹...", command=self._import_folder, accelerator="Ctrl+Shift+O")
            file_menu.add_separator()
            file_menu.add_command(label="导出当前图片...", command=self._export_current_image, accelerator="Ctrl+S")
            file_menu.add_command(label="批量导出...", command=self._export_all_images, accelerator="Ctrl+Shift+S")
            file_menu.add_separator()
            file_menu.add_command(label="退出", command=self._on_window_close, accelerator="Ctrl+Q")
            
            # 编辑菜单
            edit_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="编辑", menu=edit_menu)
            edit_menu.add_command(label="清空图片列表", command=self._clear_image_list)
            edit_menu.add_separator()
            edit_menu.add_command(label="复制水印设置", command=self._copy_watermark_settings)
            edit_menu.add_command(label="粘贴水印设置", command=self._paste_watermark_settings)
            
            # 水印菜单
            watermark_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="水印", menu=watermark_menu)
            watermark_menu.add_command(label="保存为模板...", command=self._save_watermark_template)
            watermark_menu.add_command(label="加载模板...", command=self._load_watermark_template)
            watermark_menu.add_command(label="管理模板...", command=self._manage_templates)
            
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
            ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            # 导出按钮
            ttk.Button(self.toolbar, text="导出当前", 
                      command=self._export_current_image).pack(side=tk.LEFT, padx=2)
            ttk.Button(self.toolbar, text="批量导出", 
                      command=self._export_all_images).pack(side=tk.LEFT, padx=2)
            
            # 分隔符
            ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
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
                on_remove_image=self._on_remove_image
            )
            
            # 预览面板
            self.preview_panel = PreviewPanel(
                self.center_frame,
                on_position_change=self._on_watermark_position_change
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
        """设置拖拽支持（简化版）"""
        try:
            # 这里实现一个简化的拖拽功能
            # 在实际项目中可以使用tkinterdnd2库
            pass
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
                self.position_control_panel.load_config(watermark_config.get('position', {}))
                
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
    
    def _save_config(self):
        """保存配置"""
        try:
            # 保存窗口状态
            geometry = self.root.geometry()
            size_pos = geometry.split('+')
            size = size_pos[0].split('x')
            
            self.config_manager.set_config('app.window_size', [int(size[0]), int(size[1])])
            if len(size_pos) > 2:
                self.config_manager.set_config('app.window_position', [int(size_pos[1]), int(size_pos[2])])
            
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
                        return
            
            # 清空预览
            self.current_image = None
            self.current_image_index = -1
            if self.preview_panel:
                self.preview_panel.clear_preview()
                
        except Exception as e:
            self.logger.error(f"处理图片选择事件失败: {str(e)}")
    
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
            if not (self.watermark_control_panel and self.position_control_panel):
                return
                
            watermark_config = self.watermark_control_panel.get_config()
            position_config = self.position_control_panel.get_config()
            
            # 生成水印预览
            preview_image = self._apply_watermark_to_image(
                self.current_image, watermark_config, position_config)
            
            if preview_image:
                self.current_preview_image = preview_image
                self.preview_panel.update_preview(preview_image)
                
        except Exception as e:
            self.logger.error(f"更新预览失败: {str(e)}")
    
    def _apply_watermark_to_image(self, image, watermark_config, position_config):
        """应用水印到图像"""
        try:
            # 这里是水印应用的核心逻辑，暂时返回原图
            # 后续会实现完整的水印应用功能
            return image
        except Exception as e:
            self.logger.error(f"应用水印失败: {str(e)}")
            return image
    
    # 文件操作方法（后续实现）
    def _import_images(self):
        """导入图片"""
        pass
    
    def _import_folder(self):
        """导入文件夹"""
        pass
    
    def _export_current_image(self):
        """导出当前图片"""
        pass
    
    def _export_all_images(self):
        """批量导出"""
        pass
    
    def _clear_image_list(self):
        """清空图片列表"""
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
    
    def _on_window_close(self):
        """窗口关闭事件"""
        try:
            self._save_config()
            self.root.destroy()
        except Exception as e:
            self.logger.error(f"关闭窗口失败: {str(e)}")
            self.root.destroy()