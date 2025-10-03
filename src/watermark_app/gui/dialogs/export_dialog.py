#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出设置对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportDialog:
  """导出设置对话框"""

  # 格式映射字典：界面显示 -> 格式代码
  FORMAT_MAP = {
      "原格式": "original",
      "JPEG": "jpg",
      "PNG": "png",
      "BMP": "bmp",
      "TIFF": "tiff"
  }

  def __init__(self, parent: tk.Widget, title: str = "导出设置", source_folders: set = None, config_manager=None):
    """
    初始化导出对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        source_folders: 源文件夹路径集合，用于禁止导出到这些文件夹
        config_manager: 配置管理器，用于读取默认配置
    """
    self.parent = parent
    self.logger = logging.getLogger(__name__)
    self.result = None
    self.source_folders = source_folders or set()
    self.config_manager = config_manager

    # 创建对话框
    self._create_dialog(title)

  def _create_dialog(self, title: str):
    """创建对话框界面"""
    try:
      # 创建顶级窗口
      self.dialog = tk.Toplevel(self.parent)
      self.dialog.title(title)
      self.dialog.geometry("450x480")
      self.dialog.resizable(False, False)
      self.dialog.grab_set()  # 模态对话框

      # 居中显示
      self._center_dialog()

      # 创建界面
      self._create_widgets()

    except Exception as e:
      self.logger.error(f"创建导出对话框失败: {str(e)}")

  def _center_dialog(self):
    """居中显示对话框"""
    try:
      self.dialog.update_idletasks()
      width = self.dialog.winfo_width()
      height = self.dialog.winfo_height()
      x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
      y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
      self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    except Exception as e:
      self.logger.error(f"居中对话框失败: {str(e)}")

  def _create_widgets(self):
    """创建界面组件"""
    try:
      # 主框架
      main_frame = ttk.Frame(self.dialog)
      main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

      # 输出目录设置
      output_frame = ttk.LabelFrame(main_frame, text="输出设置")
      output_frame.pack(fill=tk.X, pady=(0, 10))

      # 输出目录
      dir_frame = ttk.Frame(output_frame)
      dir_frame.pack(fill=tk.X, padx=5, pady=5)

      ttk.Label(dir_frame, text="输出目录:").pack(anchor=tk.W)
      path_frame = ttk.Frame(dir_frame)
      path_frame.pack(fill=tk.X, pady=2)

      # 默认输出目录改为用户的图片文件夹
      default_output = Path.home() / "Pictures" / "WatermarkedImages"
      self.output_dir = tk.StringVar(value=str(default_output))
      self.dir_entry = ttk.Entry(path_frame, textvariable=self.output_dir)
      self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
      ttk.Button(path_frame, text="浏览", command=self._browse_output_dir).pack(
          side=tk.RIGHT, padx=(5, 0))

      # 文件名设置
      name_frame = ttk.Frame(output_frame)
      name_frame.pack(fill=tk.X, padx=5, pady=5)

      ttk.Label(name_frame, text="文件命名:").pack(anchor=tk.W)
      self.naming_mode = tk.StringVar(value="suffix")
      # 绑定命名模式变化事件
      self.naming_mode.trace_add(
          'write', lambda *args: self._on_naming_mode_change())

      ttk.Radiobutton(name_frame, text="添加自定义后缀",
                      variable=self.naming_mode, value="suffix").pack(anchor=tk.W)
      ttk.Radiobutton(name_frame, text="添加自定义前缀",
                      variable=self.naming_mode, value="prefix").pack(anchor=tk.W)
      ttk.Radiobutton(name_frame, text="保持原文件名", variable=self.naming_mode,
                      value="overwrite").pack(anchor=tk.W)

      # 后缀/前缀输入
      suffix_frame = ttk.Frame(name_frame)
      suffix_frame.pack(fill=tk.X, pady=2)
      ttk.Label(suffix_frame, text="后缀/前缀:").pack(side=tk.LEFT)

      # 从config读取默认值
      default_suffix = "_watermarked"
      if self.config_manager:
        output_config = self.config_manager.get_config('watermark.output') or {}
        default_suffix = output_config.get('naming_suffix', "_watermarked")

      self.name_suffix = tk.StringVar(value=default_suffix)
      self.name_suffix_entry = ttk.Entry(
          suffix_frame, textvariable=self.name_suffix, width=20)
      self.name_suffix_entry.pack(side=tk.RIGHT)

      # 格式设置
      format_frame = ttk.LabelFrame(main_frame, text="格式设置")
      format_frame.pack(fill=tk.X, pady=(0, 10))

      # 输出格式
      fmt_frame = ttk.Frame(format_frame)
      fmt_frame.pack(fill=tk.X, padx=5, pady=5)

      ttk.Label(fmt_frame, text="输出格式:").pack(side=tk.LEFT)
      self.output_format = tk.StringVar(value="原格式")
      # 绑定格式变化事件
      self.output_format.trace_add(
          'write', lambda *args: self._on_format_change())
      format_combo = ttk.Combobox(fmt_frame, textvariable=self.output_format,
                                  values=["原格式", "JPEG", "PNG", "BMP", "TIFF"],
                                  state="readonly", width=15)
      format_combo.pack(side=tk.RIGHT)

      # 质量设置（仅JPEG）
      self.quality_frame = ttk.Frame(format_frame)
      self.quality_frame.pack(fill=tk.X, padx=5, pady=5)

      self.quality_label_text = ttk.Label(self.quality_frame, text="JPEG质量:")
      self.quality_label_text.pack(side=tk.LEFT)
      self.jpeg_quality = tk.IntVar(value=95)

      # 添加质量值显示标签
      self.quality_value_label = ttk.Label(self.quality_frame, text="95")
      self.quality_value_label.pack(side=tk.RIGHT, padx=(5, 0))

      self.quality_scale = ttk.Scale(self.quality_frame, from_=50, to=100, orient=tk.HORIZONTAL,
                                     variable=self.jpeg_quality,
                                     command=lambda v: self.quality_value_label.config(text=f"{int(float(v))}"))
      self.quality_scale.pack(side=tk.RIGHT, fill=tk.X,
                              expand=True, padx=(10, 0))

      # 尺寸设置
      size_frame = ttk.LabelFrame(main_frame, text="尺寸设置")
      size_frame.pack(fill=tk.X, pady=(0, 10))

      # 是否调整尺寸
      self.resize_enabled = tk.BooleanVar(value=False)
      resize_check = ttk.Checkbutton(size_frame, text="调整图片尺寸",
                                     variable=self.resize_enabled, command=self._on_resize_toggle)
      resize_check.pack(anchor=tk.W, padx=5, pady=2)

      # 尺寸输入框架
      self.size_input_frame = ttk.Frame(size_frame)
      self.size_input_frame.pack(fill=tk.X, padx=5, pady=2)

      ttk.Label(self.size_input_frame, text="宽度:").pack(side=tk.LEFT)
      self.output_width = tk.IntVar(value=1920)
      self.width_spinbox = ttk.Spinbox(self.size_input_frame, from_=100, to=10000, width=8,
                                       textvariable=self.output_width)
      self.width_spinbox.pack(side=tk.LEFT, padx=(5, 10))

      ttk.Label(self.size_input_frame, text="高度:").pack(side=tk.LEFT)
      self.output_height = tk.IntVar(value=1080)
      height_spinbox = ttk.Spinbox(self.size_input_frame, from_=100, to=10000, width=8,
                                   textvariable=self.output_height)
      height_spinbox.pack(side=tk.LEFT, padx=5)

      self.keep_aspect = tk.BooleanVar(value=True)
      # 绑定保持比例变化事件
      self.keep_aspect.trace_add(
          'write', lambda *args: self._on_keep_aspect_change())
      ttk.Checkbutton(self.size_input_frame, text="保持比例",
                      variable=self.keep_aspect).pack(side=tk.RIGHT)

      # 初始状态
      self._on_resize_toggle()

      # 按钮框架
      button_frame = ttk.Frame(main_frame)
      button_frame.pack(fill=tk.X, pady=(10, 0))

      ttk.Button(button_frame, text="取消", command=self._cancel).pack(
          side=tk.RIGHT, padx=(5, 0))
      ttk.Button(button_frame, text="开始导出",
                 command=self._ok).pack(side=tk.RIGHT)

    except Exception as e:
      self.logger.error(f"创建导出对话框界面失败: {str(e)}")

  def _browse_output_dir(self):
    """浏览输出目录"""
    try:
      directory = filedialog.askdirectory(
          title="选择输出目录",
          initialdir=self.output_dir.get()
      )
      if directory:
        self.output_dir.set(directory)
    except Exception as e:
      self.logger.error(f"浏览输出目录失败: {str(e)}")

  def _on_naming_mode_change(self):
    """命名模式变化事件处理"""
    try:
      mode = self.naming_mode.get()

      # 获取config中的默认值
      default_prefix = "wm_"
      default_suffix = "_watermarked"
      if self.config_manager:
        output_config = self.config_manager.get_config('watermark.output') or {}
        default_prefix = output_config.get('naming_prefix', 'wm_')
        default_suffix = output_config.get('naming_suffix', '_watermarked')

      if mode == "suffix":
        # 后缀模式：设置默认后缀并启用输入框
        self.name_suffix.set(default_suffix)
        self.name_suffix_entry.config(state='normal')
      elif mode == "prefix":
        # 前缀模式：设置默认前缀并启用输入框
        self.name_suffix.set(default_prefix)
        self.name_suffix_entry.config(state='normal')
      elif mode == "overwrite":
        # 保持原文件名：清空并禁用输入框
        self.name_suffix.set("")
        self.name_suffix_entry.config(state='disabled')
    except Exception as e:
      self.logger.error(f"命名模式变化处理失败: {str(e)}")

  def _on_resize_toggle(self):
    """调整尺寸切换"""
    try:
      if self.resize_enabled.get():
        # 启用尺寸控件
        for widget in self.size_input_frame.winfo_children():
          widget.config(state='normal')
        # 立即更新保持比例状态
        self._on_keep_aspect_change()
      else:
        # 禁用尺寸控件
        for widget in self.size_input_frame.winfo_children():
          if hasattr(widget, 'config'):
            try:
              widget.config(state='disabled')
            except tk.TclError:
              pass  # 某些控件不支持state属性
    except Exception as e:
      self.logger.error(f"切换尺寸设置失败: {str(e)}")

  def _on_keep_aspect_change(self):
    """保持比例切换"""
    try:
      if self.resize_enabled.get():
        if self.keep_aspect.get():
          # 保持比例：禁用宽度输入框
          self.width_spinbox.config(state='disabled')
        else:
          # 不保持比例：启用宽度输入框
          self.width_spinbox.config(state='normal')
    except Exception as e:
      self.logger.error(f"切换保持比例设置失败: {str(e)}")

  def _on_format_change(self):
    """格式变化事件处理"""
    try:
      format_display = self.output_format.get()
      # 只有"原格式"和"JPEG"时启用质量控件
      if format_display in ["原格式", "JPEG"]:
        self.quality_scale.config(state='normal')
        self.quality_label_text.config(state='normal')
        self.quality_value_label.config(state='normal')
      else:
        # 其他格式禁用质量控件
        self.quality_scale.config(state='disabled')
        self.quality_label_text.config(state='disabled')
        self.quality_value_label.config(state='disabled')
    except Exception as e:
      self.logger.error(f"格式变化处理失败: {str(e)}")

  def _validate_settings(self) -> bool:
    """验证设置"""
    try:
      # 检查输出目录
      output_path = Path(self.output_dir.get()).resolve()

      # 禁止导出到源文件夹
      for source_folder in self.source_folders:
        source_path = Path(source_folder).resolve()
        try:
          # 检查输出目录是否是源文件夹或其子目录
          output_path.relative_to(source_path)
          messagebox.showerror(
              "错误",
              f"不能导出到源文件夹或其子目录:\n{source_path}\n\n请选择其他输出目录。"
          )
          return False
        except ValueError:
          # 不是子目录，继续检查
          pass

      # 创建输出目录
      if not output_path.exists():
        try:
          output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
          messagebox.showerror("错误", f"无法创建输出目录:\n{output_path}\n\n{str(e)}")
          return False

      # 检查尺寸设置
      if self.resize_enabled.get():
        if self.output_width.get() <= 0 or self.output_height.get() <= 0:
          messagebox.showerror("错误", "图片尺寸必须大于0")
          return False

      return True

    except Exception as e:
      self.logger.error(f"验证设置失败: {str(e)}")
      messagebox.showerror("错误", f"设置验证失败: {str(e)}")
      return False

  def _ok(self):
    """确定按钮"""
    try:
      if not self._validate_settings():
        return

      # 构建尺寸调整配置
      resize_config = None
      if self.resize_enabled.get():
        if self.keep_aspect.get():
          # 保持比例：按高度缩放
          resize_config = {
              'enabled': True,
              'type': 'height',
              'height': self.output_height.get()
          }
        else:
          # 不保持比例：固定尺寸
          resize_config = {
              'enabled': True,
              'type': 'fixed',
              'width': self.output_width.get(),
              'height': self.output_height.get()
          }

      # 转换格式
      format_display = self.output_format.get()
      format_code = self.FORMAT_MAP.get(format_display, 'png')

      # 构建设置字典
      settings = {
          'output_dir': self.output_dir.get(),
          'naming_mode': self.naming_mode.get(),
          'custom_prefix': self.name_suffix.get() if self.naming_mode.get() == 'prefix' else '',
          'custom_suffix': self.name_suffix.get() if self.naming_mode.get() == 'suffix' else '',
          'format': format_code,  # 使用'format'键而不是'output_format'
          'quality': self.jpeg_quality.get(),  # 使用'quality'键而不是'jpeg_quality'
          'resize': resize_config
      }

      self.result = settings
      self.dialog.destroy()

    except Exception as e:
      self.logger.error(f"确认导出设置失败: {str(e)}")
      messagebox.showerror("错误", f"设置保存失败: {str(e)}")

  def _cancel(self):
    """取消按钮"""
    self.result = None
    self.dialog.destroy()

  def show(self) -> Optional[Dict[str, Any]]:
    """显示对话框并返回结果"""
    try:
      self.dialog.wait_window()
      return self.result
    except Exception as e:
      self.logger.error(f"显示导出对话框失败: {str(e)}")
      return None
