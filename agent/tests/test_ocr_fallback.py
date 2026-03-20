"""
OCR 备选方案降级测试
测试 OCR 服务、OCR 题目提取器以及 ImageExtractor 的降级逻辑

测试覆盖:
- OcrService: 多引擎支持、自动降级
- OcrQuestionExtractor: OCR+LLM 联合提取
- ImageExtractor: 视觉模型失败时的自动降级
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from pathlib import Path
import sys
import os
import tempfile

# 确保可以导入 agent 模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.services.ocr_service import OcrService, OcrEngine, PaddleOcrEngine, TesseractOcrEngine
from agent.extractors.ocr_question_extractor import OcrQuestionExtractor
from agent.extractors.image_extractor import ImageExtractor
from agent.config import AgentConfig


@pytest.fixture
def mock_ocr_engine():
    """创建 Mock OCR 引擎"""
    engine = Mock(spec=OcrEngine)
    engine.name = "mock_paddle"
    engine.is_available.return_value = True
    engine.recognize.return_value = "测试文字"
    return engine


@pytest.fixture
def temp_image_file():
    """创建临时图片文件"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(b"fake image content")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


# ========== OCR Service 测试 ==========

class TestOcrService:
    """测试 OCR 服务"""
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_initialize(self, mock_paddle):
        """测试 OCR 服务初始化"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        assert service is not None
        assert service.config == config
        assert service.engine is not None
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_get_current_engine(self, mock_paddle):
        """测试获取当前引擎"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        # 应该返回一个引擎实例
        assert service.current_engine == "paddle"
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_is_available(self, mock_paddle):
        """测试 OCR 服务可用性检查"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        # 应该可以检查可用性
        available = service.is_available()
        assert available is True


class TestPaddleOcrEngine:
    """测试 PaddleOCR 引擎"""
    
    def test_paddle_ocr_engine_name(self):
        """测试引擎名称"""
        engine = PaddleOcrEngine(lang="ch")
        assert engine.name == "paddle"
    
    def test_paddle_ocr_engine_init(self):
        """测试引擎初始化"""
        engine = PaddleOcrEngine(lang="ch", use_angle_cls=True)
        assert engine.lang == "ch"
        assert engine.use_angle_cls is True
        assert engine._initialized is False
    
    def test_paddle_ocr_engine_lazy_init(self):
        """测试延迟初始化"""
        engine = PaddleOcrEngine(lang="ch")
        
        # 初始状态
        assert engine._initialized is False
        
        # 调用 _lazy_init (不实际加载 PaddleOCR)
        # 注意：实际环境中需要安装 paddleocr
        # 这里测试逻辑而非实际功能
    
    def test_paddle_ocr_engine_format_result(self):
        """测试 OCR 结果格式化"""
        engine = PaddleOcrEngine(lang="ch")
        
        # 模拟 PaddleOCR 返回结果 (正确格式)
        # PaddleOCR 返回格式：[[[coords], (text, confidence)], ...]
        mock_result = [
            [  # result[0] 是检测列表
                [[[10, 10], [100, 10], [100, 30], [10, 30]], ("测试题目 1", 0.95)],
                [[[10, 40], [100, 40], [100, 60], [10, 60]], ("选项 A", 0.92)]
            ]
        ]
        
        formatted = engine._format_result(mock_result)
        assert "测试题目 1" in formatted
        assert "选项 A" in formatted
        assert isinstance(formatted, str)
        assert formatted == "测试题目 1\n选项 A"
    
    def test_paddle_ocr_engine_format_empty_result(self):
        """测试空结果格式化"""
        engine = PaddleOcrEngine(lang="ch")
        
        formatted = engine._format_result([])
        assert formatted == ""
        
        formatted = engine._format_result([[]])
        assert formatted == ""


class TestTesseractOcrEngine:
    """测试 Tesseract OCR 引擎"""
    
    def test_tesseract_engine_name(self):
        """测试引擎名称"""
        engine = TesseractOcrEngine(lang="chi_sim+eng")
        assert engine.name == "tesseract"
    
    def test_tesseract_engine_init(self):
        """测试引擎初始化"""
        engine = TesseractOcrEngine(lang="chi_sim")
        assert engine.lang == "chi_sim"
        assert engine._initialized is False


# ========== OCR Question Extractor 测试 ==========

class TestOcrQuestionExtractor:
    """测试 OCR 题目提取器"""
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_init(self, mock_llm, mock_ocr):
        """测试提取器初始化"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        ocr_config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        llm_config = {"model_id": "qwen-plus", "api_key": "test_key"}
        
        extractor = OcrQuestionExtractor(ocr_config, llm_config)
        
        assert extractor is not None
        assert extractor.ocr_service is not None
        assert extractor.llm_client is not None
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_extract_nonexistent_file(self, mock_llm, mock_ocr):
        """测试提取不存在的文件"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        extractor = OcrQuestionExtractor()
        
        with pytest.raises(FileNotFoundError):
            extractor.extract("nonexistent_file.png")
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_extract_with_mock(self, mock_llm, mock_ocr, temp_image_file):
        """测试提取功能 (Mock)"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.recognize_with_confidence.return_value = {
            "text": "测试题目\nA. 选项 1\nB. 选项 2",
            "confidence": 0.9
        }
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm_instance.chat.return_value = '{"questions": [{"type": "single_choice", "content": "测试题目", "options": ["A. 选项 1", "B. 选项 2"], "answer": "A", "explanation": ""}], "total_count": 1, "confidence": 0.8}'
        mock_llm.return_value = mock_llm_instance
        
        extractor = OcrQuestionExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert "questions" in result
        assert "extraction_method" in result
        assert result["extraction_method"] == "ocr+llm"
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_extract_empty_ocr(self, mock_llm, mock_ocr, temp_image_file):
        """测试 OCR 识别结果为空"""
        # Mock OCR 服务返回空结果
        mock_ocr_instance = Mock()
        mock_ocr_instance.recognize_with_confidence.return_value = {
            "text": "",
            "confidence": 0.0
        }
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        extractor = OcrQuestionExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert result["questions"] == []
        assert result["total_count"] == 0
        assert result.get("error") == "OCR 识别结果为空"
    
    def test_ocr_extractor_parse_response_json(self):
        """测试 JSON 响应解析"""
        # 需要 Mock 初始化
        with patch('agent.extractors.ocr_question_extractor.OcrService'):
            with patch('agent.extractors.ocr_question_extractor.ModelClient'):
                extractor = OcrQuestionExtractor()
                
                # 有效 JSON
                response = '{"questions": [], "total_count": 0, "confidence": 0.0}'
                result = extractor._parse_response(response)
                assert result["questions"] == []
                assert result["total_count"] == 0
    
    def test_ocr_extractor_parse_response_json_block(self):
        """测试 JSON 代码块解析"""
        # 需要 Mock 初始化
        with patch('agent.extractors.ocr_question_extractor.OcrService'):
            with patch('agent.extractors.ocr_question_extractor.ModelClient'):
                extractor = OcrQuestionExtractor()
                
                # JSON 代码块
                response = '''```json
 {"questions": [], "total_count": 0, "confidence": 0.0}
 ```'''
                result = extractor._parse_response(response)
                assert result["questions"] == []
    
    def test_ocr_extractor_parse_response_invalid(self):
        """测试无效响应解析"""
        # 需要 Mock 初始化
        with patch('agent.extractors.ocr_question_extractor.OcrService'):
            with patch('agent.extractors.ocr_question_extractor.ModelClient'):
                extractor = OcrQuestionExtractor()
                
                # 无效 JSON
                response = "这不是 JSON"
                result = extractor._parse_response(response)
                assert result["questions"] == []
                assert result.get("error") is not None


