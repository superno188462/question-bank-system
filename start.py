#!/usr/bin/env python3
"""
题库系统启动脚本
支持三个入口：web, mcp, wechat
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database.migrations import create_tables


def init_database():
    """初始化数据库"""
    print("🔧 初始化数据库...")
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 创建表
    create_tables()
    print("✅ 数据库初始化完成")
    return True


def start_web():
    """启动Web入口"""
    print("🌐 启动Web服务...")
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 启动Web服务器
    import uvicorn
    from web.config import settings
    
    print(f"📡 地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}{settings.DOCS_URL}")
    
    uvicorn.run(
        "web.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
    return True


def start_mcp():
    """启动MCP入口"""
    print("🤖 启动MCP服务...")
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 启动MCP服务器
    import uvicorn
    from mcp_server.config import settings
    
    print(f"📡 地址: http://{settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "mcp_server.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
    return True


def start_wechat():
    """启动微信小程序入口"""
    print("📱 启动微信小程序服务...")
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 启动微信小程序服务器
    import uvicorn
    from wechat.config import settings
    
    print(f"📡 地址: http://{settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "wechat.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
    return True


def show_status():
    """显示系统状态"""
    print("📊 系统状态检查...")
    
    # 检查数据库
    db_path = "data/question_bank.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ 数据库文件: {db_path} ({size/1024:.1f} KB)")
    else:
        print(f"❌ 数据库文件不存在: {db_path}")
    
    # 检查目录
    directories = [
        ("core/", "核心模块"),
        ("web/", "Web入口"),
        ("mcp_server/", "MCP入口"),
        ("wechat/", "微信入口"),
    ]
    
    for path, name in directories:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}目录不存在: {path}")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="题库管理系统启动脚本")
    parser.add_argument(
        "mode",
        nargs="?",
        default="status",
        choices=["web", "mcp", "wechat", "status"],
        help="运行模式: web(Web入口), mcp(MCP入口), wechat(微信入口), status(状态)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "web":
        start_web()
    elif args.mode == "mcp":
        start_mcp()
    elif args.mode == "wechat":
        start_wechat()
    elif args.mode == "status":
        show_status()
    else:
        print(f"未知模式: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()