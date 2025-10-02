#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印控制面板组件（简化版）
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)

class WatermarkControlPanel:
    """水印控制面板"""
    
    def __init__(self, parent: tk.Widget,
                 on_watermark_change: Optional[Callable[[], None]] = None):
        """
        初始化水印控制面板
        
        Args:
            parent: 父容器
            on_watermark_change: 水印改变回调
        """
        self.parent = parent
        self.on_watermark_change = on_watermark_change
        self.logger = logging.getLogger(__name__)
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        try:
            # 主容器
            main_frame = ttk.Frame(self.parent)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 水印类型选择
            type_frame = ttk.LabelFrame(main_frame, text="水印类型")
            type_frame.pack(fill=tk.X, pady=5)
            
            self.watermark_type = tk.StringVar(value="text")
            ttk.Radiobutton(type_frame, text="文本水印", variable=self.watermark_type, 
                           value="text", command=self._on_type_change).pack(anchor=tk.W)
            ttk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type, 
                           value="image", command=self._on_type_change).pack(anchor=tk.W)
            
            # 文本水印设置
            self.text_frame = ttk.LabelFrame(main_frame, text="文本设置")
            self.text_frame.pack(fill=tk.X, pady=5)
            
            # 文本内容
            ttk.Label(self.text_frame, text="文本内容:").pack(anchor=tk.W)
            self.text_entry = ttk.Entry(self.text_frame, width=30)
            self.text_entry.pack(fill=tk.X, pady=2)
            self.text_entry.insert(0, "水印文本")
            self.text_entry.bind('<KeyRelease>', self._on_text_change)
            
            # 字体大小
            size_frame = ttk.Frame(self.text_frame)
            size_frame.pack(fill=tk.X, pady=2)
            ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
            self.font_size = tk.IntVar(value=36)
            size_spinbox = ttk.Spinbox(size_frame, from_=12, to=200, width=10,
                                      textvariable=self.font_size, command=self._on_setting_change)
            size_spinbox.pack(side=tk.RIGHT)
            
            # 透明度
            opacity_frame = ttk.Frame(self.text_frame)
            opacity_frame.pack(fill=tk.X, pady=2)
            ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
            self.opacity = tk.IntVar(value=80)
            opacity_scale = ttk.Scale(opacity_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=self.opacity, command=self._on_setting_change)
            opacity_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
            
            # 图片水印设置（初始隐藏）
            self.image_frame = ttk.LabelFrame(main_frame, text="图片设置")
            
            ttk.Label(self.image_frame, text="水印图片路径:").pack(anchor=tk.W)
            path_frame = ttk.Frame(self.image_frame)
            path_frame.pack(fill=tk.X, pady=2)
            self.image_path = tk.StringVar()
            ttk.Entry(path_frame, textvariable=self.image_path, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(path_frame, text="浏览", command=self._browse_image).pack(side=tk.RIGHT, padx=2)
            
            # 初始显示文本设置
            self._on_type_change()
            
        except Exception as e:
            self.logger.error(f"创建水印控制界面失败: {str(e)}")
    
    def _on_type_change(self):
        """水印类型改变"""
        try:
            if self.watermark_type.get() == "text":
                self.text_frame.pack(fill=tk.X, pady=5)
                self.image_frame.pack_forget()
            else:
                self.text_frame.pack_forget()
                self.image_frame.pack(fill=tk.X, pady=5)
            
            self._notify_change()
        except Exception as e:
            self.logger.error(f"处理水印类型改变失败: {str(e)}")
    
    def _on_text_change(self, event=None):
        """文本改变"""
        self._notify_change()
    
    def _on_setting_change(self, event=None):
        """设置改变"""
        self._notify_change()
    
    def _browse_image(self):
        """浏览图片"""
        from tkinter import filedialog
        try:
            file_path = filedialog.askopenfilename(
                title="选择水印图片",
                filetypes=[
                    ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                    ("PNG文件", "*.png"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                self.image_path.set(file_path)
                self._notify_change()
        except Exception as e:
            self.logger.error(f"浏览图片失败: {str(e)}")
    
    def _notify_change(self):
        """通知改变"""
        if self.on_watermark_change:
            self.on_watermark_change()
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        try:
            config = {
                'type': self.watermark_type.get(),
                'text': {
                    'content': self.text_entry.get(),
                    'font_size': self.font_size.get(),
                    'opacity': self.opacity.get() / 100.0
                },
                'image': {
                    'path': self.image_path.get(),
                    'opacity': 1.0
                }
            }
            return config
        except Exception as e:
            self.logger.error(f"获取配置失败: {str(e)}")
            return {}
    
    def load_config(self, config: Dict[str, Any]):
        """载入配置"""
        try:
            if 'type' in config:
                self.watermark_type.set(config['type'])
            
            if 'text' in config:
                text_config = config['text']
                if 'content' in text_config:
                    self.text_entry.delete(0, tk.END)
                    self.text_entry.insert(0, text_config['content'])
                if 'font_size' in text_config:
                    self.font_size.set(text_config['font_size'])
                if 'opacity' in text_config:
                    self.opacity.set(int(text_config['opacity'] * 100))
            
            if 'image' in config:
                image_config = config['image']
                if 'path' in image_config:
                    self.image_path.set(image_config['path'])
            
            self._on_type_change()
            
        except Exception as e:
            self.logger.error(f"载入配置失败: {str(e)}")