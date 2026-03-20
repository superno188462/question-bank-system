"""
题目仓库补充测试
覆盖未测试的代码路径：
- create 方法
- get_by_id 方法（包括 None 返回）
- get_all 方法（各种筛选条件）
- update 方法
- delete 方法
- get_question_tags 方法
- add_tag/remove_tag 方法
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.database.repositories import QuestionRepository, StagingQuestionRepository
from core.models import QuestionCreate, QuestionUpdate, StagingQuestionCreate


class MockDBConnection:
    """Mock 数据库连接"""
    
    def __init__(self):
        self.executed_queries = []
        self.fetch_one_result = None
        self.fetch_all_result = []
    
    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        return mock_cursor
    
    def fetch_one(self, query, params=None):
        self.executed_queries.append((query, params))
        return self.fetch_one_result
    
    def fetch_all(self, query, params=None):
        self.executed_queries.append((query, params))
        return self.fetch_all_result


class TestQuestionRepositoryCreate:
    """测试题目创建"""
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_create_success(self, mock_db, mock_transaction):
        """测试成功创建题目"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        # Mock get_by_id 返回
        repo = QuestionRepository()
        
        question_data = QuestionCreate(
            content="测试题目",
            answer="A",
            options=["选项 A", "选项 B"],
            explanation="解析",
            category_id="cat1"
        )
        
        # Mock 数据库操作
        mock_db.execute = Mock()
        
        # 由于 create 方法会调用 get_by_id，我们需要 Mock 它
        with patch.object(repo, 'get_by_id') as mock_get:
            mock_get.return_value = Mock()
            result = repo.create(question_data)
            
            # 验证执行了 INSERT
            assert mock_db.execute.called
            call_args = mock_db.execute.call_args[0]
            assert 'INSERT INTO questions' in call_args[0]
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_create_with_empty_options(self, mock_db, mock_transaction):
        """测试创建题目时选项为空"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        question_data = QuestionCreate(
            content="测试题目",
            answer="A",
            options=[],
            explanation="解析"
        )
        
        mock_db.execute = Mock()
        
        with patch.object(repo, 'get_by_id') as mock_get:
            mock_get.return_value = Mock()
            result = repo.create(question_data)
            
            # 验证选项被序列化为空列表
            call_args = mock_db.execute.call_args[0]
            options_json = call_args[1][2]  # options 是第 3 个参数
            assert options_json == '[]'


class TestQuestionRepositoryGetById:
    """测试根据 ID 获取题目"""
    
    @patch('core.database.repositories.db')
    def test_get_by_id_success(self, mock_db):
        """测试成功获取题目"""
        repo = QuestionRepository()
        
        mock_row = {
            'id': 'q1',
            'content': '测试题目',
            'options': '["A", "B"]',
            'answer': 'A',
            'explanation': '解析',
            'category_id': 'cat1',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        mock_db.fetch_one.return_value = mock_row
        
        # Mock get_question_tags
        with patch.object(repo, 'get_question_tags') as mock_tags:
            mock_tags.return_value = []
            result = repo.get_by_id('q1')
            
            assert result is not None
            assert result.id == 'q1'
            assert result.content == '测试题目'
    
    @patch('core.database.repositories.db')
    def test_get_by_id_not_found(self, mock_db):
        """测试题目不存在"""
        repo = QuestionRepository()
        mock_db.fetch_one.return_value = None
        
        result = repo.get_by_id('nonexistent')
        
        assert result is None
    
    @patch('core.database.repositories.db')
    def test_get_by_id_invalid_json_options(self, mock_db):
        """测试选项 JSON 解析失败"""
        repo = QuestionRepository()
        
        mock_row = {
            'id': 'q1',
            'content': '测试题目',
            'options': 'invalid json',
            'answer': 'A',
            'explanation': '解析',
            'category_id': 'cat1',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        mock_db.fetch_one.return_value = mock_row
        
        with patch.object(repo, 'get_question_tags') as mock_tags:
            mock_tags.return_value = []
            result = repo.get_by_id('q1')
            
            # 应该返回空列表而不是抛出异常
            assert result.options == []
    
    @patch('core.database.repositories.db')
    def test_get_by_id_options_not_list(self, mock_db):
        """测试选项不是列表"""
        repo = QuestionRepository()
        
        mock_row = {
            'id': 'q1',
            'content': '测试题目',
            'options': '{"key": "value"}',
            'answer': 'A',
            'explanation': '解析',
            'category_id': 'cat1',
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }
        mock_db.fetch_one.return_value = mock_row
        
        with patch.object(repo, 'get_question_tags') as mock_tags:
            mock_tags.return_value = []
            result = repo.get_by_id('q1')
            
            assert result.options == []


class TestQuestionRepositoryGetAll:
    """测试获取所有题目"""
    
    @patch('core.database.repositories.db')
    def test_get_all_no_filters(self, mock_db):
        """测试无筛选条件"""
        repo = QuestionRepository()
        
        mock_db.fetch_one.return_value = {'total': 0}
        mock_db.fetch_all.return_value = []
        
        result = repo.get_all()
        
        assert 'data' in result
        assert 'total' in result
        assert 'page' in result
        assert 'limit' in result
    
    @patch('core.database.repositories.db')
    def test_get_all_with_category(self, mock_db):
        """测试按分类筛选"""
        repo = QuestionRepository()
        
        mock_db.fetch_one.return_value = {'total': 0}
        mock_db.fetch_all.return_value = []
        
        result = repo.get_all(category_id='cat1')
        
        # 验证查询包含 category_id 条件
        queries = [q[0] for q in mock_db.fetch_all.call_args_list]
        assert any('category_id' in str(q) for q in queries)
    
    @patch('core.database.repositories.db')
    def test_get_all_with_keyword(self, mock_db):
        """测试按关键词搜索"""
        repo = QuestionRepository()
        
        mock_db.fetch_one.return_value = {'total': 0}
        mock_db.fetch_all.return_value = []
        
        result = repo.get_all(keyword='测试')
        
        # 验证查询包含 LIKE 条件
        queries = [q[0] for q in mock_db.fetch_all.call_args_list]
        assert any('LIKE' in str(q) for q in queries)
    
    @patch('core.database.repositories.db')
    def test_get_all_with_tag(self, mock_db):
        """测试按标签筛选"""
        repo = QuestionRepository()
        
        mock_db.fetch_one.return_value = {'total': 0}
        mock_db.fetch_all.return_value = []
        
        result = repo.get_all(tag_id='tag1')
        
        # 验证查询包含 question_tags 连接
        queries = [q[0] for q in mock_db.fetch_all.call_args_list]
        assert any('question_tags' in str(q) for q in queries)
    
    @patch('core.database.repositories.db')
    def test_get_all_with_pagination(self, mock_db):
        """测试分页"""
        repo = QuestionRepository()
        
        mock_db.fetch_one.return_value = {'total': 50}
        mock_db.fetch_all.return_value = []
        
        result = repo.get_all(page=2, limit=10)
        
        assert result['page'] == 2
        assert result['limit'] == 10
        assert result['pages'] == 5  # 50/10 = 5


class TestQuestionRepositoryUpdate:
    """测试更新题目"""
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_update_success(self, mock_db, mock_transaction):
        """测试成功更新题目"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        update_data = QuestionUpdate(content="新内容")
        
        mock_db.execute = Mock()
        
        with patch.object(repo, 'get_by_id') as mock_get:
            mock_get.return_value = Mock()
            result = repo.update('q1', update_data)
            
            # 验证执行了 UPDATE
            assert mock_db.execute.called
            call_args = mock_db.execute.call_args[0]
            assert 'UPDATE questions' in call_args[0]
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_update_no_changes(self, mock_db, mock_transaction):
        """测试无更新内容"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        update_data = QuestionUpdate()  # 空更新
        
        with patch.object(repo, 'get_by_id') as mock_get:
            mock_get.return_value = Mock()
            result = repo.update('q1', update_data)
            
            # 应该直接返回，不执行 UPDATE
            mock_db.execute.assert_not_called()
            mock_get.assert_called_with('q1')


class TestQuestionRepositoryDelete:
    """测试删除题目"""
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_delete_success(self, mock_db, mock_transaction):
        """测试成功删除题目"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_db.execute.return_value = mock_cursor
        
        result = repo.delete('q1')
        
        assert result is True
        # 验证删除了题目标签关联和题目
        assert mock_db.execute.call_count == 2
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_delete_not_found(self, mock_db, mock_transaction):
        """测试删除不存在的题目"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        mock_db.execute.return_value = mock_cursor
        
        result = repo.delete('nonexistent')
        
        assert result is False


class TestQuestionRepositoryTags:
    """测试题目标签操作"""
    
    @patch('core.database.repositories.db')
    def test_get_question_tags(self, mock_db):
        """测试获取题目标签"""
        repo = QuestionRepository()
        
        mock_db.fetch_all.return_value = [
            {
                'id': 'tag1',
                'name': '标签 1',
                'color': '#FF0000',
                'created_at': '2024-01-01T00:00:00'
            }
        ]
        
        result = repo.get_question_tags('q1')
        
        assert len(result) == 1
        assert result[0].id == 'tag1'
        assert result[0].name == '标签 1'
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_add_tag_success(self, mock_db, mock_transaction):
        """测试添加标签成功"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        
        # Mock 检查不存在
        mock_db.fetch_one.return_value = {'count': 0}
        mock_db.execute = Mock()
        
        result = repo.add_tag('q1', 'tag1')
        
        assert result is True
        # 验证执行了 INSERT
        assert mock_db.execute.called
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_add_tag_already_exists(self, mock_db, mock_transaction):
        """测试标签已存在"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        
        # Mock 检查已存在
        mock_db.fetch_one.return_value = {'count': 1}
        
        result = repo.add_tag('q1', 'tag1')
        
        assert result is True
        # 不应该执行 INSERT
        mock_db.execute.assert_not_called()
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_remove_tag_success(self, mock_db, mock_transaction):
        """测试移除标签成功"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = QuestionRepository()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_db.execute.return_value = mock_cursor
        
        result = repo.remove_tag('q1', 'tag1')
        
        assert result is True
        # 验证执行了 DELETE
        call_args = mock_db.execute.call_args[0]
        assert 'DELETE FROM question_tags' in call_args[0]


