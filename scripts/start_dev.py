#!/usr/bin/env python3
"""
开发环境启动脚本
自动加载 .env 文件并使用开发配置
"""
import os
import uvicorn
from dotenv import load_dotenv

# 加载开发环境配置
load_dotenv('.env')

if __name__ == "__main__":
    # 开发环境配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发时自动重载
        reload_dirs=["app"],  # 监控app目录变化
        log_level="debug"
    )