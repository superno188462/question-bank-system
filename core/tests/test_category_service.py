"""
CategoryService 测试
测试分类管理服务的功能
"""
import pytest
import sys
import os
from unittest.mock import Mock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.models import Category, CategoryCreate, CategoryUpdate
from core.services.category_service import CategoryService
from core.database.repositories import CategoryRepository


@pytest.fixture
def mock_repo():
    """创建模拟的 CategoryRepository"""
    return Mock(spec=CategoryRepository)


@pytest.fixture
def category_service(mock_repo):
    """创建 CategoryService 实例"""
    return CategoryService(mock_repo)


class TestCategoryServiceCreate:
    """测试 CategoryService.create_category 方法"""
    
    def test_create_category_success(self, category_service, mock_repo):
        """测试成功创建分类"""
        category = Category(
            id="cat-1",
            name="测试分类",
            description="测试描述",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.create.return_value = category
        
        category_data = CategoryCreate(name="测试分类", description="测试描述")
        result = category_service.create_category(category_data)
        
        assert result is not None
        assert result.id == "cat-1"
        assert result.name == "测试分类"
        mock_repo.create.assert_called_with(category_data)
    
    def test_create_category_with_parent(self, category_service, mock_repo):
        """测试创建带父分类的子分类"""
        category = Category(
            id="cat-2",
            name="子分类",
            description="子分类描述",
            parent_id="cat-1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.create.return_value = category
        
        category_data = CategoryCreate(name="子分类", description="子分类描述", parent_id="cat-1")
        result = category_service.create_category(category_data)
        
        assert result is not None
        assert result.parent_id == "cat-1"
    
    def test_create_category_minimal(self, category_service, mock_repo):
        """测试创建最小化分类（仅名称）"""
        category = Category(
            id="cat-1",
            name="简单分类",
            description="",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.create.return_value = category
        
        category_data = CategoryCreate(name="简单分类")
        result = category_service.create_category(category_data)
        
        assert result is not None
        assert result.name == "简单分类"


class TestCategoryServiceGet:
    """测试 CategoryService 获取分类方法"""
    
    def test_get_category_success(self, category_service, mock_repo):
        """测试成功获取分类"""
        category = Category(
            id="cat-1",
            name="测试分类",
            description="测试描述",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = category
        
        result = category_service.get_category("cat-1")
        
        assert result is not None
        assert result.id == "cat-1"
        mock_repo.get_by_id.assert_called_with("cat-1")
    
    def test_get_category_not_found(self, category_service, mock_repo):
        """测试获取不存在的分类"""
        mock_repo.get_by_id.return_value = None
        
        result = category_service.get_category("nonexistent-id")
        
        assert result is None
    
    def test_get_all_categories(self, category_service, mock_repo):
        """测试获取所有分类"""
        categories = [
            Category(id="cat-1", name="分类 1", description="描述 1", parent_id=None, created_at=datetime.now(), updated_at=datetime.now()),
            Category(id="cat-2", name="分类 2", description="描述 2", parent_id=None, created_at=datetime.now(), updated_at=datetime.now())
        ]
        mock_repo.get_all.return_value = categories
        
        result = category_service.get_all_categories()
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repo.get_all.assert_called_once()
    
    def test_get_all_categories_empty(self, category_service, mock_repo):
        """测试获取空分类列表"""
        mock_repo.get_all.return_value = []
        
        result = category_service.get_all_categories()
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestCategoryServiceUpdate:
    """测试 CategoryService.update_category 方法"""
    
    def test_update_category_success(self, category_service, mock_repo):
        """测试成功更新分类"""
        old_category = Category(
            id="cat-1",
            name="原名称",
            description="原描述",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        updated_category = Category(
            id="cat-1",
            name="新名称",
            description="新描述",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.update.return_value = updated_category
        
        update_data = CategoryUpdate(name="新名称", description="新描述")
        result = category_service.update_category("cat-1", update_data)
        
        assert result is not None
        assert result.name == "新名称"
        mock_repo.update.assert_called_with("cat-1", update_data)
    
    def test_update_category_not_found(self, category_service, mock_repo):
        """测试更新不存在的分类"""
        mock_repo.update.return_value = None
        
        update_data = CategoryUpdate(name="新名称")
        result = category_service.update_category("nonexistent-id", update_data)
        
        assert result is None
    
    def test_update_category_partial(self, category_service, mock_repo):
        """测试部分更新分类"""
        category = Category(
            id="cat-1",
            name="原名称",
            description="原描述",
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.update.return_value = category
        
        update_data = CategoryUpdate(name="新名称")  # 只更新名称
        result = category_service.update_category("cat-1", update_data)
        
        assert result is not None
        mock_repo.update.assert_called_with("cat-1", update_data)
    
    def test_update_category_change_parent(self, category_service, mock_repo):
        """测试更新分类的父分类（移动分类）"""
        category = Category(
            id="cat-2",
            name="子分类",
            description="描述",
            parent_id="cat-1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.update.return_value = category
        
        update_data = CategoryUpdate(parent_id="cat-3")  # 移动到另一个父分类
        result = category_service.update_category("cat-2", update_data)
        
        assert result is not None
        mock_repo.update.assert_called_with("cat-2", update_data)


class TestCategoryServiceDelete:
    """测试 CategoryService.delete_category 方法"""
    
    def test_delete_category_success(self, category_service, mock_repo):
        """测试成功删除分类"""
        mock_repo.delete.return_value = True
        
        result = category_service.delete_category("cat-1")
        
        assert result is True
        mock_repo.delete.assert_called_with("cat-1")
    
    def test_delete_category_not_found(self, category_service, mock_repo):
        """测试删除不存在的分类"""
        mock_repo.delete.return_value = False
        
        result = category_service.delete_category("nonexistent-id")
        
        assert result is False


class TestCategoryServiceSearch:
    """测试 CategoryService.search_categories 方法"""
    
    def test_search_categories_success(self, category_service, mock_repo):
        """测试成功搜索分类"""
        categories = [
            Category(id="cat-1", name="数学分类", description="数学相关", parent_id=None, created_at=datetime.now(), updated_at=datetime.now()),
            Category(id="cat-2", name="高等数学", description="高数", parent_id="cat-1", created_at=datetime.now(), updated_at=datetime.now())
        ]
        mock_repo.search.return_value = categories
        
        result = category_service.search_categories("数学")
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repo.search.assert_called_with("数学")
    
    def test_search_categories_no_results(self, category_service, mock_repo):
        """测试搜索无结果"""
        mock_repo.search.return_value = []
        
        result = category_service.search_categories("不存在的关键词")
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_search_categories_empty_keyword(self, category_service, mock_repo):
        """测试空关键词搜索"""
        mock_repo.search.return_value = []
        
        result = category_service.search_categories("")
        
        assert isinstance(result, list)
        mock_repo.search.assert_called_with("")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
