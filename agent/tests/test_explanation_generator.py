"""
ExplanationGenerator 测试
测试题目解析生成器功能
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.generators.explanation_generator import ExplanationGenerator


class TestExplanationGeneratorInit:
    """ExplanationGenerator 初始化测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                assert generator.client is not None
                mock_client.assert_called_once()
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        custom_config = {
            'model': 'gpt-4',
            'api_key': 'custom-key',
            'base_url': 'https://api.openai.com'
        }
        
        with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            generator = ExplanationGenerator(config=custom_config)
            
            assert generator.client is not None
            mock_client.assert_called_once_with(custom_config)


class TestExplanationGeneratorGenerate:
    """解析生成功能测试"""
    
    def test_generate_single_choice(self):
        """测试生成单选题解析"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "这是生成的解析内容"
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                question_data = {
                    'id': 'q123',
                    'type': 'single_choice',
                    'content': 'Python 中列表的 append() 方法做什么？',
                    'options': [
                        'A. 在列表末尾添加元素',
                        'B. 删除列表元素',
                        'C. 排序列表',
                        'D. 反转列表'
                    ],
                    'answer': 'A'
                }
                
                result = generator.generate(question_data)
                
                assert result['success'] is True
                assert result['explanation'] == "这是生成的解析内容"
                assert result['question_id'] == 'q123'
                assert 'generated_at' in result
                
                # 验证 chat 调用
                mock_client_instance.chat.assert_called_once()
                call_args = mock_client_instance.chat.call_args
                messages = call_args.args[0]
                assert len(messages) == 1
                assert messages[0]['role'] == 'user'
                assert 'Python 中列表的 append()' in messages[0]['content']
                assert 'A. 在列表末尾添加元素' in messages[0]['content']
    
    def test_generate_fill_blank(self):
        """测试生成填空题解析"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "填空题解析内容"
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                question_data = {
                    'id': 'q456',
                    'type': 'fill_blank',
                    'content': 'Python 中用于定义函数的关键字是____',
                    'options': [],
                    'answer': 'def'
                }
                
                result = generator.generate(question_data)
                
                assert result['success'] is True
                assert result['explanation'] == "填空题解析内容"
                
                # 验证 prompt 中不包含选项部分
                call_args = mock_client_instance.chat.call_args
                messages = call_args.args[0]
                assert '【选项】' not in messages[0]['content']
    
    def test_generate_judgment(self):
        """测试生成判断题解析"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "判断题解析内容"
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                question_data = {
                    'id': 'q789',
                    'type': 'judgment',
                    'content': 'Python 是编译型语言',
                    'options': [],
                    'answer': '错误'
                }
                
                result = generator.generate(question_data)
                
                assert result['success'] is True
                assert result['explanation'] == "判断题解析内容"
    
    def test_generate_with_code_content(self):
        """测试生成包含代码的题目解析"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "代码题解析内容"
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                question_data = {
                    'id': 'q_code',
                    'type': 'single_choice',
                    'content': '''以下代码的输出是什么？
```python
def func(x):
    return x * 2
print(func(5))
```''',
                    'options': ['A. 5', 'B. 10', 'C. 25', 'D. Error'],
                    'answer': 'B'
                }
                
                result = generator.generate(question_data)
                
                assert result['success'] is True
                assert 'generated_at' in result
    
    def test_generate_missing_fields(self):
        """测试处理缺失字段的题目数据"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "解析内容"
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                # 缺少某些字段
                question_data = {
                    'content': '测试题目'
                    # 缺少 type, options, answer, id
                }
                
                result = generator.generate(question_data)
                
                assert result['success'] is True
                assert result['question_id'] is None
    
    def test_generate_api_error(self):
        """测试 API 错误处理"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.side_effect = Exception("API Error")
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                question_data = {
                    'id': 'q_error',
                    'type': 'single_choice',
                    'content': '测试题目',
                    'options': ['A. 选项'],
                    'answer': 'A'
                }
                
                result = generator.generate(question_data)
                
                assert result['success'] is False
                assert 'error' in result
                assert result['error'] == "API Error"
                assert result['question_id'] == 'q_error'
    
    def test_generate_strips_whitespace(self):
        """测试解析内容去除空白"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "  解析内容，前后有空格  \n\n"
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                question_data = {
                    'id': 'q123',
                    'type': 'single_choice',
                    'content': '测试题目',
                    'options': ['A. 选项'],
                    'answer': 'A'
                }
                
                result = generator.generate(question_data)
                
                assert result['explanation'] == "解析内容，前后有空格"


class TestExplanationGeneratorGenerateBatch:
    """批量生成测试"""
    
    def test_generate_batch_success(self):
        """测试批量生成解析成功"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.side_effect = ["解析 1", "解析 2", "解析 3"]
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                questions = [
                    {'id': 'q1', 'type': 'single_choice', 'content': '题目 1', 'options': ['A'], 'answer': 'A'},
                    {'id': 'q2', 'type': 'single_choice', 'content': '题目 2', 'options': ['B'], 'answer': 'B'},
                    {'id': 'q3', 'type': 'fill_blank', 'content': '题目 3', 'options': [], 'answer': '答案'}
                ]
                
                results = generator.generate_batch(questions)
                
                assert len(results) == 3
                assert all(r['success'] is True for r in results)
                assert results[0]['explanation'] == "解析 1"
                assert results[1]['explanation'] == "解析 2"
                assert results[2]['explanation'] == "解析 3"
    
    def test_generate_batch_empty_list(self):
        """测试空列表的批量生成"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                results = generator.generate_batch([])
                
                assert results == []
                mock_client_instance.chat.assert_not_called()
    
    def test_generate_batch_partial_failure(self):
        """测试批量生成部分失败"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.side_effect = ["解析 1", Exception("API Error"), "解析 3"]
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                
                questions = [
                    {'id': 'q1', 'type': 'single_choice', 'content': '题目 1', 'options': ['A'], 'answer': 'A'},
                    {'id': 'q2', 'type': 'single_choice', 'content': '题目 2', 'options': ['B'], 'answer': 'B'},
                    {'id': 'q3', 'type': 'fill_blank', 'content': '题目 3', 'options': [], 'answer': '答案'}
                ]
                
                results = generator.generate_batch(questions)
                
                assert len(results) == 3
                assert results[0]['success'] is True
                assert results[1]['success'] is False
                assert results[2]['success'] is True


class TestExplanationGeneratorClose:
    """资源清理测试"""
    
    def test_close(self):
        """测试关闭客户端"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                generator = ExplanationGenerator()
                generator.close()
                
                mock_client_instance.close.assert_called_once()


class TestExplanationGeneratorTimestamp:
    """时间戳测试"""
    
    def test_get_timestamp_format(self):
        """测试时间戳格式"""
        with patch('agent.generators.explanation_generator.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.generators.explanation_generator.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                generator = ExplanationGenerator()
                
                # 通过 generate 方法间接测试时间戳
                mock_client.return_value.chat.return_value = "解析"
                result = generator.generate({
                    'id': 'q1',
                    'type': 'single_choice',
                    'content': '题目',
                    'options': ['A'],
                    'answer': 'A'
                })
                
                # 验证时间戳格式 (ISO 8601)
                assert 'generated_at' in result
                timestamp = result['generated_at']
                # 尝试解析时间戳
                try:
                    datetime.fromisoformat(timestamp)
                except ValueError:
                    pytest.fail(f"Invalid timestamp format: {timestamp}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
