"""
MCP 服务器测试
测试 mcp_server/server.py 中的所有路由
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient


class TestMCPAppCreation:
    """MCP 应用创建测试"""
    
    def test_app_exists(self):
        """测试应用存在"""
        from mcp_server.server import app
        
        assert app is not None
    
    def test_app_is_fastapi(self):
        """测试应用是 FastAPI 类型"""
        from mcp_server.server import app
        from fastapi import FastAPI
        
        assert isinstance(app, FastAPI)
    
    def test_app_title(self):
        """测试应用标题"""
        from mcp_server.server import app
        
        assert app.title == "题库系统 - MCP 入口"
    
    def test_app_version(self):
        """测试应用版本"""
        from mcp_server.server import app
        
        assert app.version == "2.0"
    
    def test_app_description(self):
        """测试应用描述"""
        from mcp_server.server import app
        
        assert "MCP 协议" in app.description
        assert "AI 助手" in app.description


@patch('mcp_server.server.config')
class TestMCPRootEndpoint:
    """根端点测试"""
    
    def test_root_returns_service_info(self, mock_config):
        """测试根端点返回服务信息"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "question-bank-mcp"
        assert data["version"] == "2.0"
        assert data["description"] == "题库系统 MCP 入口"
    
    def test_root_returns_docs_url(self, mock_config):
        """测试根端点返回文档 URL"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/")
        
        data = response.json()
        assert data["docs"] == "/docs"
    
    def test_root_returns_health_url(self, mock_config):
        """测试根端点返回健康检查 URL"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/")
        
        data = response.json()
        assert data["health"] == "/health"


@patch('mcp_server.server.config')
class TestMCPHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check_returns_healthy(self, mock_config):
        """测试健康检查返回健康状态"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp"
    
    def test_health_check_content_type(self, mock_config):
        """测试健康检查返回 JSON 格式"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert "application/json" in response.headers["content-type"]
    
    def test_health_check_multiple_requests(self, mock_config):
        """测试多次健康检查请求"""
        from mcp_server.server import app
        
        client = TestClient(app)
        
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


@patch('mcp_server.server.config')
class TestMCPDocs:
    """文档端点测试"""
    
    def test_docs_endpoint_exists(self, mock_config):
        """测试文档端点存在"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/docs")
        
        # Swagger UI 应该返回 200
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_json_exists(self, mock_config):
        """测试 OpenAPI JSON 存在"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "openapi" in data
        assert data["openapi"].startswith("3.")
    
    def test_openapi_info(self, mock_config):
        """测试 OpenAPI 信息"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/openapi.json")
        
        data = response.json()
        assert data["info"]["title"] == "题库系统 - MCP 入口"
        assert data["info"]["version"] == "2.0"


@patch('mcp_server.server.config')
class TestMCPConfig:
    """配置测试"""
    
    def test_config_used_for_port(self, mock_config):
        """测试配置用于端口设置"""
        mock_config.MCP_PORT = 8765
        
        from mcp_server.server import app
        
        # 应用应该能正常创建
        assert app is not None


@patch('mcp_server.server.config')
class TestMCPHTTPMethods:
    """HTTP 方法测试"""
    
    def test_root_supports_get(self, mock_config):
        """测试根端点支持 GET"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
    
    def test_health_supports_get(self, mock_config):
        """测试健康检查支持 GET"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
    
    def test_root_post_not_allowed(self, mock_config):
        """测试根端点不允许 POST"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.post("/")
        
        # 应该返回 405 Method Not Allowed
        assert response.status_code == 405


@patch('mcp_server.server.config')
class TestMCPResponseFormat:
    """响应格式测试"""
    
    def test_root_response_is_json(self, mock_config):
        """测试根端点响应是 JSON"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)
    
    def test_health_response_is_json(self, mock_config):
        """测试健康检查响应是 JSON"""
        from mcp_server.server import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
