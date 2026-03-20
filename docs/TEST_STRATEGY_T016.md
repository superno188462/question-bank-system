# T016 OCR 备选方案 - 测试策略文档

**文档版本**: 1.0  
**创建时间**: 2026-03-20  
**测试负责人**: Test Analyst  

---

## 一、测试目标

验证 OCR 备选方案功能的正确性、可靠性和性能，确保在视觉模型不可用时能够正确降级到 OCR+LLM 方案。

---

## 二、测试范围

### 2.1 被测组件

| 组件 | 文件路径 | 测试重点 |
|------|----------|----------|
| OCR 服务核心 | `agent/services/ocr_service.py` | 多引擎支持、自动降级 |
| OCR 题目提取器 | `agent/extractors/ocr_question_extractor.py` | OCR+LLM 联合提取 |
| 图片提取器 | `agent/extractors/image_extractor.py` | 视觉模型降级逻辑 |
| 配置模块 | `agent/config.py` | OCR 相关配置项 |

### 2.2 功能边界

**纳入测试**:
- ✅ OCR 引擎初始化和可用性检查
- ✅ OCR 文字识别功能
- ✅ OCR+LLM 题目结构化提取
- ✅ 视觉模型失败时的自动降级
- ✅ 降级触发条件判断
- ✅ 配置项读取和默认值
- ✅ 错误处理和异常场景

**不纳入测试**:
- ❌ OCR 引擎本身的准确性（依赖第三方库）
- ❌ LLM 模型的回答质量（依赖外部 API）
- ❌ 视觉模型的功能（已有独立测试）

---

## 三、测试策略

### 3.1 测试层次

```
┌─────────────────────────────────────┐
│         集成测试 (10%)              │  → API 端到端流程
├─────────────────────────────────────┤
│         单元测试 (80%)              │  → 核心逻辑验证
├─────────────────────────────────────┤
│         Mock 测试 (10%)             │  → 外部依赖隔离
└─────────────────────────────────────┘
```

### 3.2 测试类型

| 测试类型 | 比例 | 说明 |
|----------|------|------|
| 功能测试 | 60% | 验证功能正确性 |
| 异常测试 | 25% | 验证错误处理 |
| 边界测试 | 10% | 验证边界条件 |
| 性能测试 | 5% | 验证响应时间 |

### 3.3 测试数据

| 数据类型 | 来源 | 用途 |
|----------|------|------|
| 模拟图片 | 临时创建 | 文件存在性检查 |
| Mock OCR 结果 | 单元测试 Mock | 隔离外部依赖 |
| Mock LLM 响应 | 单元测试 Mock | 隔离外部依赖 |
| 真实图片 (可选) | 测试资源目录 | 集成测试 |

---

## 四、测试用例设计

### 4.1 OcrService 测试用例

| ID | 用例名称 | 前置条件 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|----------|
| OS-01 | PaddleOCR 引擎初始化 | paddleocr 已安装 | 创建 PaddleOcrEngine 实例 | 初始化成功 |
| OS-02 | PaddleOCR 引擎可用性检查 | paddleocr 已安装 | 调用 is_available() | 返回 True |
| OS-03 | Tesseract 引擎初始化 | pytesseract 已安装 | 创建 TesseractOcrEngine 实例 | 初始化成功 |
| OS-04 | OcrService 自动选择引擎 | 至少一个引擎可用 | 创建 OcrService 实例 | 选择可用引擎 |
| OS-05 | OcrService 降级逻辑 | 首选引擎不可用 | 创建 OcrService 实例 | 降级到备选引擎 |
| OS-06 | OcrService 无可用引擎 | 所有引擎不可用 | 创建 OcrService 实例 | 抛出 RuntimeError |
| OS-07 | recognize 正常识别 | 引擎可用，图片存在 | 调用 recognize() | 返回识别文本 |
| OS-08 | recognize 文件不存在 | 图片不存在 | 调用 recognize() | 抛出 FileNotFoundError |
| OS-09 | recognize_with_confidence | 引擎可用 | 调用 recognize_with_confidence() | 返回带置信度的结果 |

### 4.2 OcrQuestionExtractor 测试用例

