-- 新的数据库结构
-- 满足：自定义分类、标签管理、完整题目结构

-- 1. 分类表（用户自定义）
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 标签表
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#667eea',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 题目表（新结构）
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,           -- 题干
    options TEXT,                    -- 选项（JSON数组，可为空）
    answer TEXT NOT NULL,            -- 答案
    explanation TEXT,                -- 解析（可为空）
    category_id TEXT,                -- 分类ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 4. 题目-标签关联表
CREATE TABLE question_tags (
    question_id TEXT,
    tag_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (question_id, tag_id),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_questions_category ON questions(category_id);
CREATE INDEX idx_questions_created ON questions(created_at);
CREATE INDEX idx_question_tags_question ON question_tags(question_id);
CREATE INDEX idx_question_tags_tag ON question_tags(tag_id);