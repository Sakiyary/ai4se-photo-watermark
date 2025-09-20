# 工作计划 - AI4SE Photo Watermark

## 项目架构设计

### 模块结构

```
src/
├── photo_watermark/
│   ├── __init__.py
│   ├── __main__.py          # CLI入口点
│   ├── cli.py               # 命令行参数解析
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exif_reader.py   # EXIF信息读取
│   │   ├── image_processor.py # 图像处理和水印添加
│   │   └── watermark.py     # 水印配置和渲染
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py    # 文件和目录操作
│   │   └── validators.py    # 输入验证
│   └── exceptions.py        # 自定义异常
tests/
├── __init__.py
├── test_exif_reader.py
├── test_image_processor.py
├── test_watermark.py
├── test_cli.py
└── fixtures/                # 测试用图片文件
```

### 核心组件设计

#### 1. EXIF Reader (exif_reader.py)

- **职责**：读取图片EXIF信息，提取拍摄时间
- **主要方法**：
  - `extract_date_taken(image_path)` → datetime对象
  - `format_date(datetime_obj)` → 字符串（YYYY-MM-DD）

#### 2. Watermark Engine (watermark.py)

- **职责**：水印样式配置和文本渲染
- **主要类**：
  - `WatermarkConfig`：水印配置类（位置、颜色、字体大小等）
  - `WatermarkRenderer`：水印渲染器

#### 3. Image Processor (image_processor.py)

- **职责**：图像加载、水印叠加、保存
- **主要方法**：
  - `load_image(path)` → PIL Image对象
  - `add_watermark(image, text, config)` → PIL Image对象
  - `save_image(image, output_path)`

#### 4. CLI Interface (cli.py)

- **职责**：命令行参数解析和用户交互
- **主要功能**：参数验证、帮助信息、进度显示

## 开发计划

### 第一阶段：核心功能开发 (3-4天)

#### Day 1: 项目初始化和EXIF读取

- [x] 创建项目目录结构
- [ ] 设置虚拟环境和依赖管理
- [ ] 实现EXIF读取功能
- [ ] 编写EXIF读取的单元测试

**具体任务**：

1. 创建 `src/photo_watermark/core/exif_reader.py`
2. 实现 `ExifReader` 类
3. 处理无EXIF信息的情况
4. 支持多种日期格式解析

#### Day 2: 水印引擎开发

- [ ] 实现水印配置类
- [ ] 实现水印渲染器
- [ ] 支持多种位置计算
- [ ] 编写水印功能测试

**具体任务**：

1. 创建 `WatermarkConfig` 数据类
2. 实现位置计算算法（9个预设位置）
3. 实现文本渲染和字体处理
4. 添加颜色格式支持

#### Day 3: 图像处理功能

- [ ] 实现图像加载和保存
- [ ] 集成水印叠加功能
- [ ] 处理不同图片格式
- [ ] 优化内存使用

#### Day 4: CLI接口开发

- [ ] 实现命令行参数解析
- [ ] 添加参数验证
- [ ] 实现批量处理逻辑
- [ ] 添加进度显示

### 第二阶段：测试和优化 (2天)

#### Day 5: 单元测试和集成测试

- [ ] 完善单元测试覆盖率
- [ ] 创建测试图片fixtures
- [ ] 端到端测试
- [ ] 性能测试

#### Day 6: 用户体验优化

- [ ] 错误处理和用户友好提示
- [ ] 帮助文档完善
- [ ] 命令行体验优化
- [ ] 代码重构和优化

### 第三阶段：打包和文档 (1天)

#### Day 7: 项目完善

- [ ] 创建 `setup.py` 和 `pyproject.toml`
- [ ] 更新 `README.md` 使用文档
- [ ] 创建使用示例
- [ ] 准备发布版本

## 技术实现要点

### 1. EXIF处理策略

```python
# 使用 Pillow 的内置 EXIF 功能
from PIL import Image
from PIL.ExifTags import TAGS

def extract_exif_date(image_path):
    try:
        image = Image.open(image_path)
        exifdata = image.getexif()
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTime":
                return exifdata[tag_id]
    except Exception as e:
        # 处理异常情况
        return None
```

### 2. 水印位置计算

```python
def calculate_position(image_size, text_size, position):
    img_w, img_h = image_size
    text_w, text_h = text_size
    
    positions = {
        'top-left': (10, 10),
        'top-center': (img_w//2 - text_w//2, 10),
        'top-right': (img_w - text_w - 10, 10),
        'center': (img_w//2 - text_w//2, img_h//2 - text_h//2),
        'bottom-right': (img_w - text_w - 10, img_h - text_h - 10),
        # ... 其他位置
    }
    return positions.get(position, positions['bottom-right'])
```

### 3. 批量处理流程

```python
def process_directory(input_dir, config):
    output_dir = Path(input_dir).parent / f"{Path(input_dir).name}_watermark"
    output_dir.mkdir(exist_ok=True)
    
    image_files = find_image_files(input_dir)
    
    for i, image_path in enumerate(image_files):
        try:
            process_single_image(image_path, output_dir, config)
            print(f"[{i+1}/{len(image_files)}] ✓ {image_path.name}")
        except Exception as e:
            print(f"[{i+1}/{len(image_files)}] ✗ {image_path.name}: {e}")
```

## 质量保证

### 测试策略

1. **单元测试**：每个模块独立测试，覆盖率 > 80%
2. **集成测试**：测试模块间协作
3. **功能测试**：端到端用户场景测试
4. **性能测试**：大图片和批量处理测试

### 代码质量

- 使用 `black` 进行代码格式化
- 使用 `flake8` 进行代码检查
- 使用 `mypy` 进行类型检查
- 遵循 PEP 8 编码规范

### 错误处理

- 文件不存在：清晰的错误提示
- 无EXIF信息：警告并跳过
- 权限问题：建议解决方案
- 内存不足：优化处理策略

## 风险管控

### 技术风险

1. **EXIF格式兼容性**：测试多种相机品牌的图片
2. **字体渲染问题**：提供系统字体fallback机制
3. **大文件处理**：实现内存优化策略

### 缓解措施

1. 建立全面的测试图片库
2. 实现渐进式错误处理
3. 提供详细的用户文档和FAQ

## 里程碑

- **M1** (Day 2): EXIF读取功能完成
- **M2** (Day 4): 核心水印功能完成
- **M3** (Day 6): CLI界面和批量处理完成
- **M4** (Day 7): 测试和文档完成，项目ready

## 成功标准

1. 能够正确处理主流相机拍摄的JPEG图片
2. 支持自定义水印样式和位置
3. 批量处理性能满足需求（<5秒/张）
4. 用户界面友好，错误提示清晰
5. 代码质量高，测试覆盖率达标
