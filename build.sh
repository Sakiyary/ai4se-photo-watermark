#!/bin/bash

echo "========================================"
echo "图片水印工具 - 打包脚本 (Linux/Mac)"
echo "========================================"
echo ""

# 激活虚拟环境
echo "[1/4] 激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "错误: 无法激活虚拟环境"
    exit 1
fi

# 检查是否安装了 PyInstaller
echo ""
echo "[2/4] 检查 PyInstaller..."
python -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller 未安装，正在安装..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "错误: 无法安装 PyInstaller"
        exit 1
    fi
fi

# 清理旧的构建文件
echo ""
echo "[3/4] 清理旧的构建文件..."
rm -rf build dist

# 开始打包
echo ""
echo "[4/4] 开始打包应用程序..."
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

pyinstaller --clean build.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "打包成功!"
    echo "========================================"
    echo ""
    echo "可执行文件位置: dist/WatermarkTool"
    echo ""
    echo "您可以直接运行该文件，无需Python环境"
    echo ""
else
    echo ""
    echo "========================================"
    echo "打包失败!"
    echo "========================================"
    echo ""
    echo "请检查错误信息并重试"
    echo ""
fi
