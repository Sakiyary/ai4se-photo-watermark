#!/usr/bin/env python3
"""
Photo Watermark Tool - 照片水印添加程序

This tool adds date watermarks to photos based on EXIF data.
根据 EXIF 数据为照片添加日期水印的工具。

Usage:
    python watermark.py <input_path> [options]

Author: AI Assistant
License: MIT
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.ExifTags import TAGS
except ImportError:
    print("Error: Pillow library is required. Install it using: pip install Pillow")
    sys.exit(1)


class ExifReader:
    """EXIF 数据读取器"""
    
    @staticmethod
    def extract_date(image_path: str) -> Optional[str]:
        """
        从图片的 EXIF 数据中提取拍摄日期
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            格式化的日期字符串 (YYYY-MM-DD) 或 None
        """
        try:
            with Image.open(image_path) as image:
                exif_data = image._getexif()
                
                if exif_data is not None:
                    # 尝试获取拍摄日期，按优先级顺序
                    date_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
                    
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        if tag_name in date_tags:
                            return ExifReader.format_date(value)
                            
        except Exception as e:
            print(f"Warning: Could not read EXIF from {image_path}: {e}")
            
        # 如果无法获取 EXIF 日期，使用文件修改时间
        return ExifReader.get_file_date(image_path)
    
    @staticmethod
    def format_date(date_string: str) -> str:
        """
        格式化日期字符串为 YYYY-MM-DD 格式
        
        Args:
            date_string: 原始日期字符串
            
        Returns:
            格式化的日期字符串
        """
        try:
            # EXIF 日期格式通常是 "YYYY:MM:DD HH:MM:SS"
            if ':' in date_string:
                date_part = date_string.split(' ')[0]
                return date_part.replace(':', '-')
            return date_string
        except Exception:
            return date_string
    
    @staticmethod
    def get_file_date(file_path: str) -> str:
        """
        获取文件修改时间作为备用日期
        
        Args:
            file_path: 文件路径
            
        Returns:
            格式化的日期字符串
        """
        try:
            timestamp = os.path.getmtime(file_path)
            date = datetime.fromtimestamp(timestamp)
            return date.strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')


class WatermarkGenerator:
    """水印生成器"""
    
    def __init__(self, font_size: int = 48, color: str = 'white', position: str = 'bottom-right'):
        """
        初始化水印生成器
        
        Args:
            font_size: 字体大小
            color: 字体颜色
            position: 水印位置
        """
        self.font_size = font_size
        self.color = color
        self.position = position
        self.font = self._load_font()
    
    def _load_font(self) -> ImageFont.ImageFont:
        """
        加载字体
        
        Returns:
            ImageFont 对象
        """
        try:
            # 尝试使用系统默认字体
            return ImageFont.truetype("arial.ttf", self.font_size)
        except (OSError, IOError):
            try:
                # 尝试其他常见字体
                fonts = [
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    "C:/Windows/Fonts/arial.ttf",  # Windows
                ]
                for font_path in fonts:
                    if os.path.exists(font_path):
                        return ImageFont.truetype(font_path, self.font_size)
            except (OSError, IOError):
                pass
            
            # 使用默认字体
            return ImageFont.load_default()
    
    def _calculate_position(self, image_size: Tuple[int, int], text_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        计算水印位置
        
        Args:
            image_size: 图片尺寸 (width, height)
            text_size: 文本尺寸 (width, height)
            
        Returns:
            水印位置坐标 (x, y)
        """
        img_width, img_height = image_size
        text_width, text_height = text_size
        margin = 20  # 边距
        
        if self.position == 'top-left':
            return (margin, margin)
        elif self.position == 'top-right':
            return (img_width - text_width - margin, margin)
        elif self.position == 'center':
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
        elif self.position == 'bottom-left':
            return (margin, img_height - text_height - margin)
        elif self.position == 'bottom-right':
            return (img_width - text_width - margin, img_height - text_height - margin)
        else:
            # 默认右下角
            return (img_width - text_width - margin, img_height - text_height - margin)
    
    def apply_watermark(self, image: Image.Image, text: str) -> Image.Image:
        """
        在图片上应用水印
        
        Args:
            image: PIL Image 对象
            text: 水印文本
            
        Returns:
            带水印的 PIL Image 对象
        """
        # 创建可绘制的图片副本
        watermarked = image.copy()
        draw = ImageDraw.Draw(watermarked)
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        x, y = self._calculate_position(image.size, (text_width, text_height))
        
        # 添加文字阴影效果以提高可读性
        shadow_offset = max(1, self.font_size // 20)
        draw.text((x + shadow_offset, y + shadow_offset), text, font=self.font, fill='black')
        
        # 绘制主文字
        draw.text((x, y), text, font=self.font, fill=self.color)
        
        return watermarked


class FileProcessor:
    """文件处理器"""
    
    def __init__(self, watermark_generator: WatermarkGenerator):
        """
        初始化文件处理器
        
        Args:
            watermark_generator: 水印生成器实例
        """
        self.watermark_generator = watermark_generator
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    
    def create_output_directory(self, base_path: str) -> str:
        """
        创建输出目录
        
        Args:
            base_path: 基础路径
            
        Returns:
            输出目录路径
        """
        if os.path.isfile(base_path):
            parent_dir = os.path.dirname(base_path)
            dir_name = os.path.basename(parent_dir)
        else:
            parent_dir = os.path.dirname(base_path.rstrip(os.sep))
            dir_name = os.path.basename(base_path.rstrip(os.sep))
        
        output_dir = os.path.join(base_path if os.path.isdir(base_path) else parent_dir, 
                                 f"{dir_name}_watermark")
        
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def is_image_file(self, file_path: str) -> bool:
        """
        检查文件是否为支持的图片格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为支持的图片格式
        """
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def process_single_file(self, file_path: str, output_dir: str) -> bool:
        """
        处理单个图片文件
        
        Args:
            file_path: 输入文件路径
            output_dir: 输出目录
            
        Returns:
            处理是否成功
        """
        try:
            print(f"Processing: {file_path}")
            
            # 提取日期
            date_text = ExifReader.extract_date(file_path)
            if not date_text:
                print(f"Warning: Could not extract date from {file_path}")
                return False
            
            # 打开图片
            with Image.open(file_path) as image:
                # 应用水印
                watermarked = self.watermark_generator.apply_watermark(image, date_text)
                
                # 生成输出文件名
                file_name = os.path.basename(file_path)
                output_path = os.path.join(output_dir, file_name)
                
                # 保存图片
                watermarked.save(output_path, quality=95, optimize=True)
                print(f"Saved: {output_path}")
                
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def process_directory(self, dir_path: str) -> Tuple[int, int]:
        """
        处理目录中的所有图片
        
        Args:
            dir_path: 目录路径
            
        Returns:
            (成功处理的文件数, 总文件数)
        """
        if not os.path.isdir(dir_path):
            raise ValueError(f"Directory not found: {dir_path}")
        
        # 创建输出目录
        output_dir = self.create_output_directory(dir_path)
        print(f"Output directory: {output_dir}")
        
        # 查找所有图片文件
        image_files = []
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path) and self.is_image_file(file_path):
                image_files.append(file_path)
        
        if not image_files:
            print(f"No image files found in {dir_path}")
            return 0, 0
        
        print(f"Found {len(image_files)} image files")
        
        # 处理每个文件
        success_count = 0
        for file_path in image_files:
            if self.process_single_file(file_path, output_dir):
                success_count += 1
        
        return success_count, len(image_files)
    
    def process_path(self, input_path: str) -> Tuple[int, int]:
        """
        处理输入路径（文件或目录）
        
        Args:
            input_path: 输入路径
            
        Returns:
            (成功处理的文件数, 总文件数)
        """
        if os.path.isfile(input_path):
            if not self.is_image_file(input_path):
                raise ValueError(f"File is not a supported image format: {input_path}")
            
            # 为单个文件创建输出目录
            output_dir = self.create_output_directory(input_path)
            print(f"Output directory: {output_dir}")
            
            success = self.process_single_file(input_path, output_dir)
            return (1, 1) if success else (0, 1)
        
        elif os.path.isdir(input_path):
            return self.process_directory(input_path)
        else:
            raise ValueError(f"Path not found: {input_path}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Add date watermarks to photos based on EXIF data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watermark.py /path/to/photo.jpg
  python watermark.py /path/to/photos/
  python watermark.py /path/to/photos/ --font-size 36 --color red --position top-left

Supported positions: top-left, top-right, center, bottom-left, bottom-right
Supported colors: white, black, red, green, blue, yellow, or hex codes like #FF0000
        """
    )
    
    parser.add_argument(
        'input_path',
        help='Input image file or directory path'
    )
    
    parser.add_argument(
        '--font-size',
        type=int,
        default=48,
        help='Font size for watermark text (default: 48)'
    )
    
    parser.add_argument(
        '--color',
        default='white',
        help='Font color for watermark text (default: white)'
    )
    
    parser.add_argument(
        '--position',
        choices=['top-left', 'top-right', 'center', 'bottom-left', 'bottom-right'],
        default='bottom-right',
        help='Watermark position (default: bottom-right)'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    try:
        # 解析参数
        args = parse_arguments()
        
        # 验证输入路径
        if not os.path.exists(args.input_path):
            print(f"Error: Input path does not exist: {args.input_path}")
            sys.exit(1)
        
        # 创建水印生成器
        watermark_gen = WatermarkGenerator(
            font_size=args.font_size,
            color=args.color,
            position=args.position
        )
        
        # 创建文件处理器
        processor = FileProcessor(watermark_gen)
        
        print(f"Starting watermark processing...")
        print(f"Input: {args.input_path}")
        print(f"Settings: font_size={args.font_size}, color={args.color}, position={args.position}")
        print("-" * 50)
        
        # 处理文件
        success_count, total_count = processor.process_path(args.input_path)
        
        print("-" * 50)
        print(f"Processing complete: {success_count}/{total_count} files processed successfully")
        
        if success_count < total_count:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()