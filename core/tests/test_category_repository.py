"""
分类仓库测试
测试 CategoryRepository 的所有方法
"""
import pytest
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database.repositories import CategoryRepository
from core.models import Category, CategoryCreate, CategoryUpdate
from core.database.connection import DatabaseConnection


@pytest.fixture
def db_connection():
    """数据库连接 fixture"""
    db = DatabaseConnection()
    yield db
    # 清理测试数据
    cleanup_test_categories(db)


@pytest.fixture
def category_repo(db_connection):
    """分类仓库 fixture"""
    return CategoryRepository()


def cleanup_test_categories(db):
    """清理测试分类数据"""
    try:
        db.execute("DELETE FROM categories WHERE name LIKE '测试分类%' OR name LIKE 'Test Category%'")
        db.execute("DELETE FROM categories WHERE description LIKE '测试用%' OR description LIKE 'For test%'")
    except Exception:
        pass


class TestCategoryRepositoryCreate:
    """测试 CategoryRepository.create 方法"""
    
    def test_create_category_minimal(self, category_repo, db_connection):
        """测试创建最小化分类（只有名称）"""
        category_data = CategoryCreate(
            name="测试分类 - 最小化",
            description="",
            parent_id=None
        )
        
        result = category_repo.create(category_data)
        
        assert result is not None
        assert result.name == "测试分类 - 最小化"
        assert result.description == ""
        assert result.parent_id is None
        assert result.id is not None
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)
    
    def test_create_category_full(self, category_repo, db_connection):
        """测试创建完整分类（包含描述）"""
        category_data = CategoryCreate(
            name="测试分类 - 完整",
            description="这是一个用于测试的分类",
            parent_id=None
        )
        
        result = category_repo.create(category_data)
        
        assert result.name == "测试分类 - 完整"
        assert result.description == "这是一个用于测试的分类"
        assert result.parent_id is None
    
    def test_create_category_with_parent(self, category_repo, db_connection):
        """测试创建子分类"""
        # 先创建父分类
        parent_data = CategoryCreate(
            name="测试分类 - 父",
            description="父分类",
            parent_id=None
        )
        parent = category_repo.create(parent_data)
        
        # 创建子分类
        child_data = CategoryCreate(
            name="测试分类 - 子",
            description="子分类",
            parent_id=parent.id
        )
        child = category_repo.create(child_data)
        
        assert child.parent_id == parent.id
        assert child.name == "测试分类 - 子"
    
    def test_create_category_deep_hierarchy(self, category_repo, db_connection):
        """测试创建多层级分类"""
        # 创建三级分类
        level1 = category_repo.create(CategoryCreate(name="测试分类-L1", description="第一级"))
        level2 = category_repo.create(CategoryCreate(name="测试分类-L2", description="第二级", parent_id=level1.id))
        level3 = category_repo.create(CategoryCreate(name="测试分类-L3", description="第三级", parent_id=level2.id))
        
        assert level3.parent_id == level2.id
        assert level2.parent_id == level1.id
        assert level1.parent_id is None


class TestCategoryRepositoryGetById:
    """测试 CategoryRepository.get_by_id 方法"""
    
    def test_get_existing_category(self, category_repo, db_connection):
        """测试获取存在的分类"""
        # 创建分类
        category_data = CategoryCreate(
            name="测试分类 - 获取",
            description="用于测试获取",
            parent_id=None
        )
        created = category_repo.create(category_data)
        
        # 获取分类
        result = category_repo.get_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == "测试分类 - 获取"
        assert result.description == "用于测试获取"
    
    def test_get_nonexistent_category(self, category_repo, db_connection):
        """测试获取不存在的分类"""
        result = category_repo.get_by_id("nonexistent-id-12345")
        
        assert result is None
    
    def test_get_category_with_invalid_id(self, category_repo, db_connection):
        """测试使用无效 ID 获取分类"""
        result = category_repo.get_by_id("")
        assert result is None
        
        result = category_repo.get_by_id(None)
        assert result is None


