"""
数据库仓库层

实现数据访问模式，包含：
1. 分类仓库
2. 标签仓库
3. 题目仓库
4. 预备题目仓库（AI 提取）
5. 问答日志仓库（智能问答）
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import datetime
import json
import uuid

from core.models import (
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate,
    Question, QuestionCreate, QuestionUpdate, QuestionWithTags,
    StagingQuestion, StagingQuestionCreate, StagingQuestionUpdate
)
from core.database.connection import db, transaction


T = TypeVar('T')
ID = TypeVar('ID')


class Repository(Generic[T, ID], ABC):
    """通用仓库抽象基类"""
    
    @abstractmethod
    def create(self, entity: Any) -> T:
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        pass
    
    @abstractmethod
    def update(self, entity_id: ID, update_data: Any) -> Optional[T]:
        pass
    
    @abstractmethod
    def delete(self, entity_id: ID) -> bool:
        pass
    
    @abstractmethod
    def search(self, keyword: str) -> List[T]:
        pass


class CategoryRepository(Repository[Category, str]):
    """分类仓库"""
    
    def create(self, category_data: CategoryCreate) -> Category:
        """创建分类（支持层级）"""
        category_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        sql = """
        INSERT INTO categories (id, name, description, parent_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        with transaction():
            db.execute(sql, (
                category_id,
                category_data.name,
                category_data.description or "",
                category_data.parent_id,
                now,
                now
            ))
        
        return self.get_by_id(category_id)
    
    def get_by_id(self, category_id: str) -> Optional[Category]:
        """根据 ID 获取分类"""
        sql = "SELECT * FROM categories WHERE id = ?"
        row = db.fetch_one(sql, (category_id,))
        
        if not row:
            return None
        
        return Category(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            parent_id=row['parent_id'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def get_all(self) -> List[Category]:
        """获取所有分类"""
        sql = "SELECT * FROM categories ORDER BY created_at DESC"
        rows = db.fetch_all(sql)
        
        return [
            Category(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                parent_id=row['parent_id'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            for row in rows
        ]
    
    def update(self, category_id: str, update_data: CategoryUpdate) -> Optional[Category]:
        """更新分类（支持移动层级）"""
        # 构建更新字段
        updates = []
        params = []
        
        if update_data.name is not None:
            updates.append("name = ?")
            params.append(update_data.name)
        
        if update_data.description is not None:
            updates.append("description = ?")
            params.append(update_data.description)
        
        if update_data.parent_id is not None:
            updates.append("parent_id = ?")
            params.append(update_data.parent_id)
        
        if not updates:
            return self.get_by_id(category_id)
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(category_id)
        
        sql = f"UPDATE categories SET {', '.join(updates)} WHERE id = ?"
        
        with transaction():
            db.execute(sql, tuple(params))
        
        return self.get_by_id(category_id)
    
    def delete(self, category_id: str) -> bool:
        """删除分类"""
        sql = "DELETE FROM categories WHERE id = ?"
        
        with transaction():
            cursor = db.execute(sql, (category_id,))
            return cursor.rowcount > 0
    
    def search(self, keyword: str) -> List[Category]:
        """搜索分类"""
        sql = """
        SELECT * FROM categories 
        WHERE name LIKE ? OR description LIKE ?
        ORDER BY created_at DESC
        """
        search_term = f"%{keyword}%"
        rows = db.fetch_all(sql, (search_term, search_term))
        
        return [
            Category(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            for row in rows
        ]


class TagRepository(Repository[Tag, str]):
    """标签仓库"""
    
    def create(self, tag_data: TagCreate) -> Tag:
        """创建标签"""
        tag_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        sql = """
        INSERT INTO tags (id, name, color, created_at)
        VALUES (?, ?, ?, ?)
        """
        
        with transaction():
            db.execute(sql, (
                tag_id,
                tag_data.name,
                tag_data.color,
                now
            ))
        
        return self.get_by_id(tag_id)
    
    def get_by_id(self, tag_id: str) -> Optional[Tag]:
        """根据 ID 获取标签"""
        sql = "SELECT * FROM tags WHERE id = ?"
        row = db.fetch_one(sql, (tag_id,))
        
        if not row:
            return None
        
        return Tag(
            id=row['id'],
            name=row['name'],
            color=row['color'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    def get_all(self) -> List[Tag]:
        """获取所有标签"""
        sql = "SELECT * FROM tags ORDER BY created_at DESC"
        rows = db.fetch_all(sql)
        
        return [
            Tag(
                id=row['id'],
                name=row['name'],
                color=row['color'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
            for row in rows
        ]
    
    def update(self, tag_id: str, update_data: Any) -> Optional[Tag]:
        """标签暂不支持更新，直接返回原标签"""
        return self.get_by_id(tag_id)
    
    def delete(self, tag_id: str) -> bool:
        """删除标签"""
        # 先删除题目标签关联
        with transaction():
            sql1 = "DELETE FROM question_tags WHERE tag_id = ?"
            db.execute(sql1, (tag_id,))
            
            sql2 = "DELETE FROM tags WHERE id = ?"
            cursor = db.execute(sql2, (tag_id,))
            
            return cursor.rowcount > 0
    
    def search(self, keyword: str) -> List[Tag]:
        """搜索标签"""
        sql = "SELECT * FROM tags WHERE name LIKE ? ORDER BY created_at DESC"
        search_term = f"%{keyword}%"
        rows = db.fetch_all(sql, (search_term,))
        
        return [
            Tag(
                id=row['id'],
                name=row['name'],
                color=row['color'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
            for row in rows
        ]


class QuestionRepository(Repository[Question, str]):
    """题目仓库"""
    
    def create(self, question_data: QuestionCreate) -> Question:
        """创建题目"""
        question_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # 序列化选项（确保是列表）
        options = question_data.options or []
        options_json = json.dumps(options)
        
        sql = """
        INSERT INTO questions (id, content, options, answer, explanation, category_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with transaction():
            db.execute(sql, (
                question_id,
                question_data.content,
                options_json,
                question_data.answer,
                question_data.explanation,
                question_data.category_id,
                now,
                now
            ))
        
        return self.get_by_id(question_id)
    
    def get_by_id(self, question_id: str) -> Optional[Question]:
        """根据 ID 获取题目"""
        sql = "SELECT * FROM questions WHERE id = ?"
        row = db.fetch_one(sql, (question_id,))
        
        if not row:
            return None
        
        # 解析选项（确保返回列表）
        options = []
        if row['options']:
            try:
                options = json.loads(row['options'])
                if not isinstance(options, list):
                    options = []
            except:
                options = []
        
        # 获取标签
        tags = self.get_question_tags(question_id)
        
        return Question(
            id=row['id'],
            content=row['content'],
            options=options,
            answer=row['answer'],
            explanation=row['explanation'],
            category_id=row['category_id'],
            tags=tags,
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def get_all(self, 
                category_id: Optional[str] = None,
                tag_id: Optional[str] = None,
                keyword: Optional[str] = None,
                page: int = 1,
                limit: int = 20) -> Dict[str, Any]:
        """获取所有题目（支持筛选和分页）"""
        # 构建查询条件
        conditions = []
        params = []
        
        if category_id:
            conditions.append("q.category_id = ?")
            params.append(category_id)
        
        if keyword:
            conditions.append("(q.content LIKE ? OR q.answer LIKE ? OR q.explanation LIKE ?)")
            search_term = f"%{keyword}%"
            params.extend([search_term, search_term, search_term])
        
        # 如果有标签筛选，需要连接 question_tags 表
        if tag_id:
            base_sql = """
            SELECT q.* FROM questions q
            INNER JOIN question_tags qt ON q.id = qt.question_id
            WHERE qt.tag_id = ?
            """
            if conditions:
                base_sql += " AND " + " AND ".join(conditions)
                params = [tag_id] + params
            else:
                params = [tag_id]
        else:
            base_sql = "SELECT q.* FROM questions q"
            if conditions:
                base_sql += " WHERE " + " AND ".join(conditions)
        
        # 添加排序
        base_sql += " ORDER BY q.created_at DESC"
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as total FROM ({base_sql})"
        total_row = db.fetch_one(count_sql, tuple(params))
        total = total_row['total'] if total_row else 0
        
        # 添加分页
        offset = (page - 1) * limit
        paginated_sql = f"{base_sql} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # 执行查询
        rows = db.fetch_all(paginated_sql, tuple(params))
        
        # 转换为模型
        questions = []
        for row in rows:
            # 解析选项
            options = None
            if row['options']:
                try:
                    options = json.loads(row['options'])
                except:
                    options = []
            
            # 获取标签
            tags = self.get_question_tags(row['id'])
            
            questions.append(Question(
                id=row['id'],
                content=row['content'],
                options=options,
                answer=row['answer'],
                explanation=row['explanation'],
                category_id=row['category_id'],
                tags=tags,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            ))
        
        # 计算总页数
        pages = (total + limit - 1) // limit
        
        return {
            "data": questions,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    
    def update(self, question_id: str, update_data: QuestionUpdate) -> Optional[Question]:
        """更新题目"""
        # 构建更新字段
        updates = []
        params = []
        
        if update_data.content is not None:
            updates.append("content = ?")
            params.append(update_data.content)
        
        if update_data.options is not None:
            options_json = json.dumps(update_data.options) if update_data.options else None
            updates.append("options = ?")
            params.append(options_json)
        
        if update_data.answer is not None:
            updates.append("answer = ?")
            params.append(update_data.answer)
        
        if update_data.explanation is not None:
            updates.append("explanation = ?")
            params.append(update_data.explanation)
        
        if update_data.category_id is not None:
            updates.append("category_id = ?")
            params.append(update_data.category_id)
        
        if not updates:
            return self.get_by_id(question_id)
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(question_id)
        
        sql = f"UPDATE questions SET {', '.join(updates)} WHERE id = ?"
        
        with transaction():
            db.execute(sql, tuple(params))
        
        return self.get_by_id(question_id)
    
    def delete(self, question_id: str) -> bool:
        """删除题目"""
        with transaction():
            # 先删除题目标签关联
            sql1 = "DELETE FROM question_tags WHERE question_id = ?"
            db.execute(sql1, (question_id,))
            
            # 再删除题目
            sql2 = "DELETE FROM questions WHERE id = ?"
            cursor = db.execute(sql2, (question_id,))
            
            return cursor.rowcount > 0
    
    def search(self, keyword: str) -> List[Question]:
        """搜索题目"""
        result = self.get_all(keyword=keyword, page=1, limit=100)
        return result["data"]
    
    def get_question_tags(self, question_id: str) -> List[Tag]:
        """获取题目的标签"""
        sql = """
        SELECT t.* FROM tags t
        INNER JOIN question_tags qt ON t.id = qt.tag_id
        WHERE qt.question_id = ?
        ORDER BY t.created_at DESC
        """
        rows = db.fetch_all(sql, (question_id,))
        
        return [
            Tag(
                id=row['id'],
                name=row['name'],
                color=row['color'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
            for row in rows
        ]
    
    def add_tag(self, question_id: str, tag_id: str) -> bool:
        """为题目添加标签"""
        # 检查是否已存在
        check_sql = """
        SELECT COUNT(*) as count FROM question_tags 
        WHERE question_id = ? AND tag_id = ?
        """
        row = db.fetch_one(check_sql, (question_id, tag_id))
        
        if row and row['count'] > 0:
            return True  # 已存在，返回成功
        
        # 添加关联
        sql = "INSERT INTO question_tags (question_id, tag_id) VALUES (?, ?)"
        
        try:
            with transaction():
                db.execute(sql, (question_id, tag_id))
            return True
        except:
            return False
    
    def add_tags(self, question_id: str, tag_ids: List[str]) -> bool:
        """为题目添加多个标签"""
        try:
            with transaction():
                for tag_id in tag_ids:
                    self.add_tag(question_id, tag_id)
            return True
        except:
            return False
    
    def remove_tag(self, question_id: str, tag_id: str) -> bool:
        """从题目移除标签"""
        sql = "DELETE FROM question_tags WHERE question_id = ? AND tag_id = ?"
        
        with transaction():
            cursor = db.execute(sql, (question_id, tag_id))
            return cursor.rowcount > 0
    
    def get_by_category(self, category_id: str) -> List[Question]:
        """获取指定分类下的题目"""
        result = self.get_all(category_id=category_id, page=1, limit=1000)
        return result["data"]
    
    def get_by_tag(self, tag_id: str) -> List[Question]:
        """获取指定标签下的题目"""
        result = self.get_all(tag_id=tag_id, page=1, limit=1000)
        return result["data"]


class StagingQuestionRepository:
    """预备题目数据访问（AI 提取）"""
    
    @staticmethod
    def create(question_data: Dict[str, Any]) -> int:
        """创建预备题目"""
        sql = """
        INSERT INTO staging_questions 
        (source_type, source_file, content, type, options, answer, explanation, 
         category_id, tags, confidence, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        now = datetime.now().isoformat()
        
        result = db.execute(sql, (
            question_data.get('source_type', 'image'),
            question_data.get('source_file'),
            question_data.get('content', ''),
            question_data.get('type', 'single_choice'),
            json.dumps(question_data.get('options', [])),
            question_data.get('answer', ''),
            question_data.get('explanation', ''),
            question_data.get('category_id'),
            json.dumps(question_data.get('tags', [])),
            question_data.get('confidence', 1.0),
            'pending',
            now
        ))
        
        return result.lastrowid
    
    @staticmethod
    def create_batch(questions: List[Dict[str, Any]]) -> List[int]:
        """批量创建预备题目"""
        ids = []
        for q in questions:
            q_id = StagingQuestionRepository.create(q)
            ids.append(q_id)
        return ids
    
    @staticmethod
    def get_all(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取预备题目列表"""
        if status:
            sql = """
            SELECT * FROM staging_questions 
            WHERE status = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
            """
            rows = db.fetch_all(sql, (status, limit, offset))
        else:
            sql = """
            SELECT * FROM staging_questions 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
            """
            rows = db.fetch_all(sql, (limit, offset))
        
        return [StagingQuestionRepository._row_to_dict(row) for row in rows]
    
    @staticmethod
    def get_count(status: Optional[str] = None) -> int:
        """获取预备题目数量"""
        if status:
            sql = "SELECT COUNT(*) as count FROM staging_questions WHERE status = ?"
            result = db.fetch_one(sql, (status,))
        else:
            sql = "SELECT COUNT(*) as count FROM staging_questions"
            result = db.fetch_one(sql)
        
        return result['count'] if result else 0
    
    @staticmethod
    def get_by_id(q_id: int) -> Optional[Dict]:
        """根据 ID 获取预备题目"""
        sql = "SELECT * FROM staging_questions WHERE id = ?"
        row = db.fetch_one(sql, (q_id,))
        
        if row:
            return StagingQuestionRepository._row_to_dict(row)
        return None
    
    @staticmethod
    def update(q_id: int, update_data: Dict[str, Any]) -> bool:
        """更新预备题目"""
        fields = []
        values = []
        
        allowed_fields = ['content', 'type', 'options', 'answer', 'explanation', 
                         'category_id', 'tags', 'status', 'reviewed_at', 'reviewed_by']
        
        for field in allowed_fields:
            if field in update_data:
                fields.append(f"{field} = ?")
                value = update_data[field]
                if field in ['options', 'tags'] and isinstance(value, list):
                    value = json.dumps(value)
                values.append(value)
        
        if not fields:
            return False
        
        values.append(q_id)
        sql = f"UPDATE staging_questions SET {', '.join(fields)} WHERE id = ?"
        db.execute(sql, values)
        return True
    
    @staticmethod
    def approve(q_id: int, reviewed_by: str = "system") -> bool:
        """审核通过预备题目"""
        return StagingQuestionRepository.update(q_id, {
            'status': 'approved',
            'reviewed_at': datetime.now().isoformat(),
            'reviewed_by': reviewed_by
        })
    
    @staticmethod
    def reject(q_id: int, reviewed_by: str = "system") -> bool:
        """审核拒绝预备题目"""
        return StagingQuestionRepository.update(q_id, {
            'status': 'rejected',
            'reviewed_at': datetime.now().isoformat(),
            'reviewed_by': reviewed_by
        })
    
    @staticmethod
    def delete(q_id: int) -> bool:
        """删除预备题目"""
        sql = "DELETE FROM staging_questions WHERE id = ?"
        db.execute(sql, (q_id,))
        return True
    
    @staticmethod
    def _row_to_dict(row: Dict) -> Dict:
        """将数据库行转换为字典"""
        return {
            'id': row['id'],
            'source_type': row['source_type'],
            'source_file': row['source_file'],
            'content': row['content'],
            'type': row['type'],
            'options': json.loads(row['options']) if row['options'] else [],
            'answer': row['answer'],
            'explanation': row['explanation'],
            'category_id': row['category_id'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'confidence': row['confidence'],
            'status': row['status'],
            'created_at': row['created_at'],
            'reviewed_at': row['reviewed_at'],
            'reviewed_by': row['reviewed_by']
        }


class QALogRepository:
    """问答日志数据访问（智能问答）"""
    
    @staticmethod
    def create(log_data: Dict[str, Any]) -> int:
        """创建问答日志"""
        sql = """
        INSERT INTO qa_logs 
        (user_question, ai_answer, related_question_ids, suggested_question_id, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        
        now = datetime.now().isoformat()
        
        result = db.execute(sql, (
            log_data.get('user_question', ''),
            log_data.get('ai_answer', ''),
            json.dumps(log_data.get('related_question_ids', [])),
            log_data.get('suggested_question_id'),
            now
        ))
        
        return result.lastrowid
    
    @staticmethod
    def get_all(limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取问答日志列表"""
        sql = """
        SELECT * FROM qa_logs 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
        """
        rows = db.fetch_all(sql, (limit, offset))
        
        return [QALogRepository._row_to_dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(log_id: int) -> Optional[Dict]:
        """根据 ID 获取问答日志"""
        sql = "SELECT * FROM qa_logs WHERE id = ?"
        row = db.fetch_one(sql, (log_id,))
        
        if row:
            return QALogRepository._row_to_dict(row)
        return None
    
    @staticmethod
    def _row_to_dict(row: Dict) -> Dict:
        """将数据库行转换为字典"""
        return {
            'id': row['id'],
            'user_question': row['user_question'],
            'ai_answer': row['ai_answer'],
            'related_question_ids': json.loads(row['related_question_ids']) if row['related_question_ids'] else [],
            'suggested_question_id': row['suggested_question_id'],
            'created_at': row['created_at']
        }


# 创建仓库实例
category_repo = CategoryRepository()
tag_repo = TagRepository()
question_repo = QuestionRepository()
