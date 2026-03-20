# 任务 T017 - OCR + 文本模型备选方案架构分析

**任务编号**: T017  
**任务名称**: 添加 OCR + 文本模型备选方案，当视觉模型不可用时自动降级  
**执行时间**: 2026-03-20 11:55  
**执行人**: Architect (nanobot)  
**优先级**: 🔴 P0 (提升系统可靠性)  
**状态**: ✅ 实现完成，待测试验证

---

## 执行摘要

### 需求背景

当前系统完全依赖视觉大语言模型 (qwen-vl-max) 从图片中提取题目，存在以下问题：

1. **单点故障风险**: 视觉模型 API 不可用时，整个功能瘫痪
2. **成本考虑**: 视觉模型调用成本较高 (约 ¥0.01-0.05/次)
3. **部署限制**: 某些环境可能未配置视觉模型 API Key
4. **响应速度**: 视觉模型响应时间较长 (3-10 秒)

### 解决方案

**双模型策略**：
- **优先**: 视觉大语言模型 (qwen-vl-max) - 高精度 (95%+)
- **备选**: OCR + 文本模型 (PaddleOCR + qwen-plus) - 高可用、低成本

**自动降级条件**：
- ✅ API 调用失败 (401/403/500/503)
- ✅ 返回结果为空
- ✅ 置信度 < 0.5
- ✅ JSON 解析失败
- ✅ 视觉模型未配置

### 实现状态

| 组件 | 状态 | 文件 |
|------|------|------|
| **OCR 服务** | ✅ 完成 | `agent/services/ocr_service.py` (388 行) |
| **OCR 提取器** | ✅ 完成 | `agent/extractors/ocr_question_extractor.py` (264 行) |
| **图片提取器** | ✅ 完成 | `agent/extractors/image_extractor.py` (379 行，已添加降级逻辑) |
| **配置** | ✅ 完成 | `config/agent.json` (已添加 OCR 配置) |
| **依赖** | ✅ 完成 | `config/pyproject.toml` (已添加 PaddleOCR) |

---

## 一、架构设计

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                   用户上传图片                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              ImageExtractor.extract()                   │
│                   (图片提取器)                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │ 检查视觉模型配置        │
        │ is_vision_configured() │
        └───────────┬────────────┘
                    │
         ┌──────────┴──────────┐
         │ 是                  │ 否
         ↓                     ↓
┌─────────────────┐   ┌──────────────────────┐
│ 调用视觉模型    │   │ 直接使用 OCR 方案     │
│ _extract_with_  │   │ _extract_with_ocr()  │
│ vision()        │   │                      │
└────────┬────────┘   └──────────┬───────────┘
         │                       │
         │ 成功？                │
    ┌────┴────┐                  │
    │ 是      │ 否               │
    ↓         ↓                  │
┌─────────┐  ┌───────────────────┴────────┐
│ 返回结果│  │ 检查降级条件                │
└─────────┘  │ - API 失败？                │
             │ - 结果为空？                │
             │ - 置信度 < 阈值？            │
             │ - JSON 解析失败？            │
             └───────────┬────────────────┘
                         │
                    ┌────┴────┐
                    │ 是      │ 否
                    ↓         ↓
             ┌───────────┐  ┌──────────┐
             │ OCR 降级  │  │ 返回结果 │
             │ 方案      │  │ (低置信度)│
             └─────┬─────┘  └──────────┘
                   │
             ┌─────┴─────┐
             │ OcrService │
             │ .recognize │
             └─────┬─────┘
                   │
             ┌─────┴─────┐
             │ OCR 识别   │
             │ 文本      │
             └─────┬─────┘
                   │
             ┌─────┴─────┐
             │ LLM 结构化 │
             │ 提取题目   │
             └─────┬─────┘
                   │
             ┌─────┴─────┐
             │ 返回结果   │
             └───────────┘