class TestQuestionRepositorySearch:
    """测试题目搜索"""
    
    @patch('core.database.repositories.db')
    def test_search(self, mock_db):
        """测试搜索题目"""
        repo = QuestionRepository()
        
        mock_db.fetch_one.return_value = {'total': 0}
        mock_db.fetch_all.return_value = []
        
        result = repo.search('测试')
        
        assert isinstance(result, list)


class TestStagingQuestionRepository:
    """测试预备题目仓库"""
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_create_staging_question(self, mock_db, mock_transaction):
        """测试创建预备题目"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = StagingQuestionRepository()
        
        staging_data = {
            'source_type': 'chat',
            'content': '测试预备题目',
            'type': 'single_choice',
            'answer': 'A',
            'options': ['A', 'B'],
            'explanation': '解析'
        }
        
        mock_cursor = Mock()
        mock_cursor.lastrowid = 1
        mock_db.execute.return_value = mock_cursor
        
        result = repo.create(staging_data)
        
        # 验证执行了 INSERT
        assert mock_db.execute.called
        call_args = mock_db.execute.call_args[0]
        assert 'INSERT INTO staging_questions' in call_args[0]
        assert result == 1
    
    @patch('core.database.repositories.db')
    def test_get_staging_by_id(self, mock_db):
        """测试获取预备题目"""
        repo = StagingQuestionRepository()
        
        mock_row = {
            'id': 'sq1',
            'source_type': 'chat',
            'source_file': None,
            'content': '测试预备题目',
            'type': 'single_choice',
            'answer': 'A',
            'options': '["A", "B"]',
            'explanation': '解析',
            'status': 'pending',
            'category_id': None,
            'tags': '[]',
            'confidence': 1.0,
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00',
            'reviewed_at': None,
            'reviewed_by': None
        }
        mock_db.fetch_one.return_value = mock_row
        
        result = repo.get_by_id('sq1')
        
        assert result is not None
        assert result['id'] == 'sq1'
    
    @patch('core.database.repositories.db')
    def test_get_staging_not_found(self, mock_db):
        """测试预备题目不存在"""
        repo = StagingQuestionRepository()
        mock_db.fetch_one.return_value = None
        
        result = repo.get_by_id('nonexistent')
        
        assert result is None
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_update_staging_status(self, mock_db, mock_transaction):
        """测试更新预备题目状态"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = StagingQuestionRepository()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_db.execute.return_value = mock_cursor
        
        result = repo.update('sq1', {'status': 'approved'})
        
        # 验证执行了 UPDATE
        assert mock_db.execute.called
        assert result is True
    
    @patch('core.database.repositories.transaction')
    @patch('core.database.repositories.db')
    def test_delete_staging_question(self, mock_db, mock_transaction):
        """测试删除预备题目"""
        mock_transaction.return_value.__enter__ = Mock()
        mock_transaction.return_value.__exit__ = Mock()
        
        repo = StagingQuestionRepository()
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_db.execute.return_value = mock_cursor
        
        result = repo.delete('sq1')
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
