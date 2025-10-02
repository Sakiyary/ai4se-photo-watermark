#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体名称到文件路径的映射工具
通过系统API获取字体信息，建立显示名称到文件路径的映射
"""

import os
import platform
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class FontMapper:
  """字体映射器 - 将字体显示名称映射到文件路径"""

  def __init__(self):
    # 字体族到基础字体的映射
    self.base_fonts: Dict[str, str] = {}
    # 字体族到变体的映射 {family: {(bold, italic): path}}
    self.font_variants: Dict[str, Dict[Tuple[bool, bool], str]] = {}
    # 完整的字体映射（保持向后兼容）
    self.font_map: Dict[str, str] = {}
    self._build_font_map()

  def _build_font_map(self):
    """构建字体映射表"""
    try:
      system = platform.system()
      if system == "Windows":
        self._build_windows_font_map()
      elif system == "Darwin":
        self._build_macos_font_map()
      else:
        self._build_linux_font_map()

      logger.info(
          f"构建字体映射表完成: 基础字体 {len(self.base_fonts)} 个, 变体 {sum(len(v) for v in self.font_variants.values())} 个")

    except Exception as e:
      logger.error(f"构建字体映射表失败: {e}")

  def _build_windows_font_map(self):
    """构建Windows字体映射"""
    try:
      import winreg

      # 临时存储注册表信息
      registry_fonts = {}

      # 从注册表读取字体信息
      key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')

      i = 0
      while True:
        try:
          font_name, font_file, _ = winreg.EnumValue(key, i)

          # 构建完整路径
          if not os.path.isabs(font_file):
            font_path = os.path.join(os.environ.get(
                'WINDIR', 'C:\\Windows'), 'Fonts', font_file)
          else:
            font_path = font_file

          if os.path.exists(font_path):
            registry_fonts[font_name] = font_path

          i += 1
        except WindowsError:
          break

      winreg.CloseKey(key)

      # 解析字体信息，识别基础字体和变体
      self._parse_font_registry(registry_fonts)

      # 扫描用户字体目录
      user_fonts_dir = os.path.expanduser(
          "~/AppData/Local/Microsoft/Windows/Fonts/")
      if os.path.exists(user_fonts_dir):
        self._scan_font_directory(user_fonts_dir)

    except Exception as e:
      logger.error(f"构建Windows字体映射失败: {e}")

  def _parse_font_registry(self, registry_fonts: Dict[str, str]):
    """解析注册表字体信息，分离基础字体和变体"""

    # 字体族分组
    font_families = {}

    for font_name, font_path in registry_fonts.items():
      # 解析字体名称
      family_name, is_bold, is_italic = self._parse_font_name(font_name)

      if family_name not in font_families:
        font_families[family_name] = {}

      font_families[family_name][(is_bold, is_italic)] = font_path

      # 添加到完整映射（向后兼容）
      self.font_map[font_name] = font_path
      clean_name = font_name.replace(
          ' (TrueType)', '').replace(' (OpenType)', '')
      self.font_map[clean_name] = font_path

    # 建立基础字体和变体映射
    for family_name, variants in font_families.items():
      self.font_variants[family_name] = variants

      # 确定基础字体（优先级：Regular > Normal > 排除Light/Thin等轻量版本）
      base_font = None

      # 对于微软雅黑特殊处理：强制使用标准版本
      if family_name == 'Microsoft YaHei':
        import os
        windows_fonts_dir = os.environ.get(
            'WINDIR', 'C:\\Windows') + '\\Fonts\\'
        standard_path = windows_fonts_dir + 'msyh.ttc'
        if os.path.exists(standard_path):
          base_font = standard_path
          logger.info(f"微软雅黑强制使用标准版本作为基础字体: {base_font}")

      if not base_font:
        if (False, False) in variants:  # Regular
          base_font = variants[(False, False)]
        elif variants:
          # 排除轻量版本，优先选择标准版本
          filtered_variants = {}
          for (is_bold, is_italic), path in variants.items():
            path_lower = path.lower()
            # 排除轻量版本
            if not any(light_keyword in path_lower for light_keyword in ['light', 'thin', 'ultralight']):
              filtered_variants[(is_bold, is_italic)] = path

          if filtered_variants:
            # 优先选择非粗体非斜体的版本
            if (False, False) in filtered_variants:
              base_font = filtered_variants[(False, False)]
            else:
              base_font = list(filtered_variants.values())[0]
          else:
            # 如果只有轻量版本，也要使用
            base_font = list(variants.values())[0]

      if base_font:
        self.base_fonts[family_name] = base_font
        self.font_map[family_name] = base_font

        # 添加常用别名
        self._add_font_aliases(family_name, base_font)

  def _parse_font_name(self, font_name: str) -> Tuple[str, bool, bool]:
    """解析字体名称，提取字体族名和样式信息"""

    # 移除类型后缀
    name = font_name.replace(' (TrueType)', '').replace(' (OpenType)', '')

    # 检测粗体和斜体（但不包括Light等轻量样式）
    is_bold = any(keyword in name for keyword in ['Bold', 'Heavy', 'Black']) and not any(
        light in name for light in ['Light', 'Thin'])
    is_italic = any(keyword in name for keyword in ['Italic', 'Oblique'])

    # 提取字体族名（移除样式词汇）
    family_name = name
    style_keywords = ['Bold', 'Italic', 'Regular', 'Normal', 'Heavy', 'Black', 'Light', 'Thin', 'Oblique',
                      'Ultra', 'Semi', 'Demi', 'Extra']

    # 特殊处理复合名称（如 "Microsoft YaHei & Microsoft YaHei UI"）
    if '&' in family_name:
      # 取第一个名称
      family_name = family_name.split('&')[0].strip()

    for keyword in style_keywords:
      family_name = family_name.replace(f' {keyword}', '').replace(keyword, '')

    family_name = family_name.strip()

    return family_name, is_bold, is_italic

  def _add_font_aliases(self, family_name: str, font_path: str):
    """为字体添加常用别名"""
    aliases = []

    # 中文字体别名 - 特殊处理以确保正确映射
    chinese_aliases = {
        'Microsoft YaHei': ['微软雅黑', 'MicroSoft YaHei UI', 'msyh'],
        'SimSun': ['宋体', 'NSimSun', 'STSONG'],
        'SimHei': ['黑体', 'STHEITISC'],
        'FangSong': ['仿宋', 'STFANGSO'],
        'KaiTi': ['楷体', 'STKAITI']
    }

    # 强制修正微软雅黑映射：确保优先使用标准版本
    if 'Microsoft YaHei' in family_name and not any(style in family_name for style in ['Bold', 'Light']):
      # 对于基础版本，强制使用标准版本而不是Light版本
      import os
      windows_fonts_dir = os.environ.get('WINDIR', 'C:\\Windows') + '\\Fonts\\'
      standard_path = windows_fonts_dir + 'msyh.ttc'
      if os.path.exists(standard_path):
        font_path = standard_path
        logger.info(f"微软雅黑使用标准版本: {font_path}")
      else:
        # 标准版本不存在时才使用Light版本
        font_path_lower = font_path.lower()
        if 'msyhl' in font_path_lower:
          logger.info(f"微软雅黑标准版本不存在，使用Light版本: {font_path}")

    # 添加中文字体别名
    for main_name, alias_list in chinese_aliases.items():
      if main_name in family_name or any(alias in family_name for alias in alias_list):
        aliases.extend([main_name] + alias_list)

    # 添加别名映射
    for alias in aliases:
      if alias not in self.base_fonts:  # 只在没有更好映射时添加
        self.font_map[alias] = font_path
        self.base_fonts[alias] = font_path

  def _build_macos_font_map(self):
    """构建macOS字体映射"""
    font_dirs = [
        "/System/Library/Fonts/",
        "/Library/Fonts/",
        os.path.expanduser("~/Library/Fonts/")
    ]

    for font_dir in font_dirs:
      if os.path.exists(font_dir):
        self._scan_font_directory(font_dir)

  def _build_linux_font_map(self):
    """构建Linux字体映射"""
    font_dirs = [
        "/usr/share/fonts/",
        "/usr/local/share/fonts/",
        os.path.expanduser("~/.fonts/"),
        os.path.expanduser("~/.local/share/fonts/")
    ]

    for font_dir in font_dirs:
      if os.path.exists(font_dir):
        self._scan_font_directory(font_dir)

  def _scan_font_directory(self, font_dir: str):
    """扫描字体目录，建立文件名到路径的映射"""
    try:
      for root, dirs, files in os.walk(font_dir):
        for file in files:
          if file.lower().endswith(('.ttf', '.ttc', '.otf')):
            font_path = os.path.join(root, file)
            font_name = os.path.splitext(file)[0]

            # 添加到完整映射
            self.font_map[font_name] = font_path
            self.font_map[file] = font_path

            # 尝试解析字体族和样式
            family_name, is_bold, is_italic = self._parse_filename(font_name)

            if family_name:
              if family_name not in self.font_variants:
                self.font_variants[family_name] = {}

              self.font_variants[family_name][(is_bold, is_italic)] = font_path

              # 如果是基础字体，添加到base_fonts
              if not is_bold and not is_italic:
                self.base_fonts[family_name] = font_path

    except Exception as e:
      logger.debug(f"扫描字体目录 {font_dir} 失败: {e}")

  def _parse_filename(self, filename: str) -> Tuple[str, bool, bool]:
    """从文件名解析字体族名和样式"""
    name_lower = filename.lower()

    # 检测样式
    is_bold = any(keyword in name_lower for keyword in [
                  'bold', 'bd', 'heavy', 'black'])
    is_italic = any(keyword in name_lower for keyword in [
                    'italic', 'it', 'oblique', 'slant'])

    # 提取字体族名
    family_name = filename
    style_patterns = ['bold', 'bd', 'italic', 'it', 'oblique',
                      'slant', 'regular', 'normal', 'heavy', 'black', 'light']

    for pattern in style_patterns:
      family_name = family_name.replace(pattern, '').replace(
          pattern.upper(), '').replace(pattern.capitalize(), '')

    # 清理多余的字符
    family_name = family_name.strip('_-. ')

    return family_name if family_name else filename, is_bold, is_italic

  def get_font_path(self, font_name: str, bold: bool = False, italic: bool = False) -> Optional[str]:
    """根据字体名称获取字体文件路径，支持粗体和斜体"""

    # 1. 首先查找字体族
    family_name = self._find_font_family(font_name)

    if not family_name:
      # 如果找不到字体族，尝试直接匹配
      return self.font_map.get(font_name)

    # 2. 在该字体族中查找对应的变体
    if family_name in self.font_variants:
      variants = self.font_variants[family_name]

      # 查找精确匹配的变体
      if (bold, italic) in variants:
        return variants[(bold, italic)]

      # 对于中文字体的特殊处理
      if self._is_chinese_font(family_name):
        return self._handle_chinese_font_variant(family_name, variants, bold, italic)

      # 如果找不到精确匹配，尝试降级匹配
      fallback_options = [
          (bold, False),   # 只要粗体
          (False, italic),  # 只要斜体
          (False, False),  # 基础字体
      ]

      for fb_bold, fb_italic in fallback_options:
        if (fb_bold, fb_italic) in variants and (fb_bold, fb_italic) != (bold, italic):
          logger.debug(
              f"字体 {font_name} 使用降级匹配: bold={fb_bold}, italic={fb_italic}")
          return variants[(fb_bold, fb_italic)]

    # 3. 返回基础字体
    return self.base_fonts.get(family_name)

  def _is_chinese_font(self, font_name: str) -> bool:
    """判断是否为中文字体"""
    chinese_font_names = [
        'Microsoft YaHei', '微软雅黑', 'SimSun', '宋体', 'SimHei', '黑体',
        'FangSong', '仿宋', 'KaiTi', '楷体', 'STSong', 'STHeiti', 'STFangSong', 'STKaiti'
    ]

    for chinese_name in chinese_font_names:
      if chinese_name.lower() in font_name.lower() or font_name.lower() in chinese_name.lower():
        return True

    return False

  def _handle_chinese_font_variant(self, family_name: str, variants: Dict[Tuple[bool, bool], str],
                                   bold: bool, italic: bool) -> Optional[str]:
    """处理中文字体的变体请求"""

    # 对于微软雅黑，强制使用正确的文件
    if 'Microsoft YaHei' in family_name or '微软雅黑' in family_name:
      import os
      windows_fonts_dir = os.environ.get('WINDIR', 'C:\\Windows') + '\\Fonts\\'

      if bold and italic:
        # 粗斜体：优先使用粗体文件，如果没有则用标准文件
        bold_path = windows_fonts_dir + 'msyhbd.ttc'
        if os.path.exists(bold_path):
          logger.debug(f"微软雅黑粗斜体使用粗体文件: {bold_path}")
          return bold_path
        standard_path = windows_fonts_dir + 'msyh.ttc'
        if os.path.exists(standard_path):
          logger.debug(f"微软雅黑粗斜体使用标准文件: {standard_path}")
          return standard_path
      elif bold:
        # 粗体：使用粗体文件
        bold_path = windows_fonts_dir + 'msyhbd.ttc'
        if os.path.exists(bold_path):
          return bold_path
        standard_path = windows_fonts_dir + 'msyh.ttc'
        if os.path.exists(standard_path):
          logger.debug(f"微软雅黑粗体使用标准文件: {standard_path}")
          return standard_path
      elif italic:
        # 斜体：使用标准文件（算法模拟斜体）
        standard_path = windows_fonts_dir + 'msyh.ttc'
        if os.path.exists(standard_path):
          logger.debug(f"微软雅黑斜体使用标准文件: {standard_path}")
          return standard_path
      else:
        # 普通：使用标准文件
        standard_path = windows_fonts_dir + 'msyh.ttc'
        if os.path.exists(standard_path):
          return standard_path
        # 如果标准文件不存在，使用Light版本作为备用
        light_path = windows_fonts_dir + 'msyhl.ttc'
        if os.path.exists(light_path):
          logger.debug(f"微软雅黑使用Light版本作为备用: {light_path}")
          return light_path

    # 对于其他中文字体的通用处理
    if bold and italic:
      # 粗斜体：优先使用粗体文件
      if (True, False) in variants:
        logger.debug(f"中文字体 {family_name} 粗斜体使用粗体文件")
        return variants[(True, False)]
      elif (False, False) in variants:
        logger.debug(f"中文字体 {family_name} 粗斜体使用基础文件")
        return variants[(False, False)]
    elif bold:
      # 只需粗体：查找粗体文件
      if (True, False) in variants:
        return variants[(True, False)]
      elif (False, False) in variants:
        logger.debug(f"中文字体 {family_name} 粗体使用基础文件")
        return variants[(False, False)]
    elif italic:
      # 只需斜体：使用基础文件（由WatermarkProcessor模拟斜体）
      if (False, False) in variants:
        logger.debug(f"中文字体 {family_name} 斜体使用基础文件")
        return variants[(False, False)]

    # 默认返回基础字体
    return variants.get((False, False))

  def _find_font_family(self, font_name: str) -> Optional[str]:
    """查找字体族名"""

    # 1. 直接匹配基础字体
    if font_name in self.base_fonts:
      # 优先返回有变体信息的族名
      if font_name in self.font_variants:
        return font_name
      # 对于中文字体名，优先查找英文对应的变体族
      if any(ord(c) > 127 for c in font_name):  # 包含中文字符
        for variant_family in self.font_variants.keys():
          if self._fonts_are_same_family(font_name, variant_family):
            return variant_family
      # 查找是否有对应的变体族（通用匹配）
      for variant_family in self.font_variants.keys():
        if font_name.lower() in variant_family.lower() or variant_family.lower() in font_name.lower():
          return variant_family
      return font_name

    # 2. 检查是否在字体变体中
    if font_name in self.font_variants:
      return font_name

    # 3. 特殊字体名称映射 - 优先查找有变体信息的族名
    special_mappings = {
        '微软雅黑': ['Microsoft YaHei', 'msyh', 'MicroSoft YaHei UI'],
        '宋体': ['SimSun', 'NSimSun', 'STSONG'],
        '黑体': ['SimHei', 'STHEITISC'],
        '仿宋': ['FangSong', 'STFANGSO'],
        '楷体': ['KaiTi', 'STKAITI']
    }

    # 检查特殊映射
    for main_name, aliases in special_mappings.items():
      if font_name == main_name or font_name in aliases:
        # 优先查找有变体信息的字体族
        for variant_family in self.font_variants.keys():
          if any(alias.lower() in variant_family.lower() for alias in [main_name] + aliases):
            return variant_family
        # 如果没有变体信息，查找基础字体族
        for family in self.base_fonts.keys():
          if any(alias.lower() in family.lower() for alias in [main_name] + aliases):
            return family

    # 4. 模糊匹配 - 优先有变体信息的族
    font_lower = font_name.lower()

    # 优先在变体字体中查找
    for family in self.font_variants.keys():
      if font_lower in family.lower() or family.lower() in font_lower:
        return family

    # 在基础字体中查找
    for family in self.base_fonts.keys():
      if font_lower in family.lower() or family.lower() in font_lower:
        return family

    # 在完整映射中查找
    for name in self.font_map.keys():
      name_lower = name.lower()
      if font_lower in name_lower or name_lower in font_lower:
        # 尝试提取字体族名
        family, _, _ = self._parse_font_name(name)
        if family in self.font_variants:
          return family
        if family in self.base_fonts:
          return family

    return None

  def _fonts_are_same_family(self, font1: str, font2: str) -> bool:
    """判断两个字体名是否属于同一字体族"""
    # 特殊的中英文字体对应关系
    font_pairs = [
        ('微软雅黑', 'Microsoft YaHei'),
        ('宋体', 'SimSun'),
        ('黑体', 'SimHei'),
        ('仿宋', 'FangSong'),
        ('楷体', 'KaiTi')
    ]

    font1_lower = font1.lower()
    font2_lower = font2.lower()

    for chinese, english in font_pairs:
      if ((chinese in font1 and english.lower() in font2_lower) or
              (chinese in font2 and english.lower() in font1_lower)):
        return True

    return False

  def get_available_fonts(self) -> list:
    """获取所有可用的字体族名称"""
    return list(self.base_fonts.keys())


# 全局实例
_font_mapper = None


def get_font_mapper() -> FontMapper:
  """获取字体映射器实例（单例）"""
  global _font_mapper
  if _font_mapper is None:
    _font_mapper = FontMapper()
  return _font_mapper


def get_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Optional[str]:
  """便捷函数：根据字体名称获取文件路径，支持粗体和斜体"""
  return get_font_mapper().get_font_path(font_name, bold, italic)