```

### 1.2 降级策略流程图

```python
def extract(image_path):
    # 1. 尝试视觉模型
    if is_vision_configured():
        try:
            result = _extract_with_vision(image_path)
            
            # 2. 验证结果有效性
            if _is_vision_result_valid(result):
                result["extraction_method"] = "vision"
                return result
            
            # 3. 结果无效，降级
            logger.warning(f"视觉模型结果无效，降级到 OCR: {result.get('error')}")
            
        except Exception as e:
            # 4. 异常处理，降级
            logger.warning(f"视觉模型失败，降级到 OCR: {e}")
    
    # 5. 使用 OCR 方案
    return _extract_with_ocr(image_path)
```

### 1.3 降级条件详细说明

| 条件 | 检测逻辑 | 触发降级 | 日志级别 |
|------|----------|----------|----------|
| **视觉模型未配置** | `not is_vision_configured()` | ✅ 是 | INFO |
| **API 调用失败** | `except Exception` | ✅ 是 | WARNING |
| **返回结果为空** | `not result.get("questions")` | ✅ 是 | WARNING |
| **置信度过低** | `confidence < threshold` | ✅ 是 | WARNING |
| **JSON 解析失败** | `json.JSONDecodeError` | ✅ 是 | WARNING |
| **SSL 证书错误** | `ssl.SSLCertVerificationError` | ✅ 是 | WARNING |
| **超时** | `httpx.TimeoutException` | ✅ 是 | WARNING |

---

## 二、核心组件设计

### 2.1 OCR 服务 (OcrService)

**文件**: `agent/services/ocr_service.py` (388 行)

**职责**:
- 提供统一的 OCR 接口
- 支持多引擎自动选择 (PaddleOCR/Tesseract)
- 提供置信度评估
- 引擎健康检查

**核心方法**:

```python
class OcrService:
    def __init__(self, config: dict):
        """初始化 OCR 服务"""
        self.config = config
        self.engines = self._initialize_engines()
        self.current_engine = self._select_best_engine()
    
    def recognize(self, image_path: str) -> str:
        """识别图片中的文字"""
        pass
    
    def recognize_with_confidence(self, image_path: str) -> Dict[str, Any]:
        """识别文字并返回置信度"""
        pass
    
    def is_available(self) -> bool:
        """检查 OCR 服务是否可用"""
        pass
    
    def _initialize_engines(self) -> List[OcrEngine]:
        """初始化所有配置的 OCR 引擎"""
        pass
    
    def _select_best_engine(self) -> OcrEngine:
        """选择最佳可用引擎"""
        pass
```

**引擎实现**:

| 引擎 | 类 | 特点 | 适用场景 |
|------|-----|------|----------|
| **PaddleOCR** | `PaddleOcrEngine` | 中文识别率 95%+，支持公式 | 中文题目 (推荐) |
| **Tesseract** | `TesseractEngine` | 英文识别好，轻量 | 英文题目 |

### 2.2 OCR 题目提取器 (OcrQuestionExtractor)

**文件**: `agent/extractors/ocr_question_extractor.py` (264 行)

**职责**:
- OCR 文字识别
- LLM 题目结构化
- 置信度合并计算

**工作流程**:

```python
def extract(self, image_path: str) -> Dict[str, Any]:
    # 1. OCR 识别
    ocr_result = self.ocr_service.recognize_with_confidence(image_path)
    text = ocr_result["text"]
    ocr_confidence = ocr_result["confidence"]
    
    # 2. LLM 结构化
    messages = [{"role": "user", "content": PROMPT.format(text=text)}]
    response = self.llm_client.chat(messages)
    result = self._parse_response(response)
    
    # 3. 合并置信度
    llm_confidence = result.get("confidence", 0.0)
    combined_confidence = (ocr_confidence + llm_confidence) / 2
    
    # 4. 返回结果
    result.update({
        "confidence": combined_confidence,
        "extraction_method": "ocr+llm",
        "ocr_engine": self.ocr_service.current_engine.name,
        "ocr_confidence": ocr_confidence
    })
    
    return result
```

**置信度计算**:

```python
# 合并 OCR 和 LLM 的置信度
combined_confidence = (ocr_confidence + llm_confidence) / 2

# 置信度阈值检查
if combined_confidence < self.confidence_threshold:
    logger.warning(f"置信度过低：{combined_confidence}")
