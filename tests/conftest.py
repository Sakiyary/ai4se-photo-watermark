"""
测试配置文件

配置pytest测试环境和共享fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image


@pytest.fixture
def temp_dir():
  """创建临时目录用于测试"""
  temp_dir = tempfile.mkdtemp()
  yield Path(temp_dir)
  shutil.rmtree(temp_dir)


@pytest.fixture
def sample_image(temp_dir):
  """创建测试用的示例图片"""
  # 创建一个简单的RGB图片
  image = Image.new('RGB', (100, 100), color='red')
  image_path = temp_dir / "sample.jpg"
  image.save(image_path, "JPEG")
  return str(image_path)


@pytest.fixture
def sample_png_image(temp_dir):
  """创建测试用的PNG图片"""
  # 创建带透明度的PNG图片
  image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
  image_path = temp_dir / "sample.png"
  image.save(image_path, "PNG")
  return str(image_path)


@pytest.fixture
def sample_images(temp_dir):
  """创建多个测试图片"""
  images = []
  for i in range(3):
    image = Image.new('RGB', (100, 100), color=(i*80, 0, 0))
    image_path = temp_dir / f"sample_{i}.jpg"
    image.save(image_path, "JPEG")
    images.append(str(image_path))
  return images


@pytest.fixture
def watermark_config():
  """创建测试用的水印配置"""
  return {
      'text': 'Test Watermark',
      'font_size': 20,
      'color': '#FFFFFF',
      'opacity': 128,
      'position': 'bottom-right',
      'offset_x': 10,
      'offset_y': 10
  }
