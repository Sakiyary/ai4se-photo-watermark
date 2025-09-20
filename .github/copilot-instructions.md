# Copilot Instructions for ai4se-photo-watermark

## 项目概览

本项目 `ai4se-photo-watermark` 是一个Python命令行工具，用于读取图片EXIF信息中的拍摄时间，并将其作为水印添加到图片上。项目已完成基础架构设计和项目初始化。

## 目录结构

```
src/photo_watermark/          # 主要代码包
├── __init__.py              # 包初始化，版本信息
├── __main__.py              # CLI入口点 (python -m photo_watermark)
├── cli.py                   # 命令行参数解析 (click)
├── core/                    # 核心功能模块
│   ├── exif_reader.py       # EXIF信息读取和日期提取
│   ├── image_processor.py   # 图像处理和水印叠加
│   └── watermark.py         # 水印配置和渲染逻辑
├── utils/                   # 工具函数
│   ├── file_utils.py        # 文件和目录操作
│   └── validators.py        # 输入验证
└── exceptions.py            # 自定义异常定义
tests/                       # 测试代码
└── fixtures/                # 测试用图片文件
```

## 核心功能架构

### 技术栈

- **图像处理**: Pillow (PIL) - EXIF读取和图像操作
- **命令行**: Click - 用户友好的CLI接口  
- **测试**: pytest + pytest-cov
- **代码质量**: black, flake8, mypy

### 关键组件

1. **ExifReader**: 提取图片拍摄时间，格式化为YYYY-MM-DD
2. **WatermarkRenderer**: 处理9种位置布局、字体大小/颜色配置
3. **ImageProcessor**: 图像加载、水印叠加、批量处理
4. **CLI**: 支持单文件/目录处理，输出到{原目录}_watermark子目录

## 开发工作流

### 环境设置

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 开发命令

```bash
# 运行工具
python -m photo_watermark /path/to/photos --font-size 24 --color white --position bottom-right

# 测试
pytest --cov=photo_watermark
pytest tests/test_exif_reader.py -v

# 代码质量
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 代码约定

### 错误处理策略

- 无EXIF信息: 记录警告并跳过文件
- 不支持格式: 提示并继续处理其他文件  
- 权限问题: 提供清晰错误信息和解决建议

### 水印位置常量

使用枚举定义9个预设位置: top-left, top-center, top-right, left-center, center, right-center, bottom-left, bottom-center, bottom-right

### 测试策略

- 使用`tests/fixtures/`存放测试图片
- 模拟不同EXIF格式和异常情况
- 集成测试验证端到端工作流

## 关键实现细节

### EXIF日期解析

```python
# 优先使用Pillow内置EXIF功能，fallback到exifread
from PIL.ExifTags import TAGS
exifdata = image.getexif()
# 查找DateTimeOriginal或DateTime标签
```

### 批量处理模式

- 创建`{原目录名}_watermark`子目录
- 保持原始文件名，显示处理进度
- 优雅处理内存使用（逐张处理，不并行加载）

### 命令行设计

- 位置参数: 输入路径
- 可选参数: --font-size, --color, --position
- 进度显示和错误汇总

## 开发重点

当前处于实现阶段，重点关注:

1. 确保EXIF解析的鲁棒性（不同相机品牌兼容性）
2. 水印渲染质量和性能优化
3. 用户体验（清晰的错误提示、进度显示）
4. 全面的测试覆盖（边界情况、异常处理）

参考`PRD.md`了解详细功能需求，`WORKPLAN.md`了解开发里程碑。
