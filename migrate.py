#!/usr/bin/env python3
"""
数据库迁移脚本

使用方法:
    python migrate.py           # 执行迁移
    python migrate.py --status  # 查看迁移状态
    python migrate.py --backup  # 备份数据库后迁移
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database.migrations import (
    migrate_database, 
    backup_database, 
    get_applied_migrations,
    MIGRATION_VERSION
)


def show_status():
    """显示迁移状态"""
    print("=" * 50)
    print("数据库迁移状态")
    print("=" * 50)
    
    applied = get_applied_migrations()
    print(f"\n当前版本：{applied[-1] if applied else '无'}")
    print(f"目标版本：{MIGRATION_VERSION}")
    
    if applied and applied[-1] == MIGRATION_VERSION:
        print("\n✅ 数据库已是最新版本")
    else:
        print("\n⚠️  数据库需要升级")
        print(f"   已应用迁移：{len(applied)} 个")
        if applied:
            print(f"   迁移历史：{', '.join(applied)}")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            show_status()
            return
        elif sys.argv[1] == "--backup":
            print("正在备份数据库...")
            backup_path = f"question_bank_backup_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            if backup_database(backup_path):
                print("开始迁移...")
                migrate_database(auto=False)
            return
        elif sys.argv[1] == "--help":
            print(__doc__)
            return
    
    # 默认执行迁移
    print("正在执行数据库迁移...")
    migrate_database(auto=False)


if __name__ == "__main__":
    main()
