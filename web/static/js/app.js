// 题库管理系统主应用
const API_BASE = '/api';

// 全局状态
let currentCategoryId = null;
let categoryTreeData = [];
let currentQuestions = [];
let currentPage = 1;
let totalPages = 1;
let currentViewQuestionId = null; // 当前查看的题目 ID
let currentViewQuestionType = 'normal'; // 当前查看的题目类型：'normal' 或 'staging'

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    // 加载分类树
    await refreshAllCategoryTrees();
    
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
        const response = await fetch(`${API_BASE}/categories/${categoryId}/breadcrumb`);
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
        
        // 刷新所有分类树视图
        await refreshAllCategoryTrees();
        
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
        
        await refreshAllCategoryTrees();
        if (currentCategoryId === id) {
            selectCategory(null, '全部');
        }
        showToast('分类删除成功', 'success');
    } catch (error) {
        console.error('删除分类失败:', error);
        showToast('删除失败: ' + error.message, 'error');
    }
}

// 刷新所有分类树视图
async function refreshAllCategoryTrees() {
    // 刷新题目页面的分类树
    await loadCategoryTree();
    
    // 刷新分类管理页面的分类树
    await loadCategoryManagementTree();
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
        currentQuestions = data.data || [];
        currentPage = data.page || 1;
        totalPages = data.pages || 1;
        
        renderQuestionList(currentQuestions);
        highlightCodeBlocks(); // 高亮代码块
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
                <div class="question-meta">
                    <span class="badge badge-category">${q.category_name || '未分类'}</span>
                    ${q.tags ? q.tags.map(t => `<span class="badge badge-tag">${escapeHtml(t)}</span>`).join('') : ''}
                </div>
            </div>
            <div class="question-content">${renderMarkdown(q.content)}</div>
            ${renderOptionsPreview(q.options, q.answer)}
            <div class="question-actions">
                <button class="btn btn-sm btn-primary" onclick="viewQuestion('${q.id}')">查看详情</button>
                <button class="btn btn-sm btn-secondary" onclick="editQuestion('${q.id}')">编辑</button>
                <button class="btn btn-sm btn-danger" onclick="deleteQuestion('${q.id}')">删除</button>
            </div>
        </div>
    `).join('');
    
    // 高亮代码块
    setTimeout(() => highlightCodeBlocks(), 100);
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
        const response = await fetch(`${API_BASE}/questions/search/keyword?keyword=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('搜索失败');
        
        const result = await response.json();
        currentQuestions = result.data || [];
        currentPage = result.page || 1;
        totalPages = result.pages || 1;
        
        renderQuestionList(currentQuestions);
        renderPagination();
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
        
        // 保存当前查看的题目 ID 和类型
        currentViewQuestionId = id;
        currentViewQuestionType = 'normal';
        
        document.getElementById('detailContent').innerHTML = `
            <div class="question-content">${renderMarkdown(q.content)}</div>
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
        
        // 高亮代码块
        setTimeout(() => highlightCodeBlocks(), 100);
        document.getElementById('detailModal').classList.add('active');
    } catch (error) {
        console.error('加载题目详情失败:', error);
        showToast('加载失败', 'error');
    }
}

// AI 生成解析
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
        console.error('AI 生成解析失败:', error);
        showToast('生成失败：' + error.message, 'error');
    }
}

// AI 生成解析（从表单调用，预留接口）
async function generateAIExplanationFromForm() {
    const content = document.getElementById('questionContent').value.trim();
    
    if (!content) {
        showToast('请先输入题干内容', 'warning');
        return;
    }
    
    // TODO: 实现 AI 生成解析功能
    showToast('AI 解析功能开发中，敬请期待...', 'info');
}
// 显示添加题目模态框
function showAddQuestionModal() {
    document.getElementById('questionModalTitle').textContent = '添加题目';
    document.getElementById('questionId').value = '';
    document.getElementById('questionForm').reset();
    
    // 加载分类选择器
    loadCategorySelect();
    
    // 清空选项（填空题只需一个选项，选择题可添加多个）
    document.getElementById('optionsEditor').innerHTML = `
        <div class="option-row">
            <input type="text" class="option-input" placeholder="选项 A / 填空题答案" data-index="0">
            <label class="option-correct">
                <input type="radio" name="correctOption" value="0" checked> 正确答案
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
    const container = document.getElementById('optionsEditor');
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

// 编辑预备题目
async function editStagingQuestion(id) {
    try {
        const response = await fetch(`${API_BASE}/agent/staging/${id}`);
        if (!response.ok) throw new Error('加载失败');
        
        const result = await response.json();
        if (!result.success) throw new Error(result.message || '加载失败');
        
        const q = result.data;
        
        document.getElementById('questionModalTitle').textContent = '编辑预备题目';
        document.getElementById('questionId').value = q.id;
        document.getElementById('questionId').dataset.type = 'staging'; // 标记为预备题目
        document.getElementById('questionContent').value = q.content;
        document.getElementById('questionExplanation').value = q.explanation || '';
        
        // 加载并设置分类
        await loadCategorySelect();
        document.getElementById('questionCategory').value = q.category_id || '';
        
        // 加载选项
        const container = document.getElementById('optionsEditor');
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
        } else {
            // 填空题：只有一个答案选项
            container.innerHTML = `
                <div class="option-row">
                    <input type="text" class="option-input" placeholder="填空题答案" 
                           data-index="0" value="${escapeHtml(q.answer)}">
                    <label class="option-correct">
                        <input type="radio" name="correctOption" value="0" checked> 正确答案
                    </label>
                </div>
            `;
        }
        
        document.getElementById('questionModal').classList.add('active');
    } catch (error) {
        console.error('加载预备题目失败:', error);
        showToast('加载失败', 'error');
    }
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
        document.getElementById('questionExplanation').value = q.explanation || '';
        
        // 加载并设置分类
        await loadCategorySelect();
        document.getElementById('questionCategory').value = q.category_id || '';
        
        // 加载选项
        const container = document.getElementById('optionsEditor');
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
        } else {
            // 填空题：只有一个答案选项
            container.innerHTML = `
                <div class="option-row">
                    <input type="text" class="option-input" placeholder="填空题答案" 
                           data-index="0" value="${escapeHtml(q.answer)}">
                    <label class="option-correct">
                        <input type="radio" name="correctOption" value="0" checked> 正确答案
                    </label>
                </div>
            `;
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
    const questionType = document.getElementById('questionId').dataset.type || 'normal';
    const content = document.getElementById('questionContent').value.trim();
    const categoryId = document.getElementById('questionCategory').value;
    const explanation = document.getElementById('questionExplanation').value.trim();
    
    // 收集选项
    const optionInputs = document.querySelectorAll('.option-input');
    const options = Array.from(optionInputs).map(input => input.value.trim()).filter(v => v);
    
    // 获取正确答案（从选中的选项）
    const correctIndex = document.querySelector('input[name="correctOption"]:checked')?.value;
    const answer = correctIndex !== undefined && options.length > 0 ? options[parseInt(correctIndex)] : '';
    
    if (!content) {
        showToast('请输入题干', 'error');
        return;
    }
    if (!categoryId) {
        showToast('请选择分类', 'error');
        return;
    }
    
    const data = {
        content,
        options: options.length > 0 ? options : undefined,  // 填空题不传 options
        answer,
        explanation: explanation || '',
        category_id: categoryId
    };
    
    try {
        if (questionType === 'staging') {
            // 预备题目：更新并入库
            const updateResponse = await fetch(`${API_BASE}/agent/staging/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (!updateResponse.ok) {
                const err = await updateResponse.json();
                throw new Error(err.detail || '保存失败');
            }
            
            // 更新成功后自动入库
            const approveResponse = await fetch(`${API_BASE}/agent/staging/${id}/approve`, {
                method: 'POST'
            });
            
            if (!approveResponse.ok) {
                throw new Error('入库失败');
            }
            
            closeModal('questionModal');
            document.getElementById('questionId').dataset.type = 'normal';
            await loadPendingQuestions();
            await loadQuestions(currentCategoryId, currentPage);
            showToast('题目已更新并入库', 'success');
        } else {
            // 正式题目：正常保存
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
        }
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
        const formData = new FormData();
        formData.append('reviewed_by', 'user');
        
        const response = await fetch(`${API_BASE}/agent/staging/${id}/approve`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: '操作失败' }));
            throw new Error(err.detail || '入库失败');
        }
        
        const result = await response.json();
        
        if (result.success) {
            loadPendingQuestions();
            loadQuestions();
            showToast('题目已入库', 'success');
        } else {
            throw new Error(result.detail || '入库失败');
        }
    } catch (error) {
        console.error('入库失败:', error);
        showToast('入库失败：' + error.message, 'error');
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


// 渲染 Markdown 代码块（支持语法高亮）
function renderMarkdown(text) {
    if (!text) return '';
    
    // 先转义 HTML
    let html = escapeHtml(text);
    
    // 1. 提取代码块，用占位符保存（避免换行被替换）
    const codeBlocks = [];
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const index = codeBlocks.length;
        const language = lang || 'text';
        codeBlocks.push(`<div class="code-block-wrapper"><pre><code class="language-${language}">${code.trim()}</code></pre></div>`);
        return `%%CODEBLOCK${index}%%`;
    });
    
    // 2. 处理行内代码 `...`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 3. 处理换行（此时代码块已被占位符保护）
    html = html.replace(/\n/g, '<br>');
    
    // 4. 恢复代码块
    codeBlocks.forEach((block, index) => {
        html = html.replace(`%%CODEBLOCK${index}%%`, block);
    });
    
    return html;
}

// 高亮代码块（调用 Prism.js）
function highlightCodeBlocks() {
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
}

// 编辑当前查看的题目（从详情页）
function editCurrentQuestion() {
    if (!currentViewQuestionId) {
        showToast('题目 ID 不存在', 'error');
        return;
    }
    // 关闭详情页，打开编辑页
    closeModal('detailModal');
    setTimeout(() => {
        if (currentViewQuestionType === 'staging') {
            editStagingQuestion(currentViewQuestionId);
        } else {
            editQuestion(currentViewQuestionId);
        }
    }, 200);
}

// ========== AI 上传功能 ==========

// 显示 AI 上传模态框
function showAIUploadModal() {
    document.getElementById('aiUploadModal').classList.add('active');
}

// 关闭 AI 上传模态框
function closeAIUploadModal() {
    document.getElementById('aiUploadModal').classList.remove('active');
    document.getElementById('aiUploadFiles').value = '';
    document.getElementById('aiUploadProgress').style.display = 'none';
}

// 切换提取类型
function toggleExtractType() {
    const type = document.querySelector('input[name="extractType"]:checked').value;
    const fileInput = document.getElementById('aiUploadFiles');
    
    if (type === 'image') {
        fileInput.accept = '.png,.jpg,.jpeg,.gif,.webp';
    } else {
        fileInput.accept = '.pdf,.doc,.docx,.txt,.md';
    }
}

// 上传并提取
async function uploadAndExtract() {
    const fileInput = document.getElementById('aiUploadFiles');
    const files = fileInput.files;
    
    if (!files || files.length === 0) {
        showToast('请选择要上传的文件', 'error');
        return;
    }
    
    const extractType = document.querySelector('input[name="extractType"]:checked').value;
    const progressDiv = document.getElementById('aiUploadProgress');
    const statusSpan = document.getElementById('aiUploadStatus');
    const detailDiv = document.getElementById('aiUploadDetail');
    
    progressDiv.style.display = 'block';
    statusSpan.textContent = '正在上传并提取...';
    detailDiv.textContent = `文件：${Array.from(files).map(f => f.name).join(', ')}`;
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    try {
        const endpoint = extractType === 'image' ? '/api/agent/extract/image' : '/api/agent/extract/document';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            const count = result.data.total_count;
            statusSpan.textContent = `✅ 成功提取 ${count} 道题目！`;
            detailDiv.textContent = '已保存到预备题目，请前往"预备题目"标签页审核';
            
            setTimeout(() => {
                closeAIUploadModal();
                showToast(`成功提取 ${count} 道题目`, 'success');
                // 切换到预备题目标签页
                switchTab('pending');
                loadPendingQuestions();
            }, 2000);
        } else {
            throw new Error(result.detail || '提取失败');
        }
    } catch (error) {
        statusSpan.textContent = '❌ 提取失败';
        detailDiv.textContent = error.message;
        showToast(`提取失败：${error.message}`, 'error');
    }
}

// ========== 预备题目管理 ==========

// 加载预备题目
async function loadPendingQuestions() {
    const tbody = document.getElementById('pendingTableBody');
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px;"><div class="loading-spinner"></div></td></tr>';
    
    try {
        const response = await fetch('/api/agent/staging?status=pending&page=1&limit=50');
        const result = await response.json();
        
        if (result.success) {
            const questions = result.data.questions;
            
            if (questions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px; color: var(--text-light);">暂无预备题目</td></tr>';
                return;
            }
            
            tbody.innerHTML = questions.map(q => `
                <tr>
                    <td style="max-width: 400px;">
                        <div style="font-weight: 500; margin-bottom: 5px;">${escapeHtml(q.content.substring(0, 100))}${q.content.length > 100 ? '...' : ''}</div>
                        <div style="font-size: 12px; color: var(--text-light);">
                            <span class="badge" style="background: var(--primary);">${q.type}</span>
                            ${q.source_file ? `<span class="badge" style="background: var(--secondary);">📁 ${escapeHtml(q.source_file)}</span>` : ''}
                            <span class="badge" style="background: ${q.confidence >= 0.8 ? 'var(--success)' : 'var(--warning)'}">置信度：${(q.confidence * 100).toFixed(0)}%</span>
                        </div>
                    </td>
                    <td>${q.source_type === 'image' ? '📷 图片' : '📄 文档'}</td>
                    <td style="font-size: 13px; color: var(--text-light);">${new Date(q.created_at).toLocaleString('zh-CN')}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="viewPendingQuestion(${q.id})" style="margin-right: 5px;">查看</button>
                        <button class="btn btn-sm btn-success" onclick="approvePendingQuestion(${q.id})" style="margin-right: 5px;">✓ 通过</button>
                        <button class="btn btn-sm btn-danger" onclick="rejectPendingQuestion(${q.id})">✗ 拒绝</button>
                    </td>
                </tr>
            `).join('');
        } else {
            throw new Error(result.detail || '加载失败');
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 40px; color: var(--danger);">加载失败：${error.message}</td></tr>`;
    }
}

// 查看预备题目
async function viewPendingQuestion(qId) {
    try {
        const response = await fetch(`/api/agent/staging/${qId}`);
        const result = await response.json();
        
        if (result.success) {
            const q = result.data;
            
            const content = `
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                        <span class="badge" style="background: var(--primary);">${q.type}</span>
                        <span class="badge" style="background: var(--secondary);">来源：${q.source_type}</span>
                        ${q.source_file ? `<span class="badge" style="background: var(--secondary);">文件：${escapeHtml(q.source_file)}</span>` : ''}
                        <span class="badge" style="background: ${q.confidence >= 0.8 ? 'var(--success)' : 'var(--warning)'}">置信度：${(q.confidence * 100).toFixed(0)}%</span>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <strong>题干：</strong>
                        <div style="margin-top: 10px; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                            ${renderMarkdown(q.content)}
                        </div>
                    </div>
                    
                    ${q.options && q.options.length > 0 ? `
                    <div style="margin-bottom: 15px;">
                        <strong>选项：</strong>
                        <div style="margin-top: 10px;">
                            ${q.options.map((opt, i) => `
                                <div style="padding: 8px 12px; margin: 5px 0; border-radius: 4px; background: ${opt === q.answer ? 'var(--success-light)' : 'var(--bg-secondary)'}; border-left: 3px solid ${opt === q.answer ? 'var(--success)' : 'var(--border)'};">
                                    ${String.fromCharCode(65 + i)}. ${escapeHtml(opt)}
                                    ${opt === q.answer ? ' ✓ 正确答案' : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${q.explanation ? `
                    <div style="margin-bottom: 15px;">
                        <strong>解析：</strong>
                        <div style="margin-top: 10px; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                            ${renderMarkdown(q.explanation)}
                        </div>
                    </div>
                    ` : '<div style="margin-bottom: 15px; color: var(--text-light);">暂无解析</div>'}
                </div>
            `;
            
            document.getElementById('detailContent').innerHTML = content;
            document.getElementById('detailModalTitle').textContent = '预备题目详情';
            document.getElementById('detailEditBtn').style.display = 'inline-block';
            document.getElementById('detailEditBtn').textContent = '编辑并入库';
            
            // 保存当前查看的题目 ID 和类型
            currentViewQuestionId = qId;
            currentViewQuestionType = 'staging';
            
            document.getElementById('detailModal').classList.add('active');
        } else {
            throw new Error(result.detail || '加载失败');
        }
    } catch (error) {
        showToast(`加载失败：${error.message}`, 'error');
    }
}

// 通过预备题目
async function approvePendingQuestion(qId) {
    if (!confirm('确认将此题目审核通过并入库？')) return;
    
    try {
        const formData = new FormData();
        formData.append('reviewed_by', 'user');
        
        const response = await fetch(`/api/agent/staging/${qId}/approve`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: '操作失败' }));
            throw new Error(err.detail || '操作失败');
        }
        
        const result = await response.json();
        
        if (result.success) {
            showToast('审核通过', 'success');
            loadPendingQuestions();
            loadQuestions();
        } else {
            throw new Error(result.detail || '操作失败');
        }
    } catch (error) {
        showToast(`操作失败：${error.message}`, 'error');
    }
}

// 拒绝预备题目
async function rejectPendingQuestion(qId) {
    if (!confirm('确认拒绝此题目？')) return;
    
    try {
        const formData = new FormData();
        formData.append('reviewed_by', 'user');
        
        const response = await fetch(`/api/agent/staging/${qId}/reject`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('已拒绝', 'success');
            loadPendingQuestions();
        } else {
            throw new Error(result.detail || '操作失败');
        }
    } catch (error) {
        showToast(`操作失败：${error.message}`, 'error');
    }
}

// 编辑预备题目并入库（TODO：实现）
function editAndImportPendingQuestion(qId) {
    showToast('编辑入库功能开发中...', 'info');
}

// ========== AI Agent 配置管理 ==========

// 切换标签页时加载设置
const originalSwitchTab = switchTab;
switchTab = function(tabId) {
    originalSwitchTab(tabId);
    if (tabId === 'settings') {
        loadAgentConfig();
    }
};

// 加载 Agent 配置
async function loadAgentConfig() {
    const loading = document.getElementById('settingsLoading');
    const form = document.getElementById('settingsForm');
    
    loading.style.display = 'block';
    form.style.display = 'none';
    
    try {
        const response = await fetch('/api/agent/config');
        const result = await response.json();
        
        if (result.success) {
            const config = result.data;
            
            // 填充 LLM 配置
            if (config.llm) {
                document.getElementById('llm_model_id').value = config.llm.model_id || 'qwen-plus';
                document.getElementById('llm_base_url').value = config.llm.base_url || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
                document.getElementById('llm_api_key').value = config.llm.api_key || '';
            }
            
            // 填充 Vision 配置
            if (config.vision) {
                document.getElementById('vision_model_id').value = config.vision.model_id || 'qwen-vl-max';
                document.getElementById('vision_base_url').value = config.vision.base_url || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
                document.getElementById('vision_api_key').value = config.vision.api_key || '';
            }
            
            // 填充 Embedding 配置
            if (config.embedding) {
                document.getElementById('embed_model_name').value = config.embedding.model_name || 'text-embedding-v3';
                document.getElementById('embed_base_url').value = config.embedding.base_url || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
                document.getElementById('embed_api_key').value = config.embedding.api_key || '';
            }
            
            // 填充高级设置
            if (config.settings) {
                document.getElementById('confidence_threshold').value = config.settings.confidence_threshold || 0.6;
                document.getElementById('max_file_size_mb').value = config.settings.max_file_size_mb || 50;
                document.getElementById('http_proxy').value = config.settings.http_proxy || '';
            }
            
            loading.style.display = 'none';
            form.style.display = 'block';
        } else {
            showSettingsMessage('加载配置失败：' + result.message, 'error');
            loading.style.display = 'none';
            form.style.display = 'block';
        }
    } catch (error) {
        showSettingsMessage('加载配置失败：' + error.message, 'error');
        loading.style.display = 'none';
        form.style.display = 'block';
    }
}

// 保存 Agent 配置
async function saveAgentConfig() {
    const config = {
        llm: {
            model_id: document.getElementById('llm_model_id').value.trim(),
            base_url: document.getElementById('llm_base_url').value.trim(),
            api_key: document.getElementById('llm_api_key').value.trim()
        },
        vision: {
            model_id: document.getElementById('vision_model_id').value.trim(),
            base_url: document.getElementById('vision_base_url').value.trim(),
            api_key: document.getElementById('vision_api_key').value.trim()
        },
        embedding: {
            model_name: document.getElementById('embed_model_name').value.trim(),
            base_url: document.getElementById('embed_base_url').value.trim(),
            api_key: document.getElementById('embed_api_key').value.trim()
        },
        settings: {
            confidence_threshold: parseFloat(document.getElementById('confidence_threshold').value) || 0.6,
            max_file_size_mb: parseInt(document.getElementById('max_file_size_mb').value) || 50,
            http_proxy: document.getElementById('http_proxy').value.trim() || null
        }
    };
    
    try {
        const response = await fetch('/api/agent/config', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSettingsMessage('✅ 配置保存成功！立即生效。', 'success');
            loadAgentConfig(); // 重新加载配置
        } else {
            showSettingsMessage('保存失败：' + result.message, 'error');
        }
    } catch (error) {
        showSettingsMessage('保存失败：' + error.message, 'error');
    }
}

// 测试 Agent 配置
async function testAgentConfig() {
    showSettingsMessage('🧪 测试中...', 'info');
    
    try {
        const response = await fetch('/api/agent/config/test', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSettingsMessage(`✅ 配置有效！模型：${result.data.llm_model}`, 'success');
        } else {
            showSettingsMessage('❌ ' + result.message, 'error');
        }
    } catch (error) {
        showSettingsMessage('测试失败：' + error.message, 'error');
    }
}

// 重置 Agent 配置
function resetAgentConfig() {
    if (confirm('确定要重置为默认配置吗？')) {
        document.getElementById('llm_model_id').value = 'qwen-plus';
        document.getElementById('llm_base_url').value = 'https://dashscope.aliyuncs.com/compatible-mode/v1';
        document.getElementById('llm_api_key').value = '';
        
        document.getElementById('vision_model_id').value = 'qwen-vl-max';
        document.getElementById('vision_base_url').value = 'https://dashscope.aliyuncs.com/compatible-mode/v1';
        document.getElementById('vision_api_key').value = '';
        
        document.getElementById('embed_model_name').value = 'text-embedding-v3';
        document.getElementById('embed_base_url').value = 'https://dashscope.aliyuncs.com/compatible-mode/v1';
        document.getElementById('embed_api_key').value = '';
        
        document.getElementById('confidence_threshold').value = 0.6;
        document.getElementById('max_file_size_mb').value = 50;
        
        showSettingsMessage('⚠️ 已重置为默认值，记得保存！', 'info');
    }
}

// 显示设置页面消息
function showSettingsMessage(text, type) {
    const messageArea = document.getElementById('settingsMessage');
    const bgColor = type === 'success' ? '#e8f5e9' : type === 'error' ? '#ffebee' : '#e3f2fd';
    const borderColor = type === 'success' ? '#a5d6a7' : type === 'error' ? '#ef9a9a' : '#90caf9';
    const color = type === 'success' ? '#2e7d32' : type === 'error' ? '#c62828' : '#1565c0';
    
    messageArea.innerHTML = `<div style="padding: 15px; border-radius: 6px; background: ${bgColor}; border: 1px solid ${borderColor}; color: ${color};">${text}</div>`;
    
    if (type !== 'error') {
        setTimeout(() => {
            messageArea.innerHTML = '';
        }, 3000);
    }
}
