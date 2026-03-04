#!/usr/bin/env python3
"""
题库系统前端功能验证脚本
测试所有核心 API 端点和前端功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health():
    """测试健康检查"""
    print("🔍 测试 1: 健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("   ✅ 健康检查通过")
    return True

def test_categories():
    """测试分类管理"""
    print("🔍 测试 2: 分类管理...")
    
    # 获取分类树
    response = requests.get(f"{API_BASE}/categories/tree")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    print(f"   ✅ 分类树加载成功 ({len(categories)} 个分类)")
    
    # 创建测试分类
    test_category = {
        "name": "测试分类",
        "parent_id": None
    }
    response = requests.post(f"{API_BASE}/categories", json=test_category)
    assert response.status_code == 200
    category_id = response.json()["id"]
    print(f"   ✅ 创建测试分类成功 (ID: {category_id})")
    
    # 更新分类
    response = requests.put(f"{API_BASE}/categories/{category_id}", json={"name": "更新后的测试分类"})
    assert response.status_code == 200
    print("   ✅ 更新分类成功")
    
    # 删除分类
    response = requests.delete(f"{API_BASE}/categories/{category_id}")
    assert response.status_code == 200
    print("   ✅ 删除分类成功")
    
    return True

def test_questions():
    """测试题目管理"""
    print("🔍 测试 3: 题目管理...")
    
    # 获取分类 ID 用于创建题目
    response = requests.get(f"{API_BASE}/categories/tree")
    categories = response.json()
    category_id = categories[0]["id"]
    
    # 创建测试题目（选择题）
    test_question = {
        "content": "测试题目：Python 是什么类型的语言？",
        "options": ["编译型", "解释型", "汇编语言", "机器语言"],
        "answer": "解释型",
        "explanation": "Python 是一种解释型、面向对象的高级编程语言",
        "category_id": category_id
    }
    
    response = requests.post(f"{API_BASE}/questions/", json=test_question)
    assert response.status_code == 201
    question_id = response.json()["id"]
    print(f"   ✅ 创建选择题成功 (ID: {question_id})")
    
    # 创建测试题目（填空题）
    test_question_fill = {
        "content": "测试题目：1 + 1 = ?",
        "options": [],
        "answer": "2",
        "explanation": "基础数学运算",
        "category_id": category_id
    }
    
    response = requests.post(f"{API_BASE}/questions/", json=test_question_fill)
    assert response.status_code == 201
    question_id_fill = response.json()["id"]
    print(f"   ✅ 创建填空题成功 (ID: {question_id_fill})")
    
    # 获取题目列表
    response = requests.get(f"{API_BASE}/questions/?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    print(f"   ✅ 获取题目列表成功 (共 {data['total']} 道题)")
    
    # 获取单个题目
    response = requests.get(f"{API_BASE}/questions/{question_id}")
    assert response.status_code == 200
    question = response.json()
    assert question["content"] == test_question["content"]
    print("   ✅ 获取单个题目成功")
    
    # 更新题目
    update_data = {
        "explanation": "更新后的解析：Python 是一种解释型语言，代码在运行时逐行解释执行"
    }
    response = requests.put(f"{API_BASE}/questions/{question_id}", json=update_data)
    assert response.status_code == 200
    print("   ✅ 更新题目成功")
    
    # 搜索题目
    response = requests.get(f"{API_BASE}/questions/search/keyword?keyword=Python&page=1&limit=10")
    assert response.status_code == 200
    print("   ✅ 搜索题目成功")
    
    # 删除题目
    response = requests.delete(f"{API_BASE}/questions/{question_id}")
    assert response.status_code == 200
    print("   ✅ 删除题目成功")
    
    response = requests.delete(f"{API_BASE}/questions/{question_id_fill}")
    assert response.status_code == 200
    print("   ✅ 删除填空题成功")
    
    return True

def test_tags():
    """测试标签管理"""
    print("🔍 测试 4: 标签管理...")
    
    # 创建测试标签
    test_tag = {"name": "测试标签"}
    response = requests.post(f"{API_BASE}/tags/", json=test_tag)
    assert response.status_code == 200
    tag_id = response.json()["id"]
    print(f"   ✅ 创建标签成功 (ID: {tag_id})")
    
    # 获取标签列表
    response = requests.get(f"{API_BASE}/tags/")
    assert response.status_code == 200
    print("   ✅ 获取标签列表成功")
    
    # 删除标签
    response = requests.delete(f"{API_BASE}/tags/{tag_id}")
    assert response.status_code == 200
    print("   ✅ 删除标签成功")
    
    return True

def test_frontend_page():
    """测试前端页面"""
    print("🔍 测试 5: 前端页面...")
    
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    html = response.text
    
    # 检查关键元素
    assert "题库管理系统" in html
    assert "题目管理" in html
    assert "分类管理" in html
    assert "app.js" in html
    assert "style.css" in html
    print("   ✅ 前端页面加载成功")
    
    # 检查静态文件
    response = requests.get(f"{BASE_URL}/static/css/style.css")
    assert response.status_code == 200
    print("   ✅ CSS 样式文件加载成功")
    
    response = requests.get(f"{BASE_URL}/static/js/app.js")
    assert response.status_code == 200
    print("   ✅ JavaScript 文件加载成功")
    
    return True

def test_api_docs():
    """测试 API 文档"""
    print("🔍 测试 6: API 文档...")
    
    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200
    print("   ✅ Swagger API 文档可访问")
    
    response = requests.get(f"{BASE_URL}/openapi.json")
    assert response.status_code == 200
    print("   ✅ OpenAPI 规范可访问")
    
    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 题库系统前端功能验证")
    print("=" * 60)
    print()
    
    tests = [
        test_health,
        test_categories,
        test_questions,
        test_tags,
        test_frontend_page,
        test_api_docs,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"   ❌ 测试失败：{e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ 测试异常：{e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)
    
    if failed == 0:
        print("✅ 所有测试通过！前端功能正常。")
        return 0
    else:
        print("❌ 部分测试失败，请检查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
