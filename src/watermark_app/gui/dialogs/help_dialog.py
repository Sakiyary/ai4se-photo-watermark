#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用说明对话框
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import logging


class HelpDialog:
  """使用说明对话框"""

  def __init__(self, parent):
    """
    初始化使用说明对话框

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
      self.dialog.title("使用说明")
      self.dialog.geometry("800x600")
      self.dialog.resizable(True, True)

      # 居中显示
      self.dialog.transient(self.parent)
      self._center_window()

      # 创建笔记本标签页
      notebook = ttk.Notebook(self.dialog)
      notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

      # 快速入门标签页
      self._create_quick_start_tab(notebook)

      # 功能说明标签页
      self._create_features_tab(notebook)

      # 快捷键标签页
      self._create_shortcuts_tab(notebook)

      # 常见问题标签页
      self._create_faq_tab(notebook)

      # 关闭按钮
      button_frame = ttk.Frame(self.dialog)
      button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

      ttk.Button(
          button_frame,
          text="关闭",
          command=self.dialog.destroy,
          width=15
      ).pack(side=tk.RIGHT)

    except Exception as e:
      self.logger.error(f"创建使用说明对话框失败: {str(e)}")

  def _create_quick_start_tab(self, notebook):
    """创建快速入门标签页"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="快速入门")

    # 创建滚动文本框
    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=("Microsoft YaHei UI", 10),
        padx=15,
        pady=15
    )
    text_widget.pack(fill=tk.BOTH, expand=True)

    # 添加内容
    content = """
欢迎使用图片水印工具！

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 基本使用流程

1. 导入图片
   • 点击工具栏的"导入图片"按钮,或使用菜单"文件 → 导入图片"
   • 支持拖拽图片或文件夹到窗口左侧图片列表区域
   • 支持批量导入多张图片

2. 配置水印
   • 在右侧"水印设置"面板中配置水印文本、字体、大小等参数
   • 实时预览效果会显示在中央预览区域
   • 可以调整水印的透明度、旋转角度等

3. 调整位置
   • 在"位置设置"面板中选择水印位置(九宫格)
   • 支持自由拖拽水印到任意位置(直接在预览区拖动水印)
   • 可以设置边距来微调水印位置

4. 导出图片
   • 点击"导出当前"保存单张图片
   • 点击"批量导出"保存所有添加水印的图片
   • 可以选择输出格式(JPEG/PNG/WebP)和质量


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 使用技巧

• 拖拽操作: 直接将图片/文件夹拖到窗口即可导入
• 键盘导航: 使用左右方向键快速切换图片
• 模板功能: 保存常用的水印配置为模板,下次直接加载
• 批量处理: 导入多张图片后,配置好水印即可批量导出
• 自由拖拽: 在预览区点击水印并拖动,可自由调整位置
• 对齐辅助: 拖动水印时会显示红色中心线和橙色边缘线辅助对齐


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ 支持的图片格式

输入格式: JPEG, JPG, PNG, BMP, TIFF
输出格式: JPEG, PNG, BMP, TIFF
"""

    text_widget.insert("1.0", content)
    text_widget.config(state=tk.DISABLED)

  def _create_features_tab(self, notebook):
    """创建功能说明标签页"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="功能说明")

    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=("Microsoft YaHei UI", 10),
        padx=15,
        pady=15
    )
    text_widget.pack(fill=tk.BOTH, expand=True)

    content = """
功能详细说明

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 水印设置

水印文本
  • 输入要添加的水印文字
  • 支持多行文本(使用换行符分隔)
  • 支持中英文及特殊字符

字体设置
  • 字体: 选择系统中已安装的字体
  • 大小: 调整水印文字大小(1-500像素)
  • 颜色: 点击色块选择水印颜色
  • 粗体/斜体: 勾选相应选项应用字体样式

透明度
  • 调整水印的不透明度(0-100%)
  • 0%完全透明,100%完全不透明
  • 适当降低透明度可以使水印更自然

旋转角度
  • 设置水印的旋转角度(-180° 到 +180°)
  • 正值为顺时针旋转,负值为逆时针旋转
  • 常用值: 0°(水平), 45°(斜向), 90°(垂直)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 位置设置

预设位置
  • 提供九宫格位置选择(左上、上中、右上等)
  • 点击对应位置即可快速定位

自定义位置
  • 选择"自定义"单选按钮
  • 直接在预览区拖动水印到目标位置
  • 或手动输入X、Y坐标精确定位

边距调整
  • 水平边距: 调整水印距离左/右边缘的距离
  • 垂直边距: 调整水印距离上/下边缘的距离
  • 适用于所有预设位置


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖼️ 预览功能

缩放控制
  • 适应窗口: 自动调整图片大小以适应预览区
  • 实际大小: 显示图片原始尺寸
  • 放大/缩小: 点击按钮或使用Ctrl+滚轮缩放

