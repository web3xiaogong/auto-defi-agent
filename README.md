# Auto-DeFi Agent - Web3 DeFi Command Center

## 🏆 Good Vibes Only: OpenClaw Edition Hackathon

**ML-Powered DeFi Yield Optimization Platform**

---

## 🎯 产品愿景

构建一个统一的 Web3 DeFi 指挥中心，让用户通过自然语言：

```
"找到 BSC 上 APY > 15% 的池，用最优路径兑换并质押"
        ↓
    Auto-DeFi Agent → 解析 → 执行 → 链上证明
```

---

## 🚀 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| **多链扫描** | BSC, opBNB, Ethereum, Arbitrum | ✅ |
| **ML 预测** | APY 走势 + 置信度评分 | ✅ |
| **策略分享** | ERC-8004 市场集成 | ✅ |
| **跟单交易** | 跟随顶级交易者 | ✅ |
| **链上证明** | 决策透明可验证 | ✅ |
| **多通道** | Telegram/Discord/WhatsApp | ✅ |
| **钱包集成** | MetaMask, OKX, Rabby | 🔄 |

---

## 📊 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Auto-DeFi Agent                       │
├─────────────────────────────────────────────────────────┤
│  📱 Multi-Channel Layer                                  │
│  ├── Telegram Adapter                                   │
│  ├── Discord Adapter                                    │
│  ├── WhatsApp Adapter                                   │
│  └── iMessage Adapter                                   │
├─────────────────────────────────────────────────────────┤
│  🧠 OpenClaw Agent Layer                                │
│  ├── Intent Parser                                      │
│  ├── Strategy Planner                                   │
│  └── Execution Engine                                   │
├─────────────────────────────────────────────────────────┤
│  🔧 Skills Layer                                        │
│  ├── defi-scan       (DeFi 数据扫描)                    │
│  ├── ml-predict      (ML 预测)                         │
│  ├── strategy-share  (策略分享)                         │
│  ├── copy-trading    (跟单交易)                         │
│  ├── onchain-proof   (链上证明)                        │
│  └── erc8004-registry (ERC-8004 注册)                   │
├─────────────────────────────────────────────────────────┤
│  ⛓️ Blockchain Layer                                     │
│  ├── BSC Adapter                                        │
│  ├── opBNB Adapter                                      │
│  ├── Ethereum Adapter                                   │
│  └── Arbitrum Adapter                                   │
├─────────────────────────────────────────────────────────┤
│  🌐 External APIs                                        │
│  ├── BscScan/Etherscan                                 │
│  ├── DexScreener                                        │
│  ├── PancakeSwap                                        │
│  └── Venus/Aave                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
auto-defi-agent/
├── src/
│   ├── main.py                    # 主入口
│   ├── cli.py                     # CLI 工具
│   ├── config.py                   # 配置
│   │
│   ├── agents/
│   │   └── strategy_agent.py       # OpenClaw Agent
│   │
│   ├── tools/
│   │   ├── bsc_adapter.py          # BSC 链适配器
│   │   ├── defi_service.py         # DeFi 服务
│   │   └── multi_chain_adapter.py  # 多链适配器
│   │
│   ├── ml/
│   │   ├── apy_predictor.py        # ML 预测模型
│   │   ├── viz.py                  # 可视化
│   │   └── viz_demo.py             # 演示脚本
│   │
│   ├── sharing/
│   │   ├── strategy_share.py        # 策略分享
│   │   └── onchain_proof.py        # 链上证明
│   │
│   ├── copy_trading/
│   │   └── copy_trading_manager.py # 跟单交易
│   │
│   └── integrations/
│       ├── erc8004.py              # ERC-8004 市场
│       └── channels.py             # 多通道消息
│
├── contracts/
│   ├── DecisionRegistry.sol        # 决策合约
│   └── CopyTrading.sol             # 跟单合约
│
├── tests/                          # 测试用例
├── docs/                           # 文档
│   ├── dashboard.html              # 交互式仪表盘
│   ├── VIDEO_SCRIPT.md             # 视频脚本
│   └── API_REFERENCE.md            # API 文档
│
├── SKILL.md                        # OpenClaw Skill
├── README.md                       # 项目说明
└── requirements.txt                # 依赖
```

---

## 💻 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
```bash
# 设置钱包
export WALLET_PRIVATE_KEY="0x..."

