# GitHub 登录指南

## 方式 A：浏览器登录（推荐）⭐

### 步骤 1：运行登录命令
```bash
gh auth login --web -h github.com
```

### 步骤 2：浏览器授权
- 命令会自动打开 GitHub 授权页面
- 点击 **"Continue"**
- 点击 **"Authorize github"**

### 步骤 3：验证登录
```bash
gh auth status
```
看到ged in` `✓ Log 表示成功 ✅

---

## 方式 B：令牌登录（快速）

### 步骤 1：创建访问令牌
1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token (classic)"**
3. 填写信息：
   - **Note**: `Auto-DeFi Agent`
   - **Expiration**: `90 days`
   - **Select scopes**: ✅ 勾选 `repo`
4. 点击 **"Generate token"**
5. **复制令牌**（形如 `ghp_xxxxxxxxxxxx`）

### 步骤 2：登录
```bash
echo "你的令牌" | gh auth login --with-token
```

### 步骤 3：验证
```bash
gh auth status
```

---

## 验证成功后

### 创建并推送仓库
```bash
cd /Users/Zhuanz1/Desktop/auto_defi_agent

# 添加远程仓库 (替换 YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/auto-defi-agent.git

# 推送代码
git push -u origin main

# 推送标签
git push origin v1.0.0
```

### 检查推送结果
```bash
gh repo view --web
```

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 令牌过期 | 重新生成令牌 |
| 权限不足 | 确保勾选了 `repo` |
| 推送失败 | 先 `git pull` 合并冲突 |

---

**下一步**：登录后告诉我，我帮你完成推送 🚀