| ID | 用例名称 | 前置条件 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|----------|
| OQE-01 | 初始化成功 | OCR 和 LLM 配置有效 | 创建 OcrQuestionExtractor | 初始化成功 |
| OQE-02 | extract 正常流程 | 图片存在，OCR 和 LLM 可用 | 调用 extract() | 返回结构化题目 |
| OQE-03 | extract 文件不存在 | 图片不存在 | 调用 extract() | 抛出 FileNotFoundError |
| OQE-04 | extract OCR 结果为空 | 空白图片 | 调用 extract() | 返回空题目列表 |
| OQE-05 | extract LLM 解析失败 | LLM 返回无效 JSON | 调用 extract() | 返回空题目列表，带错误信息 |
| OQE-06 | extract 题目数量限制 | 图片含多道题目 | 调用 extract() | 题目数不超过 MAX_QUESTIONS_PER_IMAGE |
| OQE-07 | extract_batch 批量处理 | 多张图片 | 调用 extract_batch() | 返回合并结果 |
| OQE-08 | extract_batch 部分失败 | 部分图片处理失败 | 调用 extract_batch() | 成功图片正常，失败图片计数 |
| OQE-09 | close 资源释放 | 提取器已创建 | 调用 close() | 服务正确关闭 |

### 4.3 ImageExtractor 降级测试用例

| ID | 用例名称 | 前置条件 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|----------|
| IE-FB-01 | 视觉模型成功不降级 | 视觉模型可用 | 调用 extract() | 使用 vision 方法，不触发降级 |
| IE-FB-02 | 视觉模型 API 错误降级 | 视觉模型抛出异常 | 调用 extract() | 降级到 OCR，extraction_method=ocr+llm |
| IE-FB-03 | 视觉模型置信度低降级 | 视觉模型返回低置信度 | 调用 extract() | 降级到 OCR |
| IE-FB-04 | 视觉模型空结果降级 | 视觉模型返回空题目 | 调用 extract() | 降级到 OCR |
| IE-FB-05 | OCR 降级禁用 | OCR_ENABLED=False | 调用 extract() | 不降级，返回视觉模型错误 |
| IE-FB-06 | 降级后返回 fallback 标记 | 触发降级 | 调用 extract() | 结果包含 fallback_used=True |
| IE-FB-07 | 降级原因记录 | 触发降级 | 调用 extract() | 结果包含 fallback_reason |
| IE-FB-08 | OCR 降级也失败 | 视觉模型和 OCR 都失败 | 调用 extract() | 返回 OCR 错误信息 |

### 4.4 Config 配置测试用例

| ID | 用例名称 | 前置条件 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|----------|
| CFG-01 | OCR_ENABLED 默认值 | 配置无 ocr 段 | 读取 OCR_ENABLED | 返回 True |
| CFG-02 | OCR_ENGINE 默认值 | 配置无 ocr 段 | 读取 OCR_ENGINE | 返回 "paddle" |
| CFG-03 | OCR_LANG 默认值 | 配置无 ocr 段 | 读取 OCR_LANG | 返回 "ch" |
| CFG-04 | VISION_FALLBACK_THRESHOLD | 配置无 settings 段 | 读取 VISION_FALLBACK_THRESHOLD | 返回 0.5 |
| CFG-05 | get_ocr_config | 配置存在 | 调用 get_ocr_config() | 返回完整 OCR 配置字典 |

---

## 五、测试环境

### 5.1 依赖要求

```txt
pytest>=7.0.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
paddlepaddle>=2.5.0  # 可选，用于集成测试
paddleocr>=2.7.0     # 可选，用于集成测试
```

### 5.2 测试执行命令

```bash
# 运行 OCR 降级测试
pytest agent/tests/test_ocr_fallback.py -v

# 运行覆盖率报告
pytest agent/tests/test_ocr_fallback.py -v --cov=agent/services/ocr_service --cov=agent/extractors/ocr_question_extractor --cov=agent/extractors/image_extractor

# 运行特定测试类
pytest agent/tests/test_ocr_fallback.py::TestOcrService -v
pytest agent/tests/test_ocr_fallback.py::TestOcrQuestionExtractor -v
pytest agent/tests/test_ocr_fallback.py::TestImageExtractorFallback -v
```

---

## 六、验收标准

### 6.1 功能验收

- [ ] 所有测试用例通过
- [ ] 单元测试覆盖率 ≥ 90%
- [ ] 降级逻辑正确触发
- [ ] 错误处理完善

### 6.2 性能验收

- [ ] OCR 识别时间 < 5 秒 (Mock 测试不验证)
- [ ] 降级切换时间 < 1 秒

### 6.3 代码质量

- [ ] 无 Pylint 严重警告
- [ ] 代码符合项目规范
- [ ] 日志记录完整

---

## 七、风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| OCR 依赖安装失败 | 中 | 低 | 使用 Mock 隔离，集成测试可选 |
| 测试环境配置复杂 | 低 | 中 | 提供测试配置示例 |
| Mock 与真实行为差异 | 中 | 低 | 补充少量集成测试验证 |

---

## 八、测试交付物

1. `agent/tests/test_ocr_fallback.py` - 测试脚本
2. `docs/TEST_STRATEGY_T016.md` - 测试策略文档 (本文档)
3. 测试覆盖率报告 (HTML)
4. 测试执行日志

---

*文档结束*
