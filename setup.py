#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai4se-photo-watermark",
    version="2.0.0",
    author="Sakiyary",
    author_email="sakiyary@outlook.com",
    description="跨平台桌面水印工具，支持图片批量添加文本和图片水印",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sakiyary/ai4se-photo-watermark",
    project_urls={
        "Bug Reports": "https://github.com/Sakiyary/ai4se-photo-watermark/issues",
        "Source": "https://github.com/Sakiyary/ai4se-photo-watermark",
        "Documentation": "https://github.com/Sakiyary/ai4se-photo-watermark/wiki",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: GTK",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "build": [
            "pyinstaller>=5.0",
            "cx-freeze>=6.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "watermark-tool=watermark_app.app:main",
        ],
        "gui_scripts": [
            "watermark-tool-gui=watermark_app.app:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
    keywords="watermark, image, photo, batch, gui, tkinter, pillow",
)