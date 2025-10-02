# 水印工具 (Watermark Tool)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-Alpha-yellow.svg)](https://github.com/Sakiyary/ai4se-photo-watermark)

一个跨平台的桌面水印工具，提供直观易用的图形界面，支持为图片批量添加文本和图片水印。

## 🚀 项目状态

**当前版本**: v2.0.0-beta  
**开发阶段**: Phase 2 完成 ✅ (核心功能开发)  
**最后更新**: 2024年12月

## ✨ 主要特性

### 已实现功能 ✅

#### 核心功能 (Phase 1 & 2)

- 🖥️ **跨平台GUI**: 基于Tkinter的现代化界面，支持Windows/macOS/Linux
- 📸 **智能文件管理**: 单张/批量导入，格式验证，重复检测，右键菜单操作
- 🎯 **高级预览系统**: 实时预览，缩放控制(10%-500%)，拖拽导航，键盘快捷键
- 📝 **增强水印功能**: 文本水印，旋转角度，阴影效果，描边效果，快速颜色选择
- 📐 **精确位置控制**: 九宫格定位，像素级偏移，实时位置预览
- 🎛️ **高效批量处理**: 多线程导出，进度监控，错误统计，取消操作支持
- 💾 **智能模板系统**: 预设模板，自定义保存，导入导出，快速应用
- ✅ **完善错误处理**: 文件验证，用户友好提示，详细错误报告

### 开发中功能 🚧

- �🖼️ **图片水印**: Logo或图片作为水印 (架构已预留)
- �️ **拖拽定位**: 鼠标直接拖拽水印位置
- 🔄 **水印旋转**: 任意角度旋转功能
- 📋 **模板系统**: 水印设置保存/加载模板

## 📦 安装说明

### 方式一：下载可执行文件 (推荐)

前往 [GitHub Releases](https://github.com/Sakiyary/ai4se-photo-watermark/releases) 下载对应平台的可执行文件：

- **Windows**: `WatermarkTool-Windows.exe`
- **macOS**: `WatermarkTool-macOS.dmg`  
- **Linux**: `WatermarkTool-Linux.AppImage`

### 方式二：从源码运行

1. 克隆项目：

```bash
git clone https://github.com/Sakiyary/ai4se-photo-watermark.git
cd ai4se-photo-watermark
```

2. 创建虚拟环境并安装依赖：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate

pip install -r requirements.txt
```

3. 运行应用：

```bash
python src/main.py
```

## 🚀 快速开始

### 基本使用流程

1. **导入图片**
   - 拖拽图片文件到主界面
   - 点击"添加文件"选择单张图片
   - 点击"添加文件夹"批量导入
   - 支持 JPEG、PNG、BMP、TIFF 格式

2. **配置水印**
   - 在左下角"水印设置"面板输入文本
   - 调节字体大小滑块 (8-128)
   - 选择颜色（点击颜色按钮）
   - 设置透明度 (0-255)
   - 选择九宫格位置或自定义偏移

3. **预览效果**
   - 右侧预览区域实时显示效果
   - 点击图片列表切换预览不同图片
   - 使用缩放按钮查看细节

4. **批量导出**
   - 点击菜单"文件" > "导出图片"
   - 选择输出目录（默认不允许覆盖原文件）
   - 设置文件命名规则（前缀/后缀）
   - 选择输出格式和质量
   - 点击"开始处理"

### 界面布局

```text
┌─────────────────┬──────────────────────────────┐
│   文件列表       │        预览区域               │
│                │                              │
│  📁 添加文件夹   │     [图片预览 + 水印效果]     │
│  📄 添加文件     │        [缩放控制]            │
│                │                              │
│  🖼️ image1.jpg │                              │
│  🖼️ image2.png │                              │
├─────────────────┼──────────────────────────────┤
│   水印设置       │        状态栏                │
│                │                              │
│  文本: [____]   │     当前: image1.jpg (1/2)   │
│  大小: [24]     │                              │
│  颜色: [⬜]     │                              │
│  透明度: [128]  │                              │
│  位置: [九宫格]  │                              │
└─────────────────┴──────────────────────────────┘
```

## 支持格式

### 输入格式

- JPEG (.jpg, .jpeg)
- PNG (.png) - 支持透明通道
- BMP (.bmp)
- TIFF (.tif, .tiff)

### 输出格式

- JPEG - 可调节压缩质量
- PNG - 保持透明通道

## 界面预览

```
┌─────────────────┬──────────────────────────────┐
│   文件列表       │        预览区域               │
│                │                              │
│  📁 添加文件夹   │     [图片预览 + 水印效果]      │
│  📄 添加文件     │                              │
│                │                              │
│  🖼️ image1.jpg │                              │
│  🖼️ image2.png │                              │
│  🖼️ image3.jpg │                              │
├─────────────────┼──────────────────────────────┤
│   水印设置       │        导出设置               │
│                │                              │
│  文本: [____]   │  输出文件夹: [____________]   │
│  大小: [__]     │  命名规则: [____________]     │
│  颜色: [__]     │  格式: [JPEG▼] 质量: [95]    │
│  透明度: [--]   │                              │
│  位置: [九宫格]  │         [开始处理]            │
└─────────────────┴──────────────────────────────┘
```

## 开发说明

### 环境准备

```bash
# 克隆项目
git clone https://github.com/Sakiyary/ai4se-photo-watermark.git
cd ai4se-photo-watermark

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 运行所有测试
pytest --cov=watermark_app

# 运行特定测试
pytest tests/test_core/ -v
```

### 代码质量

```bash
# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

## 项目结构

```
TODO
```

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -m '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 技术支持

- **问题反馈**: [GitHub Issues](https://github.com/Sakiyary/ai4se-photo-watermark/issues)
- **功能建议**: [GitHub Discussions](https://github.com/Sakiyary/ai4se-photo-watermark/discussions)
- **项目文档**: [Wiki](https://github.com/Sakiyary/ai4se-photo-watermark/wiki)

## 更新日志

### v2.0.0 (开发中)

- 🎉 全新 GUI 界面
- ✨ 实时预览功能
- 🔄 批量处理优化
- 📱 跨平台支持

### v1.0.0 (已弃用)

- 基础命令行工具
- EXIF 时间水印功能

---

更多信息请访问 [GitHub 仓库](https://github.com/Sakiyary/ai4se-photo-watermark)。

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pillow](https://pillow.readthedocs.io/) for image processing
- Uses [ExifRead](https://github.com/ianare/exif-py) for EXIF data extraction
- CLI powered by [Click](https://click.palletsprojects.com/)

## Troubleshooting

### Common Issues

**Q: "No EXIF date found" for all images**
A: Some cameras don't store date information in EXIF. Try using images from a different camera or smartphone.

**Q: Watermark appears too small/large**
A: Adjust the `--font-size` parameter. For high-resolution images, try larger values (64, 96, 128).

**Q: Custom font not working**
A: Ensure the font file path is correct and the font format is supported (.ttf, .otf).

**Q: Permission denied errors**
A: Make sure you have write permissions for the output directory.

---

For more information, issues, or feature requests, visit the [GitHub repository](https://github.com/Sakiyary/ai4se-photo-watermark).
