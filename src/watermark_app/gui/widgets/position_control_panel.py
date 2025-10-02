#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
位置控制面板组件（简化版）
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Callable, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class PositionControlPanel:
    """位置控制面板"""
    
    def __init__(self, parent: tk.Widget,
                 on_position_change: Optional[Callable[[], None]] = None):
        """
        初始化位置控制面板
        
        Args:
            parent: 父容器
            on_position_change: 位置改变回调
        """
        self.parent = parent
        self.on_position_change = on_position_change
        self.logger = logging.getLogger(__name__)
        
        # 位置按钮
        self.position_buttons = {}
        
        # 创建界面
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        try:
            # 主容器
            main_frame = ttk.Frame(self.parent)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 位置选择
            position_frame = ttk.LabelFrame(main_frame, text="水印位置")
            position_frame.pack(fill=tk.X, pady=5)
            
            # 九宫格位置
            grid_frame = ttk.Frame(position_frame)
            grid_frame.pack(pady=10)
            
            # 当前选中位置
            self.selected_position = tk.StringVar(value="bottom_right")
            
            # 创建九宫格按钮
            positions = [
                ("top_left", "左上", 0, 0),
                ("top_center", "上中", 0, 1),
                ("top_right", "右上", 0, 2),
                ("middle_left", "左中", 1, 0),
                ("center", "中心", 1, 1),
                ("middle_right", "右中", 1, 2),
                ("bottom_left", "左下", 2, 0),
                ("bottom_center", "下中", 2, 1),
                ("bottom_right", "右下", 2, 2)
            ]
            
            for pos_id, text, row, col in positions:
                btn = tk.Radiobutton(
                    grid_frame,
                    text=text,
                    variable=self.selected_position,
                    value=pos_id,
                    command=self._on_position_change,
                    indicatoron=False,
                    width=8,
                    height=2
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                self.position_buttons[pos_id] = btn
            
            # 边距设置
            margin_frame = ttk.LabelFrame(main_frame, text="边距设置")
            margin_frame.pack(fill=tk.X, pady=5)
            
            # 水平边距
            h_margin_frame = ttk.Frame(margin_frame)
            h_margin_frame.pack(fill=tk.X, pady=2)
            ttk.Label(h_margin_frame, text="水平边距:").pack(side=tk.LEFT)
            self.h_margin = tk.IntVar(value=20)
            h_spinbox = ttk.Spinbox(h_margin_frame, from_=0, to=200, width=10,
                                   textvariable=self.h_margin, command=self._on_setting_change)
            h_spinbox.pack(side=tk.RIGHT)
            
            # 垂直边距
            v_margin_frame = ttk.Frame(margin_frame)
            v_margin_frame.pack(fill=tk.X, pady=2)
            ttk.Label(v_margin_frame, text="垂直边距:").pack(side=tk.LEFT)
            self.v_margin = tk.IntVar(value=20)
            v_spinbox = ttk.Spinbox(v_margin_frame, from_=0, to=200, width=10,
                                   textvariable=self.v_margin, command=self._on_setting_change)
            v_spinbox.pack(side=tk.RIGHT)
            
            # 旋转设置
            rotation_frame = ttk.LabelFrame(main_frame, text="旋转设置")
            rotation_frame.pack(fill=tk.X, pady=5)
            
            rot_frame = ttk.Frame(rotation_frame)
            rot_frame.pack(fill=tk.X, pady=2)
            ttk.Label(rot_frame, text="旋转角度:").pack(side=tk.LEFT)
            self.rotation = tk.IntVar(value=0)
            rot_scale = ttk.Scale(rot_frame, from_=-180, to=180, orient=tk.HORIZONTAL,
                                 variable=self.rotation, command=self._on_setting_change)
            rot_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
            
            # 显示角度值
            self.rotation_label = ttk.Label(rotation_frame, text="0°")
            self.rotation_label.pack()
            
            # 重置按钮
            reset_frame = ttk.Frame(main_frame)
            reset_frame.pack(fill=tk.X, pady=5)
            ttk.Button(reset_frame, text="重置位置", command=self._reset_position).pack(side=tk.LEFT)
            ttk.Button(reset_frame, text="重置边距", command=self._reset_margins).pack(side=tk.LEFT, padx=5)
            ttk.Button(reset_frame, text="重置旋转", command=self._reset_rotation).pack(side=tk.LEFT)
            
        except Exception as e:
            self.logger.error(f"创建位置控制界面失败: {str(e)}")
    
    def _on_position_change(self):
        """位置改变"""
        try:
            self._notify_change()
        except Exception as e:
            self.logger.error(f"处理位置改变失败: {str(e)}")
    
    def _on_setting_change(self, event=None):
        """设置改变"""
        try:
            # 更新旋转角度显示
            angle = self.rotation.get()
            self.rotation_label.config(text=f"{angle}°")
            
            self._notify_change()
        except Exception as e:
            self.logger.error(f"处理设置改变失败: {str(e)}")
    
    def _reset_position(self):
        """重置位置"""
        try:
            self.selected_position.set("bottom_right")
            self._notify_change()
        except Exception as e:
            self.logger.error(f"重置位置失败: {str(e)}")
    
    def _reset_margins(self):
        """重置边距"""
        try:
            self.h_margin.set(20)
            self.v_margin.set(20)
            self._notify_change()
        except Exception as e:
            self.logger.error(f"重置边距失败: {str(e)}")
    
    def _reset_rotation(self):
        """重置旋转"""
        try:
            self.rotation.set(0)
            self.rotation_label.config(text="0°")
            self._notify_change()
        except Exception as e:
            self.logger.error(f"重置旋转失败: {str(e)}")
    
    def _notify_change(self):
        """通知改变"""
        if self.on_position_change:
            self.on_position_change()
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        try:
            config = {
                'position': self.selected_position.get(),
                'margins': {
                    'horizontal': self.h_margin.get(),
                    'vertical': self.v_margin.get()
                },
                'rotation': self.rotation.get()
            }
            return config
        except Exception as e:
            self.logger.error(f"获取配置失败: {str(e)}")
            return {}
    
    def load_config(self, config: Dict[str, Any]):
        """载入配置"""
        try:
            if 'position' in config:
                self.selected_position.set(config['position'])
            
            if 'margins' in config:
                margins = config['margins']
                if 'horizontal' in margins:
                    self.h_margin.set(margins['horizontal'])
                if 'vertical' in margins:
                    self.v_margin.set(margins['vertical'])
            
            if 'rotation' in config:
                self.rotation.set(config['rotation'])
                self.rotation_label.config(text=f"{config['rotation']}°")
            
        except Exception as e:
            self.logger.error(f"载入配置失败: {str(e)}")
    
    def get_position_coordinates(self, image_size: Tuple[int, int], 
                               watermark_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        计算水印位置坐标
        
        Args:
            image_size: 图片尺寸 (width, height)
            watermark_size: 水印尺寸 (width, height)
        
        Returns:
            水印位置坐标 (x, y)
        """
        try:
            img_w, img_h = image_size
            wm_w, wm_h = watermark_size
            h_margin = self.h_margin.get()
            v_margin = self.v_margin.get()
            
            position = self.selected_position.get()
            
            # 计算基础位置
            if position.startswith("top"):
                y = v_margin
            elif position.startswith("middle"):
                y = (img_h - wm_h) // 2
            else:  # bottom
                y = img_h - wm_h - v_margin
            
            if position.endswith("left"):
                x = h_margin
            elif position.endswith("center"):
                x = (img_w - wm_w) // 2
            else:  # right
                x = img_w - wm_w - h_margin
            
            return (x, y)
            
        except Exception as e:
            self.logger.error(f"计算位置坐标失败: {str(e)}")
            return (0, 0)