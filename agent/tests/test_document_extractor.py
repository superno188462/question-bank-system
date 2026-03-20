"""
DocumentExtractor 测试
测试文档题目提取器功能
"""
import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.extractors.document_extractor import DocumentExtractor


class TestDocumentExtractorInit:
    """DocumentExtractor 初始化测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                with patch('agent.extractors.document_extractor.AgentConfig.MAX_QUESTIONS_PER_DOCUMENT', 10):
                    mock_client_instance = Mock()
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    
                    assert extractor.client is not None
                    assert extractor.max_questions == 10
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        custom_config = {
            'model': 'gpt-4',
            'api_key': 'custom-key',
            'base_url': 'https://api.openai.com'
        }
        
        with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
            with patch('agent.extractors.document_extractor.AgentConfig.MAX_QUESTIONS_PER_DOCUMENT', 10):
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                extractor = DocumentExtractor(config=custom_config)
                
                assert extractor.client is not None
                mock_client.assert_called_once_with(custom_config)


class TestDocumentExtractorExtract:
    """文档提取功能测试"""
    
    def test_extract_file_not_found(self):
        """测试文件不存在的情况"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = DocumentExtractor()
                
                with pytest.raises(FileNotFoundError):
                    extractor.extract("/nonexistent/path/file.pdf")
    
    def test_extract_empty_document(self, tmp_path):
        """测试空文档"""
        doc_path = tmp_path / "empty.txt"
        doc_path.write_text("")
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = DocumentExtractor()
                result = extractor.extract(str(doc_path))
                
                assert result['questions'] == []
                assert result['total_count'] == 0
                assert result['confidence'] == 0.0
                assert result['error'] == "文档内容为空"
    
    def test_extract_txt_success(self, tmp_path):
        """测试提取 TXT 文档"""
        doc_path = tmp_path / "test.txt"
        doc_content = """
1. Python 中列表的 append() 方法做什么？
A. 在列表末尾添加元素
B. 删除列表元素
C. 排序列表
D. 反转列表
答案：A
"""
        doc_path.write_text(doc_content)
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_response = json.dumps({
                    "questions": [{
                        "type": "single_choice",
                        "content": "Python 中列表的 append() 方法做什么？",
                        "options": ["A. 在列表末尾添加元素", "B. 删除列表元素", "C. 排序列表", "D. 反转列表"],
                        "answer": "A",
                        "explanation": "append() 方法用于在列表末尾添加元素"
                    }],
                    "total_count": 1,
                    "confidence": 0.95
                })
                mock_client_instance.chat.return_value = mock_response
                mock_client.return_value = mock_client_instance
                
                extractor = DocumentExtractor()
                result = extractor.extract(str(doc_path))
                
                assert result['total_count'] == 1
                assert len(result['questions']) == 1
                assert result['questions'][0]['type'] == 'single_choice'
                assert result['source_type'] == 'document'
                assert result['source_file'] == 'test.txt'
                assert 'extracted_at' in result
    
    def test_extract_md_success(self, tmp_path):
        """测试提取 Markdown 文档"""
        doc_path = tmp_path / "test.md"
        doc_path.write_text("# 测试题目\n\n1. 什么是 Python？")
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_response = json.dumps({
                    "questions": [{"type": "short_answer", "content": "什么是 Python？", "options": [], "answer": "编程语言", "explanation": ""}],
                    "total_count": 1,
                    "confidence": 0.9
                })
                mock_client_instance.chat.return_value = mock_response
                mock_client.return_value = mock_client_instance
                
                extractor = DocumentExtractor()
                result = extractor.extract(str(doc_path))
                
                assert result['total_count'] == 1
    
    def test_extract_pdf_success(self, tmp_path):
        """测试提取 PDF 文档"""
        from agent.extractors.document_extractor import DocumentExtractor
        import sys
        from unittest.mock import Mock, patch, MagicMock
        import json
        
        doc_path = tmp_path / "test.pdf"
        doc_path.write_bytes(b"%PDF fake pdf content")
        
        # Mock fitz 模块
        mock_fitz = MagicMock()
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF 题目内容"
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.__len__ = Mock(return_value=1)
        mock_fitz.open.return_value = mock_doc
        
        with patch.dict('sys.modules', {'fitz': mock_fitz}):
            with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
                with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                    mock_config.return_value = {
                        'model': 'qwen-plus',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    mock_client_instance = Mock()
                    mock_response = json.dumps({
                        "questions": [{"type": "single_choice", "content": "PDF 题目", "options": [], "answer": "A", "explanation": ""}],
                        "total_count": 1,
                        "confidence": 0.9
                    })
                    mock_client_instance.chat.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    result = extractor.extract(str(doc_path))
                    
                    assert result['total_count'] == 1
    
    def test_extract_pdf_with_pdfplumber(self, tmp_path):
        """测试使用 pdfplumber 提取 PDF"""
        from agent.extractors.document_extractor import DocumentExtractor
        import sys
        from unittest.mock import Mock, patch, MagicMock
        import json
        
        doc_path = tmp_path / "test.pdf"
        doc_path.write_bytes(b"%PDF fake pdf content")
        
        # Mock pdfplumber 模块
        mock_pdfplumber = MagicMock()
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF 内容"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdfplumber.open.return_value = mock_pdf
        
        with patch.dict('sys.modules', {'fitz': None, 'pdfplumber': mock_pdfplumber}):
            with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
                with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                    mock_config.return_value = {
                        'model': 'qwen-plus',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    mock_client_instance = Mock()
                    mock_response = json.dumps({
                        "questions": [],
                        "total_count": 0,
                        "confidence": 0.0
                    })
                    mock_client_instance.chat.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    result = extractor.extract(str(doc_path))
                    
                    assert result is not None
    
    def test_extract_pdf_no_library(self, tmp_path):
        """测试 PDF 读取库未安装"""
        from agent.extractors.document_extractor import DocumentExtractor
        import sys
        from unittest.mock import Mock, patch
        import json
        
        doc_path = tmp_path / "test.pdf"
        doc_path.write_bytes(b"%PDF fake pdf content")
        
        with patch.dict('sys.modules', {'fitz': None, 'pdfplumber': None}):
            with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
                with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                    mock_config.return_value = {
                        'model': 'qwen-plus',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    mock_client_instance = Mock()
                    mock_response = json.dumps({
                        "questions": [],
                        "total_count": 0,
                        "confidence": 0.0
                    })
                    mock_client_instance.chat.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    result = extractor.extract(str(doc_path))
                    
                    # 应该返回错误信息
                    assert result is not None
                    assert 'error' in result or result['total_count'] == 0
    
    def test_extract_word_success(self, tmp_path):
        """测试提取 Word 文档"""
        from agent.extractors.document_extractor import DocumentExtractor
        import sys
        from unittest.mock import Mock, patch, MagicMock
        import json
        
        doc_path = tmp_path / "test.docx"
        doc_path.write_bytes(b"fake docx content")
        
        # Mock docx 模块
        mock_docx = MagicMock()
        mock_doc = Mock()
        mock_para = Mock()
        mock_para.text = "Word 题目内容"
        mock_doc.paragraphs = [mock_para]
        mock_docx.Document.return_value = mock_doc
        
        with patch.dict('sys.modules', {'docx': mock_docx}):
            with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
                with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                    mock_config.return_value = {
                        'model': 'qwen-plus',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    mock_client_instance = Mock()
                    mock_response = json.dumps({
                        "questions": [{"type": "short_answer", "content": "Word 题目", "options": [], "answer": "答案", "explanation": ""}],
                        "total_count": 1,
                        "confidence": 0.9
                    })
                    mock_client_instance.chat.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    result = extractor.extract(str(doc_path))
                    
                    assert result['total_count'] == 1
    
    def test_extract_word_no_library(self, tmp_path):
        """测试 Word 读取库未安装"""
        doc_path = tmp_path / "test.docx"
        doc_path.write_bytes(b"fake docx content")
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                with patch.dict('sys.modules', {'docx': None}):
                    mock_client_instance = Mock()
                    mock_response = json.dumps({
                        "questions": [],
                        "total_count": 0,
                        "confidence": 0.0
                    })
                    mock_client_instance.chat.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    result = extractor.extract(str(doc_path))
                    
                    assert result is not None
    
    def test_extract_multiple_questions(self, tmp_path):
        """测试提取多个题目"""
        doc_path = tmp_path / "multi.txt"
        doc_path.write_text("题目 1\n题目 2\n题目 3\n题目 4\n题目 5")
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                with patch('agent.extractors.document_extractor.AgentConfig.MAX_QUESTIONS_PER_DOCUMENT', 3):
                    mock_config.return_value = {
                        'model': 'qwen-plus',
                        'api_key': 'test-key',
                        'base_url': 'https://api.test.com'
                    }
                    
                    mock_client_instance = Mock()
                    mock_response = json.dumps({
                        "questions": [
                            {"type": "single_choice", "content": "题目 1", "options": [], "answer": "A", "explanation": ""},
                            {"type": "single_choice", "content": "题目 2", "options": [], "answer": "B", "explanation": ""},
                            {"type": "single_choice", "content": "题目 3", "options": [], "answer": "C", "explanation": ""},
                            {"type": "single_choice", "content": "题目 4", "options": [], "answer": "D", "explanation": ""},
                            {"type": "single_choice", "content": "题目 5", "options": [], "answer": "E", "explanation": ""}
                        ],
                        "total_count": 5,
                        "confidence": 0.9
                    })
                    mock_client_instance.chat.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    extractor = DocumentExtractor()
                    result = extractor.extract(str(doc_path))
                    
                    # 应该限制在 3 个题目
                    assert result['total_count'] == 3
                    assert len(result['questions']) == 3
    
    def test_extract_json_parse_error(self, tmp_path):
        """测试 JSON 解析错误"""
        doc_path = tmp_path / "test.txt"
        doc_path.write_text("文档内容")
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.return_value = "这不是 JSON 格式"
                mock_client.return_value = mock_client_instance
                
                extractor = DocumentExtractor()
                result = extractor.extract(str(doc_path))
                
                assert result['questions'] == []
                assert result['total_count'] == 0
                assert 'error' in result
    
    def test_extract_api_error(self, tmp_path):
        """测试 API 错误"""
        doc_path = tmp_path / "test.txt"
        doc_path.write_text("文档内容")
        
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                
                mock_client_instance = Mock()
                mock_client_instance.chat.side_effect = Exception("API Error")
                mock_client.return_value = mock_client_instance
                
                extractor = DocumentExtractor()
                result = extractor.extract(str(doc_path))
                
                assert result['questions'] == []
                assert result['total_count'] == 0
                assert result['error'] == "API Error"


class TestDocumentExtractorParseResponse:
    """响应解析测试"""
    
    def test_parse_response_direct_json(self):
        """测试直接解析 JSON"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = DocumentExtractor()
                
                json_str = '{"questions": [], "total_count": 0, "confidence": 0.0}'
                result = extractor._parse_response(json_str)
                
                assert result['total_count'] == 0
    
    def test_parse_response_json_code_block(self):
        """测试解析 JSON 代码块"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = DocumentExtractor()
                
                response = """
```json
{"questions": [{"type": "single_choice", "content": "题目", "options": [], "answer": "A", "explanation": ""}], "total_count": 1, "confidence": 0.9}
```
"""
                result = extractor._parse_response(response)
                
                assert result['total_count'] == 1
    
    def test_parse_response_json_without_marker(self):
        """测试解析没有标记的 JSON"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = DocumentExtractor()
                
                response = """
一些说明文字
{"questions": [], "total_count": 0, "confidence": 0.0}
更多说明
"""
                result = extractor._parse_response(response)
                
                assert result['total_count'] == 0
    
    def test_parse_response_invalid_json(self):
        """测试解析无效 JSON"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client.return_value = Mock()
                
                extractor = DocumentExtractor()
                
                response = "这不是有效的 JSON"
                result = extractor._parse_response(response)
                
                assert result['questions'] == []
                assert result['error'] == "无法解析响应为 JSON"


class TestDocumentExtractorClose:
    """资源清理测试"""
    
    def test_close(self):
        """测试关闭客户端"""
        with patch('agent.extractors.document_extractor.AgentConfig.get_llm_config') as mock_config:
            with patch('agent.extractors.document_extractor.ModelClient') as mock_client:
                mock_config.return_value = {
                    'model': 'qwen-plus',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com'
                }
                mock_client_instance = Mock()
                mock_client.return_value = mock_client_instance
                
                extractor = DocumentExtractor()
                extractor.close()
                
                mock_client_instance.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
