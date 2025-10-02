"""
水印工具 - 应用程序设置

负责应用程序配置的加载、保存和管理
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class WatermarkSettings:
  """水印设置数据类"""
  text: str = "Sample Watermark"
  font_size: int = 24
  font_family: str = "Arial"
  font_bold: bool = False
  font_italic: bool = False
  color: str = "#FFFFFF"
  opacity: int = 128
  position: str = "bottom-right"
  offset_x: int = 10
  offset_y: int = 10
  rotation: float = 0.0


@dataclass
class AppConfig:
  """应用程序配置数据类"""
  # 窗口设置
  window_width: int = 1200
  window_height: int = 800
  window_maximized: bool = False

  # 界面设置
  theme: str = "default"
  language: str = "zh_CN"

  # 默认路径
  last_input_directory: str = ""
  last_output_directory: str = ""

  # 水印设置
  watermark: WatermarkSettings = None

  def __post_init__(self):
    if self.watermark is None:
      self.watermark = WatermarkSettings()


class AppSettings:
  """应用程序设置管理器"""

  def __init__(self):
    """初始化设置管理器"""
    self.config_dir = self._get_config_directory()
    self.config_file = self.config_dir / "config.json"
    self.config = AppConfig()

    # 确保配置目录存在
    self.config_dir.mkdir(parents=True, exist_ok=True)

    # 加载配置
    self.load()

  def _get_config_directory(self) -> Path:
    """获取配置文件目录"""
    # Windows: %APPDATA%/WatermarkTool
    # macOS: ~/Library/Application Support/WatermarkTool
    # Linux: ~/.config/WatermarkTool

    home = Path.home()

    if os.name == 'nt':  # Windows
      config_dir = Path(os.environ.get('APPDATA', home)) / "WatermarkTool"
    elif os.name == 'posix':
      if 'darwin' in os.uname().sysname.lower():  # macOS
        config_dir = home / "Library" / "Application Support" / "WatermarkTool"
      else:  # Linux
        config_dir = home / ".config" / "WatermarkTool"
    else:
      # 默认
      config_dir = home / ".watermark_tool"

    return config_dir

  def load(self):
    """加载配置"""
    try:
      if self.config_file.exists():
        with open(self.config_file, 'r', encoding='utf-8') as f:
          data = json.load(f)

        # 加载水印设置
        if 'watermark' in data:
          watermark_data = data.pop('watermark')
          watermark = WatermarkSettings(**watermark_data)
        else:
          watermark = WatermarkSettings()

        # 加载其他配置
        self.config = AppConfig(watermark=watermark, **data)

      else:
        # 使用默认配置
        self.config = AppConfig()

    except Exception as e:
      print(f"加载配置时出错，使用默认设置: {e}")
      self.config = AppConfig()

  def save(self):
    """保存配置"""
    try:
      # 转换为字典
      config_dict = asdict(self.config)

      # 保存到文件
      with open(self.config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)

    except Exception as e:
      print(f"保存配置时出错: {e}")

  def get_watermark_settings(self) -> WatermarkSettings:
    """获取水印设置"""
    return self.config.watermark

  def set_watermark_settings(self, watermark: WatermarkSettings):
    """设置水印配置"""
    self.config.watermark = watermark

  def get_window_geometry(self) -> tuple:
    """获取窗口几何信息"""
    return (self.config.window_width, self.config.window_height, self.config.window_maximized)

  def set_window_geometry(self, width: int, height: int, maximized: bool = False):
    """设置窗口几何信息"""
    self.config.window_width = width
    self.config.window_height = height
    self.config.window_maximized = maximized

  def get_last_directories(self) -> tuple:
    """获取上次使用的目录"""
    return (self.config.last_input_directory, self.config.last_output_directory)

  def set_last_input_directory(self, directory: str):
    """设置上次输入目录"""
    self.config.last_input_directory = directory

  def set_last_output_directory(self, directory: str):
    """设置上次输出目录"""
    self.config.last_output_directory = directory

  def get_theme(self) -> str:
    """获取主题"""
    return self.config.theme

  def set_theme(self, theme: str):
    """设置主题"""
    self.config.theme = theme

  def get_language(self) -> str:
    """获取语言"""
    return self.config.language

  def set_language(self, language: str):
    """设置语言"""
    self.config.language = language
