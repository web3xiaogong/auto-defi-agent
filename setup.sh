#!/bin/bash
# Setup script for Auto-DeFi Agent
# Good Vibes Only: OpenClaw Edition Hackathon

set -e

echo "========================================"
echo "Auto-DeFi Agent - 安装脚本"
echo "========================================"
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 未安装"
    exit 1
fi

# 安装依赖
echo ""
echo "安装 Python 依赖..."
pip3 install --break-system-packages -r requirements.txt

# 创建必要目录
echo ""
echo "创建目录结构..."
mkdir -p logs
mkdir -p tests

# 复制环境文件
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env 文件不存在"
    echo "请运行: cp .env.example .env 并编辑配置"
else
    echo ""
    echo "✅ .env 文件已存在"
fi

# 运行测试
echo ""
echo "运行测试..."
python3 -m pytest tests/ -v --tb=short || true

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "下一步:"
echo "1. 编辑 .env 文件配置钱包"
echo "2. 运行: python3 src/main.py"
echo "3. 或使用 CLI: python3 src/cli.py status"
echo ""
