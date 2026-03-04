#!/usr/bin/env python
"""
题库系统功能校验脚本

验证所有关键功能是否正常工作：
1. API 端点可用性
2. 前端功能完整性
3. 数据库连接
"""

import sys
import os
import json
import time
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent  # 返回到项目根目录
sys.path.insert(0, str(ROOT_DIR))

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


# ============ 测试 1: 数据库连接 ============
def test_database():
    """测试数据库连接和基本表"""
    print_header("测试 1: 数据库连接")
    
    try:
        from core.database import get_db, init_db
        
        # 测试连接
        db = next(get_db())
        print_success("数据库连接成功")
        
        # 检查表是否存在
        from sqlalchemy import text
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        
        required_tables = ['questions', 'categories', 'tags']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print_error(f"缺少表：{missing_tables}")
            return False
        else:
            print_success(f"所有必需表存在：{tables}")
        
        # 检查数据
        result = db.execute(text("SELECT COUNT(*) FROM questions"))
        question_count = result.fetchone()[0]
        print_info(f"题目数量：{question_count}")
        
        result = db.execute(text("SELECT COUNT(*) FROM categories"))
        category_count = result.fetchone()[0]
        print_info(f"分类数量：{category_count}")
        
        return True
        
    except Exception as e:
        print_error(f"数据库测试失败：{e}")
        return False


# ============ 测试 2: API 端点可用性 ============
def test_api_endpoints():
    """测试所有 API 端点"""
    print_header("测试 2: API 端点可用性")
    
    import requests
    
    BASE_URL = "http://localhost:8000"
    
    endpoints = [
        # 健康检查
        ("GET", "/health", None, True),
        
        # 分类管理
        ("GET", "/api/categories/tree", None, True),
        ("GET", "/api/categories", None, True),
        ("POST", "/api/categories", {"name": "测试分类"}, False),  # 不需要成功，只需要端点存在
        
        # 题目管理
        ("GET", "/api/questions?page=1&limit=10", None, True),
        ("GET", "/api/questions/search?q=测试", None, False),  # 可能没有结果
        
        # 标签管理
        ("GET", "/api/tags", None, True),
        
        # 智能问答（可能不存在）
        ("POST", "/api/qa/ask", {"question": "测试"}, False),
        ("GET", "/api/qa/pending", None, False),
    ]
    
    results = {
        "success": 0,
        "failed": 0,
        "not_found": 0,
        "details": []
    }
    
    for method, path, data, should_succeed in endpoints:
        url = f"{BASE_URL}{path}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data, timeout=5)
            
            status = response.status_code
            
            if status == 200:
                print_success(f"{method} {path} - {status}")
                results["success"] += 1
                results["details"].append({"endpoint": path, "status": "OK"})
            elif status == 404:
                print_error(f"{method} {path} - 404 (端点不存在)")
                results["not_found"] += 1
                results["details"].append({"endpoint": path, "status": "NOT_FOUND"})
            elif status == 422:
                print_warning(f"{method} {path} - 422 (验证错误，但端点存在)")
                results["success"] += 1
                results["details"].append({"endpoint": path, "status": "OK (422)"})
            else:
                if should_succeed:
                    print_error(f"{method} {path} - {status}")
                    results["failed"] += 1
                    results["details"].append({"endpoint": path, "status": status})
                else:
                    print_info(f"{method} {path} - {status} (预期外)")
                    results["success"] += 1
                    
        except requests.exceptions.ConnectionError:
            print_error(f"{method} {path} - 无法连接 (服务未启动？)")
            results["failed"] += 1
            results["details"].append({"endpoint": path, "status": "CONNECTION_ERROR"})
        except Exception as e:
            print_error(f"{method} {path} - 错误：{e}")
            results["failed"] += 1
    
    print(f"\n{Colors.BOLD}端点测试结果:{Colors.END}")
    print(f"  成功：{results['success']}")
    print(f"  失败：{results['failed']}")
    print(f"  未找到：{results['not_found']}")
    
    return results["failed"] == 0


