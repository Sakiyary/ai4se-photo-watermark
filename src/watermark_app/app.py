"""
水印工具 - 应用程序主类

负责整个应用程序的初始化、配置管理和生命周期管理
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

from .gui.main_window import MainWindow
from .config.settings import AppSettings


class WatermarkApp:
  """水印工具应用程序主类"""

  def __init__(self):
    """初始化应用程序"""
    self.settings = None
    self.main_window = None
    self.root = None

    # 初始化应用程序
    self._initialize()

  def _initialize(self):
    """初始化应用程序组件"""
    # 创建Tkinter根窗口
    self.root = tk.Tk()

    # 设置应用程序基本属性
    self.root.title("水印工具 v2.0.0")
    self.root.geometry("1200x800")
    self.root.minsize(800, 600)

    # 设置应用程序图标（如果存在）
    self._set_app_icon()

    # 初始化配置
    self.settings = AppSettings()

    # 创建主窗口
    self.main_window = MainWindow(self.root, self.settings)

    # 设置窗口关闭事件
    self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

  def _set_app_icon(self):
    """设置应用程序图标"""
    try:
      # 查找图标文件
      icon_path = Path(__file__).parent.parent.parent / \
          "assets" / "icons" / "app.ico"
      if icon_path.exists():
        self.root.iconbitmap(str(icon_path))
    except Exception as e:
      # 忽略图标加载错误
      print(f"无法加载应用图标: {e}")

  def _on_closing(self):
    """应用程序关闭事件处理"""
    try:
      # 保存设置
      if self.settings:
        self.settings.save()

      # 清理资源
      if self.main_window:
        self.main_window.cleanup()

    except Exception as e:
      print(f"关闭应用时发生错误: {e}")
    finally:
      # 销毁主窗口
      if self.root:
        self.root.quit()
        self.root.destroy()

  def run(self):
    """启动应用程序"""
    if not self.root:
      raise RuntimeError("应用程序未正确初始化")

    # 启动Tkinter主循环
    self.root.mainloop()

  def get_version(self):
    """获取应用程序版本"""
    from . import __version__
    return __version__
