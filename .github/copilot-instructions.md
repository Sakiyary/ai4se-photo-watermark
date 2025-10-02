# Copilot Instructions for ai4se-photo-watermark

## 项目概览

本项目 `ai4se-photo-watermark` 是一个跨平台的桌面水印工具，使用 Python + Tkinter 开发，提供图形化界面，支持为图片批量添加文本和图片水印。项目已从命令行工具重构为 GUI 应用程序。

## 目录结构

```
src/                         # 源代码目录
├── main.py                  # 应用程序入口
├── watermark_app/           # 主应用包
│   ├── __init__.py
│   ├── app.py               # 应用程序主类
│   ├── gui/                 # GUI组件
│   │   ├── main_window.py   # 主窗口
│   │   ├── widgets/         # 自定义组件
│   │   │   ├── file_list.py       # 文件列表组件
│   │   │   ├── preview_panel.py   # 预览面板
│   │   │   ├── watermark_panel.py # 水印设置面板
│   │   │   └── export_dialog.py   # 导出对话框
│   │   └── dialogs/         # 对话框
│   ├── core/                # 核心功能模块
│   │   ├── image_processor.py     # 图像处理
│   │   ├── watermark.py           # 水印处理
│   │   ├── file_manager.py        # 文件管理
│   │   └── exporter.py            # 导出处理
│   ├── config/              # 配置管理
│   │   ├── settings.py            # 应用设置
│   │   ├── templates.py           # 模板管理
│   │   └── defaults.py            # 默认配置
│   └── utils/               # 工具函数
│       ├── validators.py          # 输入验证
│       ├── helpers.py             # 辅助函数
│       └── constants.py           # 常量定义
tests/                       # 测试代码
build/                       # 构建脚本和打包输出
assets/                      # 资源文件（图标、字体等）
```

## 核心功能架构

### 技术栈

- **GUI框架**: Tkinter (Python内置，轻量级跨平台)
- **图像处理**: Pillow (PIL) - 图像操作和水印叠加
- **打包工具**: PyInstaller - 生成各平台可执行文件
- **测试**: pytest + pytest-cov
- **代码质量**: black, flake8, mypy

### 关键组件

1. **MainWindow**: 主窗口界面，包含文件列表、预览区域、水印设置
2. **ImageProcessor**: 图像处理核心，水印叠加和格式转换
3. **WatermarkRenderer**: 文本和图片水印渲染，支持位置、样式设置
4. **FileManager**: 文件导入、管理和批量导出
5. **TemplateManager**: 水印模板的保存和加载
6. **PreviewWidget**: 实时预览组件，显示水印效果

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
# 运行应用
python src/main.py

# 测试
pytest --cov=watermark_app
pytest tests/test_core/ -v

# 代码质量
black src/ tests/
flake8 src/ tests/
mypy src/

# 打包应用
pyinstaller build/build_windows.py  # Windows
pyinstaller build/build_macos.py    # macOS
pyinstaller build/build_linux.py    # Linux
```

## 代码约定

### 错误处理策略

- 图像加载失败: 显示友好错误信息，跳过该文件
- 不支持格式: 提示用户选择支持的格式
- 导出失败: 提供重试机制和详细错误说明
- 内存不足: 自动压缩图片或建议用户减少批量数量

### 水印位置常量

使用枚举定义9个预设位置: top-left, top-center, top-right, left-center, center, right-center, bottom-left, bottom-center, bottom-right

### 测试策略

- 使用`tests/fixtures/`存放测试图片
- GUI组件单元测试和集成测试
- 跨平台兼容性测试

## 关键实现细节

### GUI架构设计

```python
# 主窗口布局：左侧文件列表，右侧预览+设置
class MainWindow(tk.Tk):
    def __init__(self):
        # 初始化界面组件
        self.setup_ui()
        self.setup_bindings()
```

### 实时预览更新

- 监听所有水印参数变化事件
- 异步更新预览，避免阻塞UI
- 缓存渲染结果，优化性能

### 批量处理机制

- 多线程处理，主线程负责UI响应
- 进度条实时更新，支持取消操作
- 错误收集和汇总报告

## 开发重点

当前处于重新开发阶段，重点关注:

1. GUI界面的直观性和易用性设计
2. 实时预览的性能优化和响应速度
3. 批量处理的稳定性和错误处理
4. 跨平台兼容性（Windows、macOS、Linux）
5. 打包和分发的自动化流程

参考`PRD.md`了解详细功能需求，`WORKPLAN.md`了解开发里程碑。
