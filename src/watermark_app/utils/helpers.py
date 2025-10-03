#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助工具函数
"""

import os
import sys
import platform
from typing import Tuple, List, Optional, Any
from pathlib import Path
import tkinter as tk
from tkinter import font

def get_system_fonts() -> List[str]:
    """
    获取系统可用字体列表
    
    Returns:
        字体名称列表
    """
    try:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        font_families = list(font.families())
        root.destroy()
        return sorted(font_families)
    except Exception:
        # 返回基本字体
        return ['Arial', 'Times New Roman', 'Courier New', 'Helvetica']

def get_system_info() -> dict:
    """
    获取系统信息
    
    Returns:
        系统信息字典
    """
    return {
        'system': platform.system(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'platform': platform.platform()
    }

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def validate_color_tuple(color: Any) -> bool:
    """
    验证颜色元组格式
    
    Args:
        color: 颜色值
        
    Returns:
        是否为有效的颜色元组
    """
    try:
        if not isinstance(color, (tuple, list)):
            return False
        
        if len(color) not in (3, 4):  # RGB或RGBA
            return False
        
        for component in color:
            if not isinstance(component, int) or not (0 <= component <= 255):
                return False
        
        return True
    except Exception:
        return False

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    RGB颜色转换为十六进制
    
    Args:
        rgb: RGB颜色元组
        
    Returns:
        十六进制颜色字符串
    """
    try:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except Exception:
        return "#FFFFFF"

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    十六进制颜色转换为RGB
    
    Args:
        hex_color: 十六进制颜色字符串
        
    Returns:
        RGB颜色元组
    """
    try:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Invalid hex color")
        
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return (255, 255, 255)

def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """
    限制数值在指定范围内
    
    Args:
        value: 要限制的值
        min_val: 最小值
        max_val: 最大值
        
    Returns:
        限制后的值
    """
    return max(min_val, min(max_val, value))

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 除零时的默认值
        
    Returns:
        除法结果
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default

def center_window(window: tk.Tk, width: int, height: int):
    """
    将窗口居中显示
    
    Args:
        window: Tkinter窗口对象
        width: 窗口宽度
        height: 窗口高度
    """
    try:
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置和大小
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        # 如果失败，使用默认位置
        window.geometry(f"{width}x{height}")

def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的完整路径，支持打包后的应用
    
    Args:
        relative_path: 相对路径
        
    Returns:
        资源文件的完整路径
    """
    try:
        # PyInstaller打包后的路径
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        
        # 开发环境路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'resources', relative_path)
    except Exception:
        return relative_path

def ensure_directory_exists(directory_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
        
    Returns:
        是否成功（目录存在或创建成功）
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def get_unique_filename(directory: str, filename: str) -> str:
    """
    获取唯一的文件名，如果文件已存在则添加序号
    
    Args:
        directory: 目录路径
        filename: 原文件名
        
    Returns:
        唯一的文件名
    """
    try:
        path = Path(directory) / filename
        if not path.exists():
            return filename
        
        stem = path.stem
        suffix = path.suffix
        counter = 1
        
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_path = Path(directory) / new_filename
            if not new_path.exists():
                return new_filename
            counter += 1
            
            # 防止无限循环
            if counter > 9999:
                import time
                timestamp = int(time.time())
                return f"{stem}_{timestamp}{suffix}"
                
    except Exception:
        import time
        timestamp = int(time.time())
        return f"file_{timestamp}.png"

def is_valid_image_size(width: int, height: int, max_size: Tuple[int, int] = (10000, 10000)) -> bool:
    """
    检查图像尺寸是否有效
    
    Args:
        width: 图像宽度
        height: 图像高度
        max_size: 最大允许尺寸
        
    Returns:
        尺寸是否有效
    """
    try:
        return (0 < width <= max_size[0] and 
                0 < height <= max_size[1])
    except Exception:
        return False

def calculate_aspect_ratio(width: int, height: int) -> float:
    """
    计算宽高比
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        宽高比
    """
    return safe_divide(width, height, 1.0)

def resize_maintain_aspect_ratio(original_size: Tuple[int, int], 
                                target_size: Tuple[int, int]) -> Tuple[int, int]:
    """
    计算保持宽高比的新尺寸
    
    Args:
        original_size: 原始尺寸 (width, height)
        target_size: 目标最大尺寸 (max_width, max_height)
        
    Returns:
        新尺寸 (width, height)
    """
    try:
        orig_width, orig_height = original_size
        max_width, max_height = target_size
        
        # 计算缩放比例
        width_ratio = max_width / orig_width
        height_ratio = max_height / orig_height
        scale_ratio = min(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(orig_width * scale_ratio)
        new_height = int(orig_height * scale_ratio)
        
        return (new_width, new_height)
    except Exception:
        return target_size