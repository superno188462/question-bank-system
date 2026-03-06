"""
数据库迁移脚本

负责：
1. 创建数据库表结构
2. 初始化默认数据
3. 执行数据迁移
4. 自动检测并应用表结构变更
"""

import os
import json
from datetime import datetime
from core.database.connection import db

# 迁移版本号
MIGRATION_VERSION = "20260306"

# 期望的表结构定义
EXPECTED_SCHEMA = {
    "questions": {
        "columns": {
            "id": "TEXT",
            "content": "TEXT",
            "options": "TEXT",
            "answer": "TEXT",
            "explanation": "TEXT",
            "category_id": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT"
        }
    },
    "categories": {
        "columns": {
            "id": "TEXT",
            "name": "TEXT",
            "description": "TEXT",
            "parent_id": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT"
        }
    },
    "tags": {
        "columns": {
            "id": "TEXT",
            "name": "TEXT",
            "color": "TEXT",
            "created_at": "TEXT"
        }
    },
    "question_tags": {
        "columns": {
            "question_id": "TEXT",
            "tag_id": "TEXT"
        }
    },
    "migrations": {
        "columns": {
            "version": "TEXT",
            "applied_at": "TEXT",
            "description": "TEXT"
        }
    }
}


def get_current_schema():
    """获取当前数据库表结构"""
    schema = {}
    tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
    
    for table in tables:
        table_name = table['name']
        if table_name.startswith('sqlite_'):
            continue
            
        columns = db.fetch_all(f"PRAGMA table_info({table_name})")
        schema[table_name] = {
            "columns": {col['name']: col['type'] for col in columns}
        }
    
    return schema


def ensure_migrations_table():
    """确保迁移记录表存在"""
    sql = """
    CREATE TABLE IF NOT EXISTS migrations (
        version TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL,
        description TEXT
    )
    """
    db.execute(sql)


def get_applied_migrations():
    """获取已应用的迁移版本"""
    try:
        result = db.fetch_all("SELECT version FROM migrations ORDER BY version")
        return [r['version'] for r in result]
    except:
        return []


def record_migration(version: str, description: str = ""):
    """记录已应用的迁移"""
    sql = """
    INSERT OR REPLACE INTO migrations (version, applied_at, description)
    VALUES (?, ?, ?)
    """
    db.execute(sql, (version, datetime.now().isoformat(), description))


def add_column_if_not_exists(table: str, column: str, column_type: str, default: str = None):
    """如果列不存在则添加"""
    schema = get_current_schema()
    if table in schema and column not in schema[table].get('columns', {}):
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"
        if default is not None:
            sql += f" DEFAULT {default}"
        db.execute(sql)
        print(f"  ✅ 添加列：{table}.{column}")
        return True
    return False


def create_tables():
    """创建所有数据库表"""
    
    # 分类表（支持多层级）
    categories_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        parent_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
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
            INSERT INTO categories (id, name, description, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            db.execute(sql, (category_id, name, description, None, now, now))
        
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


def apply_schema_migrations():
    """应用表结构变更迁移"""
    print("检查表结构变更...")
    
    # 确保迁移记录表存在
    ensure_migrations_table()
    
    # 检查并添加 questions 表的 options 列默认值（兼容旧数据）
    add_column_if_not_exists("questions", "options", "TEXT", "DEFAULT '[]'")
    
    # 检查并添加 category_name 列（如果需要）
    # add_column_if_not_exists("questions", "category_name", "TEXT")
    
    print("✅ 表结构检查完成")


def migrate_database(auto: bool = True):
    """
    执行数据库迁移
    
    Args:
        auto: 是否自动模式（静默执行，不报错）
    """
    
    try:
        if auto:
            print("🔄 自动检查数据库迁移...")
        else:
            print("开始数据库迁移...")
        
        # 确保迁移记录表存在
        ensure_migrations_table()
        
        # 检查表是否存在
        tables = ["categories", "tags", "questions", "question_tags"]
        missing_tables = []
        
        for table in tables:
            if not db.table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            print(f"发现缺失的表：{missing_tables}")
            if create_tables():
                print("✅ 缺失的表已创建")
            else:
                print("❌ 创建表失败")
                if not auto:
                    return False
        
        # 应用表结构变更
        apply_schema_migrations()
        
        # 初始化默认数据
        init_default_data()
        
        # 记录当前迁移版本
        applied = get_applied_migrations()
        if MIGRATION_VERSION not in applied:
            record_migration(MIGRATION_VERSION, "当前版本")
            print(f"✅ 迁移版本：{MIGRATION_VERSION}")
        
        if auto:
            print("✅ 数据库检查完成")
        else:
            print("✅ 数据库迁移完成")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ 数据库迁移失败：{e}"
        if auto:
            print(error_msg)
            print("⚠️  应用将继续运行，但数据库功能可能受限")
            return True  # 自动模式下不阻止启动
        else:
            print(error_msg)
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