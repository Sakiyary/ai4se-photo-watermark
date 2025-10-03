#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关于对话框
"""

import tkinter as tk
from tkinter import ttk
import logging
from ...utils.constants import APP_NAME, APP_VERSION, APP_AUTHOR, APP_DESCRIPTION


class AboutDialog:
  """关于对话框"""

  def __init__(self, parent):
    """
    初始化关于对话框

    Args:
        parent: 父窗口
    """
    self.parent = parent
    self.logger = logging.getLogger(__name__)
    self.dialog = None
    self._create_dialog()

  def _create_dialog(self):
    """创建对话框"""
    try:
      # 创建顶层窗口
      self.dialog = tk.Toplevel(self.parent)
      self.dialog.title("关于")
      self.dialog.geometry("500x700")
      self.dialog.resizable(True, True)

      # 居中显示
      self.dialog.transient(self.parent)
      self._center_window()

      # 创建画布和滚动条
      canvas = tk.Canvas(self.dialog)
      scrollbar = ttk.Scrollbar(
          self.dialog, orient="vertical", command=canvas.yview)
      scrollable_frame = ttk.Frame(canvas)

      scrollable_frame.bind(
          "<Configure>",
          lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
      )

      canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
      canvas.configure(yscrollcommand=scrollbar.set)

      # 鼠标滚轮支持
      def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
      canvas.bind_all("<MouseWheel>", _on_mousewheel)

      canvas.pack(side="left", fill="both", expand=True)
      scrollbar.pack(side="right", fill="y")

      # 主框架(在可滚动框架内)
      main_frame = ttk.Frame(scrollable_frame, padding=30)
      main_frame.pack(fill=tk.BOTH, expand=True)

      # 应用图标/标题区域
      title_frame = ttk.Frame(main_frame)
      title_frame.pack(fill=tk.X, pady=(0, 20))

      # 应用名称
      app_name_label = ttk.Label(
          title_frame,
          text=APP_NAME,
          font=("Microsoft YaHei UI", 24, "bold"),
          foreground="#2c3e50"
      )
      app_name_label.pack()

      # 版本号
      version_label = ttk.Label(
          title_frame,
          text=f"版本 {APP_VERSION}",
          font=("Microsoft YaHei UI", 12),
          foreground="#7f8c8d"
      )
      version_label.pack(pady=(5, 0))

      # 分隔线
      separator1 = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
      separator1.pack(fill=tk.X, pady=15)

      # 描述信息
      desc_label = ttk.Label(
          main_frame,
          text=APP_DESCRIPTION,
          font=("Microsoft YaHei UI", 10),
          foreground="#34495e",
          wraplength=400,
          justify=tk.CENTER
      )
      desc_label.pack(pady=(0, 20))

      # 功能特性框架
      features_frame = ttk.LabelFrame(main_frame, text="主要特性", padding=15)
      features_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

      features = [
          "✓ 支持多种图片格式(JPEG, PNG, WebP等)",
          "✓ 自定义水印文本、字体、颜色",
          "✓ 灵活的水印位置调整",
          "✓ 自由拖拽水印到任意位置",
          "✓ 水印透明度和旋转角度设置",
          "✓ 实时预览效果",
          "✓ 批量处理多张图片",
          "✓ 水印模板保存与加载",
          "✓ 多种导出格式和质量选项",
      ]

      for feature in features:
        feature_label = ttk.Label(
            features_frame,
            text=feature,
            font=("Microsoft YaHei UI", 9),
            foreground="#2c3e50"
        )
        feature_label.pack(anchor=tk.W, pady=2)

      # 分隔线
      separator2 = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
      separator2.pack(fill=tk.X, pady=15)

      # 技术栈信息
      tech_frame = ttk.Frame(main_frame)
      tech_frame.pack(fill=tk.X, pady=(0, 15))

      tech_label = ttk.Label(
          tech_frame,
          text="技术栈",
          font=("Microsoft YaHei UI", 10, "bold"),
          foreground="#34495e"
      )
      tech_label.pack()

      tech_details = ttk.Label(
          tech_frame,
          text="Python • Tkinter • PIL/Pillow",
          font=("Microsoft YaHei UI", 9),
          foreground="#7f8c8d"
      )
      tech_details.pack(pady=(5, 0))

      # 作者信息
      author_frame = ttk.Frame(main_frame)
      author_frame.pack(fill=tk.X, pady=(0, 15))

      author_label = ttk.Label(
          author_frame,
          text=f"开发者: {APP_AUTHOR}",
          font=("Microsoft YaHei UI", 9),
          foreground="#34495e"
      )
      author_label.pack()

      # 版权信息
      copyright_label = ttk.Label(
          main_frame,
          text="Copyright © 2024 All Rights Reserved",
          font=("Microsoft YaHei UI", 8),
          foreground="#95a5a6"
      )
      copyright_label.pack()

      # 开源协议
      license_label = ttk.Label(
          main_frame,
          text="本软件遵循 MIT 开源协议",
          font=("Microsoft YaHei UI", 8),
          foreground="#95a5a6"
      )
      license_label.pack(pady=(5, 0))

      # 按钮框架
      button_frame = ttk.Frame(main_frame)
      button_frame.pack(pady=(20, 0))

      # 关闭按钮
      close_button = ttk.Button(
          button_frame,
          text="关闭",
          command=self.dialog.destroy,
          width=15
      )
      close_button.pack()

    except Exception as e:
      self.logger.error(f"创建关于对话框失败: {str(e)}")

  def _center_window(self):
    """居中显示窗口"""
    self.dialog.update_idletasks()
    width = self.dialog.winfo_width()
    height = self.dialog.winfo_height()
    x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
    self.dialog.geometry(f'{width}x{height}+{x}+{y}')

  def show(self):
    """显示对话框"""
    if self.dialog:
      self.dialog.grab_set()
      self.dialog.focus_set()
      self.dialog.wait_window()
