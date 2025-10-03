# 应用打包说明

本文档说明如何将图片水印工具打包为可执行文件。

## 📦 打包方式

本项目使用 **PyInstaller** 进行应用打包,可以将Python应用打包成独立的可执行文件,无需用户安装Python环境。

## 🛠️ 打包步骤

### Windows 系统

1. **确保虚拟环境已激活**

   ```cmd
   venv\Scripts\activate
   ```

2. **运行打包脚本**

   ```cmd
   build.bat
   ```

   或者手动执行:

   ```cmd
   pip install pyinstaller
   pyinstaller --clean build.spec
   ```

3. **查找可执行文件**
   - 打包完成后,可执行文件位于 `dist\WatermarkTool.exe`
   - 可以直接双击运行,无需Python环境

### Linux / macOS 系统

1. **确保虚拟环境已激活**

   ```bash
   source venv/bin/activate
   ```

2. **添加执行权限并运行打包脚本**

   ```bash
   chmod +x build.sh
   ./build.sh
   ```

   或者手动执行:

   ```bash
   pip install pyinstaller
   pyinstaller --clean build.spec
   ```

3. **查找可执行文件**
   - 打包完成后,可执行文件位于 `dist/WatermarkTool`
   - 可以直接运行,无需Python环境

## 📋 打包配置说明

### build.spec 配置文件

```python
# 主要配置项
name='WatermarkTool'        # 可执行文件名称
console=False               # 不显示控制台窗口(GUI应用)
onefile=True               # 打包为单个文件
icon=None                  # 可添加应用图标
```

### 包含的依赖

打包会自动包含以下依赖:

- Tkinter (GUI框架)
- PIL/Pillow (图像处理)
- tkinterdnd2 (拖拽支持)
- 所有源代码模块

## 📂 输出文件结构

```
dist/
└── WatermarkTool.exe (或 WatermarkTool)  # 独立可执行文件 (~50-80MB)
```

## ⚠️ 注意事项

### 1. 配置文件位置

- 打包后的应用会在运行目录创建 `.watermark_config` 文件夹
- 配置和模板会保存在该文件夹中

### 2. 字体支持

- 应用会使用系统已安装的字体
- 确保目标系统安装了必要的字体

### 3. 文件大小

- 打包后的可执行文件约 50-80MB
- 包含了Python解释器和所有依赖库

### 4. 杀毒软件

- 某些杀毒软件可能会误报
- 可以添加白名单或使用代码签名

### 5. 跨平台

- Windows上打包的程序只能在Windows运行
- Linux/Mac需要在对应平台上重新打包

## 🚀 优化选项

### 减小文件大小

如果需要减小可执行文件大小,可以修改 `build.spec`:

```python
# 使用 UPX 压缩
upx=True
upx_exclude=[]

# 排除不需要的模块
excludes=['matplotlib', 'numpy', 'scipy']
```

### 添加应用图标

1. 准备 `.ico` 文件(Windows)或 `.icns` 文件(Mac)
2. 修改 `build.spec`:

   ```python
   icon='path/to/icon.ico'
   ```

### 包含额外资源文件

如果需要包含图标、图片等资源:

```python
datas=[
    ('resources/icons', 'icons'),
    ('resources/templates', 'templates'),
],
```

## 🐛 常见问题

### Q: 打包失败,提示找不到模块?

A: 确保在 `build.spec` 的 `hiddenimports` 中添加了所有使用的模块。

### Q: 打包后运行报错?

A:

1. 检查是否所有依赖都已正确包含
2. 查看是否有路径相关的硬编码
3. 确认配置文件路径处理正确

### Q: 文件太大?

A:

1. 使用 UPX 压缩
2. 排除不必要的依赖
3. 考虑使用 `--onedir` 模式代替 `--onefile`

### Q: 杀毒软件报毒?

A:

1. PyInstaller打包的程序可能被误报
2. 可以向杀毒软件厂商提交误报
3. 使用代码签名证书签名程序

## 📝 测试建议

打包完成后,建议进行以下测试:

1. **基本功能测试**
   - 启动应用
   - 导入图片
   - 添加水印
   - 导出图片

2. **配置测试**
   - 配置保存
   - 配置加载
   - 模板功能

3. **性能测试**
   - 大图片处理
   - 批量处理
   - 内存占用

4. **兼容性测试**
   - 不同Windows版本(如果是Windows)
   - 不同屏幕分辨率
   - 不同DPI设置

## 📦 分发建议

### Windows

1. **直接分发**
   - 将 `dist\WatermarkTool.exe` 压缩为 ZIP
   - 提供使用说明

2. **制作安装包**(可选)
   - 使用 NSIS 或 Inno Setup
   - 创建桌面快捷方式
   - 添加卸载程序

### Linux

1. 创建 AppImage 或 .deb 包
2. 提供安装脚本

### macOS

1. 创建 .app 包
2. 可选: 创建 .dmg 安装镜像

## 🔄 更新流程

当代码更新后:

1. 更新版本号(在 `constants.py`)
2. 重新运行打包脚本
3. 测试新版本
4. 分发更新

## 📚 相关资源

- [PyInstaller 官方文档](https://pyinstaller.readthedocs.io/)
- [UPX 压缩工具](https://upx.github.io/)
- [NSIS 安装包制作](https://nsis.sourceforge.io/)

---

**最后更新**: 2025年10月3日
