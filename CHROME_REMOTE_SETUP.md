# Chrome Remote Desktop 安装指南

## 📋 手动安装步骤

### 1️⃣ 打开浏览器下载
访问: https://remotedesktop.google.com/download

### 2️⃣ 选择 Mac 版
- 点击 "Download" 下载安装包
- 双击 `.dmg` 文件安装

### 3️⃣ 输入密码
- 系统会要求输入管理员密码
- 输入后点击 "Install Helper Tool"

### 4️⃣ 完成设置
- 重启 Chrome Remote Desktop
- 访问: https://remotedesktop.google.com/access
- 点击 "Turn On" 启用远程访问

---

## 🔄 或者命令行安装 (需要密码)

```bash
# 1. 安装 (需要输入密码)
brew install --cask chrome-remote-desktop-host

# 2. 启动服务
open -a "Chrome Remote Desktop Host"
```

---

## 🎬 安装后操作

### 1. 启用远程访问
访问: https://remotedesktop.google.com/access
- 点击 "Turn On"
- 选择设备
- 设置 PIN 码

### 2. 生成访问码
访问: https://remotedesktop.google.com/support
- 获取访问码

### 3. 发送给我
把访问码发给我，我就可以控制你的电脑了 🚀