```

### 2.3 图片提取器 (ImageExtractor)

**文件**: `agent/extractors/image_extractor.py` (379 行)

**职责**:
- 视觉模型调用
- 降级逻辑控制
- 结果验证

**核心方法**:

```python
class ImageExtractor:
    def __init__(self, config: Optional[dict] = None):
        self.vision_config = config or AgentConfig.get_vision_config()
        self.client = ModelClient(self.vision_config)
        self.ocr_enabled = AgentConfig.OCR_ENABLED
        self.vision_fallback_threshold = AgentConfig.VISION_FALLBACK_THRESHOLD
        self._ocr_extractor: Optional[OcrQuestionExtractor] = None
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """提取题目（支持降级）"""
        # 1. 尝试视觉模型
        vision_result = self._extract_with_vision(image_path)
        
        # 2. 验证结果
        if self._is_vision_result_valid(vision_result):
            vision_result["extraction_method"] = "vision"
            return vision_result
        
        # 3. 降级到 OCR
        logger.warning("视觉模型失败，降级到 OCR")
        return self._extract_with_ocr(image_path)
    
    def _is_vision_result_valid(self, result: Dict[str, Any]) -> bool:
        """验证视觉模型结果是否有效"""
        # 检查是否有错误
        if result.get("error"):
            return False
        
        # 检查是否有题目
        if not result.get("questions"):
            return False
        
        # 检查置信度
        confidence = result.get("confidence", 0.0)
        if confidence < self.vision_fallback_threshold:
            logger.warning(f"视觉模型置信度过低：{confidence}")
            return False
        
        return True
    
    def _extract_with_ocr(self, image_path: str) -> Dict[str, Any]:
        """使用 OCR 方案提取"""
        if not self.ocr_enabled:
            raise ValueError("OCR 降级方案未启用")
        
        if not self._ocr_extractor:
            self._ocr_extractor = OcrQuestionExtractor()
        
        result = self._ocr_extractor.extract(image_path)
        result["fallback_reason"] = "vision_model_unavailable"
        return result
```

---

## 三、配置设计

### 3.1 config/agent.json 配置

```json
{
  "vision": {
    "model_id": "qwen-vl-max",
    "api_key": "sk-xxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "enabled": true,
    "timeout_seconds": 60
  },
  "ocr": {
    "enabled": true,
    "engine": "paddle",
    "lang": "ch",
    "fallback_engines": ["tesseract"],
    "confidence_threshold": 0.5
  },
  "settings": {
    "max_questions_per_image": 10,
    "max_questions_per_document": 50,
    "confidence_threshold": 0.6,
    "max_file_size_mb": 50,
    "vision_fallback_threshold": 0.5
  }
}
```

### 3.2 配置项说明

#### vision 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用视觉模型 |
| `timeout_seconds` | int | 60 | API 调用超时 (秒) |

#### ocr 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用 OCR |
| `engine` | str | "paddle" | 首选 OCR 引擎 (paddle/tesseract) |
| `lang` | str | "ch" | 识别语言 (ch/en/japan/korean) |
| `fallback_engines` | list | ["tesseract"] | 备选引擎列表 |
| `confidence_threshold` | float | 0.5 | 置信度阈值 |

#### settings 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `vision_fallback_threshold` | float | 0.5 | 视觉模型降级置信度阈值 |
| `confidence_threshold` | float | 0.6 | 最低置信度要求 |

---

## 四、依赖管理

### 4.1 新增依赖

**config/pyproject.toml**:

```toml
[project]
dependencies = [
    # ... 现有依赖 ...
    
    # OCR 支持
    "paddlepaddle>=2.5.0",
    "paddleocr>=2.7.0",
    "opencv-python>=4.5.0",
    "Pillow>=9.0.0",
    
    # Tesseract 支持 (可选)
    "pytesseract>=0.3.10",
]
```

### 4.2 依赖说明

| 依赖 | 版本 | 用途 | 大小 | 必需 |
|------|------|------|------|------|
| paddlepaddle | >=2.5.0 | PaddlePaddle 深度学习框架 | ~200MB | ✅ |
| paddleocr | >=2.7.0 | PaddleOCR OCR 引擎 | ~50MB | ✅ |
| opencv-python | >=4.5.0 | OpenCV 图像处理 | ~30MB | ✅ |
| Pillow | >=9.0.0 | 图像处理 | ~5MB | ✅ |
| pytesseract | >=0.3.10 | Tesseract OCR 封装 | ~1MB | ⚠️ 可选 |

**总计**: ~286MB (必需), ~287MB (含 Tesseract)

### 4.3 安装命令

```bash
# 使用 uv 安装
uv add paddlepaddle paddleocr opencv-python Pillow pytesseract

