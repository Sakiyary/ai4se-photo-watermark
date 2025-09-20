# AI4SE Photo Watermark Tool

一个基于 EXIF 数据为照片添加日期水印的 Python 命令行工具。

A Python command-line tool for adding date watermarks to photos based on EXIF data.

## 功能特性 Features

- 🖼️ 支持多种图片格式：JPEG、PNG、TIFF、BMP
- 📅 自动提取 EXIF 拍摄日期信息
- 🎨 可自定义字体大小、颜色和位置
- 📁 支持单文件和批量处理
- 💾 自动创建输出目录，保持原文件不变
- 🔧 智能降级处理（无 EXIF 时使用文件时间）

## 安装 Installation

1. 克隆仓库：
```bash
git clone https://github.com/Sakiyary/ai4se-photo-watermark.git
cd ai4se-photo-watermark
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法 Usage

### 基本用法

```bash
# 处理单个图片文件
python watermark.py /path/to/photo.jpg

# 处理目录中的所有图片
python watermark.py /path/to/photos/
```

### 自定义选项

```bash
# 自定义字体大小、颜色和位置
python watermark.py /path/to/photos/ --font-size 36 --color red --position top-left

# 查看帮助信息
python watermark.py --help
```

### 参数说明

- `input_path`: 输入图片文件或目录路径
- `--font-size`: 字体大小（默认：48）
- `--color`: 字体颜色（默认：white）
- `--position`: 水印位置（默认：bottom-right）

#### 支持的位置选项
- `top-left`: 左上角
- `top-right`: 右上角  
- `center`: 居中
- `bottom-left`: 左下角
- `bottom-right`: 右下角

#### 支持的颜色
- 颜色名称：`white`, `black`, `red`, `green`, `blue`, `yellow` 等
- 十六进制颜色代码：`#FF0000`, `#00FF00` 等

## 输出说明 Output

程序会在原目录下创建名为 `原目录名_watermark` 的子目录，所有带水印的图片都会保存在这个新目录中。原始图片文件保持不变。

The program creates a subdirectory named `original_directory_name_watermark` under the original directory, where all watermarked images are saved. Original image files remain unchanged.

## 示例 Examples

```bash
# 示例 1：处理单个文件
python watermark.py ~/Photos/IMG_001.jpg

# 示例 2：批量处理，使用默认设置
python watermark.py ~/Photos/

# 示例 3：自定义水印样式
python watermark.py ~/Photos/ --font-size 60 --color "#FF6B6B" --position top-right

# 示例 4：小字体，居中位置
python watermark.py ~/Photos/ --font-size 24 --color black --position center
```

## 技术实现 Technical Details

### 依赖库
- **Pillow (PIL)**: 图像处理和文本绘制
- **Python 标准库**: argparse, pathlib, datetime, os

### 核心功能
1. **EXIF 数据提取**: 读取图片的拍摄时间信息
2. **智能降级**: 当 EXIF 数据不可用时，使用文件修改时间
3. **水印渲染**: 在指定位置绘制日期文本，包含阴影效果
4. **批量处理**: 自动识别和处理目录中的所有图片文件

### 文件结构
```
ai4se-photo-watermark/
├── watermark.py          # 主程序文件
├── requirements.txt      # 依赖包列表
├── README.md            # 使用说明
├── PRD.md              # 产品需求文档
├── WORKPLAN.md         # 工作计划文档
├── LICENSE             # MIT 许可证
└── .gitignore          # Git 忽略文件
```

## 错误处理 Error Handling

程序包含完善的错误处理机制：
- 输入路径验证
- 图片格式检查
- EXIF 数据读取异常处理
- 文件权限检查
- 内存和性能优化

## 许可证 License

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 贡献 Contributing

欢迎提交 Issue 和 Pull Request！

Issues and Pull Requests are welcome!

## 更新日志 Changelog

### v1.0.0
- 初始版本发布
- 支持基本的日期水印功能
- 支持多种自定义选项
- 完整的错误处理和文档