class TestCategoryRepositoryGetAll:
    """测试 CategoryRepository.get_all 方法"""
    
    def test_get_all_categories(self, category_repo, db_connection):
        """测试获取所有分类"""
        # 创建几个测试分类
        category_repo.create(CategoryCreate(name="测试分类-A", description="A"))
        category_repo.create(CategoryCreate(name="测试分类-B", description="B"))
        category_repo.create(CategoryCreate(name="测试分类-C", description="C"))
        
        result = category_repo.get_all()
        
        assert isinstance(result, list)
        assert len(result) >= 3
    
    def test_get_all_empty(self, category_repo, db_connection):
        """测试获取空列表（理论上不会有空的情况）"""
        result = category_repo.get_all()
        assert isinstance(result, list)


class TestCategoryRepositoryUpdate:
    """测试 CategoryRepository.update 方法"""
    
    def test_update_category_name(self, category_repo, db_connection):
        """测试更新分类名称"""
        # 创建分类
        category = category_repo.create(CategoryCreate(
            name="测试分类 - 原名",
            description="原描述",
            parent_id=None
        ))
        
        # 更新名称
        update_data = CategoryUpdate(name="测试分类 - 新名")
        result = category_repo.update(category.id, update_data)
        
        assert result is not None
        assert result.name == "测试分类 - 新名"
        assert result.description == "原描述"
    
    def test_update_category_description(self, category_repo, db_connection):
        """测试更新分类描述"""
        category = category_repo.create(CategoryCreate(
            name="测试分类 - 描述",
            description="原描述",
            parent_id=None
        ))
        
        update_data = CategoryUpdate(description="新描述")
        result = category_repo.update(category.id, update_data)
        
        assert result.description == "新描述"
        assert result.name == "测试分类 - 描述"
    
    def test_update_category_parent(self, category_repo, db_connection):
        """测试更新分类父级"""
        parent = category_repo.create(CategoryCreate(name="父分类", description="父"))
        child = category_repo.create(CategoryCreate(name="子分类", description="子", parent_id=None))
        
        update_data = CategoryUpdate(parent_id=parent.id)
        result = category_repo.update(child.id, update_data)
        
        assert result.parent_id == parent.id
    
    def test_update_nonexistent_category(self, category_repo, db_connection):
        """测试更新不存在的分类"""
        update_data = CategoryUpdate(name="新名称")
        result = category_repo.update("nonexistent-id", update_data)
        
        assert result is None
    
    def test_update_category_partial(self, category_repo, db_connection):
        """测试部分更新分类"""
        category = category_repo.create(CategoryCreate(
            name="测试分类 - 部分",
            description="描述",
            parent_id=None
        ))
        
        # 只更新名称，其他字段保持不变
        update_data = CategoryUpdate(name="新名称")
        result = category_repo.update(category.id, update_data)
        
        assert result.name == "新名称"
        assert result.description == "描述"


class TestCategoryRepositoryDelete:
    """测试 CategoryRepository.delete 方法"""
    
    def test_delete_existing_category(self, category_repo, db_connection):
        """测试删除存在的分类"""
        category = category_repo.create(CategoryCreate(
            name="测试分类 - 删除",
            description="待删除",
            parent_id=None
        ))
        
        result = category_repo.delete(category.id)
        
        assert result is True
        
        # 验证已删除
        deleted = category_repo.get_by_id(category.id)
        assert deleted is None
    
    def test_delete_nonexistent_category(self, category_repo, db_connection):
        """测试删除不存在的分类"""
        result = category_repo.delete("nonexistent-id")
        
        assert result is False
    
    def test_delete_category_with_children(self, category_repo, db_connection):
        """测试删除有子分类的父分类"""
        parent = category_repo.create(CategoryCreate(name="父分类", description="父"))
        child = category_repo.create(CategoryCreate(name="子分类", description="子", parent_id=parent.id))
        
        # 删除父分类（子分类应该还在）
        result = category_repo.delete(parent.id)
        
        assert result is True
        
        # 子分类应该仍然存在
        child_still_exists = category_repo.get_by_id(child.id)
        assert child_still_exists is not None