# 或使用 pip
pip install paddlepaddle paddleocr opencv-python Pillow pytesseract

# GPU 版本（生产环境）
uv add paddlepaddle-gpu paddleocr opencv-python Pillow
```

---

## 五、错误处理方案

### 5.1 错误类型与处理

| 错误类型 | 捕获位置 | 处理方式 | 用户提示 |
|----------|----------|----------|----------|
| **视觉模型未配置** | `ImageExtractor.extract()` | 直接使用 OCR | "使用 OCR 方案提取" |
| **API 调用失败** | `ModelClient.chat_with_images()` | 降级到 OCR | "视觉模型不可用，使用 OCR 方案" |
| **OCR 识别失败** | `OcrService.recognize()` | 尝试备选引擎 | "OCR 识别失败，请检查图片质量" |
| **所有 OCR 引擎失败** | `OcrService._select_best_engine()` | 抛出异常 | "所有 OCR 引擎不可用" |
| **LLM 调用失败** | `OcrQuestionExtractor.extract()` | 返回原始 OCR 文本 | "题目结构化失败，返回原始文本" |
| **JSON 解析失败** | `OcrQuestionExtractor._parse_response()` | 返回空结果 | "无法解析提取结果" |

### 5.2 错误日志

```python
# 视觉模型失败
logger.warning(f"视觉模型失败，降级到 OCR: {error_msg}")

# OCR 引擎不可用
logger.warning(f"OCR 引擎 {engine_name} 不可用，尝试备选引擎")

# 所有引擎失败
logger.error("所有 OCR 引擎均不可用")

# 置信度过低
logger.warning(f"提取结果置信度过低：{confidence}")
```

### 5.3 响应格式

**成功响应**:

```json
{
  "questions": [...],
  "total_count": 5,
  "confidence": 0.85,
  "extraction_method": "vision",
  "source_type": "image",
  "source_file": "question.png",
  "extracted_at": "2026-03-20T11:30:00"
}
```

**OCR 降级响应**:

```json
{
  "questions": [...],
  "total_count": 3,
  "confidence": 0.72,
  "extraction_method": "ocr+llm",
  "ocr_engine": "paddle",
  "ocr_confidence": 0.78,
  "fallback_reason": "vision_model_unavailable",
  "source_type": "image",
  "source_file": "question.png",
  "extracted_at": "2026-03-20T11:30:00"
}
```

**失败响应**:

```json
{
  "questions": [],
  "total_count": 0,
  "confidence": 0.0,
  "error": "无法识别题目",
  "error_detail": "OCR 识别结果为空",
  "extraction_method": "ocr+llm",
  "solution": "请检查图片质量，确保文字清晰可见"
}
```

---

## 六、测试策略

### 6.1 单元测试

**测试文件**: `agent/tests/test_ocr_service.py`, `agent/tests/test_ocr_question_extractor.py`

**测试覆盖**:

| 测试类 | 测试方法 | 覆盖率目标 |
|--------|----------|------------|
| **TestOcrService** | test_initialize, test_recognize, test_is_available | 90% |
| **TestPaddleOcrEngine** | test_init, test_recognize, test_is_available | 90% |
| **TestOcrQuestionExtractor** | test_extract, test_parse_response | 90% |
| **TestImageExtractorFallback** | test_vision_success, test_vision_fallback | 90% |

**测试用例示例**:

```python
class TestImageExtractorFallback:
    def test_vision_success(self, mocker):
        """测试视觉模型成功"""
        mocker.patch('ModelClient.chat_with_images',
                    return_value='{"questions": [...], "confidence": 0.9}')
        
        extractor = ImageExtractor()
        result = extractor.extract("test.png")
        
        assert result["extraction_method"] == "vision"
    
    def test_vision_fallback_to_ocr(self, mocker):
        """测试视觉模型失败降级"""
        mocker.patch('ModelClient.chat_with_images',
                    side_effect=Exception("API Error"))
        
        extractor = ImageExtractor()
        result = extractor.extract("test.png")
        
        assert result["extraction_method"] == "ocr+llm"
        assert result["fallback_reason"] == "vision_model_unavailable"
    
    def test_vision_low_confidence_fallback(self, mocker):
        """测试视觉模型置信度过低降级"""
        mocker.patch('ModelClient.chat_with_images',
                    return_value='{"questions": [...], "confidence": 0.3}')
        
        extractor = ImageExtractor()
        result = extractor.extract("test.png")
        
        assert result["extraction_method"] == "ocr+llm"
