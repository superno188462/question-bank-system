#!/usr/bin/env python3
"""
诊断脚本 - 检查为什么加载旧代码
"""
import sys
import os

print("=" * 60)
print("🔍 诊断信息")
print("=" * 60)

# 1. Python版本
print(f"\n1. Python版本: {sys.version}")
print(f"   可执行文件: {sys.executable}")

# 2. 当前工作目录
print(f"\n2. 当前工作目录: {os.getcwd()}")

# 3. Python路径
print(f"\n3. Python路径 (sys.path):")
for i, p in enumerate(sys.path):
    print(f"   [{i}] {p}")

# 4. 检查web.main模块位置
try:
    import web.main
    print(f"\n4. web.main 模块位置: {web.main.__file__}")
    
    # 读取并显示root函数的内容
    import inspect
    source = inspect.getsource(web.main.create_web_app)
    
    # 查找@app.get("/")部分
    lines = source.split('\n')
    for i, line in enumerate(lines):
        if '@app.get("/")' in line or 'response_class=HTMLResponse' in line:
            print(f"\n5. root路由定义 (第{i}行附近):")
            for j in range(max(0, i-1), min(len(lines), i+6)):
                marker = ">>> " if j == i else "    "
                print(f"{marker}{lines[j]}")
            break
    
except Exception as e:
    print(f"\n4. 导入web.main失败: {e}")

# 5. 检查模板文件是否存在
print(f"\n6. 检查模板文件:")
template_path = os.path.join(os.getcwd(), "web", "templates", "index.html")
if os.path.exists(template_path):
    print(f"   ✅ 模板文件存在: {template_path}")
else:
    print(f"   ❌ 模板文件不存在: {template_path}")

# 6. 检查静态文件
static_path = os.path.join(os.getcwd(), "web", "static", "css", "style.css")
if os.path.exists(static_path):
    print(f"   ✅ CSS文件存在: {static_path}")
else:
    print(f"   ❌ CSS文件不存在: {static_path}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