# 设置 RPC (可选)
export BSC_RPC_URL="https://bsc-dataseed1.binance.org"
```

### 3. 运行 CLI
```bash
# 扫描机会
python3 src/cli.py scan --min-apy 10

# ML 预测
python3 src/cli.py predict CAKE-BNB

# 查看排行榜
python3 src/cli.py leaderboard

# 分享策略
python3 src/cli.py share --pool CAKE-BNB --apy 15.0
```

### 4. 运行 Web 仪表盘
```bash
python3 src/ml/viz_demo.py --realtime
# 打开 docs/dashboard.html
```

---

## 🎮 OpenClaw Skills 使用

### 安装 Skill
```bash
# 复制到 OpenClaw Skills 目录
cp SKILL.md /path/to/openclaw/skills/auto-defi-agent/
```

### 在对话中使用
```
@agent: scan --min-apy 15
@agent: predict CAKE-BNB
@agent: share my strategy
```

---

## 🔗 集成 ERC-8004

### 注册 Agent
```python
from src.integrations.erc8004 import ERC8004Registry

registry = ERC8004Registry(
    rpc_url="https://base.public.blastapi.io",
    private_key="0x..."
)

agent_info = AgentInfo(
    name="Auto-DeFi Agent",
    services=["defi-optimization", "apy-prediction"],
    capabilities=["multi-chain", "ml-prediction"]
)

result = registry.register_agent(agent_info)
```

### 发布策略
```python
from src.integrations.erc8004 import StrategyMarketplace

marketplace = StrategyMarketplace(
    rpc_url="https://base.public.blastapi.io",
    private_key="0x..."
)

listing = StrategyListing(
    name="CAKE-BNB High APY Strategy",
    pool_name="PancakeSwap CAKE-BNB",
    chain="BSC",
    apy_estimate=15.0,
    risk_level="MEDIUM",
    price_eth=0.01
)

result = marketplace.publish_strategy(listing)
```

---

## 📊 多通道消息

### Telegram 示例
```python
from src.integrations.channels import ChannelManager, Channel

manager = ChannelManager()
manager.add_adapter(Channel.TELEGRAM, TelegramAdapter("BOT_TOKEN"))

data = {
    "pools": [
        {"name": "PancakeSwap", "apy": 15.2, "tvl": 12500000},
    ],
    "prediction": {"predicted_apy_7d": 16.5, "trend": "UP"}
}

manager.send_defi_result(data, Channel.TELEGRAM, chat_id="12345")
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

---

## 📈 路线图

### v1.0 (当前)
- ✅ 多链 DeFi 扫描
- ✅ ML APY 预测
- ✅ 策略分享
- ✅ 链上证明
- ✅ 基础 CLI

### v1.1 (待完成)
- 🔄 跟单交易功能
- 🔄 ERC-8004 主网集成
- 🔄 多通道消息 (Telegram/Discord)
- 🔄 实时仪表盘增强

### v2.0 (规划中)
- 📅 策略订阅市场
- 📅 社区治理
- 📅 移动端 App
- 📅 AI 交易信号

---

## 🏆 竞争优势

| 维度 | Auto-DeFi Agent | 竞品 |
|------|-----------------|------|
| **多链支持** | BSC + opBNB + ETH + ARB | 单一链 |
| **ML 预测** | 内置预测模型 | 依赖外部 |
| **链上证明** | 决策可验证 | 无 |
| **OpenClaw 集成** | 原生 Skill | 无 |
| **ERC-8004** | 即将上线 | 无 |
| **开源** | MIT License | 闭源 |

---

## 📄 许可证

MIT License

---

## 👥 团队

- **开发者**: @web3xiaogong
- **联系**: Telegram @web3xiaogong

---

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - Agent 框架
- [BNB Chain](https://bnbchain.org) - 区块链基础设施
- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) - Agent Registry 标准
- [Good Vibes Only](https://goodvibesonly.xyz) - 黑客松组织