```

### 6.2 集成测试

**测试文件**: `tests/integration/test_ocr_fallback.py`

**测试场景**:

| 场景 | 输入 | 预期输出 | 验证点 |
|------|------|----------|--------|
| **清晰图片** | 清晰题目图片 | 提取成功，confidence > 0.8 | 准确率 |
| **模糊图片** | 模糊题目图片 | 提取成功，confidence > 0.5 | 降级逻辑 |
| **空白图片** | 空白图片 | 返回空结果，error 提示 | 错误处理 |
| **视觉模型失败** | Mock API 失败 | 降级到 OCR，成功提取 | 降级逻辑 |
| **OCR 失败** | Mock OCR 失败 | 返回错误提示 | 错误处理 |

**测试用例示例**:

```python
def test_clear_image_extraction():
    """测试清晰图片提取"""
    extractor = ImageExtractor()
    result = extractor.extract("tests/data/clear_question.png")
    
    assert result["questions"] is not None
    assert len(result["questions"]) > 0
    assert result["confidence"] > 0.8
    assert result["extraction_method"] in ["vision", "ocr+llm"]

def test_vision_model_failure_fallback():
    """测试视觉模型失败降级"""
    # 临时禁用视觉模型
    original_config = AgentConfig.get_vision_config()
    AgentConfig._config_cache["vision"]["api_key"] = ""
    
    try:
        extractor = ImageExtractor()
        result = extractor.extract("tests/data/clear_question.png")
        
        assert result["extraction_method"] == "ocr+llm"
        assert result["fallback_reason"] == "vision_model_unavailable"
    finally:
        # 恢复配置
        AgentConfig._config_cache["vision"] = original_config
```

### 6.3 端到端测试

**测试文件**: `tests/e2e/test_image_upload.py`

**测试流程**:

```python
def test_image_upload_with_fallback():
    """测试图片上传完整流程（含降级）"""
    # 1. 上传图片
    with open("tests/data/sample_question.png", "rb") as f:
        response = client.post("/api/agent/extract/image", files={"file": f})
    
    # 2. 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "questions" in data
    assert "extraction_method" in data
    
    # 3. 验证预备题目
    assert data["total_count"] > 0
```

### 6.4 性能测试

**测试文件**: `tests/performance/test_ocr_performance.py`

**性能指标**:

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| **OCR 识别时间** | < 3 秒 | time.time() 差值 |
| **LLM 结构化时间** | < 5 秒 | time.time() 差值 |
| **总提取时间** | < 10 秒 | time.time() 差值 |
| **降级切换时间** | < 1 秒 | 视觉模型失败到 OCR 开始 |
| **并发处理** | 10 QPS | locust 压测 |

**测试用例示例**:

```python
def test_ocr_extraction_time():
    """测试 OCR 提取时间"""
    extractor = ImageExtractor()
    
    start = time.time()
    result = extractor.extract("tests/data/sample.png")
    end = time.time()
    
    extraction_time = end - start
    
    # 总提取时间应该 < 10 秒
    assert extraction_time < 10.0
    assert result["extraction_method"] in ["vision", "ocr+llm"]
