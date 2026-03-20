"""
标签仓库测试
测试 TagRepository 的所有方法
"""
import pytest
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database.repositories import TagRepository
from core.models import Tag, TagCreate
from core.database.connection import DatabaseConnection


@pytest.fixture
def db_connection():
    """数据库连接 fixture"""
    db = DatabaseConnection()
    yield db
    cleanup_test_tags(db)


@pytest.fixture
def tag_repo(db_connection):
    """标签仓库 fixture"""
    return TagRepository()


def cleanup_test_tags(db):
    """清理测试标签数据"""
    try:
        db.execute("DELETE FROM tags WHERE name LIKE '测试标签%' OR name LIKE 'Test Tag%'")
    except Exception:
        pass


class TestTagRepositoryCreate:
    """测试 TagRepository.create 方法"""
    
    def test_create_tag_minimal(self, tag_repo, db_connection):
        """测试创建最小化标签（只有名称）"""
        tag_data = TagCreate(
            name="测试标签 - 最小化",
            color="#000000"
        )
        
        result = tag_repo.create(tag_data)
        
        assert result is not None
        assert result.name == "测试标签 - 最小化"
        assert result.color == "#000000"
        assert result.id is not None
        assert isinstance(result.created_at, datetime)
    
    def test_create_tag_with_color(self, tag_repo, db_connection):
        """测试创建带颜色的标签"""
        tag_data = TagCreate(
            name="测试标签 - 颜色",
            color="#FF5733"
        )
        
        result = tag_repo.create(tag_data)
        
        assert result.color == "#FF5733"
    
    def test_create_multiple_tags(self, tag_repo, db_connection):
        """测试创建多个标签"""
        tags = []
        for i in range(5):
            tag_data = TagCreate(name=f"测试标签-{i}", color=f"#00000{i}")
            result = tag_repo.create(tag_data)
            tags.append(result)
        
        assert len(tags) == 5
        assert all(t.id is not None for t in tags)


class TestTagRepositoryGetById:
    """测试 TagRepository.get_by_id 方法"""
    
    def test_get_existing_tag(self, tag_repo, db_connection):
        """测试获取存在的标签"""
        tag_data = TagCreate(name="测试标签 - 获取", color="#123456")
        created = tag_repo.create(tag_data)
        
        result = tag_repo.get_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == "测试标签 - 获取"
        assert result.color == "#123456"
    
    def test_get_nonexistent_tag(self, tag_repo, db_connection):
        """测试获取不存在的标签"""
        result = tag_repo.get_by_id("nonexistent-tag-id")
        
        assert result is None
    
    def test_get_tag_with_invalid_id(self, tag_repo, db_connection):
        """测试使用无效 ID 获取标签"""
        result = tag_repo.get_by_id("")
        assert result is None


class TestTagRepositoryGetAll:
    """测试 TagRepository.get_all 方法"""
    
    def test_get_all_tags(self, tag_repo, db_connection):
        """测试获取所有标签"""
        tag_repo.create(TagCreate(name="测试标签-A", color="#AAAAAA"))
        tag_repo.create(TagCreate(name="测试标签-B", color="#BBBBBB"))
        tag_repo.create(TagCreate(name="测试标签-C", color="#CCCCCC"))
        
        result = tag_repo.get_all()
        
        assert isinstance(result, list)
        assert len(result) >= 3
    
    def test_get_all_returns_list(self, tag_repo, db_connection):
        """测试获取所有标签返回列表"""
        result = tag_repo.get_all()
        assert isinstance(result, list)


class TestTagRepositoryUpdate:
    """测试 TagRepository.update 方法"""
    
    def test_update_tag_name(self, tag_repo, db_connection):
        """测试更新标签名称"""
        tag = tag_repo.create(TagCreate(name="测试标签 - 原名", color="#000000"))
        
        update_data = TagCreate(name="测试标签 - 新名", color="#000000")
        result = tag_repo.update(tag.id, update_data)
        
        assert result is not None
        assert result.name == "测试标签 - 新名"
        assert result.color == "#000000"
    
    def test_update_tag_color(self, tag_repo, db_connection):
        """测试更新标签颜色"""
        tag = tag_repo.create(TagCreate(name="测试标签 - 颜色", color="#FFFFFF"))
        
        update_data = TagCreate(name="测试标签 - 颜色", color="#000000")
        result = tag_repo.update(tag.id, update_data)
        
        assert result.color == "#000000"
    
    def test_update_nonexistent_tag(self, tag_repo, db_connection):
        """测试更新不存在的标签"""
        update_data = TagCreate(name="新名称", color="#000000")
        result = tag_repo.update("nonexistent-id", update_data)
        
        assert result is None


class TestTagRepositoryDelete:
    """测试 TagRepository.delete 方法"""
    
    def test_delete_existing_tag(self, tag_repo, db_connection):
        """测试删除存在的标签"""
        tag = tag_repo.create(TagCreate(name="测试标签 - 删除", color="#FF0000"))
        
        result = tag_repo.delete(tag.id)
        
        assert result is True
        
        deleted = tag_repo.get_by_id(tag.id)
        assert deleted is None
    
    def test_delete_nonexistent_tag(self, tag_repo, db_connection):
        """测试删除不存在的标签"""
        result = tag_repo.delete("nonexistent-tag-id")
        
        assert result is False


class TestTagRepositorySearch:
    """测试 TagRepository.search 方法"""
    
    def test_search_by_name(self, tag_repo, db_connection):
        """测试按名称搜索标签"""
        tag_repo.create(TagCreate(name="重要标签", color="#FF0000"))
        tag_repo.create(TagCreate(name="普通标签", color="#00FF00"))
        tag_repo.create(TagCreate(name="次要标签", color="#0000FF"))
        
        result = tag_repo.search("重要")
        
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(tag.name == "重要标签" for tag in result)
    
    def test_search_no_results(self, tag_repo, db_connection):
        """测试搜索无结果"""
        result = tag_repo.search("不存在的标签 xyz")
        
        assert isinstance(result, list)
    
    def test_search_partial_match(self, tag_repo, db_connection):
        """测试部分匹配搜索"""
        tag_repo.create(TagCreate(name="数学标签", color="#111111"))
        tag_repo.create(TagCreate(name="物理标签", color="#222222"))
        
        result = tag_repo.search("学")
        
        assert len(result) >= 2  # 应该匹配"数学"和"物理"


class TestTagRepositoryGetByNames:
    """测试 TagRepository.get_by_names 方法"""
    
    def test_get_by_names(self, tag_repo, db_connection):
        """测试通过名称列表获取标签"""
        tag_repo.create(TagCreate(name="标签 A", color="#AAAAAA"))
        tag_repo.create(TagCreate(name="标签 B", color="#BBBBBB"))
        tag_repo.create(TagCreate(name="标签 C", color="#CCCCCC"))
        
        result = tag_repo.get_by_names(["标签 A", "标签 B"])
        
        assert isinstance(result, list)
        assert len(result) >= 2
        names = [t.name for t in result]
        assert "标签 A" in names
        assert "标签 B" in names
    
    def test_get_by_names_empty(self, tag_repo, db_connection):
        """测试通过空列表获取标签"""
        result = tag_repo.get_by_names([])
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_get_by_names_nonexistent(self, tag_repo, db_connection):
        """测试获取不存在的标签"""
        result = tag_repo.get_by_names(["不存在的标签"])
        
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
