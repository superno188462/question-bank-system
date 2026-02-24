#!/bin/bash
# 微信小程序部署脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  微信小程序部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"

print_menu() {
    echo -e "\n${YELLOW}请选择操作:${NC}"
    echo "1. 配置微信小程序后端"
    echo "2. 配置小程序前端"
    echo "3. 测试微信API"
    echo "4. 查看部署指南"
    echo "5. 退出"
    echo -n "选择 [1-5]: "
}

setup_backend() {
    echo -e "\n${YELLOW}[1] 配置微信小程序后端${NC}"
    
    # 检查微信API文件
    if [ ! -f "src/interfaces/wechat_api.py" ]; then
        echo -e "${RED}微信API文件不存在${NC}"
        echo "请先创建 wechat_api.py 文件"
        return 1
    fi
    
    # 配置环境变量
    echo -e "${GREEN}配置微信小程序环境变量...${NC}"
    
    read -p "请输入微信小程序 AppID: " WECHAT_APP_ID
    read -p "请输入微信小程序 AppSecret: " WECHAT_APP_SECRET
    read -p "请输入JWT密钥 (留空自动生成): " JWT_SECRET
    
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(openssl rand -hex 32)
        echo -e "${YELLOW}生成的JWT密钥: $JWT_SECRET${NC}"
    fi
    
    # 创建环境文件
    cat > .env.wechat << EOF
# 微信小程序配置
WECHAT_APP_ID=$WECHAT_APP_ID
WECHAT_APP_SECRET=$WECHAT_APP_SECRET

# JWT配置
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7

# API配置
API_BASE_URL=https://yourdomain.com
EOF
    
    echo -e "${GREEN}环境文件已创建: .env.wechat${NC}"
    
    # 更新微信API配置
    echo -e "${YELLOW}更新微信API配置...${NC}"
    
    # 检查是否需要安装jwt
    python3 -c "import jwt" 2>/dev/null || {
        echo -e "${YELLOW}安装PyJWT...${NC}"
        pip install PyJWT
    }
    
    # 测试配置
    echo -e "${GREEN}测试后端配置...${NC}"
    python3 -c "
try:
    import sys
    sys.path.append('.')
    from src.interfaces.wechat_api import WechatAPI
    print('✅ 微信API导入成功')
except Exception as e:
    print(f'❌ 导入失败: {e}')
"
    
    echo -e "\n${GREEN}后端配置完成！${NC}"
    echo "下一步: 配置小程序前端"
}

setup_frontend() {
    echo -e "\n${YELLOW}[2] 配置小程序前端${NC}"
    
    # 检查小程序目录
    if [ ! -d "wechat-miniprogram" ]; then
        echo -e "${RED}小程序目录不存在${NC}"
        echo "请先创建 wechat-miniprogram 目录"
        return 1
    fi
    
    # 获取服务器地址
    read -p "请输入服务器地址 (如 https://question.yourdomain.com): " SERVER_URL
    
    # 更新配置文件
    echo -e "${YELLOW}更新小程序配置文件...${NC}"
    
    # 创建配置文件
    cat > wechat-miniprogram/config/api.js << EOF
// 小程序API配置
const config = {
  // 服务器地址
  apiBaseUrl: '$SERVER_URL',
  
  // 微信小程序AppID
  wechatAppId: 'your_wechat_app_id', // 需要替换为您的AppID
  
  // 请求超时时间（毫秒）
  timeout: 10000,
  
  // 版本号
  version: '1.0.0',
  
  // 调试模式
  debug: true
}

module.exports = config
EOF
    
    # 更新app.js中的apiBaseUrl
    sed -i "s|apiBaseUrl: 'https://yourdomain.com'|apiBaseUrl: '$SERVER_URL'|" wechat-miniprogram/app.js
    
    echo -e "${GREEN}小程序配置已更新${NC}"
    
    # 检查需要的文件
    echo -e "${YELLOW}检查小程序文件结构...${NC}"
    
    required_files=(
        "app.js"
        "app.json"
        "app.wxss"
        "pages/index/index.js"
        "pages/index/index.wxml"
        "pages/index/index.wxss"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "wechat-miniprogram/$file" ]; then
            echo "✅ $file"
        else
            echo "❌ $file (缺失)"
        fi
    done
    
    echo -e "\n${GREEN}前端配置完成！${NC}"
    echo "下一步: 使用微信开发者工具导入项目"
}