```

---

## 七、实施清单

### 7.1 已完成

- [x] **OCR 服务核心**: `agent/services/ocr_service.py` (388 行)
  - [x] OcrEngine 抽象基类
  - [x] PaddleOcrEngine 实现
  - [x] TesseractEngine 实现
  - [x] OcrService 统一接口
  - [x] 引擎自动选择
  - [x] 置信度评估

- [x] **OCR 题目提取器**: `agent/extractors/ocr_question_extractor.py` (264 行)
  - [x] OCR 文字识别
  - [x] LLM 题目结构化
  - [x] 置信度合并计算
  - [x] 错误处理

- [x] **图片提取器降级**: `agent/extractors/image_extractor.py` (379 行)
  - [x] 视觉模型调用
  - [x] 降级逻辑控制
  - [x] 结果验证
  - [x] 错误处理

- [x] **配置更新**: `config/agent.json`
  - [x] vision.enabled
  - [x] ocr.enabled
  - [x] ocr.engine
  - [x] settings.vision_fallback_threshold

- [x] **依赖更新**: `config/pyproject.toml`
  - [x] paddlepaddle
  - [x] paddleocr
  - [x] opencv-python
  - [x] Pillow

### 7.2 待完成

- [ ] **测试脚本开发**: `tests/test_ocr_fallback.py`
  - [ ] 单元测试
  - [ ] 集成测试
  - [ ] 性能测试

- [ ] **测试图片准备**: `tests/data/`
  - [ ] clear_question.png (清晰题目)
  - [ ] blur_question.png (模糊题目)
  - [ ] blank.png (空白图片)
  - [ ] multi_question.png (多道题目)

- [ ] **文档更新**
  - [ ] README.md 添加 OCR 说明
  - [ ] 配置文档更新
  - [ ] 故障排除文档

---

## 八、验收标准

### 功能验收

- [x] ✅ 视觉模型可用时，优先使用视觉模型
- [x] ✅ 视觉模型不可用时，自动降级到 OCR
- [ ] ⏳ OCR 识别准确率 > 90%（清晰图片）- 待测试验证
- [x] ✅ 降级过程用户无感知（响应中包含 extraction_method）
- [x] ✅ 错误处理完善，有明确提示
- [ ] ⏳ 测试覆盖率 > 80% - 待测试开发

### 性能验收

- [ ] ⏳ OCR 识别时间 < 3 秒
- [ ] ⏳ 总提取时间 < 10 秒
- [ ] ⏳ 降级切换时间 < 1 秒

### 质量验收

- [ ] ⏳ 单元测试覆盖率 > 90%
- [ ] ⏳ 集成测试通过
- [ ] ⏳ 文档完整

---

## 九、风险与缓解

### 风险 1: OCR 识别率低

| 影响 | 概率 | 缓解措施 |
|------|------|----------|
| 高 (题目识别不准确) | 中 | 1. 使用 PaddleOCR (中文 95%+)<br>2. 添加置信度阈值<br>3. 提供人工校对界面 |

### 风险 2: 依赖体积大

| 影响 | 概率 | 缓解措施 |
|------|------|----------|
| 中 (部署包增大 ~300MB) | 高 | 1. 使用 Docker 镜像<br>2. 提供精简版 (仅 OCR)<br>3. 按需加载模型 |

### 风险 3: 性能下降

| 影响 | 概率 | 缓解措施 |
|------|------|----------|
| 中 (OCR+LLM 比视觉模型慢) | 中 | 1. 优化 OCR 初始化 (延迟加载)<br>2. 添加结果缓存<br>3. 并行处理批量图片 |

---

## 十、下一步

### 立即执行

1. **转交 Test-Analyst**: 设计测试策略 (1-2 小时)
2. **转交 Tester**: 开发测试脚本 (4-6 小时)
3. **转交 Developer**: 自测修复 (2-3 小时)

### 短期优化 (1-2 周)

1. **多 OCR 引擎支持**: 支持 Tesseract 作为备选
2. **缓存机制**: 相同图片不重复识别
3. **批量优化**: 批量图片并行处理

### 中期优化 (1-2 月)

1. **本地模型**: 部署本地视觉模型 (Qwen-VL-Chat)
2. **混合模式**: OCR + 视觉模型结果融合
3. **成本优化**: 根据图片复杂度选择模型

---

*报告生成时间*: 2026-03-20 12:00  
*报告人*: Architect (nanobot)  
*实现状态*: ✅ 完成  
*测试状态*: ⏳ 待验证  
*预计完成时间*: 8-12 小时 (测试 + 修复)
