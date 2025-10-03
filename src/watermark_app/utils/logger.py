#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
"""

import logging
import os
from pathlib import Path
import sys
from datetime import datetime

def setup_logger(name: str = None, log_level: str = 'INFO', 
                log_file: str = None, console_output: bool = True) -> logging.Logger:
    """
    设置并配置日志记录器
    
    Args:
        name: 日志记录器名称，None使用根日志记录器
        log_level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: 日志文件路径，None不写入文件
        console_output: 是否输出到控制台
        
    Returns:
        配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 清除现有的处理器，避免重复设置
    logger.handlers.clear()
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"创建日志文件处理器失败: {e}")
    
    # 默认创建日志文件
    if log_file is None:
        try:
            # 在用户目录创建日志文件
            log_dir = Path.home() / '.watermark_app' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用日期命名日志文件
            today = datetime.now().strftime('%Y-%m-%d')
            default_log_file = log_dir / f'watermark_app_{today}.log'
            
            file_handler = logging.FileHandler(default_log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"创建默认日志文件失败: {e}")
    
    return logger