"""
数据库连接管理
提供SQLite数据库连接和连接池管理
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Generator, Optional
import os


@contextmanager
def transaction():
    """
    事务上下文管理器
    
    用法:
        with transaction():
            # 执行数据库操作
            db.execute("INSERT INTO ...")
    """
    db = DatabaseConnection()
    conn = db.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

from shared.config import config


class DatabaseConnection:
    """数据库连接管理器（单例模式）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_connection()
        return cls._instance
    
    def _init_connection(self):
        """初始化数据库连接"""
        self.db_path = config.get_database_path()
        self._local = threading.local()
        
        # 确保数据库文件目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        获取数据库连接（线程安全）
        
        返回:
            sqlite3.Connection: SQLite数据库连接
        """
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path)
            # 启用外键约束
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂，返回字典格式
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def close_connection(self):
        """关闭当前线程的数据库连接"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
    
    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        获取数据库游标的上下文管理器
        
        使用示例:
        ```
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            result = cursor.fetchall()
        ```
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        执行SQL语句
        
        参数:
            sql: SQL语句
            params: 参数元组
            
        返回:
            sqlite3.Cursor: 执行后的游标
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """
        执行查询并返回单条记录
        
        参数:
            sql: SQL查询语句
            params: 参数元组
            
        返回:
            dict: 单条记录（字典格式）或None
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, sql: str, params: tuple = ()) -> list:
        """
        执行查询并返回所有记录
        
        参数:
            sql: SQL查询语句
            params: 参数元组
            
        返回:
            list: 所有记录（列表字典格式）
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        参数:
            table_name: 表名
            
        返回:
            bool: 表是否存在
        """
        sql = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        result = self.fetch_one(sql, (table_name,))
        return result is not None


# 创建全局数据库连接实例
db = DatabaseConnection()