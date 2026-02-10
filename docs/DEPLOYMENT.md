# Deployment Guide

## 环境要求

- Python 3.10+
- pip3
- 网络连接 (访问 BSC/opBNB)

## 快速部署

### 1. 克隆项目

```bash
cd /Users/Zhuanz1/.openclaw/workspace
git clone <repo-url> auto_defi_agent
cd auto_defi_agent
```

### 2. 安装依赖

```bash
pip3 install --break-system-packages -r requirements.txt
```

### 3. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件
nano .env
```

必需配置：
- `BSC_RPC` - BSC RPC 地址
- `WALLET_PRIVATE_KEY` - 钱包私钥
- `WALLET_ADDRESS` - 钱包地址

可选配置：
- `TELEGRAM_BOT_TOKEN` - Telegram 机器人 Token
- `TELEGRAM_CHAT_ID` - Telegram Chat ID

### 4. 运行测试

```bash
python3 -m pytest tests/ -v
```

### 5. 启动 Agent

```bash
# 前台运行
python3 src/main.py

# 后台运行
nohup python3 src/main.py > agent.log 2>&1 &
```

## Docker 部署 (可选)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "src/main.py"]
```

```bash
docker build -t auto-defi-agent .
docker run -d --env-file .env auto-defi-agent
```

## systemd 服务 (Linux)

创建 `/etc/systemd/system/auto-defi-agent.service`：

```ini
[Unit]
Description=Auto-DeFi Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/auto_defi_agent
ExecStart=/usr/bin/python3 src/main.py
Restart=always
Environment=PYTHONPATH=/home/ubuntu/auto_defi_agent

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable auto-defi-agent
sudo systemctl start auto-defi-agent
```

## 验证部署

```bash
# 检查进程
ps aux | grep main.py

# 检查日志
tail -f agent.log

# 检查状态
python3 src/cli.py status
```

## 故障排除

### 无法连接 BSC

- 检查 RPC URL 是否正确
- 检查网络连接
- 尝试更换 RPC 地址

### 钱包余额不足

- 确认钱包有足够 BNB 支付 Gas
- 建议至少 0.1 BNB

### 交易失败

- 检查 Gas 价格是否过高
- 确认滑点设置合理
- 查看错误日志获取详情
