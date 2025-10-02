@echo off
chcp 65001 >nul
title 图片水印工具

cd /d "%~dp0"

echo.
echo ===================================
echo     图片水印工具 - 启动中...
echo ===================================
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查依赖包
echo 正在检查依赖包...
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 启动应用程序
echo 正在启动应用程序...
python src/main.py

if %errorlevel% neq 0 (
    echo.
    echo 应用程序异常退出
    pause
)

echo.
echo 应用程序正常退出
timeout /t 2 >nul