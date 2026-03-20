# 快速使用指南

## 🎯 项目目标

创建一个题库系统，支持通过AI从图片或文档生成题目JSON，然后手动填写五个核心信息：
1. **题干** - 题目主要内容
2. **选项** - 选择题的选项列表（填空题为空列表）
3. **答案** - 正确答案
4. **解析** - 题目解析和说明
5. **分类** - 题目所属分类

## 🚀 快速开始

### 1. 启动服务
```bash
# 克隆项目
git clone https://github.com/superno188462/question-bank-system.git
cd question-bank-system

# 启动Web服务
./run.sh web

# 访问API文档
# http://localhost:8000/docs
```

### 2. 创建题目（手动填写）

#### 使用curl创建选择题：
```bash
curl -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Python中如何定义一个函数？",
    "options": ["使用 def 关键字", "使用 function 关键字", "使用 func 关键字", "使用 define 关键字"],
    "answer": "使用 def 关键字",
    "explanation": "在Python中，使用def关键字来定义函数，后面跟着函数名和参数列表。",
    "category_id": "分类ID",
    "tag_ids": []
  }'
```

#### 使用curl创建填空题：
```bash
curl -X POST http://localhost:8000/api/questions \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Python中用于输出内容到控制台的内置函数是______。",
    "options": [],
    "answer": "print",
    "explanation": "print()是Python的内置函数，用于将内容输出到控制台。",
    "category_id": "分类ID",
    "tag_ids": []
  }'
```

### 3. AI生成题目JSON示例

#### AI从图片/文档提取的信息：
```json
{
  "content": "以下哪个不是Python的数据类型？",
  "options": ["int", "float", "string", "double"],
  "answer": "double",
  "explanation": "Python中没有double类型，浮点数使用float表示。",
  "category_id": "programming_category_id"
}
```

#### 转换为API请求：
```python
import requests

question = {
    "content": "以下哪个不是Python的数据类型？",
    "options": ["int", "float", "string", "double"],
    "answer": "double",
    "explanation": "Python中没有double类型，浮点数使用float表示。",
    "category_id": "programming_category_id"
}

response = requests.post("http://localhost:8000/api/questions", json=question)
if response.status_code == 201:
    print("✅ 题目创建成功:", response.json())
```

## 📋 题目JSON格式

### 完整格式：
```json
{
  "content": "题干内容（必填）",
  "options": ["选项1", "选项2", "选项3", "选项4"],  // 填空题为空列表[]
  "answer": "正确答案（必填）",
  "explanation": "题目解析（必填）",
  "category_id": "分类ID（必填）",
  "tag_ids": ["标签ID1", "标签ID2"]  // 可选
}
```

### 验证规则：
1. **content**: 非空字符串，至少1个字符
2. **options**: 必须是列表，填空题为空列表`[]`
3. **answer**: 非空字符串，至少1个字符
4. **explanation**: 非空字符串，至少1个字符
5. **category_id**: 非空字符串，至少1个字符

## 🔧 获取分类ID

在创建题目前，需要先获取分类ID：

```bash
# 获取所有分类
curl http://localhost:8000/api/categories

# 响应示例
[
  {
    "id": "0fb26801-acca-4b7a-947a-6025b87568d2",
    "name": "数学",
    "description": "数学相关题目",
    "created_at": "2026-02-25T12:00:00",
    "updated_at": "2026-02-25T12:00:00"
  }
]
```

## 📁 批量导入题目

### 创建批量导入文件 `batch_questions.json`:
```json
{
  "questions": [
    {
      "content": "题目1",
      "options": ["A", "B", "C"],
      "answer": "A",
      "explanation": "解析1",
      "category_id": "分类ID1"
    },
    {
      "content": "题目2",
      "options": [],
      "answer": "答案",
      "explanation": "解析2",
      "category_id": "分类ID2"
    }
  ]
}
```

### 批量导入脚本 `batch_import.py`:
```python
import requests
import json

with open('batch_questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

success_count = 0
for question in data['questions']:
    response = requests.post('http://localhost:8000/api/questions', json=question)
    if response.status_code == 201:
        success_count += 1
        print(f"✅ 创建成功: {question['content'][:30]}...")
    else:
        print(f"❌ 创建失败: {response.text}")

print(f"\n🎯 批量导入完成: {success_count}/{len(data['questions'])} 成功")
```

## 🧪 测试验证

### 运行测试脚本：
```bash
# 测试题目创建功能
python3 test_question_creation.py

# 查看AI生成JSON示例
python3 example_question_json.py
```

### 验证API端点：
```bash
# 健康检查
curl http://localhost:8000/health

# 获取题目列表
curl http://localhost:8000/api/questions

# 搜索题目
curl "http://localhost:8000/api/questions/search?keyword=Python"
```

## 🔍 查看数据

### 数据库文件位置：
```
data/question_bank.db
```

### 使用SQLite查看数据：
```bash
sqlite3 data/question_bank.db

# 查看所有题目
SELECT id, content, answer FROM questions;

# 查看题目数量
SELECT COUNT(*) FROM questions;

# 退出
.quit
```

## 🛠️ 故障排除

### 常见问题：

1. **端口被占用**：
   ```bash
   # 停止所有服务
   ./run.sh stop
   
   # 重新启动
   ./run.sh web
   ```

2. **数据库错误**：
   ```bash
   # 删除数据库文件重新创建
   rm -f data/question_bank.db
   ./run.sh setup
   ```

3. **依赖问题**：
   ```bash
   # 使用uv安装依赖
   uv pip install -r config/requirements.txt
   ```

4. **验证失败**：
   - 检查五个核心信息是否都填写
   - 检查字段是否为空字符串
   - 检查category_id是否正确

## 📞 支持

### 查看日志：
```bash
# 查看Web服务日志
tail -f /tmp/web_test.log

# 查看验证日志
ls test/logs/
```

### 运行完整验证：
```bash
# 快速验证
bash test/quick_validate.sh

# 完整验证
python3 test/validate_project.py
```

## 🎯 下一步

### 当前已实现：
- ✅ 题目五个核心信息模型
- ✅ 必填字段验证
- ✅ API接口
- ✅ 数据库存储
- ✅ 验证脚本
- ✅ AI生成JSON示例

### 后续可扩展：
- AI图片/文档解析集成
- Web管理界面
- 批量导入界面
- 题目统计分析
- 用户答题系统

---

**项目已准备好接收AI生成的题目JSON数据！**