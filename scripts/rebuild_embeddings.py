#!/usr/bin/env python3
"""
向量重建脚本

用于在切换 Embedding 模型后重建题目向量索引
支持：
- 重建所有题目向量
- 仅重建未向量化的题目
- 仅重建模型版本不匹配的题目
- 智能检测（跳过无需重建的题目）

使用方法:
    python scripts/rebuild_embeddings.py           # 交互式
    python scripts/rebuild_embeddings.py --all     # 重建所有
    python scripts/rebuild_embeddings.py --missing # 仅缺失的
    python scripts/rebuild_embeddings.py --mismatch # 仅版本不匹配的
    python scripts/rebuild_embeddings.py --check   # 检查状态
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database.connection import db
from core.services.vector_index import VectorIndex
from agent.services.embedding_service import get_embedding_service
from agent.config import AgentConfig


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def check_status():
    """检查向量化状态"""
    print_header("向量化状态检查")
    
    vi = VectorIndex(db)
    stats = vi.get_stats()
    
    print(f"\n📊 题目统计:")
    print(f"   总题目数：{stats['total_questions']}")
    print(f"   已向量：{stats['with_embedding']}")
    print(f"   未向量：{stats['without_embedding']}")
    
    if stats['versions']:
        print(f"\n📦 向量版本分布:")
        for version in stats['versions']:
            print(f"   - {version['version']}: {version['count']} 题 (最后更新：{version['last_updated']})")
    
    # 获取当前模型版本
    try:
        config = AgentConfig._load_config()
        embedding_config = config.get('embedding', {})
        current_model = embedding_config.get('model_name', 'unknown')
        print(f"\n🎯 当前模型：{current_model}")
        
        # 检查版本不匹配
        mismatched = vi.get_mismatched_embeddings(current_model)
        if mismatched:
            print(f"   ⚠️  版本不匹配：{len(mismatched)} 题需要重建")
        else:
            print(f"   ✅ 所有题目版本匹配")
    except Exception as e:
        print(f"   ❌ 无法获取当前模型配置：{e}")
    
    print()


def rebuild_all(embedding_service, model_version: str):
    """重建所有题目向量"""
    print_header("重建所有题目向量")
    
    vi = VectorIndex(db)
    
    confirm = input(f"\n⚠️  将重建所有题目的向量（耗时较长），确认继续？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    start_time = datetime.now()
    result = vi.rebuild_all(embedding_service, model_version)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ 重建完成!")
    print(f"   成功：{result['processed']} 题")
    print(f"   失败：{result['errors']} 题")
    print(f"   总计：{result['total']} 题")
    print(f"   耗时：{duration:.1f} 秒")
    print(f"   速度：{result['processed'] / duration:.1f} 题/秒")


def rebuild_missing(embedding_service, model_version: str):
    """重建未向量化的题目"""
    print_header("重建未向量化的题目")
    
    vi = VectorIndex(db)
    missing = vi.get_missing_embeddings()
    
    if not missing:
        print("\n✅ 所有题目已矢量化，无需处理")
        return
    
    print(f"\n📋 发现 {len(missing)} 题未矢量化")
    
    confirm = input(f"确认重建？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    start_time = datetime.now()
    processed = 0
    errors = 0
    
    for i, question in enumerate(missing):
        try:
            embedding = embedding_service.embed(question['content'])
            vi.update_embedding(
                question['id'],
                embedding,
                model_version,
                question['content'],
                None  # options 可能不存在
            )
            processed += 1
            
            if (i + 1) % 50 == 0:
                print(f"   进度：{i + 1}/{len(missing)} ({(i + 1) / len(missing) * 100:.1f}%)")
                
        except Exception as e:
            print(f"   ❌ 题目 {question['id']} 失败：{e}")
            errors += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ 重建完成!")
    print(f"   成功：{processed} 题")
    print(f"   失败：{errors} 题")
    print(f"   耗时：{duration:.1f} 秒")


def rebuild_mismatched(embedding_service, model_version: str):
    """重建模型版本不匹配的题目"""
    print_header("重建模型版本不匹配的题目")
    
    vi = VectorIndex(db)
    mismatched = vi.get_mismatched_embeddings(model_version)
    
    if not mismatched:
        print("\n✅ 所有题目模型版本匹配，无需处理")
        return
    
    print(f"\n📋 发现 {len(mismatched)} 题模型版本不匹配")
    print(f"   当前模型：{model_version}")
    
    # 显示版本分布
    versions = {}
    for q in mismatched:
        v = q.get('embedding_version', 'unknown')
        versions[v] = versions.get(v, 0) + 1
    
    print(f"\n📦 版本分布:")
    for v, count in versions.items():
        print(f"   - {v}: {count} 题")
    
    confirm = input(f"\n确认重建？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    start_time = datetime.now()
    processed = 0
    errors = 0
    
    for i, question in enumerate(mismatched):
        try:
            embedding = embedding_service.embed(question['content'])
            vi.update_embedding(
                question['id'],
                embedding,
                model_version,
                question['content'],
                None  # options 可能不存在
            )
            processed += 1
            
            if (i + 1) % 50 == 0:
                print(f"   进度：{i + 1}/{len(mismatched)} ({(i + 1) / len(mismatched) * 100:.1f}%)")
                
        except Exception as e:
            print(f"   ❌ 题目 {question['id']} 失败：{e}")
            errors += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ 重建完成!")
    print(f"   成功：{processed} 题")
    print(f"   失败：{errors} 题")
    print(f"   耗时：{duration:.1f} 秒")


def smart_rebuild(embedding_service, model_version: str):
    """智能重建（仅重建需要的题目）"""
    print_header("智能重建（仅重建需要的题目）")
    
    vi = VectorIndex(db)
    
    # 获取所有题目
    all_questions = db.fetch_all("SELECT id, content, options FROM questions")
    
    needs_update = []
    for q in all_questions:
        needs, reason = vi.needs_reembedding(
            q['id'], 
            q['content'], 
            q.get('options'),
            model_version
        )
        if needs:
            needs_update.append((q, reason))
    
    if not needs_update:
        print("\n✅ 所有题目无需重建！")
        print(f"   当前模型：{model_version}")
        print(f"   已矢量化：{db.fetch_one('SELECT COUNT(*) as c FROM questions WHERE embedding IS NOT NULL')['c']} 题")
        return
    
    # 按原因分类
    reasons = {}
    for _, reason in needs_update:
        reasons[reason] = reasons.get(reason, 0) + 1
    
    print(f"\n📋 需要重建的题目: {len(needs_update)} 题")
    for reason, count in reasons.items():
        print(f"   - {reason}: {count} 题")
    
    confirm = input(f"\n确认重建？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    start_time = datetime.now()
    processed = 0
    errors = 0
    
    for i, (question, reason) in enumerate(needs_update):
        try:
            embedding = embedding_service.embed(question['content'])
            vi.update_embedding(
                question['id'],
                embedding,
                model_version,
                question['content'],
                question.get('options')
            )
            processed += 1
            
            if (i + 1) % 50 == 0:
                print(f"   进度：{i + 1}/{len(needs_update)} ({(i + 1) / len(needs_update) * 100:.1f}%)")
        except Exception as e:
            print(f"   ❌ 题目 {question['id']} 失败：{e}")
            errors += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✅ 重建完成!")
    print(f"   成功：{processed} 题")
    print(f"   失败：{errors} 题")
    print(f"   耗时：{duration:.1f} 秒")
    if duration > 0:
        print(f"   速度：{processed / duration:.1f} 题/秒")


def main():
    parser = argparse.ArgumentParser(description='向量重建工具')
    parser.add_argument('--all', action='store_true', help='重建所有题目')
    parser.add_argument('--missing', action='store_true', help='仅重建未向量化的')
    parser.add_argument('--mismatch', action='store_true', help='仅重建版本不匹配的')
    parser.add_argument('--check', action='store_true', help='仅检查状态')
    parser.add_argument('--no-confirm', action='store_true', help='跳过确认提示')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # 检查状态模式
    if args.check:
        check_status()
        return
    
    # 初始化服务
    print("🔄 初始化服务...")
    try:
        config = AgentConfig._load_config()
        embedding_config = config.get('embedding', {})
        
        if not embedding_config:
            print("❌ 未配置 Embedding 服务，请先在设置中配置")
            return
        
        embedding_service = get_embedding_service(embedding_config)
        model_version = embedding_service.get_model_version()
        
        print(f"✅ 服务初始化成功")
        print(f"   模型：{model_version}")
        print(f"   API: {embedding_config.get('base_url', 'unknown')}")
        
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        print("\n请检查:")
        print("1. config/agent.json 配置文件是否存在")
        print("2. Embedding 服务配置是否正确")
        print("3. Ollama 服务是否运行（如果使用本地模型）")
        return
    
    # 执行重建
    if args.all:
        rebuild_all(embedding_service, model_version)
    elif args.missing:
        rebuild_missing(embedding_service, model_version)
    elif args.mismatch:
        rebuild_mismatched(embedding_service, model_version)
    else:
        # 默认智能重建
        smart_rebuild(embedding_service, model_version)
    
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
