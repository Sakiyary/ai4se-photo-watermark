#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理核心模块
负责应用配置、用户设置和水印模板的管理
"""

import time as import_time
import json
import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import copy

logger = logging.getLogger(__name__)


class ConfigManager:
  """配置管理器类"""

  DEFAULT_CONFIG = {
      'app': {
          'version': '1.0.0',
          'window_size': [1200, 800],
          'window_position': [100, 100],
          'last_input_directory': '',
          'last_output_directory': '',
          'language': 'zh_CN'
      },
      'watermark': {
          'text': {
              'content': 'watermark',
              'font_family': 'arial',
              'font_size': 36,
              'color': [255, 255, 255, 128],
              'bold': False,
              'italic': False,
              'shadow': False,
              'shadow_offset': [2, 2],
              'shadow_color': [0, 0, 0, 64],
              'stroke_width': 1,
              'stroke_color': [0, 0, 0, 255]
          },
          'image': {
              'path': '',
              'opacity': 1.0,
              'size': [100, 100],
              'keep_aspect_ratio': True
          },
          'position': {
              'preset': 'bottom_right',  # 九宫格位置
              'custom_x': 0,
              'custom_y': 0,
              'margins': {
                  'horizontal': 20,
                  'vertical': 20
              },
              'rotation': 0.0
          },
          'output': {
              'format': 'png',
              'quality': 85,
              'resize_enabled': False,
              'resize_width': 0,
              'resize_height': 0,
              'resize_percentage': 100,
              'naming_rule': 'suffix',  # 'original', 'prefix', 'suffix'
              'naming_prefix': 'wm_',
              'naming_suffix': '_watermarked'
          }
      }
  }

  def __init__(self, config_dir: str = None):
    """
    初始化配置管理器

    Args:
        config_dir: 配置文件目录，None使用默认目录
    """
    self.logger = logging.getLogger(__name__)

    # 设置配置目录
    if config_dir:
      self.config_dir = Path(config_dir)
    else:
      # 优先使用当前工作目录，如果不可写则使用系统临时目录
      try:
        # 尝试在当前工作目录创建配置文件夹
        current_dir = Path.cwd() / '.watermark_config'
        current_dir.mkdir(exist_ok=True)
        # 测试是否可写
        test_file = current_dir / '.test'
        test_file.write_text('test')
        test_file.unlink()
        self.config_dir = current_dir
        self.logger.info(f"使用当前目录保存配置: {self.config_dir}")
      except (PermissionError, OSError):
        # 如果当前目录不可写，使用系统临时目录
        import tempfile
        self.config_dir = Path(tempfile.gettempdir()) / 'watermark_app'
        self.logger.info(f"使用临时目录保存配置: {self.config_dir}")

    self.config_dir.mkdir(exist_ok=True)

    # 配置文件路径
    self.config_file = self.config_dir / 'config.json'
    self.templates_file = self.config_dir / 'templates.json'

    # 当前配置
    self.config = copy.deepcopy(self.DEFAULT_CONFIG)
    self.templates = {}

    # 加载配置
    self.load_config()
    self.load_templates()

  def load_config(self) -> bool:
    """
    加载配置文件

    Returns:
        bool: 是否成功加载
    """
    try:
      if self.config_file.exists():
        with open(self.config_file, 'r', encoding='utf-8') as f:
          loaded_config = json.load(f)
          # 合并配置，保留默认值
          self._merge_config(self.config, loaded_config)
          self.logger.info("成功加载配置文件")
      else:
        # 首次运行，创建默认配置文件
        self.save_config()
        self.logger.info("创建默认配置文件")
      return True
    except Exception as e:
      self.logger.error(f"加载配置文件失败: {str(e)}")
      return False

  def save_config(self) -> bool:
    """
    保存配置文件

    Returns:
        bool: 是否成功保存
    """
    try:
      with open(self.config_file, 'w', encoding='utf-8') as f:
        json.dump(self.config, f, indent=2, ensure_ascii=False)
      self.logger.info("成功保存配置文件")
      return True
    except Exception as e:
      self.logger.error(f"保存配置文件失败: {str(e)}")
      return False

  def load_templates(self) -> bool:
    """
    加载水印模板

    Returns:
        bool: 是否成功加载
    """
    try:
      if self.templates_file.exists():
        with open(self.templates_file, 'r', encoding='utf-8') as f:
          self.templates = json.load(f)
          self.logger.info(f"成功加载 {len(self.templates)} 个水印模板")
      else:
        self.templates = {}
      return True
    except Exception as e:
      self.logger.error(f"加载模板文件失败: {str(e)}")
      self.templates = {}
      return False

  def save_templates(self) -> bool:
    """
    保存水印模板

    Returns:
        bool: 是否成功保存
    """
    try:
      with open(self.templates_file, 'w', encoding='utf-8') as f:
        json.dump(self.templates, f, indent=2, ensure_ascii=False)
      self.logger.info("成功保存模板文件")
      return True
    except Exception as e:
      self.logger.error(f"保存模板文件失败: {str(e)}")
      return False

  def get_config(self, key_path: str = None) -> Any:
    """
    获取配置值

    Args:
        key_path: 配置键路径，如'app.window_size'，None返回全部配置

    Returns:
        配置值
    """
    if key_path is None:
      return copy.deepcopy(self.config)

    keys = key_path.split('.')
    value = self.config

    try:
      for key in keys:
        value = value[key]
      return copy.deepcopy(value)
    except (KeyError, TypeError):
      self.logger.warning(f"配置键不存在: {key_path}")
      return None

  def set_config(self, key_path: str, value: Any) -> bool:
    """
    设置配置值

    Args:
        key_path: 配置键路径
        value: 配置值

    Returns:
        bool: 是否成功设置
    """
    keys = key_path.split('.')
    config = self.config

    try:
      # 导航到父级
      for key in keys[:-1]:
        if key not in config:
          config[key] = {}
        config = config[key]

      # 设置值
      config[keys[-1]] = copy.deepcopy(value)
      return True
    except Exception as e:
      self.logger.error(f"设置配置失败 {key_path}: {str(e)}")
      return False

  def get_watermark_config(self) -> Dict[str, Any]:
    """
    获取当前水印配置

    Returns:
        水印配置字典
    """
    return self.get_config('watermark')

  def set_watermark_config(self, watermark_config: Dict[str, Any]) -> bool:
    """
    设置水印配置

    Args:
        watermark_config: 水印配置字典

    Returns:
        bool: 是否成功设置
    """
    try:
      # 深拷贝以避免修改原始数据
      config = copy.deepcopy(watermark_config)

      # 更新到配置中
      if 'watermark' not in self.config:
        self.config['watermark'] = {}

      # 逐个键更新，而不是整体替换
      for key, value in config.items():
        self.config['watermark'][key] = value

      return True
    except Exception as e:
      self.logger.error(f"设置水印配置失败: {str(e)}")
      return False

  def save_template(self, name: str, description: str = '') -> bool:
    """
    保存当前水印设置为模板

    Args:
        name: 模板名称
        description: 模板描述

    Returns:
        bool: 是否成功保存
    """
    try:
      if not name.strip():
        self.logger.error("模板名称不能为空")
        return False

      template_data = {
          'name': name.strip(),
          'description': description.strip(),
          'config': copy.deepcopy(self.get_watermark_config()),
          'created_time': import_time.time(),
          'modified_time': import_time.time()
      }

      self.templates[name] = template_data
      success = self.save_templates()

      if success:
        self.logger.info(f"成功保存模板: {name}")

      return success

    except Exception as e:
      self.logger.error(f"保存模板失败: {str(e)}")
      return False

  def load_template(self, name: str) -> bool:
    """
    加载模板并应用到当前配置

    Args:
        name: 模板名称

    Returns:
        bool: 是否成功加载
    """
    try:
      if name not in self.templates:
        self.logger.error(f"模板不存在: {name}")
        return False

      # 获取模板配置
      template_data = self.templates.get(name)
      if not template_data:
        self.logger.error(f"模板数据为空: {name}")
        return False

      template_config = template_data.get('config', {})
      if not template_config:
        self.logger.error(f"模板配置为空: {name}")
        return False

      # 应用配置
      success = self.set_watermark_config(template_config)

      if success:
        self.logger.info(f"成功加载模板: {name}")

      return success

    except Exception as e:
      import traceback
      self.logger.error(f"加载模板失败: {str(e)}")
      self.logger.error(f"错误堆栈: {traceback.format_exc()}")
      return False

  def delete_template(self, name: str) -> bool:
    """
    删除模板

    Args:
        name: 模板名称

    Returns:
        bool: 是否成功删除
    """
    try:
      if name not in self.templates:
        self.logger.warning(f"模板不存在: {name}")
        return False

      del self.templates[name]
      success = self.save_templates()

      if success:
        self.logger.info(f"成功删除模板: {name}")

      return success

    except Exception as e:
      self.logger.error(f"删除模板失败: {str(e)}")
      return False

  def get_template(self, name: str) -> Optional[Dict[str, Any]]:
    """
    获取模板配置

    Args:
        name: 模板名称

    Returns:
        模板配置字典，如果模板不存在则返回 None
    """
    try:
      if name not in self.templates:
        self.logger.error(f"模板不存在: {name}")
        return None

      return self.templates[name]['config']

    except Exception as e:
      self.logger.error(f"获取模板配置失败: {str(e)}")
      return None

  def get_template_list(self) -> List[Dict[str, Any]]:
    """
    获取模板列表

    Returns:
        模板信息列表
    """
    return [
        {
            'name': name,
            'description': template.get('description', ''),
            'created_time': template.get('created_time', 0),
            'modified_time': template.get('modified_time', 0)
        }
        for name, template in self.templates.items()
    ]

  def export_template(self, name: str, file_path: str) -> bool:
    """
    导出模板到文件

    Args:
        name: 模板名称
        file_path: 导出文件路径

    Returns:
        bool: 是否成功导出
    """
    try:
      if name not in self.templates:
        self.logger.error(f"模板不存在: {name}")
        return False

      with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(self.templates[name], f, indent=2, ensure_ascii=False)

      self.logger.info(f"成功导出模板: {name} -> {file_path}")
      return True

    except Exception as e:
      self.logger.error(f"导出模板失败: {str(e)}")
      return False

  def import_template(self, file_path: str) -> bool:
    """
    从文件导入模板

    Args:
        file_path: 模板文件路径

    Returns:
        bool: 是否成功导入
    """
    try:
      if not os.path.exists(file_path):
        self.logger.error(f"模板文件不存在: {file_path}")
        return False

      with open(file_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

      # 验证模板数据格式
      if not all(key in template_data for key in ['name', 'config']):
        self.logger.error("模板文件格式无效")
        return False

      name = template_data['name']
      self.templates[name] = template_data
      success = self.save_templates()

      if success:
        self.logger.info(f"成功导入模板: {name}")

      return success

    except Exception as e:
      self.logger.error(f"导入模板失败: {str(e)}")
      return False

  def _merge_config(self, default: Dict, loaded: Dict):
    """
    合并配置，保留默认值结构

    Args:
        default: 默认配置
        loaded: 加载的配置
    """
    for key, value in loaded.items():
      if key in default:
        if isinstance(default[key], dict) and isinstance(value, dict):
          self._merge_config(default[key], value)
        else:
          default[key] = value


# 添加时间模块导入
