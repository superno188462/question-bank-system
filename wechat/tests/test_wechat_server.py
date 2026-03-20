"""
微信小程序服务器测试
测试 wechat/server.py 中的所有路由
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient


class TestWechatAppCreation:
    """微信小程序应用创建测试"""
    
    def test_create_wechat_app(self):
        """测试创建微信小程序应用"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        
        assert app is not None
        assert app.title == "题库管理系统 - 微信小程序入口"
        assert app.version == "1.0"
    
    def test_app_has_cors_middleware(self):
        """测试应用配置了 CORS 中间件"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        
        # 检查中间件是否存在
        middleware_types = [type(m).name for m in app.user_middleware]
        assert any('CORSMiddleware' in str(m) for m in middleware_types)


@patch('wechat.server.config')
class TestWechatRootEndpoint:
    """根端点测试"""
    
    def test_root_returns_service_info(self, mock_config):
        """测试根端点返回服务信息"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "status" in data
        assert data["status"] == "运行中"
    
    def test_root_returns_docs_url(self, mock_config):
        """测试根端点返回文档 URL"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/")
        
        data = response.json()
        assert data["docs"] == "/docs"


@patch('wechat.server.config')
class TestWechatHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check_returns_healthy(self, mock_config):
        """测试健康检查返回健康状态"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "wechat"
    
    def test_health_check_multiple_times(self, mock_config):
        """测试多次健康检查"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


@patch('wechat.server.config')
class TestWechatQuestionsEndpoint:
    """题目端点测试"""
    
    def test_get_questions_returns_success(self, mock_config):
        """测试获取题目返回成功"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/api/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "message" in data
    
    def test_get_questions_message_indicates_todo(self, mock_config):
        """测试获取题目消息提示待实现"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/api/questions")
        
        data = response.json()
        assert "待实现" in data["message"]
    
    def test_get_questions_with_params(self, mock_config):
        """测试带参数获取题目"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/api/questions?page=1&limit=10")
        
        assert response.status_code == 200


@patch('wechat.server.config')
class TestWechatCORS:
    """CORS 配置测试"""
    
    def test_cors_headers_present(self, mock_config):
        """测试 CORS 头存在"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/", headers={"Origin": "http://example.com"})
        
        # 检查 CORS 头
        assert "access-control-allow-origin" in response.headers
    
    def test_cors_allows_all_origins(self, mock_config):
        """测试 CORS 允许所有来源"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/", headers={"Origin": "http://any-origin.com"})
        
        # 应该允许任何来源
        assert response.headers.get("access-control-allow-origin") == "*"


@patch('wechat.server.config')
class TestWechatDocs:
    """文档端点测试"""
    
    def test_docs_endpoint_exists(self, mock_config):
        """测试文档端点存在"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/docs")
        
        # Swagger UI 应该返回 200
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_json_exists(self, mock_config):
        """测试 OpenAPI JSON 存在"""
        from wechat.server import create_wechat_app
        
        app = create_wechat_app()
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "题库管理系统 - 微信小程序入口"


@patch('wechat.server.config')
class TestWechatAppInstance:
    """应用实例测试"""
    
    def test_app_instance_exists(self, mock_config):
        """测试应用实例存在"""
        from wechat.server import app
        
        assert app is not None
    
    def test_app_instance_is_fastapi(self, mock_config):
        """测试应用实例是 FastAPI 类型"""
        from wechat.server import app
        from fastapi import FastAPI
        
        assert isinstance(app, FastAPI)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
