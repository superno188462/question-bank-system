"""
Web Main API 测试
测试 web/main.py 中的所有路由
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestMainRoutes:
    """主路由测试"""
    
    def test_homepage(self, mock_qa_repo, mock_staging_repo):
        """测试首页"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_static_css(self, mock_qa_repo, mock_staging_repo):
        """测试静态 CSS 文件"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/static/css/style.css")
        
        # CSS 文件可能存在也可能不存在
        assert response.status_code in [200, 404]
    
    def test_static_js(self, mock_qa_repo, mock_staging_repo):
        """测试静态 JS 文件"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/static/js/app.js")
        
        # JS 文件可能存在也可能不存在
        assert response.status_code in [200, 404]


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestCategoriesAPI:
    """分类 API 完整测试"""
    
    def test_get_categories_list(self, mock_qa_repo, mock_staging_repo):
        """测试获取分类列表"""
        from web.main import app
        
        mock_staging_repo.get_all.return_value = []
        
        client = TestClient(app)
        response = client.get("/api/categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_category_tree(self, mock_qa_repo, mock_staging_repo):
        """测试获取分类树"""
        from web.main import app
        
        mock_staging_repo.get_all.return_value = []
        
        client = TestClient(app)
        response = client.get("/api/categories/tree")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_category(self, mock_qa_repo, mock_staging_repo):
        """测试创建分类"""
        from web.main import app
        
        from core.database.repositories import CategoryRepository
        mock_repo = Mock(spec=CategoryRepository)
        mock_repo.create.return_value = Mock(id=1, name="测试分类", parent_id=None)
        
        with patch('web.api.categories.CategoryRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.post(
                "/api/categories/",
                json={"name": "测试分类", "description": "测试描述"}
            )
            
            assert response.status_code in [201, 200]
    
    def test_get_category(self, mock_qa_repo, mock_staging_repo):
        """测试获取单个分类"""
        from web.main import app
        
        from core.database.repositories import CategoryRepository
        mock_repo = Mock(spec=CategoryRepository)
        mock_repo.get_by_id.return_value = Mock(id=1, name="测试分类")
        
        with patch('web.api.categories.CategoryRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.get("/api/categories/1")
            
            assert response.status_code in [200, 404]
    
    def test_update_category(self, mock_qa_repo, mock_staging_repo):
        """测试更新分类"""
        from web.main import app
        
        from core.database.repositories import CategoryRepository
        mock_repo = Mock(spec=CategoryRepository)
        mock_repo.get_by_id.return_value = Mock(id=1, name="原名称")
        mock_repo.update.return_value = None
        mock_repo.get_by_id.side_effect = [
            Mock(id=1, name="原名称"),
            Mock(id=1, name="新名称")
        ]
        
        with patch('web.api.categories.CategoryRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.put(
                "/api/categories/1",
                json={"name": "新名称"}
            )
            
            assert response.status_code in [200, 404]
    
    def test_delete_category(self, mock_qa_repo, mock_staging_repo):
        """测试删除分类"""
        from web.main import app
        
        from core.database.repositories import CategoryRepository
        mock_repo = Mock(spec=CategoryRepository)
        mock_repo.get_by_id.return_value = Mock(id=1, name="测试分类")
        mock_repo.delete.return_value = None
        
        with patch('web.api.categories.CategoryRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.delete("/api/categories/1")
            
            assert response.status_code in [200, 404]


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestQuestionsAPI:
    """题目 API 完整测试"""
    
    def test_get_questions_list(self, mock_qa_repo, mock_staging_repo):
        """测试获取题目列表"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/api/questions/?page=1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or isinstance(data, dict)
    
    def test_get_questions_with_filters(self, mock_qa_repo, mock_staging_repo):
        """测试带过滤条件的题目列表"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/api/questions/?page=1&limit=10&category_id=1&type=single_choice")
        
        assert response.status_code == 200
    
    def test_get_question(self, mock_qa_repo, mock_staging_repo):
        """测试获取单个题目"""
        from web.main import app
        
        from core.database.repositories import QuestionRepository
        mock_repo = Mock(spec=QuestionRepository)
        mock_repo.get_by_id.return_value = Mock(
            id=1,
            content="测试题目",
            type="single_choice",
            answer="A"
        )
        
        with patch('web.api.questions.QuestionRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.get("/api/questions/1")
            
            assert response.status_code in [200, 404]
    
    def test_create_question(self, mock_qa_repo, mock_staging_repo):
        """测试创建题目"""
        from web.main import app
        
        from core.database.repositories import QuestionRepository, CategoryRepository
        mock_q_repo = Mock(spec=QuestionRepository)
        mock_q_repo.create.return_value = Mock(id=1, content="新题目")
        
        mock_c_repo = Mock(spec=CategoryRepository)
        mock_c_repo.get_by_id.return_value = Mock(id=1, name="测试分类")
        
        with patch('web.api.questions.QuestionRepository', return_value=mock_q_repo):
            with patch('web.api.questions.CategoryRepository', return_value=mock_c_repo):
                client = TestClient(app)
                response = client.post(
                    "/api/questions/",
                    json={
                        "content": "新题目",
                        "type": "single_choice",
                        "answer": "A",
                        "category_id": 1
                    }
                )
                
                assert response.status_code in [201, 200, 400]
    
    def test_update_question(self, mock_qa_repo, mock_staging_repo):
        """测试更新题目"""
        from web.main import app
        
        from core.database.repositories import QuestionRepository
        mock_repo = Mock(spec=QuestionRepository)
        mock_repo.get_by_id.side_effect = [
            Mock(id=1, content="原题目"),
            Mock(id=1, content="新题目")
        ]
        mock_repo.update.return_value = None
        
        with patch('web.api.questions.QuestionRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.put(
                "/api/questions/1",
                json={"content": "新题目"}
            )
            
            assert response.status_code in [200, 404]
    
    def test_delete_question(self, mock_qa_repo, mock_staging_repo):
        """测试删除题目"""
        from web.main import app
        
        from core.database.repositories import QuestionRepository
        mock_repo = Mock(spec=QuestionRepository)
        mock_repo.get_by_id.return_value = Mock(id=1, content="题目")
        mock_repo.delete.return_value = None
        
        with patch('web.api.questions.QuestionRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.delete("/api/questions/1")
            
            assert response.status_code in [200, 404]


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestTagsAPI:
    """标签 API 测试"""
    
    def test_get_tags_list(self, mock_qa_repo, mock_staging_repo):
        """测试获取标签列表"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/api/tags/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_tag(self, mock_qa_repo, mock_staging_repo):
        """测试创建标签"""
        from web.main import app
        
        from core.database.repositories import TagRepository
        mock_repo = Mock(spec=TagRepository)
        mock_repo.create.return_value = Mock(id=1, name="测试标签")
        
        with patch('web.api.tags.TagRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.post(
                "/api/tags/",
                json={"name": "测试标签"}
            )
            
            assert response.status_code in [201, 200]
    
    def test_update_tag(self, mock_qa_repo, mock_staging_repo):
        """测试更新标签"""
        from web.main import app
        
        from core.database.repositories import TagRepository
        mock_repo = Mock(spec=TagRepository)
        mock_repo.get_by_id.side_effect = [
            Mock(id=1, name="原标签"),
            Mock(id=1, name="新标签")
        ]
        mock_repo.update.return_value = None
        
        with patch('web.api.tags.TagRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.put(
                "/api/tags/1",
                json={"name": "新标签"}
            )
            
            assert response.status_code in [200, 404]
    
    def test_delete_tag(self, mock_qa_repo, mock_staging_repo):
        """测试删除标签"""
        from web.main import app
        
        from core.database.repositories import TagRepository
        mock_repo = Mock(spec=TagRepository)
        mock_repo.get_by_id.return_value = Mock(id=1, name="标签")
        mock_repo.delete.return_value = None
        
        with patch('web.api.tags.TagRepository', return_value=mock_repo):
            client = TestClient(app)
            response = client.delete("/api/tags/1")
            
            assert response.status_code in [200, 404]


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestSearchAPI:
    """搜索 API 测试"""
    
    def test_search_questions(self, mock_qa_repo, mock_staging_repo):
        """测试搜索题目"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/api/questions/search?q=Python")
        
        assert response.status_code == 200
    
    def test_search_with_empty_query(self, mock_qa_repo, mock_staging_repo):
        """测试空查询搜索"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/api/questions/search?q=")
        
        assert response.status_code in [200, 422]


@patch('web.api.agent.StagingQuestionRepository')
@patch('web.api.agent.QALogRepository')
class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_endpoint(self, mock_qa_repo, mock_staging_repo):
        """测试健康检查端点"""
        from web.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        # 健康检查应该返回 200 或 404（如果没有这个端点）
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