# ========== ImageExtractor 降级逻辑测试 ==========

class TestImageExtractorFallback:
    """测试 ImageExtractor 降级逻辑"""
    
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_image_extractor_init(self, mock_client):
        """测试提取器初始化"""
        # Mock ModelClient
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        extractor = ImageExtractor()
        
        assert extractor is not None
        assert extractor.vision_config is not None
        assert extractor.client is not None
        assert extractor.ocr_enabled is not None
    
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_vision_success(self, mock_client, mock_ocr_extractor, temp_image_file):
        """测试视觉模型成功"""
        # Mock ModelClient
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.return_value = '{"questions": [{"type": "single_choice", "content": "测试题目", "options": ["A"], "answer": "A", "explanation": ""}], "total_count": 1, "confidence": 0.9}'
        mock_client.return_value = mock_client_instance
        
        extractor = ImageExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert result["extraction_method"] == "vision"
        assert result.get("fallback_used") is None
    
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_vision_fallback_to_ocr(self, mock_client, mock_ocr_extractor, temp_image_file):
        """测试视觉模型失败降级到 OCR"""
        # Mock ModelClient - 视觉模型失败
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.side_effect = Exception("API 调用失败")
        mock_client.return_value = mock_client_instance
        
        # Mock OCR 提取器
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract.return_value = {
            "questions": [{"type": "single_choice", "content": "测试题目", "options": ["A"], "answer": "A", "explanation": ""}],
            "total_count": 1,
            "confidence": 0.8,
            "extraction_method": "ocr+llm"
        }
        mock_ocr_extractor.return_value = mock_ocr_instance
        
        extractor = ImageExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert result["extraction_method"] == "ocr+llm"
        assert result.get("fallback_used") is True
        assert result.get("fallback_reason") is not None
    
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_vision_low_confidence_fallback(self, mock_client, mock_ocr_extractor, temp_image_file):
        """测试视觉模型置信度过低降级"""
        # Mock ModelClient - 返回低置信度
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.return_value = '{"questions": [{"type": "single_choice", "content": "测试题目", "options": ["A"], "answer": "A", "explanation": ""}], "total_count": 1, "confidence": 0.3}'
        mock_client.return_value = mock_client_instance
        
        # Mock OCR 提取器
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract.return_value = {
            "questions": [{"type": "single_choice", "content": "测试题目", "options": ["A"], "answer": "A", "explanation": ""}],
            "total_count": 1,
            "confidence": 0.8,
            "extraction_method": "ocr+llm"
        }
        mock_ocr_extractor.return_value = mock_ocr_instance
        
        extractor = ImageExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert result["extraction_method"] == "ocr+llm"
        assert result.get("fallback_used") is True
    
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_vision_empty_result_fallback(self, mock_client, mock_ocr_extractor, temp_image_file):
        """测试视觉模型返回空结果降级"""
        # Mock ModelClient - 返回空结果
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.return_value = '{"questions": [], "total_count": 0, "confidence": 0.0}'
        mock_client.return_value = mock_client_instance
        
        # Mock OCR 提取器
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract.return_value = {
            "questions": [{"type": "single_choice", "content": "测试题目", "options": ["A"], "answer": "A", "explanation": ""}],
            "total_count": 1,
            "confidence": 0.8,
            "extraction_method": "ocr+llm"
        }
        mock_ocr_extractor.return_value = mock_ocr_instance
        
        extractor = ImageExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert result["extraction_method"] == "ocr+llm"
        assert result.get("fallback_used") is True
    
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_ocr_disabled_no_fallback(self, mock_client, mock_ocr_extractor, temp_image_file):
        """测试 OCR 禁用时无降级"""
        # Mock ModelClient - 视觉模型失败
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.side_effect = Exception("API 调用失败")
        mock_client.return_value = mock_client_instance
        
        extractor = ImageExtractor()
        extractor.ocr_enabled = False  # 禁用 OCR
        
        result = extractor.extract(temp_image_file)
        
        assert result is not None
        assert result["extraction_method"] == "vision"
        assert result.get("fallback_used") is None
        assert result.get("error") is not None
    
    def test_is_vision_result_valid_with_error(self):
        """测试验证视觉模型结果 - 有错误"""
        extractor = ImageExtractor.__new__(ImageExtractor)  # 不调用__init__
        extractor.vision_fallback_threshold = 0.5
        
        result = {"error": "API 失败", "questions": [], "confidence": 0.0}
        assert extractor._is_vision_result_valid(result) is False
    
    def test_is_vision_result_valid_empty_questions(self):
        """测试验证视觉模型结果 - 空题目"""
        extractor = ImageExtractor.__new__(ImageExtractor)  # 不调用__init__
        extractor.vision_fallback_threshold = 0.5
        
        result = {"questions": [], "total_count": 0, "confidence": 0.0}
        assert extractor._is_vision_result_valid(result) is False
    
    def test_is_vision_result_valid_low_confidence(self):
        """测试验证视觉模型结果 - 低置信度"""
        extractor = ImageExtractor.__new__(ImageExtractor)  # 不调用__init__
        extractor.vision_fallback_threshold = 0.5
        
        result = {"questions": [{"type": "single_choice"}], "total_count": 1, "confidence": 0.3}
        assert extractor._is_vision_result_valid(result) is False
    
    def test_is_vision_result_valid_success(self):
        """测试验证视觉模型结果 - 成功"""
        extractor = ImageExtractor.__new__(ImageExtractor)  # 不调用__init__
        extractor.vision_fallback_threshold = 0.5
        
        result = {"questions": [{"type": "single_choice"}], "total_count": 1, "confidence": 0.9}
        assert extractor._is_vision_result_valid(result) is True
    
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_extract_batch(self, mock_client, mock_ocr_extractor):
        """测试批量提取"""
        # Mock ModelClient
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.return_value = '{"questions": [{"type": "single_choice"}], "total_count": 1, "confidence": 0.9}'
        mock_client.return_value = mock_client_instance
        
        extractor = ImageExtractor()
        result = extractor.extract_batch(["image1.png", "image2.png"])
        
        assert result is not None
        assert result["total_count"] >= 0
        assert result["source_type"] == "image_batch"


