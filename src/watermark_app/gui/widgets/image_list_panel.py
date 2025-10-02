#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片列表面板组件
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class ImageListPanel:
    """图片列表面板"""
    
    def __init__(self, parent: tk.Widget, 
                 on_selection_change: Optional[Callable[[int], None]] = None,
                 on_remove_image: Optional[Callable[[int], None]] = None):
        """
        初始化图片列表面板
        
        Args:
            parent: 父容器
            on_selection_change: 选择改变回调
            on_remove_image: 移除图片回调
        """
        self.parent = parent
        self.on_selection_change = on_selection_change
        self.on_remove_image = on_remove_image
        self.logger = logging.getLogger(__name__)
        
        # 数据
        self.image_list = []
        self.selected_index = -1
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        try:
            # 主容器
            main_frame = ttk.Frame(self.parent)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = ttk.Label(main_frame, text="图片列表", font=('Arial', 12, 'bold'))
            title_label.pack(pady=5)
            
            # 列表框架
            list_frame = ttk.Frame(main_frame)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建Treeview
            columns = ('name', 'size', 'format')
            self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
            
            # 设置列标题
            self.tree.heading('name', text='文件名')
            self.tree.heading('size', text='大小')
            self.tree.heading('format', text='格式')
            
            # 设置列宽
            self.tree.column('name', width=150, minwidth=100)
            self.tree.column('size', width=80, minwidth=60)
            self.tree.column('format', width=60, minwidth=40)
            
            # 滚动条
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            
            # 打包
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # 按钮
            ttk.Button(button_frame, text="移除选中", 
                      command=self._remove_selected).pack(side=tk.LEFT, padx=2)
            ttk.Button(button_frame, text="清空列表", 
                      command=self._clear_all).pack(side=tk.LEFT, padx=2)
            
            # 绑定事件
            self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
            self.tree.bind('<Double-1>', self._on_double_click)
            
        except Exception as e:
            self.logger.error(f"创建图片列表界面失败: {str(e)}")
    
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
                
                self.tree.insert('', tk.END, values=(name, size, format_ext), tags=(str(i),))
            
            self.logger.info(f"刷新图片列表完成，共 {len(image_list)} 个文件")
            
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
                
                self.tree.insert('', tk.END, values=(name, size, format_ext), 
                                tags=(str(start_index + i),))
                
                self.image_list.append(image_info)
            
            self.logger.info(f"添加 {len(image_list)} 个图片到列表")
            
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
            # 清空树形视图
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 清空数据
            self.image_list.clear()
            self.selected_index = -1
            
            # 通知选择改变
            if self.on_selection_change:
                self.on_selection_change(-1)
                
            self.logger.info("已清空图片列表")
            
        except Exception as e:
            self.logger.error(f"清空图片列表失败: {str(e)}")
    
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