# 任务 T016 - OCR + 文本模型备选方案技术方案

**任务编号**: T016  
**任务名称**: 添加 OCR + 文本模型备选方案  
**执行时间**: 2026-03-20 11:15  
**执行人**: Architect (nanobot)  
**优先级**: 🔴 P0 (提升系统可靠性)  
**需求来源**: 用户希望图片上传功能不依赖视觉大语言模型

---

## 执行摘要

### 需求背景

当前系统完全依赖视觉大语言模型 (qwen-vl-max) 从图片中提取题目，存在以下问题：

1. **单点故障风险**: 视觉模型 API 不可用时，整个功能瘫痪
2. **成本考虑**: 视觉模型调用成本较高
3. **网络依赖**: 需要稳定的网络连接
4. **响应速度**: 视觉模型响应时间较长 (3-10 秒)

### 解决方案

引入 **双模型策略**：
- **优先**: 视觉大语言模型 (高精度)
- **备选**: OCR + 文本模型 (高可用、低成本)

### 技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| **OCR 引擎** | PaddleOCR | 中文识别准确率高、支持多种语言、离线可用 |
| **文本模型** | qwen-plus (已有) | 复用现有配置、成本低、响应快 |
| **降级策略** | 自动降级 | 视觉模型失败时自动切换 OCR |

---

## 一、双模型策略设计

### 1.1 策略流程图

```
用户上传图片
    ↓
检查视觉模型配置
    ↓
┌─────────────────┐
│ 视觉模型可用？   │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 是      │ 否
    ↓         ↓
┌─────────┐  ┌──────────────┐
│ 调用视觉 │  │ 使用 OCR 方案 │
│ 模型    │  │              │
└────┬────┘  └─────┬────────┘
     │             │
     │  成功？     │
     └──┬──┘       │
     ┌──┴──┐       │
     │ 是  │ 否    │
     ↓     ↓       │
┌─────────┐  ┌─────┴────────┐
│ 返回结果│  │ 自动降级到   │
└─────────┘  │ OCR + 文本模型│
             └─────┬────────┘
                   │
             ┌─────┴─────┐
             │ OCR 识别   │
             │ 文本      │
             └─────┬─────┘
                   │
             ┌─────┴─────┐
             │ 文本模型   │
             │ 结构化    │
             └─────┬─────┘
                   │
             ┌─────┴─────┐
             │ 返回结果   │
             └───────────┘
```

### 1.2 降级条件

| 条件 | 触发降级 | 说明 |
|------|----------|------|
| **视觉模型未配置** | ✅ 是 | API Key 为空或占位符 |
| **API 调用失败** | ✅ 是 | 401/403/500/503 错误 |
| **网络连接失败** | ✅ 是 | 超时、DNS 解析失败 |
| **SSL 证书错误** | ✅ 是 | 证书验证失败 |
| **模型不可用** | ✅ 是 | 模型不存在或未开通 |
| **成本考虑** | ⚠️ 可选 | 用户手动选择 OCR 模式 |
| **响应超时** | ✅ 是 | > 30 秒未响应 |

### 1.3 优先级策略

```python
# 伪代码
def extract_from_image(image_path):
    # 1. 检查视觉模型配置
    if vision_model_configured():
        try:
            # 2. 尝试视觉模型
            result = call_vision_model(image_path)
            if result.success and result.confidence > 0.6:
                return result
        except APIError as e:
            log.warning(f"视觉模型失败：{e}")
            # 3. 自动降级到 OCR
            return extract_with_ocr(image_path)
    
    # 4. 视觉模型未配置，直接使用 OCR
    return extract_with_ocr(image_path)
```

---

## 二、OCR 引擎选型分析

### 2.1 候选引擎对比

| 特性 | PaddleOCR | Tesseract | EasyOCR |
|------|-----------|-----------|---------|
| **中文准确率** | ⭐⭐⭐⭐⭐ 95%+ | ⭐⭐⭐ 80% | ⭐⭐⭐⭐ 90% |
| **英文准确率** | ⭐⭐⭐⭐⭐ 95%+ | ⭐⭐⭐⭐⭐ 95%+ | ⭐⭐⭐⭐ 92% |
| **多语言支持** | 80+ 语言 | 100+ 语言 | 80+ 语言 |
| **离线使用** | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| **安装复杂度** | 中等 | 简单 | 简单 |
| **模型大小** | ~200MB | ~100MB | ~300MB |
| **识别速度** | 快 (0.5-2s) | 中 (1-3s) | 中 (1-3s) |
| **公式支持** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **表格支持** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **维护活跃度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **文档质量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### 2.2 选型结论