test_api() {
    echo -e "\n${YELLOW}[3] 测试微信API${NC}"
    
    # 检查服务是否运行
    echo -e "${YELLOW}检查服务状态...${NC}"
    
    if curl -s http://localhost:8000/ > /dev/null; then
        echo -e "${GREEN}✅ 服务运行正常${NC}"
    else
        echo -e "${RED}❌ 服务未运行${NC}"
        echo "请先启动服务: uvicorn src.interfaces.web_interface:app --host 0.0.0.0 --port 8000"
        return 1
    fi
    
    # 测试微信API端点
    echo -e "${YELLOW}测试微信API端点...${NC}"
    
    endpoints=(
        "/api/wechat/config"
        "/api/wechat/questions/hot"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s "http://localhost:8000$endpoint" > /dev/null; then
            echo "✅ $endpoint"
        else
            echo "❌ $endpoint"
        fi
    done
    
    # 测试HTTPS（如果配置了）
    read -p "是否测试HTTPS? [y/N]: " test_https
    if [[ $test_https == "y" || $test_https == "Y" ]]; then
        read -p "请输入HTTPS地址 (如 https://yourdomain.com): " https_url
        
        if curl -s "$https_url/api/wechat/config" > /dev/null; then
            echo -e "${GREEN}✅ HTTPS访问正常${NC}"
        else
            echo -e "${RED}❌ HTTPS访问失败${NC}"
        fi
    fi
    
    echo -e "\n${GREEN}API测试完成！${NC}"
}

show_guide() {
    echo -e "\n${YELLOW}[4] 查看部署指南${NC}"
    
    echo -e "${BLUE}微信小程序部署步骤:${NC}"
    echo ""
    echo "1. 注册微信小程序账号"
    echo "   https://mp.weixin.qq.com"
    echo ""
    echo "2. 获取AppID和AppSecret"
    echo "   在微信公众平台 → 开发 → 开发设置"
    echo ""
    echo "3. 配置服务器域名"
    echo "   request合法域名: https://yourdomain.com"
    echo ""
    echo "4. 下载微信开发者工具"
    echo "   https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html"
    echo ""
    echo "5. 导入小程序项目"
    echo "   选择 wechat-miniprogram 目录"
    echo ""
    echo "6. 修改配置文件"
    echo "   - app.js 中的 apiBaseUrl"
    echo "   - config/api.js 中的服务器地址"
    echo ""
    echo "7. 测试和调试"
    echo "   - 使用开发者工具预览"
    echo "   - 真机调试"
    echo ""
    echo "8. 提交审核和发布"
    echo "   - 上传代码"
    echo "   - 提交审核"
    echo "   - 发布上线"
    echo ""
    
    echo -e "${GREEN}详细指南请查看 WECHAT_MINIPROGRAM_GUIDE.md${NC}"
}

main() {
    while true; do
        print_menu
        read choice
        
        case $choice in
            1)
                setup_backend
                ;;
            2)
                setup_frontend
                ;;
            3)
                test_api
                ;;
            4)
                show_guide
                ;;
            5)
                echo -e "${GREEN}退出${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择${NC}"
                ;;
        esac
        
        echo ""
        echo -e "${YELLOW}按回车键继续...${NC}"
        read
    done
}

# 检查是否在项目目录
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    echo "当前目录: $(pwd)"
    exit 1
fi

main