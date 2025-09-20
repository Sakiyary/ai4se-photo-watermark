# 产品需求文档 (PRD) - AI4SE Photo Watermark

## 1. 产品概述

### 1.1 产品名称

AI4SE Photo Watermark - 基于EXIF时间信息的图片水印工具

### 1.2 产品简介

一个Python命令行工具，能够自动读取图片的EXIF拍摄时间信息，将年月日格式化为文本水印并添加到图片上，支持批量处理和自定义水印样式。

### 1.3 目标用户

- 摄影爱好者和专业摄影师
- 需要为照片添加时间戳的用户
- 需要批量处理图片的用户

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 图片处理功能

- **输入**：用户指定图片文件路径（支持单个文件或目录）
- **EXIF读取**：自动解析图片的EXIF数据，提取拍摄时间信息
- **时间格式化**：将拍摄时间转换为年-月-日格式（如：2024-03-15）
- **水印添加**：将格式化的日期作为文本水印绘制到图片上
- **输出保存**：在原目录下创建"{原目录名}_watermark"子目录，保存处理后的图片

#### 2.1.2 水印自定义功能

- **字体大小**：用户可设置水印文字的字体大小
- **字体颜色**：支持设置水印文字颜色（RGB/十六进制）
- **水印位置**：支持多种预设位置
  - 左上角 (top-left)
  - 上方居中 (top-center)
  - 右上角 (top-right)
  - 左侧居中 (left-center)
  - 正中央 (center)
  - 右侧居中 (right-center)
  - 左下角 (bottom-left)
  - 下方居中 (bottom-center)
  - 右下角 (bottom-right)

### 2.2 命令行接口

#### 2.2.1 基本命令格式

```bash
python -m photo_watermark [OPTIONS] INPUT_PATH
```

#### 2.2.2 参数定义

- `INPUT_PATH`：必需参数，图片文件或目录路径
- `--font-size, -s`：字体大小，默认值：32
- `--color, -c`：字体颜色，默认值：white
- `--position, -p`：水印位置，默认值：bottom-right
- `--help, -h`：显示帮助信息
- `--version, -v`：显示版本信息

#### 2.2.3 使用示例

```bash
# 基本用法
python -m photo_watermark /path/to/photos

# 自定义参数
python -m photo_watermark /path/to/photos --font-size 24 --color "#FF0000" --position top-left

# 处理单个文件
python -m photo_watermark /path/to/photo.jpg --font-size 18 --color white
```

## 3. 技术需求

### 3.1 技术栈

- **编程语言**：Python 3.8+
- **图像处理**：Pillow (PIL Fork)
- **EXIF处理**：ExifRead 或 Pillow内置EXIF功能
- **命令行解析**：argparse
- **文件系统操作**：pathlib

### 3.2 依赖库

```txt
Pillow>=9.0.0
exifread>=3.0.0
```

### 3.3 支持的图片格式

- JPEG (.jpg, .jpeg)
- TIFF (.tiff, .tif)
- 其他包含EXIF信息的格式

## 4. 非功能性需求

### 4.1 性能要求

- 单张图片处理时间 < 5秒
- 支持批量处理大量图片
- 内存使用优化，避免同时加载过多图片

### 4.2 可用性要求

- 命令行界面简洁易用
- 详细的错误提示和帮助信息
- 支持进度显示（批量处理时）

### 4.3 兼容性要求

- 支持Windows、macOS、Linux操作系统
- Python 3.8及以上版本兼容

### 4.4 错误处理

- 无EXIF信息的图片：跳过并记录警告
- 不支持的文件格式：跳过并提示
- 文件权限问题：提供清晰的错误信息
- 输出目录创建失败：提供解决建议

## 5. 用户界面设计

### 5.1 命令行输出示例

```
Photo Watermark Tool v1.0.0

Processing: /path/to/photos
Found 15 image files

[1/15] Processing IMG_001.jpg... ✓ (2024-03-15)
[2/15] Processing IMG_002.jpg... ✓ (2024-03-15)
[3/15] Processing IMG_003.jpg... ⚠ No EXIF date found, skipping
...
[15/15] Processing IMG_015.jpg... ✓ (2024-03-16)

Summary:
- Processed: 14 images
- Skipped: 1 image
- Output directory: /path/to/photos_watermark

Completed successfully!
```

## 6. 验收标准

### 6.1 功能验收

- [ ] 能够正确读取JPEG图片的EXIF拍摄时间
- [ ] 能够将时间格式化为YYYY-MM-DD格式
- [ ] 能够在指定位置添加文本水印
- [ ] 能够自定义字体大小和颜色
- [ ] 能够批量处理目录中的所有图片
- [ ] 能够在正确位置创建输出目录

### 6.2 质量验收

- [ ] 代码覆盖率 > 80%
- [ ] 所有单元测试通过
- [ ] 支持的操作系统测试通过
- [ ] 性能基准测试通过

## 7. 风险评估

### 7.1 技术风险

- **EXIF解析复杂性**：不同相机品牌的EXIF格式可能有差异
- **字体渲染**：不同操作系统的字体支持可能不同
- **内存使用**：大图片批量处理可能导致内存问题

### 7.2 缓解方案

- 使用成熟的EXIF解析库（ExifRead/Pillow）
- 提供默认字体，支持用户自定义字体路径
- 实现流式处理，避免同时加载多张大图