# ========== 集成测试 ==========

class TestIntegration:
    """集成测试"""
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_with_mock_engine(self, mock_paddle):
        """测试 OCR 服务与 Mock 引擎"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_engine.recognize.return_value = "测试文字"
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        result = service.recognize("test.png")
        assert result == "测试文字"
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_recognize_with_confidence(self, mock_paddle):
        """测试 OCR 服务带置信度识别"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_engine.recognize.return_value = "测试题目\n选项 A\n选项 B"
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        result = service.recognize_with_confidence("test.png")
        
        assert result is not None
        assert "text" in result
        assert "confidence" in result
        assert result["text"] == "测试题目\n选项 A\n选项 B"


# ========== 性能测试 ==========

class TestPerformance:
    """性能测试"""
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_initialization_time(self, mock_paddle):
        """测试 OCR 服务初始化时间"""
        import time
        
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        start = time.time()
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        end = time.time()
        
        # 初始化应该在 1 秒内完成
        assert (end - start) < 1.0
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_initialization_time(self, mock_llm, mock_ocr):
        """测试 OCR 提取器初始化时间"""
        import time
        
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        start = time.time()
        extractor = OcrQuestionExtractor()
        end = time.time()
        
        # 初始化应该在 1 秒内完成
        assert (end - start) < 1.0
    
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_image_extractor_initialization_time(self, mock_client):
        """测试图片提取器初始化时间"""
        import time
        
        # Mock ModelClient
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        start = time.time()
        extractor = ImageExtractor()
        end = time.time()
        
        # 初始化应该在 1 秒内完成
        assert (end - start) < 1.0