**推荐：PaddleOCR**

**理由**:
1. **中文识别率最高**: 对中文题目识别效果最佳
2. **公式支持好**: 支持 LaTeX 公式识别
3. **表格支持**: 能识别表格结构
4. **百度背书**: 持续维护，社区活跃
5. **文档完善**: 中文文档详细，易于集成

### 2.3 PaddleOCR 安装

```bash
# 基础安装
pip install paddlepaddle paddleocr

# 或使用 uv
uv add paddlepaddle paddleocr

# CPU 版本 (推荐开发环境)
pip install paddlepaddle

# GPU 版本 (生产环境)
pip install paddlepaddle-gpu
```

---

## 三、配置设计

### 3.1 config/agent.json 新增配置

```json
{
  "vision": {
    "model_id": "qwen-vl-max",
    "api_key": "sk-xxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "enabled": true,
    "timeout": 30,
    "fallback_to_ocr": true
  },
  "ocr": {
    "engine": "paddleocr",
    "enabled": true,
    "lang": "ch",
    "use_gpu": false,
    "show_log": false,
    "det_model_dir": null,
    "rec_model_dir": null,
    "max_text_length": 5000,
    "confidence_threshold": 0.6
  },
  "extraction_strategy": {
    "prefer_vision": true,
    "auto_fallback": true,
    "vision_timeout": 30,
    "max_retries": 2,
    "cost_optimization": false
  }
}
```

### 3.2 配置项说明

#### vision 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用视觉模型 |
| `timeout` | int | 30 | API 调用超时 (秒) |
| `fallback_to_ocr` | bool | true | 失败时是否降级到 OCR |

#### ocr 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `engine` | str | "paddleocr" | OCR 引擎 (paddleocr/tesseract) |
| `enabled` | bool | true | 是否启用 OCR |
| `lang` | str | "ch" | 识别语言 (ch/en/japan/korean) |
| `use_gpu` | bool | false | 是否使用 GPU |
| `show_log` | bool | false | 是否显示日志 |
| `max_text_length` | int | 5000 | 最大识别文本长度 |
| `confidence_threshold` | float | 0.6 | 置信度阈值 |

#### extraction_strategy 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prefer_vision` | bool | true | 是否优先使用视觉模型 |
| `auto_fallback` | bool | true | 是否自动降级 |
| `vision_timeout` | int | 30 | 视觉模型超时时间 |
| `max_retries` | int | 2 | 最大重试次数 |
| `cost_optimization` | bool | false | 是否启用成本优化 (始终用 OCR) |

---

## 四、代码修改清单

### 4.1 新增文件

#### agent/extractors/ocr_extractor.py (新建)

