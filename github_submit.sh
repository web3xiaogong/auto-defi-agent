#!/bin/bash
# GitHub 提交脚本 - Auto-DeFi Agent

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Auto-DeFi Agent - GitHub 提交脚本                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查是否在项目目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   cd /Users/Zhuanz1/Desktop/auto_defi_agent"
    exit 1
fi

echo "📁 当前目录: $(pwd)"
echo ""

# 步骤 1: 添加 MIT License
echo "✅ 1. 已添加 LICENSE 文件"
git add LICENSE
git commit -m "Add MIT License"

# 步骤 2: 更新 .gitignore
echo "✅ 2. .gitignore 已配置"

# 步骤 3: 显示 Git 状态
echo ""
echo "📊 Git 状态:"
git status --short | head -10

# 步骤 4: 提示用户创建 GitHub 仓库
echo ""
echo "════════════════════════════════════════════════════════════"
echo "🚀 下一步: 创建 GitHub 仓库并推送"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  访问 https://github.com/new 创建仓库"
echo "    • 仓库名: auto-defi-agent"
echo "    • 选择: Public"
echo "    • 不要勾选 'Add a README file'"
echo ""
echo "2️⃣  运行以下命令:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/auto-defi-agent.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣  验证后访问: https://github.com/YOUR_USERNAME/auto-defi-agent"
echo ""
echo "4️⃣  提交到黑客松:"
echo "    • 复制仓库链接"
echo "    • 粘贴到 Good Vibes Only 提交页面"
echo "    • 填写下方信息"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "📝 黑客松提交信息模板"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
项目名称: Auto-DeFi Agent
描述: 智能 DeFi 收益优化助手，支持多链、ML预测、跟单交易

主要特性:
• 🤖 OpenClaw AI Agent 集成
• 🔮 ML APY 预测引擎
• 🌉 多链支持 (BSC, opBNB, Ethereum, Arbitrum)
• 👥 跟单交易系统
• 📤 策略分享 (二维码)
• ⛓️ 链上决策证明

技术栈:
• Python, Web3.py, OpenClaw
• Solidity 智能合约
• pytest 测试

GitHub: https://github.com/YOUR_USERNAME/auto-defi-agent
EOF
echo ""
echo "════════════════════════════════════════════════════════════"
echo "📦 提交前检查清单"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "☐ README.md 完整"
echo "☐ requirements.txt 正确"
echo "☐ SKILL.md 包含"
echo "☐ 测试全部通过 (41 passed)"
echo "☐ 演示视频已录制"
echo "☐ 幻灯片已准备"
echo ""
echo "🎯 提交截止: 2026-02-19"
echo ""
