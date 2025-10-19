#!/usr/bin/env python3
"""
生产环境启动脚本
使用生产环境配置和优化设置
"""
import os
import uvicorn
from dotenv import load_dotenv

# 加载生产环境配置
load_dotenv('.env.production')

if __name__ == "__main__":
    # 生产环境配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 多进程 workers
        log_level="info"
    )