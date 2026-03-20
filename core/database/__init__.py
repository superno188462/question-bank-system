"""
数据库模块
提供 SQLite 数据库连接管理
"""

from core.database.connection import db, DatabaseConnection, transaction


def get_db_connection():
    """
    获取数据库连接
    
    返回:
        sqlite3.Connection: SQLite 数据库连接
    """
    return db.get_connection()


__all__ = ['db', 'DatabaseConnection', 'get_db_connection', 'transaction']
