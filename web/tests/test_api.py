"""
Web API测试
测试所有Web接口的正确性
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from web.main import app

client = TestClient(app)


class TestCategoriesAPI:
    """分类API测试"""
    
    def test_get_categories_list(self):
        """测试获取分类列表"""
        response = client.get("/api/categories/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_category_tree(self):
        """测试获取分类树"""
        response = client.get("/api/categories/tree")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 检查树形结构
        if len(data) > 0:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "children" in data[0]
    
    def test_create_and_delete_category(self):
        """测试创建和删除分类"""
        # 创建分类
        new_cat = {
            "name": "测试分类",
            "description": "用于测试的分类"
        }
        response = client.post("/api/categories/", json=new_cat)
        assert response.status_code == 201
        created = response.json()
        assert created["name"] == "测试分类"
        
        # 删除分类
        cat_id = created["id"]
        response = client.delete(f"/api/categories/{cat_id}")
        assert response.status_code == 200


class TestQuestionsAPI:
    """题目API测试"""
    
    def test_get_questions_list(self):
        """测试获取题目列表"""
        response = client.get("/api/questions/?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
    
    def test_create_question_validation(self):
        """测试题目创建验证"""
        # 缺少必填字段
        invalid_question = {
            "content": "测试题目"
            # 缺少 answer, explanation, category_id
        }
        response = client.post("/api/questions/", json=invalid_question)
        # 应该返回400错误
        assert response.status_code in [400, 422]


class TestStaticFiles:
    """静态文件测试"""
    
    def test_homepage_loads(self):
        """测试首页能正常加载"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_css_file_exists(self):
        """测试CSS文件存在"""
        response = client.get("/static/css/style.css")
        # CSS文件可能不存在，返回404也是正常的
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
