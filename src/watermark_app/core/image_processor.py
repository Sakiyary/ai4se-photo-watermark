#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像处理核心模块
负责图像的基本处理操作，包括加载、缩放、格式转换等
"""

import os
import logging
from typing import Optional, Tuple, List
from PIL import Image, ImageTk
import tkinter as tk

logger = logging.getLogger(__name__)

class ImageProcessor:
    """图像处理器类"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
    }
    
    def __init__(self):
        """初始化图像处理器"""
        self.logger = logging.getLogger(__name__)
        
    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持该格式
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in cls.SUPPORTED_FORMATS
    
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """
        加载图像文件
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            PIL.Image对象，加载失败返回None
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"文件不存在: {file_path}")
                return None
                
            if not self.is_supported_format(file_path):
                self.logger.error(f"不支持的文件格式: {file_path}")
                return None
                
            # 加载图像
            image = Image.open(file_path)
            
            # 确保图像模式正确
            if image.mode not in ('RGB', 'RGBA'):
                if image.mode == 'P' and 'transparency' in image.info:
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')
            
            self.logger.info(f"成功加载图像: {file_path}, 尺寸: {image.size}, 模式: {image.mode}")
            return image
            
        except Exception as e:
            self.logger.error(f"加载图像失败 {file_path}: {str(e)}")
            return None
    
    def resize_image(self, image: Image.Image, target_size: Tuple[int, int], 
                    keep_aspect_ratio: bool = True) -> Image.Image:
        """
        调整图像尺寸
        
        Args:
            image: PIL图像对象
            target_size: 目标尺寸 (width, height)
            keep_aspect_ratio: 是否保持宽高比
            
        Returns:
            调整后的PIL图像对象
        """
        try:
            if keep_aspect_ratio:
                # 计算保持宽高比的新尺寸
                image.thumbnail(target_size, Image.Resampling.LANCZOS)
                return image
            else:
                # 直接调整到指定尺寸
                return image.resize(target_size, Image.Resampling.LANCZOS)
                
        except Exception as e:
            self.logger.error(f"调整图像尺寸失败: {str(e)}")
            return image
    
    def create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (150, 150)) -> Image.Image:
        """
        创建缩略图
        
        Args:
            image: 原始图像
            size: 缩略图尺寸
            
        Returns:
            缩略图图像
        """
        try:
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            return thumbnail
        except Exception as e:
            self.logger.error(f"创建缩略图失败: {str(e)}")
            return image
    
    def image_to_tkinter(self, image: Image.Image) -> Optional[ImageTk.PhotoImage]:
        """
        将PIL图像转换为Tkinter可用的PhotoImage
        
        Args:
            image: PIL图像对象
            
        Returns:
            ImageTk.PhotoImage对象
        """
        try:
            return ImageTk.PhotoImage(image)
        except Exception as e:
            self.logger.error(f"转换为Tkinter图像失败: {str(e)}")
            return None
    
    def get_image_info(self, image: Image.Image) -> dict:
        """
        获取图像信息
        
        Args:
            image: PIL图像对象
            
        Returns:
            包含图像信息的字典
        """
        return {
            'size': image.size,
            'mode': image.mode,
            'format': getattr(image, 'format', 'Unknown'),
            'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
        }
    
    def validate_image_file(self, file_path: str) -> Tuple[bool, str]:
        """
        验证图像文件是否有效
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            if not os.path.exists(file_path):
                return False, "文件不存在"
                
            if not self.is_supported_format(file_path):
                return False, "不支持的文件格式"
                
            # 尝试打开文件验证
            with Image.open(file_path) as img:
                img.verify()
                
            return True, ""
            
        except Exception as e:
            return False, f"文件验证失败: {str(e)}"