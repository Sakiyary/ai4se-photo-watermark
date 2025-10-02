"""
测试设置模块
"""

import pytest
import tempfile
from pathlib import Path
from src.watermark_app.config.settings import AppSettings, WatermarkSettings, AppConfig


class TestWatermarkSettings:
  """测试水印设置类"""

  def test_default_values(self):
    """测试默认值"""
    settings = WatermarkSettings()

    assert settings.text == "Sample Watermark"
    assert settings.font_size == 24
    assert settings.color == "#FFFFFF"
    assert settings.opacity == 128
    assert settings.position == "bottom-right"

  def test_custom_values(self):
    """测试自定义值"""
    settings = WatermarkSettings(
        text="Custom Text",
        font_size=32,
        color="#FF0000",
        opacity=200,
        position="center"
    )

    assert settings.text == "Custom Text"
    assert settings.font_size == 32
    assert settings.color == "#FF0000"
    assert settings.opacity == 200
    assert settings.position == "center"


class TestAppConfig:
  """测试应用配置类"""

  def test_default_config(self):
    """测试默认配置"""
    config = AppConfig()

    assert config.window_width == 1200
    assert config.window_height == 800
    assert config.window_maximized is False
    assert config.theme == "default"
    assert config.language == "zh_CN"
    assert isinstance(config.watermark, WatermarkSettings)

  def test_watermark_initialization(self):
    """测试水印设置初始化"""
    config = AppConfig()

    # 水印设置应该自动初始化
    assert config.watermark is not None
    assert isinstance(config.watermark, WatermarkSettings)


class TestAppSettings:
  """测试应用设置管理器"""

  def test_initialization(self):
    """测试初始化"""
    with tempfile.TemporaryDirectory() as temp_dir:
      # 模拟配置目录
      settings = AppSettings()

      assert settings.config is not None
      assert isinstance(settings.config, AppConfig)

  def test_watermark_settings_access(self):
    """测试水印设置访问"""
    settings = AppSettings()

    # 获取水印设置
    watermark = settings.get_watermark_settings()
    assert isinstance(watermark, WatermarkSettings)

    # 修改水印设置
    new_watermark = WatermarkSettings(text="New Text", font_size=36)
    settings.set_watermark_settings(new_watermark)

    retrieved = settings.get_watermark_settings()
    assert retrieved.text == "New Text"
    assert retrieved.font_size == 36

  def test_window_geometry(self):
    """测试窗口几何信息"""
    settings = AppSettings()

    # 设置窗口几何
    settings.set_window_geometry(800, 600, True)

    width, height, maximized = settings.get_window_geometry()
    assert width == 800
    assert height == 600
    assert maximized is True

  def test_directories(self):
    """测试目录设置"""
    settings = AppSettings()

    # 设置目录
    settings.set_last_input_directory("/test/input")
    settings.set_last_output_directory("/test/output")

    input_dir, output_dir = settings.get_last_directories()
    assert input_dir == "/test/input"
    assert output_dir == "/test/output"

  def test_theme_and_language(self):
    """测试主题和语言设置"""
    settings = AppSettings()

    # 测试主题
    settings.set_theme("dark")
    assert settings.get_theme() == "dark"

    # 测试语言
    settings.set_language("en_US")
    assert settings.get_language() == "en_US"
