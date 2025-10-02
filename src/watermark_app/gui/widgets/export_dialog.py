"""
水印工具 - 导出对话框组件

用于配置批量导出设置和执行导出操作
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class ExportDialog:
  """导出对话框"""

  def __init__(self, parent, image_files, watermark_config):
    """初始化导出对话框

    Args:
        parent: 父窗口
        image_files: 图片文件列表
        watermark_config: 水印配置
    """
    self.parent = parent
    self.image_files = image_files
    self.watermark_config = watermark_config

    # 设置变量
    self.output_dir = tk.StringVar()
    self.naming_rule = tk.StringVar(value="suffix")
    self.prefix_text = tk.StringVar(value="wm_")
    self.suffix_text = tk.StringVar(value="_watermarked")
    self.output_format = tk.StringVar(value="original")
    self.jpeg_quality = tk.IntVar(value=95)

    # 进度控制
    self.is_processing = False
    self.should_cancel = False

    self._create_dialog()

  def _create_dialog(self):
    """创建对话框"""
    self.dialog = tk.Toplevel(self.parent)
    self.dialog.title("导出设置")
    self.dialog.geometry("500x600")
    self.dialog.resizable(False, False)
    self.dialog.transient(self.parent)
    self.dialog.grab_set()

    # 居中显示
    self.dialog.update_idletasks()
    x = (self.dialog.winfo_screenwidth() // 2) - \
        (self.dialog.winfo_width() // 2)
    y = (self.dialog.winfo_screenheight() // 2) - \
        (self.dialog.winfo_height() // 2)
    self.dialog.geometry(f"+{x}+{y}")

    # 创建界面
    self._setup_ui()

  def _setup_ui(self):
    """设置用户界面"""
    # 主框架
    main_frame = ttk.Frame(self.dialog, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 文件信息
    info_frame = ttk.LabelFrame(main_frame, text="待处理文件", padding=5)
    info_frame.pack(fill=tk.X, pady=(0, 10))

    info_label = ttk.Label(
        info_frame,
        text=f"共 {len(self.image_files)} 个文件待处理"
    )
    info_label.pack(anchor=tk.W)

    # 输出目录设置
    output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding=5)
    output_frame.pack(fill=tk.X, pady=(0, 10))

    # 输出目录
    dir_frame = ttk.Frame(output_frame)
    dir_frame.pack(fill=tk.X, pady=2)

    ttk.Label(dir_frame, text="输出目录:").pack(anchor=tk.W)

    dir_select_frame = ttk.Frame(dir_frame)
    dir_select_frame.pack(fill=tk.X, pady=2)

    self.output_entry = ttk.Entry(
        dir_select_frame, textvariable=self.output_dir)
    self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    self.browse_btn = ttk.Button(
        dir_select_frame,
        text="浏览",
        command=self._browse_output_dir,
        width=8
    )
    self.browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

    # 命名规则
    naming_frame = ttk.LabelFrame(main_frame, text="文件命名", padding=5)
    naming_frame.pack(fill=tk.X, pady=(0, 10))

    # 命名规则选择
    ttk.Radiobutton(
        naming_frame,
        text="保留原文件名",
        variable=self.naming_rule,
        value="original"
    ).pack(anchor=tk.W)

    # 前缀选项
    prefix_frame = ttk.Frame(naming_frame)
    prefix_frame.pack(fill=tk.X, pady=2)

    ttk.Radiobutton(
        prefix_frame,
        text="添加前缀:",
        variable=self.naming_rule,
        value="prefix"
    ).pack(side=tk.LEFT)

    self.prefix_entry = ttk.Entry(
        prefix_frame,
        textvariable=self.prefix_text,
        width=15
    )
    self.prefix_entry.pack(side=tk.LEFT, padx=(5, 0))

    # 后缀选项
    suffix_frame = ttk.Frame(naming_frame)
    suffix_frame.pack(fill=tk.X, pady=2)

    ttk.Radiobutton(
        suffix_frame,
        text="添加后缀:",
        variable=self.naming_rule,
        value="suffix"
    ).pack(side=tk.LEFT)

    self.suffix_entry = ttk.Entry(
        suffix_frame,
        textvariable=self.suffix_text,
        width=15
    )
    self.suffix_entry.pack(side=tk.LEFT, padx=(5, 0))

    # 格式设置
    format_frame = ttk.LabelFrame(main_frame, text="输出格式", padding=5)
    format_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Radiobutton(
        format_frame,
        text="保持原格式",
        variable=self.output_format,
        value="original"
    ).pack(anchor=tk.W)

    ttk.Radiobutton(
        format_frame,
        text="JPEG格式",
        variable=self.output_format,
        value="jpeg"
    ).pack(anchor=tk.W)

    # JPEG质量设置
    quality_frame = ttk.Frame(format_frame)
    quality_frame.pack(fill=tk.X, pady=2, padx=(20, 0))

    ttk.Label(quality_frame, text="JPEG质量:").pack(side=tk.LEFT)

    self.quality_scale = ttk.Scale(
        quality_frame,
        from_=10,
        to=100,
        variable=self.jpeg_quality,
        orient=tk.HORIZONTAL,
        length=150
    )
    self.quality_scale.pack(side=tk.LEFT, padx=(5, 5))

    self.quality_label = ttk.Label(quality_frame, text="95")
    self.quality_label.pack(side=tk.LEFT)

    ttk.Radiobutton(
        format_frame,
        text="PNG格式",
        variable=self.output_format,
        value="png"
    ).pack(anchor=tk.W)

    # 进度显示
    progress_frame = ttk.LabelFrame(main_frame, text="处理进度", padding=5)
    progress_frame.pack(fill=tk.X, pady=(0, 10))

    self.progress = ttk.Progressbar(
        progress_frame,
        mode='determinate',
        maximum=len(self.image_files)
    )
    self.progress.pack(fill=tk.X, pady=2)

    self.status_label = ttk.Label(progress_frame, text="准备就绪")
    self.status_label.pack(anchor=tk.W, pady=(2, 0))

    # 按钮区域
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))

    self.start_btn = ttk.Button(
        button_frame,
        text="开始处理",
        command=self._start_export
    )
    self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

    self.cancel_btn = ttk.Button(
        button_frame,
        text="取消",
        command=self._cancel_export
    )
    self.cancel_btn.pack(side=tk.LEFT)

    self.close_btn = ttk.Button(
        button_frame,
        text="关闭",
        command=self._close_dialog
    )
    self.close_btn.pack(side=tk.RIGHT)

    # 绑定事件
    self.jpeg_quality.trace_add('write', self._update_quality_label)

    # 设置默认输出目录
    self._set_default_output_dir()

  def _update_quality_label(self, *args):
    """更新质量标签"""
    self.quality_label.config(text=str(self.jpeg_quality.get()))

  def _set_default_output_dir(self):
    """设置默认输出目录"""
    if self.image_files:
      first_file = Path(self.image_files[0])
      default_dir = first_file.parent / f"{first_file.parent.name}_watermarked"
      self.output_dir.set(str(default_dir))

  def _browse_output_dir(self):
    """浏览输出目录"""
    directory = filedialog.askdirectory(
        title="选择输出目录",
        initialdir=self.output_dir.get()
    )
    if directory:
      self.output_dir.set(directory)

  def _start_export(self):
    """开始导出"""
    # 验证设置
    if not self.output_dir.get().strip():
      messagebox.showerror("错误", "请选择输出目录")
      return

    output_path = Path(self.output_dir.get())
    if not output_path.exists():
      try:
        output_path.mkdir(parents=True)
      except Exception as e:
        messagebox.showerror("错误", f"无法创建输出目录: {e}")
        return

    # 检查是否为原文件目录
    if self.image_files:
      first_file_dir = Path(self.image_files[0]).parent
      if output_path.samefile(first_file_dir):
        if not messagebox.askyesno(
            "警告",
            "输出目录与原文件目录相同，可能会覆盖原文件。确定继续吗？"
        ):
          return

    # 开始处理
    self.is_processing = True
    self.should_cancel = False

    # 更新界面状态
    self.start_btn.config(state='disabled')
    self.browse_btn.config(state='disabled')
    self.close_btn.config(state='disabled')

    # 重置进度
    self.progress['value'] = 0
    self.status_label.config(text="开始处理...")

    # 在后台线程中处理
    threading.Thread(target=self._process_images, daemon=True).start()

  def _cancel_export(self):
    """取消导出"""
    if self.is_processing:
      self.should_cancel = True
      self.status_label.config(text="正在取消...")

  def _close_dialog(self):
    """关闭对话框"""
    if self.is_processing:
      if messagebox.askyesno("确认", "正在处理中，确定要关闭吗？"):
        self.should_cancel = True
        self.dialog.destroy()
    else:
      self.dialog.destroy()

  def _process_images(self):
    """处理图片（在后台线程中运行）"""
    try:
      output_path = Path(self.output_dir.get())
      processed = 0
      errors = []

      for i, image_file in enumerate(self.image_files):
        if self.should_cancel:
          break

        try:
          # 更新状态
          self.dialog.after(0, lambda: self.status_label.config(
              text=f"处理: {Path(image_file).name}"
          ))

          # 处理单个图片
          self._process_single_image(image_file, output_path)
          processed += 1

          # 更新进度
          self.dialog.after(0, lambda: self.progress.config(value=processed))

        except Exception as e:
          errors.append(f"{Path(image_file).name}: {str(e)}")

      # 处理完成
      if self.should_cancel:
        self.dialog.after(0, lambda: self.status_label.config(text="已取消"))
      else:
        success_msg = f"处理完成！成功: {processed}, 失败: {len(errors)}"
        self.dialog.after(0, lambda: self.status_label.config(text=success_msg))

        if errors:
          error_msg = "以下文件处理失败:\n" + "\n".join(errors[:10])
          if len(errors) > 10:
            error_msg += f"\n... 还有 {len(errors) - 10} 个错误"
          self.dialog.after(
              0, lambda: messagebox.showwarning("处理警告", error_msg))

    except Exception as e:
      self.dialog.after(
          0, lambda: messagebox.showerror("错误", f"处理过程中发生错误: {e}"))

    finally:
      # 恢复界面状态
      self.dialog.after(0, self._finish_processing)

  def _finish_processing(self):
    """完成处理，恢复界面状态"""
    self.is_processing = False
    self.start_btn.config(state='normal')
    self.browse_btn.config(state='normal')
    self.close_btn.config(state='normal')

  def _process_single_image(self, image_file, output_dir):
    """处理单个图片"""
    # 打开图片
    with Image.open(image_file) as image:
      # 应用水印
      watermarked = self._apply_watermark(image)

      # 生成输出文件名
      output_file = self._generate_output_filename(image_file, output_dir)

      # 保存图片
      if self.output_format.get() == "jpeg":
        # 转换为RGB模式并保存为JPEG
        if watermarked.mode in ('RGBA', 'P'):
          rgb_image = Image.new('RGB', watermarked.size, (255, 255, 255))
          if watermarked.mode == 'RGBA':
            rgb_image.paste(watermarked, mask=watermarked.split()[3])
          else:
            rgb_image.paste(watermarked)
          watermarked = rgb_image

        watermarked.save(output_file, "JPEG", quality=self.jpeg_quality.get())

      elif self.output_format.get() == "png":
        watermarked.save(output_file, "PNG")

      else:  # 原格式
        # 保持原始格式
        original_format = image.format or 'JPEG'
        if original_format == 'JPEG' and watermarked.mode in ('RGBA', 'P'):
          rgb_image = Image.new('RGB', watermarked.size, (255, 255, 255))
          if watermarked.mode == 'RGBA':
            rgb_image.paste(watermarked, mask=watermarked.split()[3])
          else:
            rgb_image.paste(watermarked)
          watermarked = rgb_image

        save_kwargs = {}
        if original_format == 'JPEG':
          save_kwargs['quality'] = 95

        watermarked.save(output_file, original_format, **save_kwargs)

  def _apply_watermark(self, image):
    """应用水印"""
    # 这里复用PreviewPanel中的水印应用逻辑
    watermarked = image.copy()

    if not self.watermark_config.get('text', '').strip():
      return watermarked

    try:
      draw = ImageDraw.Draw(watermarked)

      # 获取配置
      text = self.watermark_config['text']
      font_size = self.watermark_config.get('font_size', 24)
      color = self.watermark_config.get('color', '#FFFFFF')
      opacity = self.watermark_config.get('opacity', 128)
      position = self.watermark_config.get('position', 'bottom-right')
      offset_x = self.watermark_config.get('offset_x', 10)
      offset_y = self.watermark_config.get('offset_y', 10)

      # 字体
      try:
        font = ImageFont.truetype("arial.ttf", font_size)
      except:
        font = ImageFont.load_default()

      # 计算位置
      bbox = draw.textbbox((0, 0), text, font=font)
      text_width = bbox[2] - bbox[0]
      text_height = bbox[3] - bbox[1]

      x, y = self._calculate_watermark_position(
          position, image.size, (text_width, text_height), offset_x, offset_y
      )

      # 应用水印
      if color.startswith('#'):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        text_color = (r, g, b, opacity)
      else:
        text_color = (255, 255, 255, opacity)

      # 创建透明层
      overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
      overlay_draw = ImageDraw.Draw(overlay)
      overlay_draw.text((x, y), text, font=font, fill=text_color)

      # 合并
      watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay)
      watermarked = watermarked.convert('RGB')

    except Exception as e:
      print(f"应用水印失败: {e}")

    return watermarked

  def _calculate_watermark_position(self, position, image_size, text_size, offset_x, offset_y):
    """计算水印位置"""
    img_w, img_h = image_size
    text_w, text_h = text_size

    position_map = {
        'top-left': (offset_x, offset_y),
        'top-center': ((img_w - text_w) // 2, offset_y),
        'top-right': (img_w - text_w - offset_x, offset_y),
        'left-center': (offset_x, (img_h - text_h) // 2),
        'center': ((img_w - text_w) // 2, (img_h - text_h) // 2),
        'right-center': (img_w - text_w - offset_x, (img_h - text_h) // 2),
        'bottom-left': (offset_x, img_h - text_h - offset_y),
        'bottom-center': ((img_w - text_w) // 2, img_h - text_h - offset_y),
        'bottom-right': (img_w - text_w - offset_x, img_h - text_h - offset_y),
    }

    return position_map.get(position, position_map['bottom-right'])

  def _generate_output_filename(self, input_file, output_dir):
    """生成输出文件名"""
    input_path = Path(input_file)
    base_name = input_path.stem

    # 根据命名规则生成新名称
    if self.naming_rule.get() == "prefix":
      new_name = self.prefix_text.get() + base_name
    elif self.naming_rule.get() == "suffix":
      new_name = base_name + self.suffix_text.get()
    else:  # original
      new_name = base_name

    # 确定扩展名
    if self.output_format.get() == "jpeg":
      extension = ".jpg"
    elif self.output_format.get() == "png":
      extension = ".png"
    else:  # original
      extension = input_path.suffix

    # 生成完整路径
    output_file = output_dir / f"{new_name}{extension}"

    # 避免文件名冲突
    counter = 1
    original_output_file = output_file
    while output_file.exists():
      output_file = output_dir / f"{new_name}_{counter}{extension}"
      counter += 1

    return output_file
