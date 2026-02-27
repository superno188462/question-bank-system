// 题库管理系统主应用
const API_BASE = '/api';

// 全局状态
let currentCategoryId = null;
let categoryTreeData = [];
let currentQuestions = [];
let currentPage = 1;
let totalPages = 1;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    // 加载分类树
    await loadCategoryTree();
    
    // 加载题目列表
    await loadQuestions();
    
    // 绑定事件
    bindEvents();
    
    // 显示欢迎消息
    showToast('欢迎使用题库管理系统！', 'info');
}

// ============ 分类管理 ============

// 加载分类树
async function loadCategoryTree() {
    try {
        const treeContainer = document.getElementById('categoryTree');
        if (!treeContainer) {
            console.error('找不到categoryTree元素');
            return;
        }
        
        const response = await fetch(`${API_BASE}/categories/tree`);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`加载分类失败: ${response.status} - ${errorText}`);
        }
        
        categoryTreeData = await response.json();
        console.log('分类数据:', categoryTreeData);
        
        if (!Array.isArray(categoryTreeData)) {
            throw new Error('返回的数据格式不正确');
        }
        
        renderCategoryTree(categoryTreeData, treeContainer);
    } catch (error) {
        console.error('加载分类树失败:', error);
        showToast('加载分类失败: ' + error.message, 'error');
        // 显示错误信息在页面上
        const treeContainer = document.getElementById('categoryTree');
        if (treeContainer) {
            treeContainer.innerHTML = `<div style="color: red; padding: 10px;">加载失败: ${error.message}</div>`;
        }
    }
}

// 渲染分类树
function renderCategoryTree(categories, container, level = 0) {
    container.innerHTML = '';
    
    categories.forEach(cat => {
        const item = document.createElement('li');
        item.className = 'tree-item';
        
        const hasChildren = cat.children && cat.children.length > 0;
        
        item.innerHTML = `
            <div class="tree-toggle">
                <span class="tree-icon">${hasChildren ? '▶' : '•'}</span>
                <span class="tree-label ${cat.id === currentCategoryId ? 'active' : ''}" 
                      data-id="${cat.id}" 
                      onclick="selectCategory('${cat.id}', '${cat.name}')">
                    ${cat.name}
                </span>
                <div class="tree-actions">
                    <button class="tree-btn add" onclick="showAddCategoryModal('${cat.id}')" title="添加子分类">+</button>
                    <button class="tree-btn edit" onclick="showEditCategoryModal('${cat.id}', '${cat.name}')" title="编辑">✎</button>
                    <button class="tree-btn delete" onclick="deleteCategory('${cat.id}')" title="删除">×</button>
                </div>
            </div>
            ${hasChildren ? `<ul class="tree-children hidden"></ul>` : ''}
        `;
        
        container.appendChild(item);
        
        // 递归渲染子分类
        if (hasChildren) {
            const childrenContainer = item.querySelector('.tree-children');
            renderCategoryTree(cat.children, childrenContainer, level + 1);
            
            // 展开/收起功能
            const toggle = item.querySelector('.tree-icon');
            toggle.style.cursor = 'pointer';
            toggle.onclick = (e) => {
                e.stopPropagation();
                childrenContainer.classList.toggle('hidden');
                toggle.textContent = childrenContainer.classList.contains('hidden') ? '▶' : '▼';
            };
        }
    });
}

// 选择分类
function selectCategory(id, name) {
    currentCategoryId = id;
    
    // 更新UI
    document.querySelectorAll('.tree-label').forEach(el => el.classList.remove('active'));
    document.querySelector(`[data-id="${id}"]`)?.classList.add('active');
    
    // 更新面包屑
    updateBreadcrumb(id);
    
    // 加载该分类的题目（包含子分类）
    loadQuestions(id);
}