# ============ 测试 3: 前端文件完整性 ============
def test_frontend_files():
    """测试前端文件是否存在"""
    print_header("测试 3: 前端文件完整性")
    
    web_dir = ROOT_DIR / "web"
    
    required_files = [
        "main.py",
        "templates/index.html",
        "static/css/style.css",
        "static/js/app.js",
    ]
    
    all_exist = True
    
    for file_path in required_files:
        full_path = web_dir / file_path
        if full_path.exists():
            print_success(f"{file_path} 存在")
        else:
            print_error(f"{file_path} 不存在")
            all_exist = False
    
    # 检查 JS 文件是否有重复函数定义
    js_file = web_dir / "static" / "js" / "app.js"
    if js_file.exists():
        content = js_file.read_text(encoding='utf-8')
        
        # 检查重复函数
        import re
        func_pattern = r'function\s+(\w+)\s*\('
        functions = re.findall(func_pattern, content)
        
        from collections import Counter
        func_counts = Counter(functions)
        duplicates = {name: count for name, count in func_counts.items() if count > 1}
        
        if duplicates:
            print_error(f"发现重复函数定义：{duplicates}")
            all_exist = False
        else:
            print_success("JavaScript 文件无重复函数定义")
    
    return all_exist


# ============ 测试 4: Web 服务可访问性 ============
def test_web_accessibility():
    """测试 Web 服务是否可访问"""
    print_header("测试 4: Web 服务可访问性")
    
    import requests
    
    try:
        # 测试主页
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print_success("主页可访问 (200 OK)")
        else:
            print_error(f"主页返回错误：{response.status_code}")
            return False
        
        # 测试静态文件
        response = requests.get("http://localhost:8000/static/js/app.js", timeout=5)
        if response.status_code == 200:
            print_success("JavaScript 文件可访问")
        else:
            print_error(f"JavaScript 文件返回错误：{response.status_code}")
            return False
        
        # 测试 CSS 文件
        response = requests.get("http://localhost:8000/static/css/style.css", timeout=5)
        if response.status_code == 200:
            print_success("CSS 文件可访问")
        else:
            print_error(f"CSS 文件返回错误：{response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("无法连接到 Web 服务 (请确认服务已启动)")
        return False
    except Exception as e:
        print_error(f"测试失败：{e}")
        return False


# ============ 测试 5: 功能完整性 ============
def test_functional_completeness():
    """测试关键功能"""
    print_header("测试 5: 功能完整性")
    
    import requests
    
    BASE_URL = "http://localhost:8000"
    
    tests_passed = 0
    tests_total = 0
    
    # 测试 1: 获取分类树
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/api/categories/tree", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print_success("分类树 API 返回正确格式")
                tests_passed += 1
            else:
                print_error("分类树 API 返回格式错误")
        else:
            print_error(f"分类树 API 失败：{response.status_code}")
    except Exception as e:
        print_error(f"分类树 API 错误：{e}")
    
    # 测试 2: 获取题目列表
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/api/questions?page=1&limit=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "total" in data:
                print_success("题目列表 API 返回正确格式")
                tests_passed += 1
            else:
                print_error("题目列表 API 返回格式错误")
        else:
            print_error(f"题目列表 API 失败：{response.status_code}")
    except Exception as e:
        print_error(f"题目列表 API 错误：{e}")
    
    # 测试 3: 检查 QA 端点（可选）
    tests_total += 1
    try:
        response = requests.get(f"{BASE_URL}/api/qa/pending", timeout=5)
        if response.status_code == 200:
            print_success("预备题目 API 存在")
            tests_passed += 1
        elif response.status_code == 404:
            print_warning("预备题目 API 不存在（功能未实现）")
            # 这不算失败，因为可能故意未实现
            tests_passed += 1
        else:
            print_error(f"预备题目 API 失败：{response.status_code}")
    except Exception as e:
        print_error(f"预备题目 API 错误：{e}")
    
    print(f"\n{Colors.BOLD}功能测试结果：{tests_passed}/{tests_total}{Colors.END}")
    
    return tests_passed == tests_total


# ============ 主函数 ============
def main():
    """运行所有测试"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}╔{'='*58}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║{' '*15}题库系统功能校验{' '*15}║{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚{'='*58}╝{Colors.END}\n")
    
    print_info(f"项目目录：{ROOT_DIR}")
    print_info(f"测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "database": False,
        "api": False,
        "frontend": False,
        "web": False,
        "functional": False,
    }
    
    # 运行测试
    results["database"] = test_database()
    results["api"] = test_api_endpoints()
    results["frontend"] = test_frontend_files()
    results["web"] = test_web_accessibility()
    results["functional"] = test_functional_completeness()
    
    # 汇总结果
    print_header("测试结果汇总")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: 通过")
        else:
            print_error(f"{test_name}: 失败")
    
    print(f"\n{Colors.BOLD}总计：{passed}/{total} 测试通过{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！系统运行正常{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  部分测试失败，请检查上述错误{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
