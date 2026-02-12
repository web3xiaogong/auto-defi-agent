# Auto-DeFi Agent OpenClaw Skill

## 📋 Skill 配置

```json
{
  "name": "auto-defi-agent",
  "version": "1.0.0",
  "description": "ML-Powered DeFi Yield Optimization Agent",
  "author": "web3xiaogong",
  "channels": ["telegram", "discord", "whatsapp", "imessage"],
  "models": ["claude-opus-4", "gpt-4", "minimax-m2.1"],
  "permissions": [
    "read:wallet",
    "execute:swap",
    "read:defi-data",
    "write:strategy"
  ],
  "commands": [
    {
      "name": "scan",
      "description": "Scan DeFi opportunities across chains",
      "usage": "scan --chain bsc --min-apy 10"
    },
    {
      "name": "predict",
      "description": "Get APY predictions with ML",
      "usage": "predict CAKE-BNB"
    },
    {
      "name": "trade",
      "description": "Execute DeFi strategies",
      "usage": "trade --pool CAKE-BNB --amount 100"
    },
    {
      "name": "share",
      "description": "Share strategy with signature",
      "usage": "share --pool CAKE-BNB --apy 15.0"
    }
  ]
}
```

## 🚀 使用方法

### 1. 安装 Skill
```bash
# 在 OpenClaw 中
skill install auto-defi-agent
```

### 2. 配置钱包
```bash
# 设置钱包地址
defi set wallet <WALLET_ADDRESS>

# 设置 RPC (可选)
defi set rpc bsc <BSC_RPC_URL>
```

### 3. 开始使用
```
@agent scan --min-apy 10
@agent predict CAKE-BNB
@agent trade --pool CAKE-BNB --amount 100 --slippage 1
@agent share --pool CAKE-BNB --apy 15.0
```

## 🔧 核心功能

### 1. 多链扫描
```python
# 扫描 BSC, opBNB, Ethereum, Arbitrum
defi scan --chain all --min-apy 10 --limit 20
```

### 2. ML 预测
```python
# APY 走势预测
defi predict CAKE-BNB --days 7
```

### 3. 策略执行
```python
# 自动最优路径兑换
defi swap BNB CAKE --amount 1.0 --slippage 0.5

# 质押到高 APY 池
defi stake CAKE-BNB --amount 10
```

### 4. 策略分享
```python
# 生成可验证的分享链接
defi share --pool CAKE-BNB --apy 15.0 --days 7

# 输出：
# 🔗 https://auto-defi.agent/share/ABC123
# 📱 QR Code 生成
# ✅ Signature: 0x8f7a...
```

### 5. 跟单交易
```python
# 查看顶级交易者
defi leaders --chain bsc --limit 10

# 跟单
defi follow 0x1234... --amount 100 --copy-ratio 0.5
```

## 🔐 安全特性

1. **链上签名验证**
   - 所有策略带签名
   - 可在链上验证真实性

2. **交易预览**
   - 执行前显示预估结果
   - 支持滑点设置

3. **风险提示**
   - 自动评估池风险
   - 显示 TVL、TVL 变化、rug 概率

## 📊 数据来源

| 链 | RPC | 数据 API |
|----|-----|----------|
| BSC | https://bsc-dataseed1.binance.org | BscScan |
| opBNB | https://opbnb-mainnet-rpc.bnbchain.org | opBNBScan |
| Ethereum | https://eth.llamarpc.com | Etherscan |
| Arbitrum | https://arb1.arbitrum.io/rpc | Arbiscan |

## 🎯 集成 ERC-8004

### 注册 Agent
```python
# 在 ERC-8004 注册
defi register --name "Auto-DeFi Agent" \
  --metadata ipfs://QmXXX... \
  --services defi-optimization,strategy-sharing
```

### 发布策略到市场
```python
# 发布到 ERC-8004 市场
defi publish --strategy-id <ID> \
  --price 0.01 ETH \
  --description "High APY CAKE-BNB LP Strategy"
```

## 📝 命令列表

| 命令 | 别名 | 描述 |
|------|------|------|
| `scan` | `s`, `scan-opportunities` | 扫描 DeFi 机会 |
| `predict` | `p`, `forecast` | ML APY 预测 |
| `trade` | `t`, `execute` | 执行交易 |
| `share` | `sh`, `publish` | 分享策略 |
| `follow` | `f`, `copy` | 跟单交易 |
| `status` | `st`, `portfolio` | 投资组合状态 |
| `leaderboard` | `lb`, `leaders` | 交易者排行榜 |
| `register` | `reg` | ERC-8004 注册 |
| `config` | `cfg` | 配置管理 |

## 🧪 测试

```bash
# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=src
```

## 📄 许可证

MIT License