// 更新面包屑
async function updateBreadcrumb(categoryId) {
    const breadcrumb = document.getElementById('breadcrumb');
    
    if (!categoryId) {
        breadcrumb.innerHTML = '<span class="breadcrumb-current">全部题目</span>';
        return;
    }
    
    // 获取分类路径
    try {
        const response = await fetch(`${API_BASE}/categories/${categoryId}/path`);
        const path = await response.json();
        
        let html = '<span class="breadcrumb-item" onclick="selectCategory(null, \'全部\')">全部题目</span>';
        
        path.forEach((cat, index) => {
            html += '<span class="breadcrumb-separator">/</span>';
            if (index === path.length - 1) {
                html += `<span class="breadcrumb-current">${cat.name}</span>`;
            } else {
                html += `<span class="breadcrumb-item" onclick="selectCategory('${cat.id}', '${cat.name}')">${cat.name}</span>`;
            }
        });
        
        breadcrumb.innerHTML = html;
    } catch (error) {
        console.error('获取分类路径失败:', error);
    }
}

// 显示添加分类模态框
function showAddCategoryModal(parentId = null) {
    document.getElementById('categoryModalTitle').textContent = parentId ? '添加子分类' : '添加分类';
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryName').value = '';
    document.getElementById('categoryParentId').value = parentId || '';
    document.getElementById('categoryParentName').value = parentId ? '子分类' : '无（根分类）';
    document.getElementById('categoryDescription').value = '';
    document.getElementById('categoryModal').classList.add('active');
}

// 打开分类模态框（兼容HTML中的调用）
function openCategoryModal() {
    showAddCategoryModal(null);
}

// 显示编辑分类模态框
function showEditCategoryModal(id, name) {
    document.getElementById('categoryModalTitle').textContent = '编辑分类';
    document.getElementById('categoryId').value = id;
    document.getElementById('categoryName').value = name;
    document.getElementById('categoryParentId').value = '';
    document.getElementById('categoryParentName').value = '';
    document.getElementById('categoryDescription').value = '';
    document.getElementById('categoryModal').classList.add('active');
}

// 关闭分类模态框
function closeCategoryModal() {
    document.getElementById('categoryModal')?.classList.remove('active');
}

// 保存分类
async function saveCategory() {
    const id = document.getElementById('categoryId').value;
    const name = document.getElementById('categoryName').value.trim();
    const description = document.getElementById('categoryDescription').value.trim();
    const parentId = document.getElementById('categoryParentId').value;
    
    if (!name) {
        showToast('请输入分类名称', 'error');
        return;
    }
    
    try {
        const url = id ? `${API_BASE}/categories/${id}` : `${API_BASE}/categories`;
        const method = id ? 'PUT' : 'POST';
        const body = id ? { name } : { name, parent_id: parentId || null };
        
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) throw new Error('保存失败');
        
        closeModal('categoryModal');
        await loadCategoryTree();
        showToast(id ? '分类更新成功' : '分类创建成功', 'success');
    } catch (error) {
        console.error('保存分类失败:', error);
        showToast('保存失败: ' + error.message, 'error');
    }
}

