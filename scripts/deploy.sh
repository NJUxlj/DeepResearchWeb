#!/bin/bash
# DeepResearchWeb 部署脚本

set -e

echo "=== DeepResearchWeb 部署脚本 ==="

# 检查环境变量文件
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "错误: .env 文件不存在，正在从 .env.example 复制..."
        cp .env.example .env
        echo "已创建 .env 文件，请配置实际值后再运行此脚本"
        exit 1
    else
        echo "错误: .env 文件不存在，请创建"
        exit 1
    fi
fi

# 创建必要目录
echo "创建必要目录..."
mkdir -p logs
mkdir -p nginx/ssl

# 生成 SSL 证书（如果没有）- 仅开发环境使用
if [ ! -f nginx/ssl/cert.pem ] && [ ! -f nginx/ssl/key.pem ]; then
    echo "生成自签名 SSL 证书..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" 2>/dev/null || true
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker 未运行，请启动 Docker"
    exit 1
fi

# 拉取最新镜像或构建
echo "构建 Docker 镜像..."
docker-compose build --no-cache

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待数据库就绪
echo "等待数据库就绪..."
sleep 10

# 检查服务健康状态
echo "检查服务状态..."
docker-compose ps

# 健康检查
echo "执行健康检查..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/api/v1/monitoring/health > /dev/null 2>&1; then
        echo "后端服务已就绪"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "等待服务启动... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "警告: 服务可能未完全启动，请检查日志"
    docker-compose logs backend
fi

echo ""
echo "=== 部署完成 ==="
echo ""
echo "服务访问地址:"
echo "  - 前端 UI: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - RabbitMQ Management: http://localhost:15672"
echo ""
echo "常用命令:"
echo "  - 查看日志: docker-compose logs -f backend"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""
