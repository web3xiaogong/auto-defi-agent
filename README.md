# Auto-DeFi Agent

## 🏆 Good Vibes Only: OpenClaw Edition Hackathon 参赛项目

**智能 DeFi 收益优化助手** - 支持多链、ML 预测、跟单交易

---

## 🎯 项目亮点

| 功能 | 描述 | 状态 |
|------|------|------|
| 🤖 AI Agent | OpenClaw 框架集成 | ✅ |
| 🔮 ML 预测 | APY 走势预测 | ✅ |
| 🌉 多链支持 | BSC, opBNB, Ethereum, Arbitrum | ✅ |
| 👥 跟单系统 | 跟随顶级交易者 | ✅ |
| 📤 策略分享 | 可分享的策略链接 | ✅ |
| ⛓️ 链上证明 | 决策透明可验证 | ✅ |

---

## 📊 项目统计

- **代码文件**: 25+
- **测试用例**: 27
- **文档**: 10+
- **支持链**: 4

---

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/your-repo/auto-defi-agent.git
cd auto_defi_agent

# 安装依赖
pip install -r requirements.txt --break-system-packages

# 配置钱包
cp .env.example .env
# 编辑 .env 添加 WALLET_PRIVATE_KEY

# 运行
python3 src/main.py
```

---

## 📁 项目结构

```
auto_defi_agent/
├── src/
│   ├── main.py                    # 主入口
│   ├── cli.py                     # CLI 工具
│   ├── config.py                  # 配置
│   ├── agents/
│   │   └── strategy_agent.py      # Agent 核心
│   ├── tools/
│   │   ├── bsc_adapter.py         # BSC 适配器
│   │   └── defi_service.py        # DeFi 服务
│   ├── ml/
│   │   └── apy_predictor.py       # ML 预测
│   ├── sharing/
│   │   ├── strategy_share.py      # 策略分享
│   │   └── onchain_proof.py       # 链上证明
│   ├── multi_chain/
│   │   └── multi_chain_adapter.py # 多链适配器
│   └── copy_trading/
│       └── copy_trading_manager.py # 跟单系统
├── contracts/
│   ├── DecisionRegistry.sol       # 决策合约
│   └── copy_trading/
│       └── CopyTrading.sol        # 跟单合约
├── tests/                         # 测试用例
├── docs/                          # 文档
└── SKILL.md                       # OpenClaw 技能
```

---

## 💻 使用方法

### CLI 命令

```bash
# 查看状态
python3 src/cli.py status

# 扫描机会
python3 src/cli.py scan --min-apy 10

# 查看策略
python3 src/cli.py strategy --chain BSC

# 风险分析
python3 src/cli.py risk --chain BSC
```

### ML 预测

```bash
python3 src/ml/apy_predictor.py --pool "CAKE-USDT" --points 14
```

### 策略分享

```bash
python3 src/sharing/strategy_share.py --pool "CAKE-USDT" --apy 15.0 --qr
```

### 多链扫描

```bash
python3 src/multi_chain/__init__.py --scan
```

### 跟单演示

```bash
python3 src/copy_trading/copy_trading_manager.py --demo
```

---

## 🧪 测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 测试覆盖率
python3 -m pytest tests/ --cov=src
```

---

## 📖 文档

- [README.md](README.md) - 项目说明
- [SKILL.md](SKILL.md) - OpenClaw 技能
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - API 文档
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - 部署指南
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - 演示脚本
- [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) - 完整演示指南
- [docs/PLAN_B_COMPLETE.md](docs/PLAN_B_COMPLETE.md) - 方案 B 完成报告
- [docs/PLAN_C_COMPLETE.md](docs/PLAN_C_COMPLETE.md) - 方案 C 完成报告

---

## 🎓 技术栈

- **Python 3.10+**
- **Web3.py** - 区块链交互
- **OpenClaw** - Agent 框架
- **Pandas/NumPy** - 数据分析
- **Solidity** - 智能合约
- **pytest** - 测试

---

## 📅 开发时间线

- **2026-02-10**: 项目启动
- **2026-02-10**: 基础功能完成
- **2026-02-10**: 方案 B 完成 (ML预测+分享+链上证明)
- **2026-02-10**: 方案 C 完成 (多链+跟单)
- **2026-02-19**: 黑客松提交截止

---

## 👥 团队

- **开发者**: @web3xiaogong
- **联系**: Telegram @web3xiaogong

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - Agent 框架
- [BNB Chain](https://bnbchain.org) - 区块链基础设施
- [Good Vibes Only](https://goodvibesonly.xyz) - 黑客松组织