拖拽水印
  • 点击水印并拖动可自由调整位置
  • 拖动时显示蓝色边界框
  • 接近中心或边缘时显示红色/橙色对齐线
  • 松开鼠标即保存新位置


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 导出功能

导出当前图片
  • 导出当前正在预览的图片
  • 可选择保存位置和文件名
  • 支持选择输出格式和质量

批量导出
  • 一次性导出列表中的所有图片
  • 选择输出文件夹
  • 设置统一的输出格式和质量
  • 可选择文件命名规则(保持原名/添加后缀等)

输出格式
  • JPEG: 适合照片,文件小,有损压缩
  • PNG: 适合图形,支持透明背景,无损压缩
  • WebP: 现代格式,文件更小,支持透明和动画


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 模板功能

保存模板
  • 将当前的水印配置保存为模板
  • 输入模板名称和描述
  • 下次可快速加载复用

加载模板
  • 从已保存的模板中选择
  • 一键应用模板中的所有设置

管理模板
  • 查看所有已保存的模板
  • 重命名、删除或更新模板
"""

    text_widget.insert("1.0", content)
    text_widget.config(state=tk.DISABLED)

  def _create_shortcuts_tab(self, notebook):
    """创建快捷键标签页"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="快捷键")

    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=("Microsoft YaHei UI", 10),
        padx=15,
        pady=15
    )
    text_widget.pack(fill=tk.BOTH, expand=True)

    content = """
快捷键列表

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 文件操作

Ctrl + O              导入图片
Ctrl + Shift + O      导入文件夹
Ctrl + S              导出当前图片
Ctrl + Shift + S      批量导出
Ctrl + Q              退出程序


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✏️ 编辑操作

Ctrl + Delete         清空图片列表
Delete                删除选中的图片


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 导航操作

←  或  ↑             上一张图片
→  或  ↓             下一张图片
Escape                清除选择
F5                    刷新当前图片


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 视图操作

Ctrl + 加号           放大预览
Ctrl + 减号           缩小预览
Ctrl + 0              适应窗口
Ctrl + 1              实际大小
Ctrl + 滚轮           缩放预览图


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖱️ 鼠标操作

点击水印 + 拖动       自由调整水印位置
拖拽图片到窗口        导入图片
拖拽文件夹到窗口      批量导入
"""

    text_widget.insert("1.0", content)
    text_widget.config(state=tk.DISABLED)

  def _create_faq_tab(self, notebook):
    """创建常见问题标签页"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="常见问题")

    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=("Microsoft YaHei UI", 10),
        padx=15,
        pady=15
    )
    text_widget.pack(fill=tk.BOTH, expand=True)

    content = """
常见问题解答

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 支持哪些图片格式?
A: 输入支持: JPEG, JPG, PNG, BMP, TIFF, 等常见格式
   输出支持: JPEG, PNG, BMP, TIFF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 水印可以设置透明度吗?
A: 可以。在"水印设置"面板中调整"透明度"滑块,范围是 0-100%。
   建议设置在 30-70% 之间,既能看清水印又不会过于突兀。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 如何让水印斜着显示?
A: 在"水印设置"面板中调整"旋转角度",常用值为 45° 或 -45°。
   正值为顺时针旋转,负值为逆时针旋转。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 如何精确调整水印位置?
A: 有三种方式:
   1. 使用九宫格预设位置快速定位
   2. 直接在预览区拖动水印
   3. 选择"自定义"后手动输入X、Y坐标

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 为什么我的字体没有显示?
A: 请确保选择的字体已安装在系统中。程序只能使用系统已安装的字体。
   建议使用常见字体如"微软雅黑"、"宋体"、"Arial"等。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 批量导出时会覆盖原文件吗?
A: 不会。默认情况下会在原文件名后添加"_watermarked"后缀。
   您也可以在导出对话框中自定义命名规则。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 导出的图片质量如何控制?
A: 在导出对话框中可以设置输出质量:
   • JPEG: 1-100,建议 85-95
   • PNG: 自动无损压缩
   • WebP: 1-100,建议 80-90

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 如何保存常用的水印配置?
A: 使用模板功能:
   1. 配置好水印参数
   2. 点击"保存模板"按钮
   3. 输入模板名称和描述
   4. 下次点击"加载模板"即可快速应用

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 预览图和导出的图片不一样?
A: 预览图是为了显示方便可能进行了缩放,但导出的图片是基于原始
   分辨率处理的,水印位置和大小比例会保持一致。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 能否给不同的图片设置不同的水印?
A: 目前版本所有图片使用相同的水印配置。如需不同水印,建议:
   1. 分批导入需要相同水印的图片
   2. 配置水印后批量导出
   3. 清空列表后导入下一批图片

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 程序运行缓慢怎么办?
A: 建议:
   • 避免一次性导入过多高分辨率图片
   • 关闭其他占用资源的程序
   • 导出时选择合适的输出质量(不必追求最高)
"""

    text_widget.insert("1.0", content)
    text_widget.config(state=tk.DISABLED)

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
