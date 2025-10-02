"""
水印工具 - 常量定义

定义应用程序中使用的各种常量
"""

# 应用程序信息
APP_NAME = "水印工具"
APP_VERSION = "2.0.0-alpha"
APP_AUTHOR = "Sakiyary"

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = {
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
}

SUPPORTED_FORMATS_DISPLAY = {
    'JPEG': ['*.jpg', '*.jpeg'],
    'PNG': ['*.png'],
    'BMP': ['*.bmp'],
    'TIFF': ['*.tiff', '*.tif']
}

# 水印位置常量
WATERMARK_POSITIONS = {
    'top-left': '左上角',
    'top-center': '上方居中',
    'top-right': '右上角',
    'left-center': '左侧居中',
    'center': '正中央',
    'right-center': '右侧居中',
    'bottom-left': '左下角',
    'bottom-center': '下方居中',
    'bottom-right': '右下角'
}

# 默认设置
DEFAULT_WATERMARK_TEXT = "Sample Watermark"
DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_COLOR = "#FFFFFF"
DEFAULT_OPACITY = 128
DEFAULT_POSITION = "bottom-right"
DEFAULT_OFFSET_X = 10
DEFAULT_OFFSET_Y = 10

# 界面设置
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# 文件大小限制
MAX_IMAGE_SIZE_MB = 100  # 最大图片大小 (MB)
MAX_BATCH_SIZE = 1000    # 最大批处理数量

# 导出设置
DEFAULT_JPEG_QUALITY = 95
MIN_JPEG_QUALITY = 10
MAX_JPEG_QUALITY = 100

# 错误消息
ERROR_MESSAGES = {
    'file_not_found': '文件不存在',
    'unsupported_format': '不支持的文件格式',
    'file_too_large': '文件过大',
    'memory_error': '内存不足',
    'permission_denied': '权限不足',
    'disk_full': '磁盘空间不足',
    'invalid_image': '无效的图片文件'
}

# 成功消息
SUCCESS_MESSAGES = {
    'export_completed': '导出完成',
    'settings_saved': '设置已保存',
    'template_saved': '模板已保存',
    'template_loaded': '模板已加载'
}
