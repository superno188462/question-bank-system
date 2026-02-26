#!/bin/bash

echo "🚀 启动题库系统前端..."

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 启动开发服务器
echo "🌐 启动开发服务器..."
npm run dev
