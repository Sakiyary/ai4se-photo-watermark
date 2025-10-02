#!/usr/bin/env python3
"""
水印工具 - 应用程序入口

跨平台桌面水印工具主程序入口
"""

from watermark_app.app import WatermarkApp
import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
  """主程序入口"""
  try:
    # 创建主应用
    app = WatermarkApp()

    # 启动GUI主循环
    app.run()

  except Exception as e:
    # 捕获未处理的异常
    error_msg = f"应用程序启动失败: {str(e)}"
    print(f"错误: {error_msg}")

    # 尝试显示错误对话框
    try:
      root = tk.Tk()
      root.withdraw()  # 隐藏主窗口
      messagebox.showerror("启动错误", error_msg)
      root.destroy()
    except:
      pass

    sys.exit(1)


if __name__ == "__main__":
  main()
