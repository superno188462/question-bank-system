#!/usr/bin/env python3
"""
一键启动所有前端服务
"""

import os
import sys
import subprocess
import time
import signal

def start_services():
    """启动所有服务"""
    print("🚀 题库系统 - 一键启动所有前端服务")
    print("=" * 50)
    
    # 检查是否在项目根目录
    if not os.path.exists("start.py"):
        print("❌ 请在项目根目录运行")
        return False
    
    # 初始化数据库
    print("🔧 初始化数据库...")
    init_result = subprocess.run([sys.executable, "start.py", "init"], 
                                capture_output=True, text=True)
    if init_result.returncode != 0:
        print("❌ 数据库初始化失败")
        print(init_result.stderr)
        return False
    
    print("✅ 数据库初始化完成")
    print("")
    
    # 服务配置
    services = [
        {
            "name": "Web入口",
            "cmd": [sys.executable, "start.py", "web"],
            "port": 8000,
            "url": "http://localhost:8000",
            "description": "管理界面和API文档"
        },
        {
            "name": "MCP入口", 
            "cmd": [sys.executable, "start.py", "mcp"],
            "port": 8001,
            "url": "http://localhost:8001",
            "description": "AI助手接口"
        },
        {
            "name": "微信入口",
            "cmd": [sys.executable, "start.py", "wechat"],
            "port": 8002,
            "url": "http://localhost:8002",
            "description": "微信小程序API"
        }
    ]
    
    processes = []
    
    print("📡 启动三个服务进程...")
    print("")
    
    for service in services:
        print(f"🚀 启动{service['name']}...")
        print(f"   地址: {service['url']}")
        print(f"   端口: {service['port']}")
        print(f"   描述: {service['description']}")
        
        # 启动服务
        process = subprocess.Popen(
            service["cmd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        processes.append((service["name"], process))
        
        print(f"   PID: {process.pid}")
        print("")
        time.sleep(3)  # 等待服务启动
    
    print("✅ 所有服务已启动！")
    print("")
    print("📊 服务状态:")
    for service in services:
        print(f"   🔗 {service['name']}: {service['url']}")
    print("")
    print("📝 查看服务输出:")
    print("   每个服务会在终端输出日志")
    print("")
    print("🛑 停止服务:")
    print("   按 Ctrl+C 停止所有服务")
    print("")
    print("=" * 50)
    
    # 等待用户中断
    try:
        # 简单显示服务状态
        for i in range(60):
            status = "运行中" + "." * (i % 4)
            print(f"📡 服务{status} (已运行{i+1}秒，按Ctrl+C停止)", end='\r')
            time.sleep(1)
        print("")
        print("⏰ 运行时间结束，停止所有服务...")
    except KeyboardInterrupt:
        print("")
        print("🛑 收到停止信号，正在停止所有服务...")
    
    # 停止所有进程
    print("")
    for name, process in processes:
        if process.poll() is None:  # 进程还在运行
            print(f"🛑 停止{name} (PID: {process.pid})...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print(f"✅ {name}已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {name}未响应，强制停止...")
                process.kill()
                process.wait()
                print(f"✅ {name}已强制停止")
    
    print("")
    print("✅ 所有服务已停止")
    return True


if __name__ == "__main__":
    try:
        start_services()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)