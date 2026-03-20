"""
TagService 测试
测试标签管理服务的功能
"""
import pytest
import sys
import os
from unittest.mock import Mock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.models import Tag, TagCreate
from core.services.tag_service import TagService
from core.database.repositories import TagRepository


@pytest.fixture
def mock_repo():
    """创建模拟的 TagRepository"""
    return Mock(spec=TagRepository)


@pytest.fixture
def tag_service(mock_repo):
    """创建 TagService 实例"""
    return TagService(mock_repo)


class TestTagServiceCreate:
    """测试 TagService.create_tag 方法"""
    
    def test_create_tag_success(self, tag_service, mock_repo):
        """测试成功创建标签"""
        tag = Tag(
            id="tag-1",
            name="测试标签",
            color="#FF0000",
            created_at=datetime.now()
        )
        mock_repo.create.return_value = tag
        
        tag_data = TagCreate(name="测试标签", color="#FF0000")
        result = tag_service.create_tag(tag_data)
        
        assert result is not None
        assert result.id == "tag-1"
        assert result.name == "测试标签"
        assert result.color == "#FF0000"
        mock_repo.create.assert_called_with(tag_data)
    
    def test_create_tag_default_color(self, tag_service, mock_repo):
        """测试创建标签使用默认颜色"""
        tag = Tag(
            id="tag-1",
            name="简单标签",
            color="#CCCCCC",
            created_at=datetime.now()
        )
        mock_repo.create.return_value = tag
        
        tag_data = TagCreate(name="简单标签", color="#CCCCCC")
        result = tag_service.create_tag(tag_data)
        
        assert result is not None
        assert result.color == "#CCCCCC"
    
    def test_create_tag_multiple(self, tag_service, mock_repo):
        """测试创建多个标签"""
        tags = [
            Tag(id="tag-1", name="标签 1", color="#FF0000", created_at=datetime.now()),
            Tag(id="tag-2", name="标签 2", color="#00FF00", created_at=datetime.now()),
            Tag(id="tag-3", name="标签 3", color="#0000FF", created_at=datetime.now())
        ]
        
        for expected_tag in tags:
            mock_repo.create.return_value = expected_tag
            tag_data = TagCreate(name=expected_tag.name, color=expected_tag.color)
            result = tag_service.create_tag(tag_data)
            assert result.name == expected_tag.name


class TestTagServiceGet:
    """测试 TagService 获取标签方法"""
    
    def test_get_tag_success(self, tag_service, mock_repo):
        """测试成功获取标签"""
        tag = Tag(
            id="tag-1",
            name="测试标签",
            color="#FF0000",
            created_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = tag
        
        result = tag_service.get_tag("tag-1")
        
        assert result is not None
        assert result.id == "tag-1"
        assert result.name == "测试标签"
        mock_repo.get_by_id.assert_called_with("tag-1")
    
    def test_get_tag_not_found(self, tag_service, mock_repo):
        """测试获取不存在的标签"""
        mock_repo.get_by_id.return_value = None
        
        result = tag_service.get_tag("nonexistent-id")
        
        assert result is None
    
    def test_get_all_tags(self, tag_service, mock_repo):
        """测试获取所有标签"""
        tags = [
            Tag(id="tag-1", name="标签 1", color="#FF0000", created_at=datetime.now()),
            Tag(id="tag-2", name="标签 2", color="#00FF00", created_at=datetime.now()),
            Tag(id="tag-3", name="标签 3", color="#0000FF", created_at=datetime.now())
        ]
        mock_repo.get_all.return_value = tags
        
        result = tag_service.get_all_tags()
        
        assert isinstance(result, list)
        assert len(result) == 3
        mock_repo.get_all.assert_called_once()
    
    def test_get_all_tags_empty(self, tag_service, mock_repo):
        """测试获取空标签列表"""
        mock_repo.get_all.return_value = []
        
        result = tag_service.get_all_tags()
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestTagServiceDelete:
    """测试 TagService.delete_tag 方法"""
    
    def test_delete_tag_success(self, tag_service, mock_repo):
        """测试成功删除标签"""
        mock_repo.delete.return_value = True
        
        result = tag_service.delete_tag("tag-1")
        
        assert result is True
        mock_repo.delete.assert_called_with("tag-1")
    
    def test_delete_tag_not_found(self, tag_service, mock_repo):
        """测试删除不存在的标签"""
        mock_repo.delete.return_value = False
        
        result = tag_service.delete_tag("nonexistent-id")
        
        assert result is False
    
    def test_delete_tag_with_questions(self, tag_service, mock_repo):
        """测试删除有关联题目的标签（仓库层应处理关联）"""
        mock_repo.delete.return_value = True
        
        result = tag_service.delete_tag("tag-1")
        
        assert result is True
        # 仓库层应该处理 question_tags 的级联删除


class TestTagServiceSearch:
    """测试 TagService.search_tags 方法"""
    
    def test_search_tags_success(self, tag_service, mock_repo):
        """测试成功搜索标签"""
        tags = [
            Tag(id="tag-1", name="重要标签", color="#FF0000", created_at=datetime.now()),
            Tag(id="tag-2", name="次要标签", color="#00FF00", created_at=datetime.now())
        ]
        mock_repo.search.return_value = tags
        
        result = tag_service.search_tags("标签")
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repo.search.assert_called_with("标签")
    
    def test_search_tags_by_name(self, tag_service, mock_repo):
        """测试按名称搜索标签"""
        tags = [
            Tag(id="tag-1", name="数学标签", color="#FF0000", created_at=datetime.now())
        ]
        mock_repo.search.return_value = tags
        
        result = tag_service.search_tags("数学")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == "数学标签"
    
    def test_search_tags_no_results(self, tag_service, mock_repo):
        """测试搜索无结果"""
        mock_repo.search.return_value = []
        
        result = tag_service.search_tags("不存在的标签")
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_search_tags_partial_match(self, tag_service, mock_repo):
        """测试部分匹配搜索"""
        tags = [
            Tag(id="tag-1", name="Python 编程", color="#111111", created_at=datetime.now()),
            Tag(id="tag-2", name="Java 编程", color="#222222", created_at=datetime.now())
        ]
        mock_repo.search.return_value = tags
        
        result = tag_service.search_tags("编程")
        
        assert isinstance(result, list)
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