// 删除分类
async function deleteCategory(id) {
    if (!confirm('确定要删除这个分类吗？其中的题目将移动到未分类。')) return;
    
    try {
        const response = await fetch(`${API_BASE}/categories/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('删除失败');
        
        await loadCategoryTree();
        if (currentCategoryId === id) {
            selectCategory(null, '全部');
        }
        showToast('分类删除成功', 'success');
    } catch (error) {
        console.error('删除分类失败:', error);
        showToast('删除失败: ' + error.message, 'error');
    }
}

// ============ 题目管理 ============

// 加载题目列表
async function loadQuestions(categoryId = null, page = 1) {
    try {
        let url = `${API_BASE}/questions?page=${page}&limit=10`;
        if (categoryId) {
            url += `&category_id=${categoryId}&include_children=true`;
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('加载题目失败');
        
        const data = await response.json();
        currentQuestions = data.questions || [];
        currentPage = data.page || 1;
        totalPages = data.total_pages || 1;
        
        renderQuestionList(currentQuestions);
        renderPagination();
    } catch (error) {
        console.error('加载题目失败:', error);
        document.getElementById('questionList').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <div class="empty-title">加载失败</div>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// 渲染题目列表
function renderQuestionList(questions) {
    const container = document.getElementById('questionList');
    
    if (questions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📝</div>
                <div class="empty-title">暂无题目</div>
                <p>点击"添加题目"创建第一个题目</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = questions.map(q => `
        <div class="question-card" data-id="${q.id}">
            <div class="question-header">
                <div class="question-title">${escapeHtml(q.content.substring(0, 100))}${q.content.length > 100 ? '...' : ''}</div>
                <div class="question-meta">
                    <span class="badge badge-category">${q.category_name || '未分类'}</span>
                    ${q.tags ? q.tags.map(t => `<span class="badge badge-tag">${escapeHtml(t)}</span>`).join('') : ''}
                </div>
            </div>
            <div class="question-content">${escapeHtml(q.content)}</div>
            ${renderOptionsPreview(q.options, q.answer)}
            <div class="question-actions">
                <button class="btn btn-sm btn-primary" onclick="viewQuestion('${q.id}')">查看详情</button>
                <button class="btn btn-sm btn-secondary" onclick="editQuestion('${q.id}')">编辑</button>
                <button class="btn btn-sm btn-danger" onclick="deleteQuestion('${q.id}')">删除</button>
            </div>
        </div>
    `).join('');
}

// 渲染选项预览
function renderOptionsPreview(options, answer) {
    if (!options || options.length === 0) return '';
    
    return `
        <div class="question-options">
            ${options.map((opt, idx) => `
                <div class="option-item ${opt === answer ? 'correct' : ''}">
                    ${String.fromCharCode(65 + idx)}. ${escapeHtml(opt)} ${opt === answer ? ' ✓' : ''}
                </div>
            `).join('')}
        </div>
    `;
}

// 渲染分页
function renderPagination() {
    const container = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // 上一页
    html += `<button class="page-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>上一页</button>`;
    
    // 页码
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += `<span>...</span>`;
        }
    }
    
    // 下一页
    html += `<button class="page-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>下一页</button>`;
    
    container.innerHTML = html;
}

// 切换页面
function changePage(page) {
    if (page < 1 || page > totalPages) return;
    loadQuestions(currentCategoryId, page);
}

// 搜索题目
async function searchQuestions() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        loadQuestions(currentCategoryId);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/questions/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('搜索失败');
        
        const questions = await response.json();
        renderQuestionList(questions);
        document.getElementById('pagination').innerHTML = '';
    } catch (error) {
        console.error('搜索失败:', error);
        showToast('搜索失败', 'error');
    }
}

