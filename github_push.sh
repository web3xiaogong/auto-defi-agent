#!/bin/bash
# GitHub 推送脚本 - 非交互式版本

cd /Users/Zhuanz1/Desktop/auto_defi_agent

echo "🔗 请在浏览器中完成 GitHub 登录:"
echo "   https://github.com/login"
echo ""
echo "📝 或者创建访问令牌:"
echo "   1. 访问 https://github.com/settings/tokens"
echo "   2. 创建新令牌 (classic)"
echo "   3. 勾选 'repo' 权限"
echo "   4. 复制令牌并运行: gh auth login --with-token"
echo ""
echo "🌐 创建 GitHub 仓库:"
echo "   访问: https://github.com/new"
echo "   仓库名: auto-defi-agent"
echo "   选择: Public"
echo "   不要勾选 README"
echo ""
echo "💻 推送命令:"
echo "   cd /Users/Zhuanz1/Desktop/auto_defi_agent"
echo "   git remote add origin https://github.com/YOUR_USERNAME/auto-defi-agent.git"
echo "   git push -u origin main"
echo "   git push origin v1.0.0"