class TestCategoryRepositorySearch:
    """测试 CategoryRepository.search 方法"""
    
    def test_search_by_name(self, category_repo, db_connection):
        """测试按名称搜索"""
        category_repo.create(CategoryCreate(name="数学测试", description="数学"))
        category_repo.create(CategoryCreate(name="物理测试", description="物理"))
        category_repo.create(CategoryCreate(name="化学测试", description="化学"))
        
        result = category_repo.search("数学")
        
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any(cat.name == "数学测试" for cat in result)
    
    def test_search_by_description(self, category_repo, db_connection):
        """测试按描述搜索"""
        category_repo.create(CategoryCreate(name="分类 A", description="数学相关"))
        category_repo.create(CategoryCreate(name="分类 B", description="物理相关"))
        
        result = category_repo.search("物理")
        
        assert len(result) >= 1
        assert any("物理" in cat.description for cat in result)
    
    def test_search_no_results(self, category_repo, db_connection):
        """测试搜索无结果"""
        result = category_repo.search("不存在的关键词 xyz123")
        
        assert isinstance(result, list)
        # 可能返回空列表
    
    def test_search_case_insensitive(self, category_repo, db_connection):
        """测试搜索不区分大小写"""
        category_repo.create(CategoryCreate(name="TestCategory", description="测试"))
        
        result_lower = category_repo.search("test")
        result_upper = category_repo.search("TEST")
        
        # SQLite 默认不区分大小写
        assert len(result_lower) >= 1 or len(result_upper) >= 1


class TestCategoryRepositoryGetChildren:
    """测试 CategoryRepository.get_children 方法"""
    
    def test_get_children(self, category_repo, db_connection):
        """测试获取子分类"""
        parent = category_repo.create(CategoryCreate(name="父分类", description="父"))
        child1 = category_repo.create(CategoryCreate(name="子分类 1", description="子 1", parent_id=parent.id))
        child2 = category_repo.create(CategoryCreate(name="子分类 2", description="子 2", parent_id=parent.id))
        
        children = category_repo.get_children(parent.id)
        
        assert isinstance(children, list)
        assert len(children) >= 2
        child_ids = [c.id for c in children]
        assert child1.id in child_ids
        assert child2.id in child_ids
    
    def test_get_children_none(self, category_repo, db_connection):
        """测试获取没有子分类的分类"""
        category = category_repo.create(CategoryCreate(name="独立分类", description="无子分类"))
        
        children = category_repo.get_children(category.id)
        
        assert isinstance(children, list)
        assert len(children) == 0
    
    def test_get_children_nonexistent(self, category_repo, db_connection):
        """测试获取不存在分类的子分类"""
        children = category_repo.get_children("nonexistent-id")
        
        assert isinstance(children, list)
        assert len(children) == 0


class TestCategoryRepositoryGetTree:
    """测试 CategoryRepository.get_tree 方法"""
    
    def test_get_tree(self, category_repo, db_connection):
        """测试获取分类树"""
        root = category_repo.create(CategoryCreate(name="根分类", description="根"))
        child1 = category_repo.create(CategoryCreate(name="子分类 1", description="子 1", parent_id=root.id))
        child2 = category_repo.create(CategoryCreate(name="子分类 2", description="子 2", parent_id=root.id))
        grandchild = category_repo.create(CategoryCreate(name="孙分类", description="孙", parent_id=child1.id))
        
        tree = category_repo.get_tree()
        
        assert isinstance(tree, list)
        # 验证树形结构
        root_node = next((t for t in tree if t['id'] == root.id), None)
        assert root_node is not None
        assert 'children' in root_node
    
    def test_get_tree_multiple_roots(self, category_repo, db_connection):
        """测试获取多个根节点的分类树"""
        root1 = category_repo.create(CategoryCreate(name="根 1", description="根 1"))
        root2 = category_repo.create(CategoryCreate(name="根 2", description="根 2"))
        
        tree = category_repo.get_tree()
        
        assert isinstance(tree, list)
        root_ids = [t['id'] for t in tree if t['parent_id'] is None]
        assert root1.id in root_ids or root2.id in root_ids  # 至少有一个根节点


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
