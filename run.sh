#!/bin/bash
# Run script for Auto-DeFi Agent
# Good Vibes Only: OpenClaw Edition Hackathon

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="${PYTHON_CMD:-python3}"

cd "$SCRIPT_DIR"

echo "========================================"
echo "Auto-DeFi Agent - 启动脚本"
echo "========================================"

# 检查配置
if [ ! -f .env ]; then
    echo "❌ 错误: .env 文件不存在"
    echo "请先运行: cp .env.example .env"
    exit 1
fi

# 检查依赖
echo ""
echo "检查依赖..."
python3 -c "import web3; import pandas; import requests; import dotenv" 2>/dev/null || {
    echo "⚠️  依赖未安装，运行安装脚本..."
    bash setup.sh
}

# 运行
echo ""
echo "启动 Agent..."
echo "========================================"

$PYTHON_CMD src/main.py

echo ""
echo "========================================"
echo "Agent 已停止"
echo "========================================"
