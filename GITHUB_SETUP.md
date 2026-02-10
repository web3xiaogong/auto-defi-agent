# GitHub 上传指南

## 1. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 输入仓库名: `auto-defi-agent`
3. 选择 Public
4. 不要勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

## 2. 推送到 GitHub

```bash
cd /Users/Zhuanz1/Desktop/auto_defi_agent

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/auto-defi-agent.git

# 推送
git branch -M main
git push -u origin main
```

## 3. 验证

访问 https://github.com/YOUR_USERNAME/auto-defi-agent 查看项目

## 4. 提交到黑客松

1. 复制仓库链接
2. 粘贴到黑客松提交页面
3. 填写项目信息
4. 提交