// 查看题目详情
async function viewQuestion(id) {
    try {
        const response = await fetch(`${API_BASE}/questions/${id}`);
        if (!response.ok) throw new Error('加载失败');
        
        const q = await response.json();
        
        document.getElementById('viewQuestionContent').innerHTML = `
            <div class="question-content">${escapeHtml(q.content)}</div>
            ${q.options && q.options.length > 0 ? `
                <div class="question-options">
                    <strong>选项：</strong>
                    ${q.options.map((opt, idx) => `
                        <div class="option-item ${opt === q.answer ? 'correct' : ''}">
                            ${String.fromCharCode(65 + idx)}. ${escapeHtml(opt)} ${opt === q.answer ? ' ✓ 正确答案' : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            <div class="question-answer">
                <strong>答案：</strong>${escapeHtml(q.answer)}
            </div>
            ${q.explanation ? `
                <div class="question-explanation">
                    <div class="explanation-header">
                        <strong>解析：</strong>
                    </div>
                    ${escapeHtml(q.explanation)}
                </div>
            ` : `
                <div class="question-explanation">
                    <div class="explanation-header">
                        <strong>解析：</strong>
                        <button class="ai-parse-btn" onclick="generateAIExplanation('${q.id}')">
                            🤖 AI生成解析
                        </button>
                    </div>
                    <p style="color: #999;">暂无解析，可使用AI生成</p>
                </div>
            `}
            <div class="question-meta" style="margin-top: 15px;">
                <span class="badge badge-category">${q.category_name || '未分类'}</span>
                ${q.tags ? q.tags.map(t => `<span class="badge badge-tag">${escapeHtml(t)}</span>`).join('') : ''}
            </div>
        `;
        
        document.getElementById('viewQuestionModal').classList.add('active');
    } catch (error) {
        console.error('加载题目详情失败:', error);
        showToast('加载失败', 'error');
    }
}

// AI生成解析
async function generateAIExplanation(questionId) {
    showToast('正在生成解析...', 'info');
    
    try {
        const response = await fetch(`${API_BASE}/questions/${questionId}/ai-explanation`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('生成失败');
        
        const result = await response.json();
        
        // 刷新详情显示
        viewQuestion(questionId);
        showToast('解析生成成功', 'success');
    } catch (error) {
        console.error('AI生成解析失败:', error);
        showToast('生成失败: ' + error.message, 'error');
    }
}

// 显示添加题目模态框
function showAddQuestionModal() {
    document.getElementById('questionModalTitle').textContent = '添加题目';
    document.getElementById('questionId').value = '';
    document.getElementById('questionForm').reset();
    
    // 加载分类选择器
    loadCategorySelect();
    
    // 清空选项
    document.getElementById('optionsContainer').innerHTML = `
        <div class="option-row">
            <input type="text" class="option-input" placeholder="选项 A" data-index="0">
            <label class="option-correct">
                <input type="radio" name="correctOption" value="0"> 正确答案
            </label>
        </div>
        <div class="option-row">
            <input type="text" class="option-input" placeholder="选项 B" data-index="1">
            <label class="option-correct">
                <input type="radio" name="correctOption" value="1"> 正确答案
            </label>
        </div>
    `;
    
    document.getElementById('questionModal').classList.add('active');
}

// 加载分类下拉选择器
async function loadCategorySelect() {
    const select = document.getElementById('questionCategory');
    select.innerHTML = '<option value="">请选择分类</option>';
    
    function addOptions(categories, prefix = '') {
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = prefix + cat.name;
            select.appendChild(option);
            
            if (cat.children && cat.children.length > 0) {
                addOptions(cat.children, prefix + '　');
            }
        });
    }
    
    addOptions(categoryTreeData);
}

// 添加选项输入框
function addOptionInput() {
    const container = document.getElementById('optionsContainer');
    const index = container.querySelectorAll('.option-row').length;
    
    const row = document.createElement('div');
    row.className = 'option-row';
    row.innerHTML = `
        <input type="text" class="option-input" placeholder="选项 ${String.fromCharCode(65 + index)}" data-index="${index}">
        <label class="option-correct">
            <input type="radio" name="correctOption" value="${index}"> 正确答案
        </label>
        <button type="button" class="btn btn-sm btn-danger" onclick="this.parentElement.remove()">删除</button>
    `;
    
    container.appendChild(row);
}

// 编辑题目
async function editQuestion(id) {
    try {
        const response = await fetch(`${API_BASE}/questions/${id}`);
        if (!response.ok) throw new Error('加载失败');
        
        const q = await response.json();
        
        document.getElementById('questionModalTitle').textContent = '编辑题目';
        document.getElementById('questionId').value = q.id;
        document.getElementById('questionContent').value = q.content;
        document.getElementById('questionAnswer').value = q.answer;
        document.getElementById('questionExplanation').value = q.explanation || '';
        
        // 加载并设置分类
        await loadCategorySelect();
        document.getElementById('questionCategory').value = q.category_id || '';
        
        // 加载选项
        const container = document.getElementById('optionsContainer');
        container.innerHTML = '';
        
        if (q.options && q.options.length > 0) {
            q.options.forEach((opt, idx) => {
                const isCorrect = opt === q.answer;
                const row = document.createElement('div');
                row.className = 'option-row';
                row.innerHTML = `
                    <input type="text" class="option-input" placeholder="选项 ${String.fromCharCode(65 + idx)}" 
                           data-index="${idx}" value="${escapeHtml(opt)}">
                    <label class="option-correct">
                        <input type="radio" name="correctOption" value="${idx}" ${isCorrect ? 'checked' : ''}> 正确答案
                    </label>
                    ${idx > 1 ? `<button type="button" class="btn btn-sm btn-danger" onclick="this.parentElement.remove()">删除</button>` : ''}
                `;
                container.appendChild(row);
            });
        }
        
        document.getElementById('questionModal').classList.add('active');
    } catch (error) {
        console.error('加载题目失败:', error);
        showToast('加载失败', 'error');
    }
}

// 保存题目
async function saveQuestion() {
    const id = document.getElementById('questionId').value;
    const content = document.getElementById('questionContent').value.trim();
    const categoryId = document.getElementById('questionCategory').value;
    const explanation = document.getElementById('questionExplanation').value.trim();
    
    // 收集选项
    const optionInputs = document.querySelectorAll('.option-input');
    const options = Array.from(optionInputs).map(input => input.value.trim()).filter(v => v);
    
    // 获取正确答案
    const correctIndex = document.querySelector('input[name="correctOption"]:checked')?.value;
    const answer = correctIndex !== undefined ? options[parseInt(correctIndex)] : '';
    
    if (!content) {
        showToast('请输入题干', 'error');
        return;
    }
    if (!answer) {
        showToast('请设置正确答案', 'error');
        return;
    }
    if (!categoryId) {
        showToast('请选择分类', 'error');
        return;
    }
    
    const data = {
        content,
        options,
        answer,
        explanation: explanation || '',
        category_id: categoryId
    };
    
    try {
        const url = id ? `${API_BASE}/questions/${id}` : `${API_BASE}/questions`;
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || '保存失败');
        }
        
        closeModal('questionModal');
        await loadQuestions(currentCategoryId, currentPage);
        showToast(id ? '题目更新成功' : '题目创建成功', 'success');
    } catch (error) {
        console.error('保存题目失败:', error);
        showToast('保存失败: ' + error.message, 'error');
    }
}

