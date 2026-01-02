#!/bin/bash
# 云享积分平台 - 一键部署脚本

set -e

echo "============================================"
echo "云享积分平台 - 生产环境部署"
echo "============================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在服务器上
if [ ! -f ".env.production" ]; then
    echo -e "${RED}错误: 未找到 .env.production 文件${NC}"
    echo "请先创建生产环境配置文件"
    exit 1
fi

# 复制环境变量
echo -e "${YELLOW}[1/8] 配置环境变量...${NC}"
cp .env.production .env
echo -e "${GREEN}✓ 环境变量配置完成${NC}"
echo ""

# 检查Docker
echo -e "${YELLOW}[2/8] 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo "请先安装Docker: curl -fsSL https://get.docker.com | sh"
    exit 1
fi
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker环境检查通过${NC}"
echo ""

# 构建前端应用
echo -e "${YELLOW}[3/8] 构建管理后台...${NC}"
cd admin
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..
echo -e "${GREEN}✓ 管理后台构建完成${NC}"
echo ""

echo -e "${YELLOW}[4/8] 构建用户端PC...${NC}"
cd pc-user
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..
echo -e "${GREEN}✓ 用户端PC构建完成${NC}"
echo ""

echo -e "${YELLOW}[4.5/8] 构建H5端...${NC}"
cd webapp
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build:h5
cd ..
echo -e "${GREEN}✓ H5端构建完成${NC}"
echo ""

# 停止旧服务
echo -e "${YELLOW}[5/8] 停止旧服务...${NC}"
docker-compose -f docker-compose.prod.yml down || true
# 强力清场: 确保没有残留容器占用名字
echo -e "${YELLOW}确保旧容器已移除...${NC}"
docker rm -f points_backend points_nginx points_mysql points_redis 2>/dev/null || true
echo -e "${GREEN}✓ 旧服务已停止并清理${NC}"
echo ""

# 构建镜像
echo -e "${YELLOW}[6/8] 构建Docker镜像...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache
echo -e "${GREEN}✓ Docker镜像构建完成${NC}"
echo ""

# 启动服务
echo -e "${YELLOW}[7/8] 启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✓ 服务启动成功${NC}"
echo ""

# 等待服务就绪
echo -e "${YELLOW}[8/8] 等待服务就绪...${NC}"
sleep 10

# 检查服务状态
echo ""
echo "============================================"
echo "服务状态检查"
echo "============================================"
docker-compose -f docker-compose.prod.yml ps

# 执行数据库迁移
echo ""
echo "============================================"
echo "执行数据库迁移"
echo "============================================"
echo "正在检查并更新数据库结构..."
docker-compose -f docker-compose.prod.yml exec -T backend python /app/scripts/update_db.py || echo "⚠️ 数据库迁移警告（非致命）"

# 健康检查
echo ""
echo "============================================"
echo "健康检查"
echo "============================================"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务健康${NC}"
else
    echo -e "${RED}✗ 后端服务异常${NC}"
fi

echo ""
echo "============================================"
echo -e "${GREEN}部署完成！${NC}"
echo "============================================"
echo ""
echo "访问地址："
echo "  - 主站: http://cloudexp.top"
echo "  - 管理后台: http://cloudexp.top/admin"
echo "  - API文档: http://cloudexp.top/docs"
echo ""
echo "查看日志："
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "重启服务："
echo "  docker-compose -f docker-compose.prod.yml restart"
echo ""
