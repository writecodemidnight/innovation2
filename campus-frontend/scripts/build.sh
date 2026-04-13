#!/bin/bash

# 校园社团活动评估系统 - 前端统一构建脚本

set -e

echo "=========================================="
echo "  校园社团活动评估系统 - 前端构建脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查pnpm
if ! command -v pnpm &> /dev/null; then
    echo -e "${RED}错误: 未找到 pnpm，请先安装${NC}"
    echo "安装命令: npm install -g pnpm"
    exit 1
fi

echo -e "${YELLOW}步骤 1: 安装依赖...${NC}"
pnpm install

echo ""
echo -e "${YELLOW}步骤 2: 构建共享包...${NC}"
pnpm --filter @campus/shared build

echo ""
echo -e "${YELLOW}步骤 3: 构建学生端（微信小程序）...${NC}"
pnpm --filter @campus/student build:mp-weixin

echo ""
echo -e "${YELLOW}步骤 4: 构建社团端...${NC}"
pnpm --filter @campus/club build

echo ""
echo -e "${YELLOW}步骤 5: 构建管理端...${NC}"
pnpm --filter @campus/admin build

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  构建完成！${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "构建产物目录:"
echo "  - 学生端: packages/student/dist/build/mp-weixin"
echo "  - 社团端: packages/club/dist"
echo "  - 管理端: packages/admin/dist"
echo ""
