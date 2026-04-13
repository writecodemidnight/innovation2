#!/bin/bash

# 校园社团活动评估系统 - 前端部署脚本

set -e

# 配置
DEPLOY_HOST="your-server-host"
DEPLOY_USER="your-username"
DEPLOY_PATH="/usr/share/nginx/html"
NGINX_CONF_PATH="/etc/nginx/conf.d"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  校园社团活动评估系统 - 前端部署脚本"
echo "=========================================="
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo "用法: ./deploy.sh [all|student|club|admin]"
    echo ""
    echo "参数说明:"
    echo "  all     - 部署所有端"
    echo "  student - 仅部署学生端"
    echo "  club    - 仅部署社团端"
    echo "  admin   - 仅部署管理端"
    exit 1
fi

TARGET=$1

# 部署函数
deploy_club() {
    echo -e "${YELLOW}部署社团端...${NC}"
    rsync -avz --delete packages/club/dist/ ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/club/
    echo -e "${GREEN}社团端部署完成${NC}"
}

deploy_admin() {
    echo -e "${YELLOW}部署管理端...${NC}"
    rsync -avz --delete packages/admin/dist/ ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/admin/
    echo -e "${GREEN}管理端部署完成${NC}"
}

deploy_student() {
    echo -e "${YELLOW}学生端构建产物位置:${NC}"
    echo "  packages/student/dist/build/mp-weixin"
    echo ""
    echo -e "${YELLOW}请使用微信开发者工具上传代码${NC}"
}

case $TARGET in
    all)
        deploy_student
        deploy_club
        deploy_admin
        echo ""
        echo -e "${GREEN}全部部署完成！${NC}"
        ;;
    student)
        deploy_student
        ;;
    club)
        deploy_club
        ;;
    admin)
        deploy_admin
        ;;
    *)
        echo -e "${RED}未知目标: $TARGET${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "提示: 部署完成后请检查 Nginx 配置并重新加载"
echo "  sudo nginx -t && sudo nginx -s reload"
echo "=========================================="
