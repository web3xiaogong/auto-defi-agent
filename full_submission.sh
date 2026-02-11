#!/bin/bash
# Auto-DeFi Agent - GitHub 完整提交脚本
# 此脚本会引导你完成所有 GitHub 和黑客松提交步骤

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Auto-DeFi Agent - GitHub 完整提交脚本               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/Zhuanz1/Desktop/auto_defi_agent

# 步骤 1: GitHub 登录
echo "════════════════════════════════════════════════════════════"
echo "📋 步骤 1: GitHub 登录"
echo "════════════════════════════════════════════════════════════"
echo ""

if ! gh auth status &>/dev/null; then
    echo "❌ 你还没有登录 GitHub"
    echo ""
    echo "请选择登录方式:"
    echo ""
    echo "1️⃣  方式 A - 浏览器登录 (推荐)"
    echo "    运行: gh auth login --web -h github.com"
    echo "    然后在浏览器中完成授权"
    echo ""
    echo "2️⃣  方式 B - 使用访问令牌"
    echo "    a) 访问 https://github.com/settings/tokens"
    echo "    b) 点击 'Generate new token (classic)'"
    echo "    c) 设置名称: 'Auto-DeFi Agent'"
    echo "    d) 勾选 'repo' 权限"
    echo "    e) 创建令牌并复制"
    echo "    f) 运行: gh auth login --with-token"
    echo "    g) 粘贴令牌"
    echo ""
    echo "请完成登录后按回车键继续..."
    read -r
else
    echo "✅ 已登录 GitHub"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📋 步骤 2: 创建 GitHub 仓库"
echo "════════════════════════════════════════════════════════════"
echo ""

# 检查远程仓库是否已设置
if git remote get-url origin &>/dev/null; then
    echo "✅ 远程仓库已设置: $(git remote get-url origin)"
else
    echo "请输入你的 GitHub 用户名:"
    read -r GITHUB_USERNAME
    
    if [ -z "$GITHUB_USERNAME" ]; then
        echo "❌ 用户名不能为空"
        exit 1
    fi
    
    echo ""
    echo "🌐 创建仓库..."
    
    # 使用 gh CLI 创建仓库
    if gh repo create auto-defi-agent --public --description "Auto-DeFi Agent - 智能 DeFi 收益优化助手 - Good Vibes Only Hackathon" 2>&1; then
        echo "✅ 仓库创建成功!"
        
        # 添加远程仓库
        git remote add origin "https://github.com/$GITHUB_USERNAME/auto-defi-agent.git"
        echo "✅ 远程仓库已添加"
    else
        echo "❌ 仓库创建失败 (可能已存在)"
        echo ""
        echo "请手动访问 https://github.com/new 创建仓库"
        echo "仓库名: auto-defi-agent"
        echo "选择: Public"
        echo ""
        echo "然后运行:"
        echo "  git remote add origin https://github.com/$GITHUB_USERNAME/auto-defi-agent.git"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📋 步骤 3: 推送代码"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "🚀 推送到 GitHub..."
git branch -M main

if git push -u origin main 2>&1; then
    echo "✅ 代码推送成功!"
else
    echo "❌ 推送失败"
    exit 1
fi

# 推送标签
echo ""
echo "🏷️  推送版本标签..."
git push origin v1.0.0 2>&1 || echo "标签可能已存在"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ GitHub 推送完成!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📦 你的项目已推送到:"
echo "   https://github.com/$GITHUB_USERNAME/auto-defi-agent"
echo ""
echo "🏷️  版本标签: v1.0.0"
echo ""

# 步骤 4: 提交到黑客松
echo "════════════════════════════════════════════════════════════"
echo "📋 步骤 4: 提交到 Good Vibes Only 黑客松"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "请访问 Good Vibes Only 黑客松提交页面"
echo ""
echo "📝 需要填写的信息 (参考 SUBMISSION_TEMPLATE.md):"
echo ""
cat << EOF
项目名称: Auto-DeFi Agent
仓库链接: https://github.com/$GITHUB_USERNAME/auto-defi-agent
轨道: Agent Track

项目描述:
Auto-DeFi Agent 是一个基于 OpenClaw 框架的智能 DeFi 收益优化助手。
结合了 AI Agent、ML 预测、多链支持、跟单交易和链上证明等创新功能。

核心功能:
• 🤖 OpenClaw AI Agent 集成
• 🔮 ML APY 预测引擎
• 🌉 多链支持 (BSC, opBNB, Ethereum, Arbitrum)
• 👥 跟单交易系统
• 📤 策略分享 (二维码)
• ⛓️ 链上决策证明

技术栈:
• Python, Web3.py, OpenClaw
• Solidity 智能合约
• pytest (41 tests passing)
EOF
echo ""

# 步骤 5: 上传材料
echo ""
echo "════════════════════════════════════════════════════════════"
echo "📋 步骤 5: 上传演示材料"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "请上传以下材料到黑客松提交页面:"
echo ""
echo "📹 演示视频 (5分钟)"
echo "   • 使用 docs/VIDEO_SCRIPT.md 作为脚本"
echo "   • 使用 QuickTime: Cmd+Shift+5 录屏"
echo "   • 导出为 demo_video.mp4"
echo ""
echo "📊 幻灯片 (10页)"
echo "   • 打开 docs/presentation.html"
echo "   • 打印为 PDF 或截图"
echo "   • 或使用 Google Slides 制作"
echo ""
echo "📄 项目文档"
echo "   • README.md (已准备)"
echo "   • SKILL.md (已准备)"
echo "   • docs/DEMO_GUIDE.md (已准备)"
echo ""

# 最终清单
echo ""
echo "════════════════════════════════════════════════════════════"
echo "📋 最终提交清单"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "☐ GitHub 仓库: https://github.com/$GITHUB_USERNAME/auto-defi-agent"
echo "☐ 演示视频: demo_video.mp4"
echo "☐ 幻灯片: presentation.pdf"
echo "☐ 项目描述已填写"
echo "☐ 所有必需字段已填写"
echo "☐ 提交表单已提交"
echo ""
echo "⏰ 提交截止: 2026-02-19"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "🎉 祝你好运！希望你能赢得大奖！"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "💡 提示:"
echo "   • 确保演示视频清晰展示核心功能"
echo "   • 幻灯片简洁，突出创新点"
echo "   • 项目描述突出解决的实际问题"
echo "   • 提前提交，避免最后时刻网络问题"
echo ""
