#!/usr/bin/env python3
"""
预备题目入库功能自验证脚本
测试场景：
1. 创建测试预备题目（选择题，答案为 A/B/C/D 格式）
2. 执行入库操作
3. 验证正式题目创建成功
4. 验证预备题目状态更新
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from datetime import datetime
from web.api.agent import approve_staging_question
import asyncio

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_create_staging_question():
    """测试 1: 创建测试预备题目"""
    print_section("测试 1: 创建测试预备题目")
    
    conn = sqlite3.connect('data/question_bank.db')
    cursor = conn.cursor()
    
    # 清理旧数据
    cursor.execute('DELETE FROM staging_questions WHERE content LIKE ?', ('%测试题目%',))
    
    # 创建测试预备题目（选择题，答案为 A 格式）
    test_cases = [
        {
            'content': '测试题目：Python 中列表的 append() 方法做什么？',
            'type': 'single_choice',
            'answer': 'A',
            'options': '["在列表末尾添加元素", "删除列表元素", "排序列表", "反转列表"]',
            'explanation': 'append() 方法用于在列表的末尾添加一个新元素。'
        },
        {
            'content': '测试题目：以下哪个是 Python 的内置数据类型？',
            'type': 'single_choice',
            'answer': 'C',
            'options': '["File", "Stream", "list", "Pointer"]',
            'explanation': 'list 是 Python 的内置数据类型，其他选项不是。'
        },
        {
            'content': '测试题目：1+1 等于多少？',
            'type': 'fill_blank',
            'answer': '2',
            'options': '[]',
            'explanation': '基础数学题。'
        }
    ]
    
    created_ids = []
    for i, test in enumerate(test_cases, 1):
        cursor.execute('''
            INSERT INTO staging_questions (content, type, answer, options, explanation, status, source_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test['content'],
            test['type'],
            test['answer'],
            test['options'],
            test['explanation'],
            'pending',
            'chat',
            datetime.now().isoformat()
        ))
        created_ids.append(cursor.lastrowid)
        print(f"  ✅ 创建测试预备题目 #{i}: ID={cursor.lastrowid}, 答案={test['answer']}")
    
    conn.commit()
    conn.close()
    
    return created_ids

async def test_approve_staging_question(question_id, test_name):
    """测试 2: 执行入库操作"""
    print_section(f"测试 2: 入库操作 - {test_name}")
    
    try:
        result = await approve_staging_question(question_id=question_id, reviewed_by="auto_test")
        print(f"  ✅ API 调用成功：{result}")
        return True
    except Exception as e:
        print(f"  ❌ API 调用失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database_state():
    """测试 3: 验证数据库状态"""
    print_section("测试 3: 验证数据库状态")
    
    conn = sqlite3.connect('data/question_bank.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 检查正式题目
    print("  📚 正式题目表 (questions):")
    cursor.execute('''
        SELECT q.id, q.content, q.answer, q.category_id, c.name as category_name
        FROM questions q
        LEFT JOIN categories c ON q.category_id = c.id
        WHERE q.content LIKE ?
        ORDER BY q.created_at DESC
    ''', ('%测试题目%',))
    
    questions = cursor.fetchall()
    if questions:
        for q in questions:
            print(f"    ✅ ID={q['id'][:8]}..., 答案={q['answer']}, 分类={q['category_name']}")
            print(f"       内容：{q['content'][:40]}...")
    else:
        print("    ❌ 没有找到测试题目")
    
    # 检查预备题目状态
    print("\n  📥 预备题目表 (staging_questions):")
    cursor.execute('''
        SELECT id, content, status, reviewed_at, reviewed_by
        FROM staging_questions
        WHERE content LIKE ?
        ORDER BY id DESC
    ''', ('%测试题目%',))
    
    staging = cursor.fetchall()
    if staging:
        for s in staging:
            status_icon = "✅" if s['status'] == 'approved' else "⏳" if s['status'] == 'pending' else "❌"
            print(f"    {status_icon} ID={s['id']}, 状态={s['status']}, 审核人={s['reviewed_by']}")
            print(f"       内容：{s['content'][:40]}...")
    else:
        print("    ❌ 没有找到测试预备题目")
    
    conn.close()
    return len(questions) > 0

async def main():
    print("\n" + "="*60)
    print("  预备题目入库功能 - 自动化验证")
    print("="*60)
    
    # 测试 1: 创建测试数据
    created_ids = test_create_staging_question()
    
    # 测试 2: 执行入库
    results = []
    test_names = [
        "选择题 (答案 A)",
        "选择题 (答案 C)",
        "填空题 (答案 2)"
    ]
    
    for qid, name in zip(created_ids, test_names):
        success = await test_approve_staging_question(qid, name)
        results.append(success)
    
    # 测试 3: 验证数据库
    db_ok = verify_database_state()
    
    # 总结
    print_section("验证总结")
    
    total = len(results)
    passed = sum(results)
    
    print(f"  入库测试：{passed}/{total} 通过")
    print(f"  数据库验证：{'✅ 通过' if db_ok else '❌ 失败'}")
    
    if passed == total and db_ok:
        print("\n  🎉 所有测试通过！入库功能正常！\n")
        return 0
    else:
        print("\n  ⚠️  部分测试失败，请检查日志\n")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