```python
"""
OCR 题目提取器
使用 PaddleOCR 识别图片中的文本，然后使用文本模型结构化
"""
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from paddleocr import PaddleOCR

from agent.config import AgentConfig
from agent.services.model_client import ModelClient


class OCRExtractor:
    """OCR 题目提取器"""
    
    # 结构化 Prompt 模板
    STRUCTURE_PROMPT = """
请分析以下 OCR 识别的文本，提取其中的题目信息。

OCR 识别结果：
{text}

要求：
1. 识别题目类型（选择题、填空题、判断题、简答题等）
2. 完整提取题干内容，如果包含代码请用 ``` 语言 ``` 包裹
3. 准确提取选项（如果有）
4. 提取正确答案
5. 如果有解析，也一并提取

请严格按照以下 JSON 格式返回：
{
    "questions": [
        {
            "type": "single_choice|multiple_choice|fill_blank|judgment|short_answer",
            "content": "完整的题干内容",
            "options": ["A. 选项内容", "B. 选项内容"],
            "answer": "正确答案",
            "explanation": "解析内容"
        }
    ],
    "total_count": 题目总数，
    "confidence": 0.0-1.0 之间的置信度，
    "ocr_text": "原始 OCR 文本"
}

如果无法识别题目，返回：
{"questions": [], "total_count": 0, "confidence": 0.0}
"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化 OCR 提取器
        
        Args:
            config: OCR 配置
        """
        ocr_config = config or AgentConfig.get_ocr_config()
        
        # 初始化 PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=ocr_config.get('lang', 'ch'),
            use_gpu=ocr_config.get('use_gpu', False),
            show_log=ocr_config.get('show_log', False),
        )
        
        # 初始化文本模型客户端
        llm_config = AgentConfig.get_llm_config()
        self.llm_client = ModelClient(llm_config)
        
        self.max_length = ocr_config.get('max_text_length', 5000)
        self.confidence_threshold = ocr_config.get('confidence_threshold', 0.6)
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        从图片中提取题目
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            提取结果
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{image_path}")
        
        try:
            # 1. OCR 识别
            ocr_result = self.ocr.ocr(str(image_path), cls=True)
            
            # 2. 提取文本
            ocr_text = self._extract_text(ocr_result)
            
            if not ocr_text.strip():
                return {
                    "questions": [],
                    "total_count": 0,
                    "confidence": 0.0,
                    "error": "OCR 未识别到文本",
                    "extraction_method": "ocr"
                }
            
            # 3. 使用文本模型结构化
            structured_result = self._structure_text(ocr_text)
            
            # 4. 添加元信息
            structured_result["source_type"] = "image"
            structured_result["source_file"] = image_path.name
            structured_result["extraction_method"] = "ocr"
            structured_result["ocr_text"] = ocr_text
            structured_result["extracted_at"] = self._get_timestamp()
            
            return structured_result
            
        except Exception as e:
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": f"OCR 提取失败：{str(e)}",
                "extraction_method": "ocr"
            }
    
    def _extract_text(self, ocr_result: List) -> str:
        """从 OCR 结果中提取文本"""
        if not ocr_result or not ocr_result[0]:
            return ""
        
        texts = []
        for line in ocr_result[0]:
            if line and len(line) >= 2:
                text = line[1][0]  # 文本内容
                confidence = line[1][1]  # 置信度
                
                if confidence > self.confidence_threshold:
                    texts.append(text)
        
        return "\n".join(texts)[:self.max_length]
    
    def _structure_text(self, ocr_text: str) -> Dict[str, Any]:
        """使用文本模型结构化 OCR 文本"""
        messages = [
            {
                "role": "user",
                "content": self.STRUCTURE_PROMPT.format(text=ocr_text)
            }
        ]
        
        try:
            response = self.llm_client.chat(messages, temperature=0.3)
            result = self._parse_response(response)
            result["ocr_text"] = ocr_text
            return result
        except Exception as e:
            return {
                "questions": [],
                "total_count": 0,
                "confidence": 0.0,
                "error": f"结构化失败：{str(e)}",
                "ocr_text": ocr_text
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析模型响应"""
        import re
        
        # 尝试直接解析
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON 代码块
        json_pattern = r'```(?:json)?\s*({.*?})\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 解析失败
        return {
            "questions": [],
            "total_count": 0,
            "confidence": 0.0,
            "error": "无法解析响应为 JSON"
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def close(self):
        """关闭客户端"""
        self.llm_client.close()
```

### 4.2 修改文件

#### agent/extractors/image_extractor.py (修改)

```python
# 在文件开头添加导入
from agent.extractors.ocr_extractor import OCRExtractor

# 修改 ImageExtractor 类
class ImageExtractor:
    def __init__(self, config: Optional[dict] = None):
        vision_config = config or AgentConfig.get_vision_config()
        self.client = ModelClient(vision_config)
        self.max_questions = AgentConfig.MAX_QUESTIONS_PER_IMAGE
        
        # 添加 OCR 提取器
        self.ocr_extractor = None
        if AgentConfig.should_fallback_to_ocr():
            self.ocr_extractor = OCRExtractor()
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """从图片中提取题目（支持降级）"""
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{image_path}")
        
        # 检查是否使用视觉模型
        use_vision = AgentConfig.is_vision_configured()
        
        if use_vision:
            try:
                # 尝试视觉模型
                result = self._extract_with_vision(image_path)
                if result.get("confidence", 0) > 0.6:
                    result["extraction_method"] = "vision"
                    return result
                else:
                    # 置信度低，降级到 OCR
                    if self.ocr_extractor:
                        return self._extract_with_ocr(image_path)
            except Exception as e:
                # 视觉模型失败，降级到 OCR
                if self.ocr_extractor:
                    return self._extract_with_ocr(image_path)
                else:
                    raise
        
        # 直接使用 OCR
        if self.ocr_extractor:
            return self._extract_with_ocr(image_path)
        else:
            raise ValueError("视觉模型和 OCR 均未配置")
    
    def _extract_with_vision(self, image_path: Path) -> Dict[str, Any]:
        """使用视觉模型提取"""
        # 原有代码...
        pass
    
    def _extract_with_ocr(self, image_path: Path) -> Dict[str, Any]:
        """使用 OCR 提取"""
        if not self.ocr_extractor:
            raise ValueError("OCR 未配置")
        
        result = self.ocr_extractor.extract(str(image_path))
        result["extraction_method"] = "ocr"
        result["fallback_reason"] = "vision_model_unavailable"
        return result
```

#### agent/config.py (修改)

```python
# 添加新的配置方法
class AgentConfig:
    # ... 现有代码 ...
    
    @classmethod
    def get_ocr_config(cls) -> dict:
        """获取 OCR 配置"""
        return cls._config.get("ocr", {
            "engine": "paddleocr",
            "enabled": True,
            "lang": "ch",
            "use_gpu": False,
            "show_log": False,
            "max_text_length": 5000,
            "confidence_threshold": 0.6
        })
    
    @classmethod
    def is_vision_configured(cls) -> bool:
        """检查视觉模型是否已配置"""
        vision_config = cls.get_vision_config()
        api_key = vision_config.get("api_key", "")
        enabled = vision_config.get("enabled", True)
        
        return (enabled and 
                api_key and 
                api_key != "YOUR_VISION_API_KEY_HERE")
    
    @classmethod
    def should_fallback_to_ocr(cls) -> bool:
        """检查是否应该降级到 OCR"""
        vision_config = cls.get_vision_config()
        return vision_config.get("fallback_to_ocr", True)
    
    @classmethod
    def get_extraction_strategy(cls) -> dict:
        """获取提取策略配置"""
        return cls._config.get("extraction_strategy", {
            "prefer_vision": True,
            "auto_fallback": True,
            "vision_timeout": 30,
            "max_retries": 2,
            "cost_optimization": False
        })
```

#### web/api/agent.py (修改)

```python
# 在响应中添加提取方法信息
@router.post("/extract/image")
async def extract_from_image(files: List[UploadFile] = File(...)):
    # ... 现有代码 ...
    
    # 保存到预备题目
    saved_questions = []
    if result.get("questions"):
        for q_data in result["questions"]:
            q_data['source_type'] = result.get('source_type', 'image')
            q_data['source_file'] = result.get('source_file', '')
            q_data['extraction_method'] = result.get('extraction_method', 'unknown')
            
            q_id = StagingQuestionRepository.create(q_data)
            saved_questions.append({
                "id": q_id,
                "type": q_data.get("type"),
                "content": q_data.get("content", "")[:100]
            })
    
    # 返回结果
    return {
        "success": True,
        "questions": saved_questions,
        "total_count": result.get("total_count", 0),
        "confidence": result.get("confidence", 0),
        "extraction_method": result.get("extraction_method", "unknown"),
        "fallback_reason": result.get("fallback_reason"),
        "message": f"提取成功，共 {len(saved_questions)} 道题目"
    }
```

---

## 五、依赖清单

### 5.1 新增依赖

```txt
# requirements.txt 新增
paddlepaddle>=2.5.0        # PaddlePaddle 深度学习框架
paddleocr>=2.7.0           # PaddleOCR OCR 引擎
opencv-python>=4.5.0       # OpenCV 图像处理（PaddleOCR 依赖）
Pillow>=9.0.0              # 图像处理
```

### 5.2 安装命令

```bash
# 使用 uv 安装
uv add paddlepaddle paddleocr opencv-python Pillow

# 或使用 pip
pip install paddlepaddle paddleocr opencv-python Pillow

# GPU 版本（生产环境）
uv add paddlepaddle-gpu paddleocr opencv-python Pillow
```

### 5.3 依赖说明

| 依赖 | 版本 | 用途 | 大小 |
|------|------|------|------|
| paddlepaddle | >=2.5.0 | 深度学习框架 | ~200MB |
| paddleocr | >=2.7.0 | OCR 引擎 | ~50MB |
| opencv-python | >=4.5.0 | 图像处理 | ~30MB |
| Pillow | >=9.0.0 | 图像处理 | ~5MB |

**总计**: ~285MB

---

## 六、测试建议

### 6.1 单元测试

```python
# agent/tests/test_ocr_extractor.py

class TestOCRExtractor:
    def test_ocr_extract_success(self):
        """测试 OCR 提取成功"""
        extractor = OCRExtractor()
        result = extractor.extract("test_data/sample_question.png")
        
        assert result["questions"] is not None
        assert "extraction_method" in result
        assert result["extraction_method"] == "ocr"
    
    def test_ocr_extract_empty_image(self):
        """测试空白图片"""
        extractor = OCRExtractor()
        result = extractor.extract("test_data/blank.png")
        
        assert result["questions"] == []
        assert result["total_count"] == 0
    
    def test_ocr_extract_nonexistent_file(self):
        """测试不存在的文件"""
        extractor = OCRExtractor()
        
        with pytest.raises(FileNotFoundError):
            extractor.extract("nonexistent.png")


class TestImageExtractorFallback:
    def test_vision_success(self, mocker):
        """测试视觉模型成功"""
        mocker.patch('agent.extractors.image_extractor.ModelClient.chat_with_images',
                    return_value='{"questions": [...], "confidence": 0.9}')
        
        extractor = ImageExtractor()
        result = extractor.extract("test_data/sample.png")
        
        assert result["extraction_method"] == "vision"
    
    def test_vision_fallback_to_ocr(self, mocker):
        """测试视觉模型失败降级到 OCR"""
        mocker.patch('agent.extractors.image_extractor.ModelClient.chat_with_images',
                    side_effect=Exception("API Error"))
        
        extractor = ImageExtractor()
        result = extractor.extract("test_data/sample.png")
        
        assert result["extraction_method"] == "ocr"
        assert result["fallback_reason"] == "vision_model_unavailable"
```

### 6.2 集成测试

```python
# tests/integration/test_ocr_extraction.py

def test_ocr_extraction_workflow():
    """测试 OCR 提取完整流程"""
    # 1. 上传图片
    with open("test_data/sample_question.png", "rb") as f:
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

### 6.3 性能测试

```python
# tests/performance/test_ocr_performance.py

def test_ocr_extraction_time():
    """测试 OCR 提取时间"""
    extractor = OCRExtractor()
    
    start = time.time()
    result = extractor.extract("test_data/sample.png")
    end = time.time()
    
    extraction_time = end - start
    
    # OCR 提取应该在 5 秒内完成
    assert extraction_time < 5.0
    assert result["extraction_method"] == "ocr"
```

---

## 七、实施计划

### 阶段 1: 环境准备 (1 小时)

- [ ] 安装 PaddleOCR 依赖
- [ ] 下载 OCR 模型文件
- [ ] 验证 OCR 引擎正常工作

### 阶段 2: 代码开发 (4-6 小时)

- [ ] 创建 OCRExtractor 类
- [ ] 修改 ImageExtractor 支持降级
- [ ] 修改 AgentConfig 添加配置方法
- [ ] 修改 API 响应添加提取方法信息

### 阶段 3: 配置更新 (30 分钟)

- [ ] 更新 config/agent.json
- [ ] 更新 .env.example
- [ ] 添加配置文档

### 阶段 4: 测试验证 (2-3 小时)

- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 性能测试
- [ ] 手动测试

### 阶段 5: 文档更新 (1 小时)

- [ ] 更新 README
- [ ] 添加 OCR 配置文档
- [ ] 添加故障排除文档

**总预计时间**: 8-12 小时

---

## 八、风险与缓解

### 风险 1: OCR 识别率低
- **影响**: 高 (题目识别不准确)
- **概率**: 中
- **缓解**:
  - 使用 PaddleOCR (中文识别率 95%+)
  - 添加置信度阈值
  - 提供人工校对界面

### 风险 2: 依赖体积大
- **影响**: 中 (部署包增大 ~300MB)
- **概率**: 高
- **缓解**:
  - 使用 Docker 镜像
  - 提供精简版 (仅 OCR)
  - 按需加载模型

### 风险 3: GPU 依赖
- **影响**: 低 (CPU 也可运行)
- **概率**: 低
- **缓解**:
  - 默认使用 CPU 模式
  - 提供 GPU 配置选项
  - 文档说明性能差异

---

## 九、验收标准

### 功能验收
- [ ] OCR 提取功能正常
- [ ] 视觉模型失败时自动降级
- [ ] 响应中包含 extraction_method 字段
- [ ] 支持手动选择提取方式

### 性能验收
- [ ] OCR 提取时间 < 5 秒
- [ ] 视觉模型超时 < 30 秒
- [ ] 降级切换时间 < 1 秒

### 质量验收
- [ ] 单元测试覆盖率 > 90%
- [ ] 集成测试通过
- [ ] 文档完整

---

## 十、后续优化

### 短期优化 (1-2 周)
1. **多 OCR 引擎支持**: 支持 Tesseract 作为备选
2. **缓存机制**: 相同图片不重复识别
3. **批量优化**: 批量图片并行处理

### 中期优化 (1-2 月)
1. **本地模型**: 部署本地视觉模型 (Qwen-VL-Chat)
2. **混合模式**: OCR + 视觉模型结果融合
3. **成本优化**: 根据图片复杂度选择模型

### 长期优化 (3-6 月)
1. **自训练模型**: 针对题目优化 OCR 模型
2. **边缘计算**: 前端 OCR 识别
3. **多模态融合**: 结合视觉和 OCR 优势

---

*报告生成时间*: 2026-03-20 11:20  
*报告人*: Architect (nanobot)  
*预计完成时间*: 8-12 小时  
*优先级*: P0
