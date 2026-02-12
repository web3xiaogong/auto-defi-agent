# ERC-8004 测试网部署指南

## 📋 前提条件

1. **测试币** - 至少 0.02 ETH (Sepolia)
2. **网络连接** - 稳定的互联网

## 🚀 一键部署

```bash
cd /Users/Zhuanz1/Desktop/auto_defi_agent

# 部署到 Sepolia
./scripts/deploy_testnet.sh sepolia

# 或 Base Sepolia
./scripts/deploy_testnet.sh base-sepolia
```

## 📱 钱包信息

| 项目 | 值 |
|------|-----|
| **地址** | `0x0F9953E773D16C90ab2e8bC51d57e6541E34BE7d` |
| **私钥** | `5957179309b97b7df0c555ecb8c7f249efaf18dc30ecc672df584e696fabbe51` |

⚠️ **私钥已包含在脚本中，仅用于测试！**

## 💰 获取测试币

### Sepolia
- https://sepoliafaucet.com/
- https://faucet.sepolia.org/

### Base Sepolia  
- https://bridge.base.org/deposit

## 📊 预期输出

部署成功后：

```
✅ ERC-8004 Agent Registry: 0x...
✅ ERC-8004 Strategy Marketplace: 0x...

📁 配置已保存到: src/integrations/erc8004_config.json
```

## 🔗 Explorer 链接

- Sepolia: https://sepolia.etherscan.io/
- Base Sepolia: https://sepolia.basescan.org/

## 📞 如果网络问题

```bash
# 检查网络连接
curl https://rpc.sepolia.org

# 或使用其他 RPC
export ETH_RPC_URL="https://rpc.sepolia.org"
```
