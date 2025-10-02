#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印处理桌面应用
主程序入口文件

作者: AI Assistant
日期: 2025-10-03
版本: 1.0.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
  from watermark_app.gui.main_window import MainWindow
  from watermark_app.utils.logger import setup_logger
except ImportError as e:
  print(f"导入模块失败: {e}")
  sys.exit(1)


def main():
  """主函数"""
  try:
    # 设置日志
    logger = setup_logger()
    logger.info("应用程序启动")

    # 创建主窗口
    root = TkinterDnD.Tk()
    app = MainWindow(root)

    # 启动GUI主循环
    root.mainloop()

    logger.info("应用程序正常退出")
  except Exception as e:
    error_msg = f"应用程序启动失败: {str(e)}"
    print(error_msg)
    messagebox.showerror("错误", error_msg)
    sys.exit(1)


if __name__ == "__main__":
  main()