// 删除题目
async function deleteQuestion(id) {
    if (!confirm('确定要删除这道题目吗？此操作不可恢复。')) return;
    
    try {
        const response = await fetch(`${API_BASE}/questions/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('删除失败');
        
        await loadQuestions(currentCategoryId, currentPage);
        showToast('题目删除成功', 'success');
    } catch (error) {
        console.error('删除题目失败:', error);
        showToast('删除失败', 'error');
    }
}

// ============ 智能问答 ============

// 发送问题
async function sendQuestion() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    
    if (!question) return;
    
    // 添加用户消息
    addChatMessage(question, 'user');
    input.value = '';
    
    try {
        const response = await fetch(`${API_BASE}/qa/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) throw new Error('请求失败');
        
        const result = await response.json();
        
        // 显示回答和相关题目
        let botMessage = result.answer;
        
        if (result.related_questions && result.related_questions.length > 0) {
            botMessage += '\n\n📚 相关题目推荐：';
            result.related_questions.forEach((q, idx) => {
                botMessage += `\n${idx + 1}. ${q.content.substring(0, 50)}...`;
            });
        }
        
        addChatMessage(botMessage, 'bot');
        
        // 如果有预备题目，刷新列表
        if (result.pending_question) {
            loadPendingQuestions();
        }
    } catch (error) {
        console.error('问答请求失败:', error);
        addChatMessage('抱歉，处理您的问题时出现错误。', 'bot');
    }
}

// 添加聊天消息
function addChatMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `<div class="message-bubble">${escapeHtml(text).replace(/\n/g, '<br>')}</div>`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// 加载预备题目
async function loadPendingQuestions() {
    try {
        const response = await fetch(`${API_BASE}/qa/pending`);
        if (!response.ok) throw new Error('加载失败');
        
        const questions = await response.json();
        const tbody = document.getElementById('pendingTableBody');
        
        if (questions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:20px;">暂无预备题目</td></tr>';
            return;
        }
        
        tbody.innerHTML = questions.map(q => `
            <tr>
                <td>${escapeHtml(q.content.substring(0, 50))}${q.content.length > 50 ? '...' : ''}</td>
                <td>${escapeHtml(q.answer)}</td>
                <td>${new Date(q.created_at).toLocaleString()}</td>
                <td class="pending-actions">
                    <button class="btn btn-sm btn-primary" onclick="viewPendingQuestion('${q.id}')">查看</button>
                    <button class="btn btn-sm btn-secondary" onclick="approvePendingQuestion('${q.id}')">入库</button>
                    <button class="btn btn-sm btn-danger" onclick="rejectPendingQuestion('${q.id}')">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('加载预备题目失败:', error);
    }
}

// 批准预备题目入库
async function approvePendingQuestion(id) {
    try {
        const response = await fetch(`${API_BASE}/qa/pending/${id}/approve`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('操作失败');
        
        loadPendingQuestions();
        loadQuestions();
        showToast('题目已入库', 'success');
    } catch (error) {
        console.error('入库失败:', error);
        showToast('入库失败', 'error');
    }
}

// 拒绝/删除预备题目
async function rejectPendingQuestion(id) {
    if (!confirm('确定要删除这道预备题目吗？')) return;
    
    try {
        const response = await fetch(`${API_BASE}/qa/pending/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('删除失败');
        
        loadPendingQuestions();
        showToast('已删除', 'success');
    } catch (error) {
        console.error('删除失败:', error);
        showToast('删除失败', 'error');
    }
}

// ============ 工具函数 ============

// 绑定事件
function bindEvents() {
    // 标签页切换
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;
            switchTab(tabId);
        });
    });
    
    // 搜索框回车
    document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchQuestions();
    });
    
    // 聊天输入框回车
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    });
}

