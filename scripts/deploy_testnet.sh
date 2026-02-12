#!/bin/bash
# ERC-8004 测试网部署脚本

echo "========================================"
echo "🚀 部署 ERC-8004 到测试网"
echo "========================================"

# 配置
PRIVATE_KEY="5957179309b97b7df0c555ecb8c7f249efaf18dc30ecc672df584e696fabbe51"
NETWORK=${1:-sepolia}

echo "🌐 网络: $NETWORK"
echo "📱 钱包: 0x0F9953E773D16C90ab2e8bC51d57e6541E34BE7d"
echo ""

# 检查余额
echo "💰 检查余额..."
python3 -c "
from web3 import Web3
from eth_account import Account
wallet = Account.from_key('$PRIVATE_KEY')
w3 = Web3(Web3.HTTPProvider('https://rpc.sepolia.org'))
balance = float(w3.from_wei(w3.eth.get_balance(wallet.address), 'ether'))
print(f'余额: {balance:.4f} ETH')
if balance < 0.01:
    print('⚠️  余额不足，需要至少 0.01 ETH')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 请先领取测试币"
    echo "📋 水龙头: https://sepoliafaucet.com/"
    exit 1
fi

# 部署
echo ""
echo "📦 部署合约..."
cd /Users/Zhuanz1/Desktop/auto_defi_agent
python3 scripts/deploy_erc8004.py --network $NETWORK --private-key "$PRIVATE_KEY"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 部署成功！"
    echo "📁 配置已保存到 src/integrations/erc8004_config.json"
else
    echo "❌ 部署失败"
fi
