"""
Web Config 模块测试
测试 web/config.py 中的配置类
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestWebConfigInit:
    """测试 WebConfig 初始化"""
    
    @patch('web.config.shared_config')
    def test_init_with_shared_config(self, mock_shared):
        """测试使用共享配置初始化"""
        mock_shared.WEB_PORT = 8000
        mock_shared.DATABASE_URL = "sqlite:///test.db"
        mock_shared.DEBUG = True
        mock_shared.APP_NAME = "Test App"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.shared == mock_shared
        assert config.HOST == "0.0.0.0"
        assert config.PORT == 8000
        assert config.DOCS_URL == "/docs"
    
    @patch('web.config.shared_config')
    def test_init_default_host(self, mock_shared):
        """测试默认 HOST 配置"""
        mock_shared.WEB_PORT = 8000
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.HOST == "0.0.0.0"
    
    @patch('web.config.shared_config')
    def test_init_port_from_shared(self, mock_shared):
        """测试 PORT 从共享配置获取"""
        mock_shared.WEB_PORT = 9000
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.PORT == 9000
    
    @patch('web.config.shared_config')
    def test_init_docs_url(self, mock_shared):
        """测试 DOCS_URL 配置"""
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DOCS_URL == "/docs"


class TestWebConfigProperties:
    """测试 WebConfig 属性"""
    
    @patch('web.config.shared_config')
    def test_database_url_property(self, mock_shared):
        """测试 DATABASE_URL 属性"""
        mock_shared.DATABASE_URL = "sqlite:///custom.db"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DATABASE_URL == "sqlite:///custom.db"
    
    @patch('web.config.shared_config')
    def test_database_url_from_shared(self, mock_shared):
        """测试 DATABASE_URL 从共享配置获取"""
        mock_shared.DATABASE_URL = "postgresql://user:pass@localhost/db"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DATABASE_URL == "postgresql://user:pass@localhost/db"
    
    @patch('web.config.shared_config')
    def test_debug_property_true(self, mock_shared):
        """测试 DEBUG 属性为 True"""
        mock_shared.DEBUG = True
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DEBUG is True
    
    @patch('web.config.shared_config')
    def test_debug_property_false(self, mock_shared):
        """测试 DEBUG 属性为 False"""
        mock_shared.DEBUG = False
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DEBUG is False
    
    @patch('web.config.shared_config')
    def test_app_name_property(self, mock_shared):
        """测试 APP_NAME 属性"""
        mock_shared.APP_NAME = "题库系统"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.APP_NAME == "题库系统 (Web)"
    
    @patch('web.config.shared_config')
    def test_app_name_with_suffix(self, mock_shared):
        """测试 APP_NAME 包含 (Web) 后缀"""
        mock_shared.APP_NAME = "My App"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.APP_NAME.endswith(" (Web)")
        assert "My App" in config.APP_NAME


class TestWebConfigInstance:
    """测试 WebConfig 实例"""
    
    @patch('web.config.shared_config')
    def test_settings_instance_created(self, mock_shared):
        """测试 settings 实例被创建"""
        mock_shared.WEB_PORT = 8000
        mock_shared.DATABASE_URL = "sqlite:///test.db"
        mock_shared.DEBUG = False
        mock_shared.APP_NAME = "Test"
        
        # 重新导入以创建 settings 实例
        import importlib
        import web.config
        importlib.reload(web.config)
        
        from web.config import settings
        assert settings is not None
    
    @patch('web.config.shared_config')
    def test_settings_has_all_attributes(self, mock_shared):
        """测试 settings 拥有所有必要属性"""
        mock_shared.WEB_PORT = 8000
        mock_shared.DATABASE_URL = "sqlite:///test.db"
        mock_shared.DEBUG = True
        mock_shared.APP_NAME = "Test"
        
        import importlib
        import web.config
        importlib.reload(web.config)
        
        from web.config import settings
        
        assert hasattr(settings, 'HOST')
        assert hasattr(settings, 'PORT')
        assert hasattr(settings, 'DOCS_URL')
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'DEBUG')
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'shared')


class TestWebConfigInheritance:
    """测试 WebConfig 继承关系"""
    
    @patch('web.config.shared_config')
    def test_shared_config_reference(self, mock_shared):
        """测试共享配置引用"""
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.shared == mock_shared
    
    @patch('web.config.shared_config')
    def test_shared_config_properties_access(self, mock_shared):
        """测试通过 shared 访问属性"""
        mock_shared.CUSTOM_PROPERTY = "custom_value"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.shared.CUSTOM_PROPERTY == "custom_value"


class TestWebConfigWithDifferentPorts:
    """测试不同端口配置"""
    
    @patch('web.config.shared_config')
    def test_port_3000(self, mock_shared):
        """测试端口 3000"""
        mock_shared.WEB_PORT = 3000
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.PORT == 3000
    
    @patch('web.config.shared_config')
    def test_port_8080(self, mock_shared):
        """测试端口 8080"""
        mock_shared.WEB_PORT = 8080
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.PORT == 8080
    
    @patch('web.config.shared_config')
    def test_port_443(self, mock_shared):
        """测试端口 443"""
        mock_shared.WEB_PORT = 443
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.PORT == 443


class TestWebConfigDatabaseUrls:
    """测试不同数据库 URL"""
    
    @patch('web.config.shared_config')
    def test_sqlite_url(self, mock_shared):
        """测试 SQLite URL"""
        mock_shared.DATABASE_URL = "sqlite:///./data.db"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DATABASE_URL.startswith("sqlite://")
    
    @patch('web.config.shared_config')
    def test_postgresql_url(self, mock_shared):
        """测试 PostgreSQL URL"""
        mock_shared.DATABASE_URL = "postgresql://user:password@localhost:5432/mydb"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DATABASE_URL.startswith("postgresql://")
    
    @patch('web.config.shared_config')
    def test_mysql_url(self, mock_shared):
        """测试 MySQL URL"""
        mock_shared.DATABASE_URL = "mysql://user:password@localhost:3306/mydb"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DATABASE_URL.startswith("mysql://")


class TestWebConfigDebugModes:
    """测试不同调试模式"""
    
    @patch('web.config.shared_config')
    def test_debug_enabled(self, mock_shared):
        """测试调试模式启用"""
        mock_shared.DEBUG = True
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DEBUG is True
    
    @patch('web.config.shared_config')
    def test_debug_disabled(self, mock_shared):
        """测试调试模式禁用"""
        mock_shared.DEBUG = False
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.DEBUG is False


class TestWebConfigAppNames:
    """测试不同应用名称"""
    
    @patch('web.config.shared_config')
    def test_app_name_chinese(self, mock_shared):
        """测试中文应用名称"""
        mock_shared.APP_NAME = "题库管理系统"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.APP_NAME == "题库管理系统 (Web)"
    
    @patch('web.config.shared_config')
    def test_app_name_english(self, mock_shared):
        """测试英文应用名称"""
        mock_shared.APP_NAME = "Question Bank System"
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.APP_NAME == "Question Bank System (Web)"
    
    @patch('web.config.shared_config')
    def test_app_name_empty(self, mock_shared):
        """测试空应用名称"""
        mock_shared.APP_NAME = ""
        
        from web.config import WebConfig
        config = WebConfig()
        
        assert config.APP_NAME == " (Web)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
