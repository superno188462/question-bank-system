"""
测试题库系统架构
"""

import unittest
from datetime import datetime
from src.core.question_bank_system import Question, QuestionRepository, TestPaperGenerator
from src.domain.question_services import InMemoryQuestionRepository, QuestionValidator, QuestionFactory
from src.domain.test_paper_services import RandomTestPaperGenerator
from src.application.question_bank_app import QuestionBankApplication


class TestQuestionArchitecture(unittest.TestCase):
    """测试题目架构"""
    
    def test_question_creation(self):
        """测试题目创建"""
        validator = QuestionValidator()
        factory = QuestionFactory(validator)
        
        question_data = {
            "content": "Python中如何定义类？",
            "question_type": "multiple_choice",
            "difficulty": "easy",
            "tags": ["python", "oop"],
            "metadata": {"category": "programming"}
        }
        
        question = factory.create_question(question_data)
        self.assertIsNotNone(question)
        self.assertEqual(question.content, "Python中如何定义类？")
        self.assertEqual(question.difficulty, "easy")
    
    def test_repository_interface(self):
        """测试仓储接口"""
        repository = InMemoryQuestionRepository()
        
        # 创建测试题目
        question = Question(
            id="test-1",
            content="测试题目",
            question_type="multiple_choice",
            difficulty="easy",
            tags=["test"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        
        # 测试保存
        saved = repository.save(question)
        self.assertEqual(saved.id, "test-1")
        
        # 测试查找
        found = repository.find_by_id("test-1")
        self.assertIsNotNone(found)
        self.assertEqual(found.content, "测试题目")
        
        # 测试按标签查找
        tagged = repository.find_by_tags(["test"])
        self.assertEqual(len(tagged), 1)
        
        # 测试删除
        deleted = repository.delete("test-1")
        self.assertTrue(deleted)
        
        not_found = repository.find_by_id("test-1")
        self.assertIsNone(not_found)


class TestApplicationLayer(unittest.TestCase):
    """测试应用层"""
    
    def test_application_service(self):
        """测试应用服务"""
        app = QuestionBankApplication()
        
        # 创建题目
        question_data = {
            "content": "测试应用层题目",
            "question_type": "short_answer",
            "difficulty": "medium",
            "tags": ["test", "application"]
        }
        
        question = app.create_question(question_data)
        self.assertIsNotNone(question)
        
        # 获取题目
        retrieved = app.get_question(question.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "测试应用层题目")
        
        # 搜索题目
        results = app.search_questions(["test"])
        self.assertGreaterEqual(len(results), 1)


class TestSingleReturnPrinciple(unittest.TestCase):
    """测试单一return原则"""
    
    def test_methods_have_single_return(self):
        """检查方法是否只有一个return语句"""
        import ast
        import os
        
        def count_returns_in_file(filepath):
            """统计文件中的return语句数量"""
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            return_counts = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
                    return_counts[node.name] = return_count
            
            return return_counts
        
        # 测试核心文件
        core_file = "src/core/question_bank_system.py"
        if os.path.exists(core_file):
            return_counts = count_returns_in_file(core_file)
            
            # 检查抽象方法
            for method_name, count in return_counts.items():
                if method_name in ['save', 'find_by_id', 'find_by_tags', 'delete', 
                                  'generate', 'validate', 'score', 'analyze']:
                    self.assertEqual(count, 1, 
                                   f"方法 {method_name} 应该有且只有一个return语句，但有 {count} 个")


if __name__ == "__main__":
    unittest.main()