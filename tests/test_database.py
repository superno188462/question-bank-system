#!/usr/bin/env python3
"""
简单数据库测试脚本
验证数据库是否正常工作
"""

import os
import sqlite3
import json

def test_database():
    """测试数据库"""
    db_file = "data/question_bank.db"
    
    print("=" * 60)
    print("数据库测试工具")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(db_file):
        print(f"❌ 数据库文件 {db_file} 不存在")
        print("正在创建空数据库...")
        try:
            conn = sqlite3.connect(db_file)
            conn.close()
            print(f"✅ 已创建空数据库文件: {db_file}")
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"✅ 成功连接到数据库: {db_file}")
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ 找到 {len(tables)} 个表:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  数据库中没有表")
            print("正在创建questions表...")
            cursor.execute('''
            CREATE TABLE questions (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                question_type TEXT NOT NULL,
                difficulty TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            print("✅ 已创建questions表")
        
        # 检查questions表数据
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ questions表中有 {count} 条记录")
            
            # 显示前3条记录
            cursor.execute("SELECT id, content, difficulty FROM questions LIMIT 3")
            print("\n📋 示例题目:")
            for row in cursor.fetchall():
                print(f"   ID: {row[0]}")
                print(f"   内容: {row[1]}")
                print(f"   难度: {row[2]}")
                print()
        else:
            print("⚠️  questions表中没有数据")
            print("正在插入示例数据...")
            
            import uuid
            sample_data = [
                (str(uuid.uuid4()), "Python中如何定义函数？", "short_answer", "easy", "python,function", 
                 json.dumps({"category": "programming"})),
                (str(uuid.uuid4()), "什么是HTTP协议？", "multiple_choice", "easy", "web,http", 
                 json.dumps({"category": "web"})),
            ]
            
            cursor.executemany('''
            INSERT INTO questions (id, content, question_type, difficulty, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_data)
            
            conn.commit()
            print("✅ 已插入2条示例数据")
        
        # 检查文件大小
        file_size = os.path.getsize(db_file)
        print(f"\n📊 数据库文件信息:")
        print(f"   文件路径: {os.path.abspath(db_file)}")
        print(f"   文件大小: {file_size} 字节 ({file_size/1024:.1f} KB)")
        
        # 测试查询
        print("\n🧪 测试查询:")
        cursor.execute("SELECT question_type, COUNT(*) as count FROM questions GROUP BY question_type")
        for row in cursor.fetchall():
            print(f"   题型 '{row[0]}': {row[1]} 题")
        
        conn.close()
        print("\n🎉 数据库测试通过！")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def simple_test():
    """最简单的测试"""
    print("执行简单数据库测试...")
    
    try:
        import sqlite3
        
        # 确保数据库文件存在
        if not os.path.exists("data/question_bank.db"):
            print("创建数据库文件...")
            conn = sqlite3.connect("data/question_bank.db")
            conn.close()
        
        # 连接并创建表
        conn = sqlite3.connect("data/question_bank.db")
        cursor = conn.cursor()
        
        # 创建简单表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        ''')
        
        # 插入测试数据
        cursor.execute("INSERT OR IGNORE INTO test_table (name) VALUES ('test')")
        conn.commit()
        
        # 查询数据
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ 数据库测试通过！表中有 {count} 条记录")
        print(f"✅ 数据库文件: question_bank.db")
        return True
        
    except Exception as e:
        print(f"❌ 简单测试失败: {e}")
        return False

if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整测试")
    print("2. 简单测试")
    print("3. 仅检查文件")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        test_database()
    elif choice == "2":
        simple_test()
    elif choice == "3":
        if os.path.exists("data/question_bank.db"):
            size = os.path.getsize("data/question_bank.db")
            print(f"✅ 数据库文件存在: question_bank.db")
            print(f"   文件大小: {size} 字节")
            print(f"   绝对路径: {os.path.abspath('data/question_bank.db')}")
        else:
            print("❌ 数据库文件不存在")
    else:
        print("无效选择")