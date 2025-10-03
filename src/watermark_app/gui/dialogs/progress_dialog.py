#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度对话框模块
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional, Any


class ProgressDialog:
  """进度显示对话框"""

  def __init__(self, parent: tk.Widget, title: str = "处理中..."):
    """
    初始化进度对话框

    Args:
        parent: 父窗口
        title: 对话框标题
    """
    self.parent = parent
    self.dialog = None
    self.progress_var = None
    self.status_var = None
    self.cancel_var = False
    self.task_thread = None

    self._create_dialog(title)

  def _create_dialog(self, title: str):
    """创建对话框界面"""
    self.dialog = tk.Toplevel(self.parent)
    self.dialog.title(title)
    self.dialog.geometry("400x150")
    self.dialog.resizable(False, False)
    self.dialog.grab_set()  # 模态对话框

    # 居中显示
    self._center_dialog()

    # 创建界面
    main_frame = ttk.Frame(self.dialog)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # 状态标签
    self.status_var = tk.StringVar(value="正在初始化...")
    status_label = ttk.Label(main_frame, textvariable=self.status_var)
    status_label.pack(pady=(0, 10))

    # 进度条
    self.progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        main_frame,
        variable=self.progress_var,
        maximum=100,
        length=350,
        mode='determinate'
    )
    progress_bar.pack(pady=(0, 20))

    # 取消按钮
    button_frame = ttk.Frame(main_frame)
    button_frame.pack()

    cancel_btn = ttk.Button(
        button_frame,
        text="取消",
        command=self._cancel_task
    )
    cancel_btn.pack()

    # 防止用户关闭窗口
    self.dialog.protocol("WM_DELETE_WINDOW", self._cancel_task)

  def _center_dialog(self):
    """居中显示对话框"""
    self.dialog.update_idletasks()
    width = self.dialog.winfo_width()
    height = self.dialog.winfo_height()
    x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
    self.dialog.geometry(f'{width}x{height}+{x}+{y}')

  def _cancel_task(self):
    """取消任务"""
    self.cancel_var = True
    if self.task_thread and self.task_thread.is_alive():
      # 等待线程结束
      self.task_thread.join(timeout=1.0)
    self.close()

  def update_progress(self, percentage: float, status: str = ""):
    """
    更新进度

    Args:
        percentage: 进度百分比 (0-100)
        status: 状态文本
    """
    if self.dialog and self.dialog.winfo_exists():
      self.progress_var.set(percentage)
      if status:
        self.status_var.set(status)
      self.dialog.update()

  def run_task(self, task_func: Callable, *args, **kwargs) -> Any:
    """
    在后台线程中运行任务

    Args:
        task_func: 要执行的任务函数
        *args: 任务函数的位置参数
        **kwargs: 任务函数的关键字参数

    Returns:
        任务函数的返回值
    """
    result = None
    exception = None

    def task_wrapper():
      nonlocal result, exception
      try:
        result = task_func(self, *args, **kwargs)
      except Exception as e:
        exception = e

    # 启动任务线程
    self.task_thread = threading.Thread(target=task_wrapper)
    self.task_thread.daemon = True
    self.task_thread.start()

    # 等待任务完成
    while self.task_thread.is_alive() and not self.cancel_var:
      self.dialog.update()
      time.sleep(0.1)

    # 关闭对话框
    self.close()

    # 处理异常
    if exception:
      raise exception

    return result

  def close(self):
    """关闭对话框"""
    if self.dialog and self.dialog.winfo_exists():
      self.dialog.destroy()

  def is_cancelled(self) -> bool:
    """检查任务是否被取消"""
    return self.cancel_var
