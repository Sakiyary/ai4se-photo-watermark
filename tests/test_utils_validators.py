"""
测试验证工具
"""

import pytest
from src.watermark_app.utils.validators import (
    is_valid_image_file,
    validate_image_files,
    is_valid_hex_color,
    validate_font_size,
    validate_opacity,
    validate_watermark_text,
    validate_directory_path,
    validate_filename,
    sanitize_filename
)


class TestImageValidation:
  """测试图片文件验证"""

  def test_valid_image_file(self, sample_image):
    """测试有效图片文件"""
    assert is_valid_image_file(sample_image) is True

  def test_invalid_image_file(self):
    """测试无效图片文件"""
    assert is_valid_image_file("nonexistent.jpg") is False
    assert is_valid_image_file("test.txt") is False

  def test_validate_image_files(self, sample_images, temp_dir):
    """测试批量图片验证"""
    # 添加一个无效文件
    invalid_file = str(temp_dir / "invalid.txt")
    all_files = sample_images + [invalid_file]

    valid, invalid = validate_image_files(all_files)

    assert len(valid) == len(sample_images)
    assert len(invalid) == 1
    assert invalid[0] == invalid_file


class TestColorValidation:
  """测试颜色验证"""

  def test_valid_hex_colors(self):
    """测试有效的十六进制颜色"""
    valid_colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]

    for color in valid_colors:
      assert is_valid_hex_color(color) is True

  def test_invalid_hex_colors(self):
    """测试无效的十六进制颜色"""
    invalid_colors = ["000000", "#FFF", "#GGGGGG", "red", "", None]

    for color in invalid_colors:
      assert is_valid_hex_color(color) is False


class TestFontValidation:
  """测试字体验证"""

  def test_valid_font_sizes(self):
    """测试有效字体大小"""
    valid_sizes = [8, 12, 24, 48, 72, 128, 500]

    for size in valid_sizes:
      assert validate_font_size(size) is True

  def test_invalid_font_sizes(self):
    """测试无效字体大小"""
    invalid_sizes = [7, 501, -1, 0, "24", None]

    for size in invalid_sizes:
      assert validate_font_size(size) is False


class TestOpacityValidation:
  """测试透明度验证"""

  def test_valid_opacity(self):
    """测试有效透明度"""
    valid_values = [0, 128, 255, 100, 200]

    for value in valid_values:
      assert validate_opacity(value) is True

  def test_invalid_opacity(self):
    """测试无效透明度"""
    invalid_values = [-1, 256, 1000, "128", None, 128.5]

    for value in invalid_values:
      assert validate_opacity(value) is False


class TestTextValidation:
  """测试文本验证"""

  def test_valid_texts(self):
    """测试有效文本"""
    valid_texts = [
        "",  # 空文本应该有效
        "Hello World",
        "测试文本",
        "Text with\nnewlines",
        "Special chars: !@#$%^&*()"
    ]

    for text in valid_texts:
      is_valid, _ = validate_watermark_text(text)
      assert is_valid is True

  def test_invalid_texts(self):
    """测试无效文本"""
    # 过长文本
    long_text = "x" * 501
    is_valid, msg = validate_watermark_text(long_text)
    assert is_valid is False
    assert "长度" in msg

    # 非字符串类型
    is_valid, msg = validate_watermark_text(123)
    assert is_valid is False
    assert "字符串" in msg


class TestFilenameValidation:
  """测试文件名验证"""

  def test_valid_filenames(self):
    """测试有效文件名"""
    valid_names = [
        "test.jpg",
        "my_file.png",
        "document-v1.2.pdf",
        "测试文件.txt"
    ]

    for name in valid_names:
      is_valid, _ = validate_filename(name)
      assert is_valid is True

  def test_invalid_filenames(self):
    """测试无效文件名"""
    invalid_names = [
        "",  # 空文件名
        "test<file>.txt",  # 包含非法字符
        "CON.txt",  # 保留名称
        "a" * 300,  # 过长文件名
    ]

    for name in invalid_names:
      is_valid, _ = validate_filename(name)
      assert is_valid is False

  def test_sanitize_filename(self):
    """测试文件名清理"""
    test_cases = [
        ("test<file>.txt", "test_file_.txt"),
        ("", "untitled"),
        ("   ..   ", "untitled"),
        ("normal_file.jpg", "normal_file.jpg")
    ]

    for input_name, expected in test_cases:
      result = sanitize_filename(input_name)
      assert result == expected


class TestDirectoryValidation:
  """测试目录路径验证"""

  def test_valid_directory(self, temp_dir):
    """测试有效目录"""
    is_valid, _ = validate_directory_path(str(temp_dir))
    assert is_valid is True

    # 测试不存在但可以创建的目录
    new_dir = temp_dir / "new_directory"
    is_valid, _ = validate_directory_path(str(new_dir))
    assert is_valid is True

  def test_invalid_directory(self):
    """测试无效目录"""
    invalid_paths = [
        "",  # 空路径
        None,  # None值
    ]

    for path in invalid_paths:
      is_valid, _ = validate_directory_path(path)
      assert is_valid is False