// 切换标签页
function switchTab(tabId) {
    // 更新导航
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`)?.classList.add('active');
    
    // 更新内容
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`${tabId}Tab`)?.classList.add('active');
    
    // 特殊处理
    if (tabId === 'qa') {
        loadPendingQuestions();

// ============ 工具函数 ============

// 绑定事件
function bindEvents() {
    // 标签页切换
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;
            switchTab(tabId);
        });
    });
    
    // 搜索框回车
    document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchQuestions();
    });
    
    // 聊天输入框回车
    document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    });
}

// 切换标签页
function switchTab(tabId) {
    // 更新导航
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabId}"]`)?.classList.add('active');
    
    // 更新内容
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`tab-${tabId}`)?.classList.add('active');
    
    // 特殊处理
    if (tabId === 'pending') {
        loadPendingQuestions();
    }
    if (tabId === 'categories') {
        loadCategoryManagementTree();
    }
}

// 加载分类管理树
async function loadCategoryManagementTree() {
    const container = document.getElementById('categoryManagementTree');
    if (!container) return;
    
    try {
        const response = await fetch(`${API_BASE}/categories/tree`);
        if (!response.ok) throw new Error('加载失败');
        
        const categories = await response.json();
        renderCategoryManagementTree(categories, container);
    } catch (error) {
        console.error('加载分类管理树失败:', error);
        container.innerHTML = '<div style="color: red; padding: 10px;">加载失败</div>';
    }
}

// 渲染分类管理树
function renderCategoryManagementTree(categories, container, level = 0) {
    if (level === 0) container.innerHTML = '';
    
    categories.forEach(cat => {
        const item = document.createElement('div');
        item.className = 'tree-item';
        item.style.paddingLeft = `${level * 20}px`;
        item.innerHTML = `
            <span>${cat.name}</span>
            <div class="tree-actions">
                <button class="btn btn-sm" onclick="showAddCategoryModal('${cat.id}')">+</button>
                <button class="btn btn-sm" onclick="showEditCategoryModal('${cat.id}', '${cat.name}')">编辑</button>
                <button class="btn btn-sm btn-danger" onclick="deleteCategory('${cat.id}')">删除</button>
            </div>
        `;
        container.appendChild(item);
        
        if (cat.children && cat.children.length > 0) {
            renderCategoryManagementTree(cat.children, container, level + 1);
        }
    });
}

// 关闭模态框
function closeModal(modalId) {
    document.getElementById(modalId)?.classList.remove('active');
}

// 关闭题目模态框（兼容HTML调用）
function closeQuestionModal() {
    closeModal('questionModal');
}

// 关闭分类模态框（兼容HTML调用）
function closeCategoryModal() {
    closeModal('categoryModal');
}

// 关闭详情模态框（兼容HTML调用）
function closeDetailModal() {
    closeModal('detailModal');
}

// 添加选项行（兼容HTML调用）
function addOptionRow() {
    addOptionInput();
}

// 发送聊天消息（兼容HTML调用）
function sendChatMessage() {
    sendQuestion();
}

// 显示提示
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// HTML转义
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 点击模态框外部关闭
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('active');
    }
});
