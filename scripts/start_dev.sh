#!/bin/bash
# DeepResearchWeb 开发环境启动脚本

set -e

echo "=== DeepResearchWeb 开发环境启动 ==="

# 检查 .env 文件
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "从 .env.example 创建 .env..."
        cp .env.example .env
    fi
fi

# 创建日志目录
mkdir -p logs

# 启动所有服务
echo "启动 Docker 服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 15

# 显示服务状态
echo ""
echo "=== 服务状态 ==="
docker-compose ps

echo ""
echo "=== 启动完成 ==="
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - RabbitMQ: http://localhost:15672"
echo ""
echo "查看日志:"
echo "  - docker-compose logs -f backend"
echo "  - docker-compose logs -f frontend"
echo ""
