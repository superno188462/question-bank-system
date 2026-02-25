"""
数据库迁移脚本

负责：
1. 创建数据库表结构
2. 初始化默认数据
3. 执行数据迁移
"""

import os
from core.database.connection import db


def create_tables():
    """创建所有数据库表"""
    
    # 分类表
    categories_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """
    
    # 标签表
    tags_sql = """
    CREATE TABLE IF NOT EXISTS tags (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        color TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """
    
    # 题目表（先不添加外键约束）
    questions_sql = """
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        options TEXT NOT NULL DEFAULT '[]',  -- JSON格式存储选项列表
        answer TEXT NOT NULL,
        explanation TEXT NOT NULL,
        category_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """
    
    # 题目标签关联表（先不添加外键约束）
    question_tags_sql = """
    CREATE TABLE IF NOT EXISTS question_tags (
        question_id TEXT NOT NULL,
        tag_id TEXT NOT NULL,
        PRIMARY KEY (question_id, tag_id)
    )
    """
    
    # 创建索引
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_questions_created ON questions(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name)",
        "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)",
        "CREATE INDEX IF NOT EXISTS idx_question_tags_question ON question_tags(question_id)",
        "CREATE INDEX IF NOT EXISTS idx_question_tags_tag ON question_tags(tag_id)"
    ]
    
    try:
        print("开始创建数据库表...")
        
        # 执行建表语句（注意顺序：先创建被引用的表）
        db.execute(categories_sql)
        db.execute(tags_sql)
        db.execute(questions_sql)
        db.execute(question_tags_sql)
        
        # 创建索引
        for index_sql in indexes_sql:
            db.execute(index_sql)
        
        # 添加外键约束（SQLite需要重新建表或使用PRAGMA）
        print("✅ 数据库表创建完成")
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        return False


def init_default_data():
    """初始化默认数据"""
    
    try:
        print("开始初始化默认数据...")
        
        # 检查是否已有数据
        count_sql = "SELECT COUNT(*) as count FROM categories"
        result = db.fetch_one(count_sql)
        
        if result and result['count'] > 0:
            print("✅ 数据库已有数据，跳过初始化")
            return True
        
        # 插入默认分类
        categories = [
            ("数学", "数学相关题目"),
            ("语文", "语文相关题目"),
            ("英语", "英语相关题目"),
            ("物理", "物理相关题目"),
            ("化学", "化学相关题目"),
            ("历史", "历史相关题目"),
            ("地理", "地理相关题目"),
            ("生物", "生物相关题目")
        ]
        
        import uuid
        from datetime import datetime
        
        for name, description in categories:
            category_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            sql = """
            INSERT INTO categories (id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """
            db.execute(sql, (category_id, name, description, now, now))
        
        # 插入默认标签
        tags = [
            ("易", "#10b981"),
            ("中", "#f59e0b"),
            ("难", "#ef4444"),
            ("重点", "#8b5cf6"),
            ("考点", "#3b82f6"),
            ("例题", "#06b6d4"),
            ("真题", "#ec4899")
        ]
        
        for name, color in tags:
            tag_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            sql = """
            INSERT INTO tags (id, name, color, created_at)
            VALUES (?, ?, ?, ?)
            """
            db.execute(sql, (tag_id, name, color, now))
        
        print("✅ 默认数据初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ 初始化默认数据失败: {e}")
        return False


def migrate_database():
    """执行数据库迁移"""
    
    try:
        print("开始数据库迁移...")
        
        # 检查表是否存在
        tables = ["categories", "tags", "questions", "question_tags"]
        missing_tables = []
        
        for table in tables:
            if not db.table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            print(f"发现缺失的表: {missing_tables}")
            if create_tables():
                print("✅ 缺失的表已创建")
            else:
                print("❌ 创建表失败")
                return False
        
        # 初始化默认数据
        init_default_data()
        
        print("✅ 数据库迁移完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False


def backup_database(backup_path: str = "question_bank_backup.db"):
    """备份数据库"""
    try:
        import shutil
        db_path = db.db_path
        
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return False
        
        shutil.copy2(db_path, backup_path)
        print(f"✅ 数据库已备份到: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ 备份数据库失败: {e}")
        return False


def restore_database(backup_path: str = "question_bank_backup.db"):
    """恢复数据库"""
    try:
        if not os.path.exists(backup_path):
            print(f"❌ 备份文件不存在: {backup_path}")
            return False
        
        db_path = db.db_path
        shutil.copy2(backup_path, db_path)
        print(f"✅ 数据库已从备份恢复: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ 恢复数据库失败: {e}")
        return False


if __name__ == "__main__":
    # 直接运行此脚本时执行迁移
    migrate_database()