# ========== 边界条件测试 ==========

class TestEdgeCases:
    """边界条件测试"""
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_empty_config(self, mock_paddle):
        """测试 OCR 服务空配置"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        config = {}
        service = OcrService(config)
        
        # 应该使用默认配置
        assert service is not None
        assert service.preferred_engine == "paddle"
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_none_config(self, mock_llm, mock_ocr):
        """测试 OCR 提取器 None 配置"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        extractor = OcrQuestionExtractor(None, None)
        
        # 应该使用默认配置
        assert extractor is not None
        assert extractor.ocr_service is not None
    
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_image_extractor_nonexistent_image(self, mock_client):
        """测试图片提取器处理不存在的图片"""
        # Mock ModelClient
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        extractor = ImageExtractor()
        
        with pytest.raises(FileNotFoundError):
            extractor.extract("nonexistent_image.png")
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    @patch('agent.services.ocr_service.TesseractOcrEngine')
    def test_ocr_service_fallback_to_next_engine(self, mock_tesseract, mock_paddle):
        """测试 OCR 服务引擎降级"""
        # Mock PaddleOcrEngine 不可用
        mock_paddle_engine = Mock()
        mock_paddle_engine.name = "paddle"
        mock_paddle_engine.is_available.return_value = False
        mock_paddle.return_value = mock_paddle_engine
        
        # Mock TesseractOcrEngine 可用
        mock_tesseract_engine = Mock()
        mock_tesseract_engine.name = "tesseract"
        mock_tesseract_engine.is_available.return_value = True
        mock_tesseract_engine.recognize.return_value = "测试文字"
        mock_tesseract.return_value = mock_tesseract_engine
        
        config = {"enabled": True, "engine": "paddle", "fallback_engines": ["tesseract"]}
        service = OcrService(config)
        
        # 应该降级到 tesseract 引擎
        assert service.current_engine == "tesseract"
        
        result = service.recognize("test.png")
        assert result == "测试文字"


