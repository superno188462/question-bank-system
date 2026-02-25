#!/bin/bash
# 预提交验证脚本
# 在提交代码前运行，确保项目完整性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔍 预提交验证 - 题库系统"
echo "时间: $(date)"
echo "项目: $PROJECT_ROOT"
echo ""

# 创建验证日志目录
VALIDATION_LOG_DIR="$PROJECT_ROOT/test/logs"
mkdir -p "$VALIDATION_LOG_DIR"
VALIDATION_LOG="$VALIDATION_LOG_DIR/validation_$(date +%Y%m%d_%H%M%S).log"

# 开始记录日志
{
echo "=== 预提交验证日志 ==="
echo "时间: $(date)"
echo "项目: $PROJECT_ROOT"
echo ""

# 1. 检查Git状态
print_info "1. 检查Git状态..."
if [ -d "$PROJECT_ROOT/.git" ]; then
    echo "  ✅ Git仓库存在"
    
    # 检查是否有未提交的更改
    if git -C "$PROJECT_ROOT" status --porcelain | grep -q .; then
        echo "  ⚠️  有未提交的更改"
        git -C "$PROJECT_ROOT" status --porcelain
    else
        echo "  ✅ 没有未提交的更改"
    fi
    
    # 检查当前分支
    CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" branch --show-current)
    echo "  📍 当前分支: $CURRENT_BRANCH"
else
    echo "  ⚠️  不是Git仓库"
fi

echo ""

# 2. 运行快速验证
print_info "2. 运行快速验证..."
if bash "$PROJECT_ROOT/test/quick_validate.sh" 2>&1 | tee -a "$VALIDATION_LOG"; then
    print_success "快速验证通过"
else
    print_error "快速验证失败"
    echo "详细日志: $VALIDATION_LOG"
    exit 1
fi

echo ""

# 3. 运行完整验证
print_info "3. 运行完整验证..."
cd "$PROJECT_ROOT"
if python test/validate_project.py 2>&1 | tee -a "$VALIDATION_LOG"; then
    print_success "完整验证通过"
else
    print_error "完整验证失败"
    echo "详细日志: $VALIDATION_LOG"
    exit 1
fi

echo ""

# 4. 检查依赖
print_info "4. 检查依赖..."
cd "$PROJECT_ROOT"

if [ -f "config/requirements.txt" ]; then
    echo "  ✅ requirements.txt存在"
    
    # 检查是否使用uv
    if command -v uv > /dev/null 2>&1; then
        echo "  ✅ uv已安装"
        
        # 检查虚拟环境
        if [ -d ".venv" ]; then
            echo "  ✅ 虚拟环境存在"
            
            # 检查依赖安装
            if uv pip list --format=freeze 2>/dev/null | grep -q fastapi; then
                echo "  ✅ 核心依赖已安装"
            else
                echo "  ⚠️  核心依赖未安装，尝试安装..."
                uv pip install -r config/requirements.txt
            fi
        else
            echo "  ⚠️  虚拟环境不存在，建议创建: uv venv"
        fi
    else
        echo "  ⚠️  uv未安装，建议安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
else
    echo "  ❌ requirements.txt不存在"
    exit 1
fi

echo ""

# 5. 检查配置文件
print_info "5. 检查配置文件..."
config_files=(
    "config/requirements.txt"
    "config/pyproject.toml"
    "shared/config.py"
    "web/config.py"
    "mcp_server/config.py"
    "wechat/config.py"
)

for config_file in "${config_files[@]}"; do
    if [ -f "$PROJECT_ROOT/$config_file" ]; then
        # 检查文件是否为空
        if [ -s "$PROJECT_ROOT/$config_file" ]; then
            echo "  ✅ $config_file (非空)"
        else
            echo "  ❌ $config_file (空文件)"
            exit 1
        fi
    else
        echo "  ❌ $config_file (不存在)"
        exit 1
    fi
done

echo ""

# 6. 检查API端点
print_info "6. 检查API端点..."

# 启动Web服务进行API测试
print_info "  启动Web服务进行API测试..."
"$PROJECT_ROOT/run.sh" stop > /dev/null 2>&1 || true
sleep 2

"$PROJECT_ROOT/run.sh" web > /tmp/api_test.log 2>&1 &
WEB_PID=$!
sleep 5

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Web服务启动成功"
    
    # 测试API端点
    endpoints=(
        "/"
        "/health"
        "/docs"
        # "/api"  # 注释掉，因为/api没有直接定义路由
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint" | grep -q "200\|301\|302"; then
            echo "  ✅ 端点可访问: $endpoint"
        else
            echo "  ❌ 端点不可访问: $endpoint"
            kill $WEB_PID 2>/dev/null || true
            exit 1
        fi
    done
    
    # 停止服务
    kill $WEB_PID 2>/dev/null || true
    sleep 2
    print_success "API端点检查通过"
else
    echo "  ❌ Web服务启动失败"
    cat /tmp/api_test.log
    kill $WEB_PID 2>/dev/null || true
    exit 1
fi

echo ""

# 7. 生成验证报告
print_info "7. 生成验证报告..."
VALIDATION_REPORT="$VALIDATION_LOG_DIR/validation_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$VALIDATION_REPORT" << EOF
# 预提交验证报告

## 基本信息
- **项目**: 题库系统
- **时间**: $(date)
- **验证脚本**: pre_commit_validate.sh
- **日志文件**: $(basename "$VALIDATION_LOG")

## 验证结果
✅ 所有验证通过

## 验证项目
1. ✅ Git状态检查
2. ✅ 快速验证 (quick_validate.sh)
3. ✅ 完整验证 (validate_project.py)
4. ✅ 依赖检查
5. ✅ 配置文件检查
6. ✅ API端点检查

## 系统信息
- **操作系统**: $(uname -s) $(uname -r)
- **Python版本**: $(python --version 2>&1)
- **uv版本**: $(uv --version 2>/dev/null || echo "未安装")
- **项目目录**: $PROJECT_ROOT

## 建议
1. 保持验证脚本的更新
2. 每次提交前运行验证
3. 定期检查依赖更新

---
*验证完成时间: $(date)*
EOF

print_success "验证报告生成: $(basename "$VALIDATION_REPORT")"

echo ""
print_success "🎉 预提交验证全部通过！"
echo ""
echo "📋 验证项目:"
echo "  ✅ Git状态"
echo "  ✅ 快速验证"
echo "  ✅ 完整验证"
echo "  ✅ 依赖检查"
echo "  ✅ 配置文件"
echo "  ✅ API端点"
echo ""
echo "📄 验证日志: $VALIDATION_LOG"
echo "📊 验证报告: $VALIDATION_REPORT"
echo ""
echo "🚀 可以安全提交代码！"

} 2>&1 | tee "$VALIDATION_LOG"

# 设置退出码
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    exit 0
else
    exit 1
fi