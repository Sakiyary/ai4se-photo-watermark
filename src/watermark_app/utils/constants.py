#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用常量定义
"""

# 应用信息
APP_NAME = "图片水印处理工具"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Sakiyary"
APP_DESCRIPTION = "一款简单易用的图片批量水印处理工具,支持自定义水印样式、位置调整和批量导出"

# 窗口设置
DEFAULT_WINDOW_SIZE = (1200, 800)
MIN_WINDOW_SIZE = (800, 600)
DEFAULT_WINDOW_POSITION = (100, 100)

# 文件相关
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
SUPPORTED_MIME_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png',
    'image/bmp', 'image/tiff', 'image/x-ms-bmp'
}

# 图像处理
MAX_IMAGE_SIZE = (5000, 5000)  # 最大图像尺寸
THUMBNAIL_SIZE = (150, 150)    # 缩略图尺寸
PREVIEW_SIZE = (800, 600)      # 预览图尺寸

# 水印设置
DEFAULT_WATERMARK_TEXT = "水印文本"
DEFAULT_FONT_SIZE = 36
DEFAULT_TEXT_COLOR = (255, 255, 255, 128)  # 白色半透明
DEFAULT_SHADOW_COLOR = (0, 0, 0, 64)       # 黑色半透明
DEFAULT_STROKE_COLOR = (0, 0, 0, 255)      # 黑色不透明

# 位置预设
POSITION_PRESETS = {
    'top_left': '左上角',
    'top_center': '正上方',
    'top_right': '右上角',
    'middle_left': '左中',
    'center': '正中心',
    'middle_right': '右中',
    'bottom_left': '左下角',
    'bottom_center': '正下方',
    'bottom_right': '右下角'
}

# 输出格式
OUTPUT_FORMATS = {
    'png': {
        'name': 'PNG',
        'extension': '.png',
        'supports_transparency': True,
        'supports_quality': False
    },
    'jpeg': {
        'name': 'JPEG',
        'extension': '.jpg',
        'supports_transparency': False,
        'supports_quality': True
    },
    'jpg': {
        'name': 'JPEG',
        'extension': '.jpg',
        'supports_transparency': False,
        'supports_quality': True
    }
}

# 命名规则
NAMING_RULES = {
    'original': '保留原文件名',
    'prefix': '添加前缀',
    'suffix': '添加后缀'
}

# 界面颜色
COLORS = {
    'primary': '#2196F3',
    'secondary': '#FFC107',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'text_primary': '#212121',
    'text_secondary': '#757575'
}

# 日志级别
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

# 配置文件
CONFIG_DIR_NAME = '.watermark_app'
CONFIG_FILE_NAME = 'config.json'
TEMPLATES_FILE_NAME = 'templates.json'
LOG_DIR_NAME = 'logs'

# 错误消息
ERROR_MESSAGES = {
    'file_not_found': '文件不存在',
    'unsupported_format': '不支持的文件格式',
    'invalid_image': '无效的图像文件',
    'permission_denied': '权限不足',
    'disk_full': '磁盘空间不足',
    'memory_error': '内存不足',
    'unknown_error': '未知错误'
}