# ========== 错误处理测试 ==========

class TestErrorHandling:
    """错误处理测试"""
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_recognize_error(self, mock_paddle):
        """测试 OCR 识别错误"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_engine.recognize.side_effect = Exception("识别失败")
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        with pytest.raises(Exception, match="识别失败"):
            service.recognize("test.png")
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_recognize_with_confidence_error(self, mock_paddle):
        """测试带置信度识别错误"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_engine.recognize.side_effect = Exception("识别失败")
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        # 应该返回错误信息而不是抛出异常
        result = service.recognize_with_confidence("test.png")
        assert result["text"] == ""
        assert result["confidence"] == 0.0
        assert "error" in result
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_llm_error(self, mock_llm, mock_ocr, temp_image_file):
        """测试 LLM 错误处理"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.recognize_with_confidence.return_value = {
            "text": "测试题目",
            "confidence": 0.9
        }
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端抛出异常
        mock_llm_instance = Mock()
        mock_llm_instance.chat.side_effect = Exception("LLM 调用失败")
        mock_llm.return_value = mock_llm_instance
        
        extractor = OcrQuestionExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result["questions"] == []
        assert result["total_count"] == 0
        assert "error" in result
    
    @patch('agent.extractors.image_extractor.ModelClient')
    @patch('agent.extractors.image_extractor.OcrQuestionExtractor')
    def test_image_extractor_both_vision_and_ocr_fail(self, mock_ocr_extractor, mock_client, temp_image_file):
        """测试视觉模型和 OCR 都失败"""
        # Mock ModelClient - 视觉模型失败
        mock_client_instance = Mock()
        mock_client_instance.chat_with_images.side_effect = Exception("API 失败")
        mock_client.return_value = mock_client_instance
        
        # Mock OCR 提取器也失败
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract.side_effect = Exception("OCR 失败")
        mock_ocr_extractor.return_value = mock_ocr_instance
        
        extractor = ImageExtractor()
        result = extractor.extract(temp_image_file)
        
        assert result["questions"] == []
        assert result["total_count"] == 0
        assert "error" in result
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    @patch('agent.services.ocr_service.TesseractOcrEngine')
    def test_paddle_ocr_engine_not_initialized(self, mock_tesseract, mock_paddle):
        """测试 PaddleOCR 引擎未初始化"""
        # Mock PaddleOcrEngine 不可用
        mock_paddle_engine = Mock()
        mock_paddle_engine.name = "paddle"
        mock_paddle_engine.is_available.return_value = False
        mock_paddle.return_value = mock_paddle_engine
        
        # Mock TesseractOcrEngine 也不可用
        mock_tesseract_engine = Mock()
        mock_tesseract_engine.name = "tesseract"
        mock_tesseract_engine.is_available.return_value = False
        mock_tesseract.return_value = mock_tesseract_engine
        
        config = {"enabled": True, "engine": "paddle", "fallback_engines": ["tesseract"]}
        
        # 应该抛出 RuntimeError
        with pytest.raises(RuntimeError, match="没有可用的 OCR 引擎"):
            OcrService(config)
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_close(self, mock_paddle):
        """测试 OCR 服务关闭"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        service = OcrService(config)
        
        # close() 应该不抛出异常
        service.close()
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_close(self, mock_llm, mock_ocr):
        """测试 OCR 提取器关闭"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        extractor = OcrQuestionExtractor()
        
        # close() 应该不抛出异常
        extractor.close()
    
    @patch('agent.extractors.image_extractor.ModelClient')
    def test_image_extractor_close(self, mock_client):
        """测试图片提取器关闭"""
        # Mock ModelClient
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        extractor = ImageExtractor()
        
        # close() 应该不抛出异常
        extractor.close()
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_context_manager(self, mock_paddle):
        """测试 OCR 服务上下文管理器"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        config = {"enabled": True, "engine": "paddle", "lang": "ch"}
        
        with OcrService(config) as service:
            assert service is not None
        
        # 退出上下文后应该自动关闭
    
    @patch('agent.extractors.ocr_question_extractor.OcrService')
    @patch('agent.extractors.ocr_question_extractor.ModelClient')
    def test_ocr_extractor_context_manager(self, mock_llm, mock_ocr):
        """测试 OCR 提取器上下文管理器"""
        # Mock OCR 服务
        mock_ocr_instance = Mock()
        mock_ocr_instance.current_engine = "paddle"
        mock_ocr.return_value = mock_ocr_instance
        
        # Mock LLM 客户端
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        with OcrQuestionExtractor() as extractor:
            assert extractor is not None
        
        # 退出上下文后应该自动关闭
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    @patch('agent.services.ocr_service.TesseractOcrEngine')
    def test_ocr_service_unknown_engine_type(self, mock_tesseract, mock_paddle):
        """测试未知引擎类型"""
        # Mock PaddleOcrEngine 不可用
        mock_paddle_engine = Mock()
        mock_paddle_engine.name = "paddle"
        mock_paddle_engine.is_available.return_value = False
        mock_paddle.return_value = mock_paddle_engine
        
        # Mock TesseractOcrEngine 可用
        mock_tesseract_engine = Mock()
        mock_tesseract_engine.name = "tesseract"
        mock_tesseract_engine.is_available.return_value = True
        mock_tesseract.return_value = mock_tesseract_engine
        
        config = {"enabled": True, "engine": "unknown_engine", "fallback_engines": ["tesseract"]}
        service = OcrService(config)
        
        # 应该降级到备选引擎
        assert service is not None
        assert service.current_engine == "tesseract"
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_tesseract_engine_creation(self, mock_paddle):
        """测试 Tesseract 引擎创建"""
        # Mock PaddleOcrEngine 不可用
        mock_paddle_engine = Mock()
        mock_paddle_engine.name = "paddle"
        mock_paddle_engine.is_available.return_value = False
        mock_paddle.return_value = mock_paddle_engine
        
        with patch('agent.services.ocr_service.TesseractOcrEngine') as mock_tesseract:
            mock_tesseract_engine = Mock()
            mock_tesseract_engine.name = "tesseract"
            mock_tesseract_engine.is_available.return_value = True
            mock_tesseract.return_value = mock_tesseract_engine
            
            config = {"enabled": True, "engine": "paddle", "fallback_engines": ["tesseract"]}
            service = OcrService(config)
            
            assert service.current_engine == "tesseract"
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_language_mapping_chinese(self, mock_paddle):
        """测试中文语言映射"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        # 测试不同中文语言代码
        for lang_code in ["ch", "chi_sim", "chi_tra", "zh", "zh-CN"]:
            config = {"enabled": True, "engine": "paddle", "lang": lang_code}
            service = OcrService(config)
            assert service is not None
    
    @patch('agent.services.ocr_service.PaddleOcrEngine')
    def test_ocr_service_language_mapping_english(self, mock_paddle):
        """测试英文语言映射"""
        # Mock PaddleOcrEngine
        mock_engine = Mock()
        mock_engine.name = "paddle"
        mock_engine.is_available.return_value = True
        mock_paddle.return_value = mock_engine
        
        # 测试英文语言代码
        for lang_code in ["en", "eng"]:
            config = {"enabled": True, "engine": "paddle", "lang": lang_code}
            service = OcrService(config)
            assert service is not None
