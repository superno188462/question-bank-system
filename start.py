#!/usr/bin/env python3
"""
题库系统智能启动脚本

支持三个入口的启动和管理：
1. web - Web管理界面
2. mcp - MCP协议入口
3. wechat - 微信小程序入口
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database.migrations import migrate_database
from shared.config import config


def init_database():
    """初始化数据库"""
    print("🔧 初始化数据库...")
    
    # 确保必要的目录存在
    config.ensure_directories()
    
    # 执行数据库迁移
    if migrate_database():
        print("✅ 数据库初始化完成")
        return True
    else:
        print("❌ 数据库初始化失败")
        return False


def start_web():
    """启动Web入口"""
    print("🌐 启动Web入口...")
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 启动Web服务器
    import uvicorn
    from web.config import settings
    
    print(f"📡 Web地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}{settings.DOCS_URL}")
    print(f"🌐 前端界面: http://{settings.HOST}:{settings.PORT}/static/index.html")
    
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
    print("🤖 启动MCP入口...")
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 检查MCP模块是否存在
    try:
        import mcp
    except ImportError:
        print("❌ MCP模块未安装，请先安装: pip install mcp")
        return False
    
    # 启动MCP服务器
    print(f"📡 MCP地址: http://{config.MCP_HOST}:{config.MCP_PORT}")
    print("⚠️  MCP服务器功能待实现，目前返回提示信息")
    
    # 临时实现：启动一个简单的HTTP服务器
    import http.server
    import socketserver
    
    class MCPHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = f"""
            <html>
            <body>
                <h1>MCP入口</h1>
                <p>MCP服务器正在开发中...</p>
                <p>地址: {config.MCP_HOST}:{config.MCP_PORT}</p>
                <p>共享数据库: {config.DATABASE_URL}</p>
            </body>
            </html>
            """
            self.wfile.write(message.encode())
    
    with socketserver.TCPServer((config.MCP_HOST, config.MCP_PORT), MCPHandler) as httpd:
        print(f"🚀 MCP服务器已启动，按Ctrl+C停止")
        httpd.serve_forever()
    
    return True


def start_wechat():
    """启动微信小程序入口"""
    print("📱 启动微信小程序入口...")
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 检查微信配置
    if not config.WECHAT_APP_ID or not config.WECHAT_APP_SECRET:
        print("⚠️  微信小程序配置未设置，请设置环境变量:")
        print("   export WECHAT_APP_ID=your-app-id")
        print("   export WECHAT_APP_SECRET=your-app-secret")
        print("   或编辑 shared/config.py")
    
    # 启动微信小程序服务器
    print(f"📡 微信地址: http://{config.WECHAT_HOST}:{config.WECHAT_PORT}")
    print("⚠️  微信小程序服务器功能待实现，目前返回提示信息")
    
    # 临时实现：启动一个简单的HTTP服务器
    import http.server
    import socketserver
    
    class WeChatHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = f"""
            <html>
            <body>
                <h1>微信小程序入口</h1>
                <p>微信小程序服务器正在开发中...</p>
                <p>地址: {config.WECHAT_HOST}:{config.WECHAT_PORT}</p>
                <p>App ID: {config.WECHAT_APP_ID or '未设置'}</p>
                <p>共享数据库: {config.DATABASE_URL}</p>
            </body>
            </html>
            """
            self.wfile.write(message.encode())
    
    with socketserver.TCPServer((config.WECHAT_HOST, config.WECHAT_PORT), WeChatHandler) as httpd:
        print(f"🚀 微信小程序服务器已启动，按Ctrl+C停止")
        httpd.serve_forever()
    
    return True


def start_all():
    """启动所有入口（开发模式）"""
    print("🚀 启动所有入口...")
    print("")
    print("📡 启动三个服务进程...")
    print("   🌐 Web入口: http://localhost:8000")
    print("   🤖 MCP入口: http://localhost:8001")
    print("   📱 微信入口: http://localhost:8002")
    print("")
    print("🔧 推荐使用专门的启动脚本:")
    print("   ./scripts/start_all.sh    # 一键启动所有服务")
    print("   ./scripts/stop_all.sh     # 一键停止所有服务")
    print("")
    print("📝 或分别启动:")
    print("   python start.py web       # 启动Web")
    print("   python start.py mcp       # 启动MCP")
    print("   python start.py wechat    # 启动微信")
    print("")
    
    # 初始化数据库
    if not init_database():
        return False
    
    return True


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    # 运行数据库测试
    if migrate_database():
        print("✅ 数据库测试通过")
        
        # 运行其他测试
        print("📋 运行功能测试...")
        
        # 测试Web入口
        try:
            from web.main import create_web_app
            app = create_web_app()
            print("✅ Web应用创建成功")
        except Exception as e:
            print(f"❌ Web应用测试失败: {e}")
            return False
        
        # 测试核心模块
        try:
            from core.models import QuestionCreate
            question = QuestionCreate(
                content="测试题目",
                options=["A", "B", "C"],
                answer="A",
                explanation="测试解析"
            )
            print("✅ 核心模型测试通过")
        except Exception as e:
            print(f"❌ 核心模型测试失败: {e}")
            return False
        
        print("✅ 所有测试通过")
        return True
    else:
        print("❌ 数据库测试失败")
        return False


def show_status():
    """显示系统状态"""
    print("📊 系统状态检查...")
    
    # 检查数据库
    db_path = config.get_database_path()
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
        ("shared/", "共享模块"),
    ]
    
    for path, name in directories:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}目录不存在: {path}")
    
    # 显示配置
    print(f"\n⚙️  配置信息:")
    print(f"  数据库: {config.DATABASE_URL}")
    print(f"  Web端口: {config.WEB_PORT}")
    print(f"  MCP端口: {config.MCP_PORT}")
    print(f"  微信端口: {config.WECHAT_PORT}")
    print(f"  调试模式: {config.DEBUG}")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="题库管理系统 - 多入口启动")
    parser.add_argument(
        "mode",
        nargs="?",
        default="status",
        choices=["web", "mcp", "wechat", "all", "init", "test", "status"],
        help="运行模式: web(Web入口), mcp(MCP入口), wechat(微信入口), all(全部), init(初始化), test(测试), status(状态)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "web":
        start_web()
    elif args.mode == "mcp":
        start_mcp()
    elif args.mode == "wechat":
        start_wechat()
    elif args.mode == "all":
        start_all()
    elif args.mode == "init":
        init_database()
    elif args.mode == "test":
        run_tests()
    elif args.mode == "status":
        show_status()
    else:
        print(f"未知模式: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()