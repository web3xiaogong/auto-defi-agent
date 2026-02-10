# Demo Script for Good Vibes Only: OpenClaw Edition

## 演示流程 (约5分钟)

### 开场 (30秒)
```
"大家好，我是 Auto-DeFi Agent，今天要展示的是一个基于 OpenClaw 框架的智能 DeFi 收益优化助手。"
```

---

### 1. 项目介绍 (1分钟)

```bash
# 显示项目结构
tree -L 2 -I '__pycache__|*.pyc'
```

```
auto_defi_agent/
├── src/
│   ├── main.py           # 主入口
│   ├── cli.py           # 命令行工具
│   ├── config.py        # 配置管理
│   ├── agents/         # Agent 核心
│   └── tools/          # BSC/DeFi 工具
├── tests/              # 测试用例
├── docs/               # 文档
└── SKILL.md            # OpenClaw 技能
```

---

### 2. 功能演示 (2分钟)

#### 2.1 扫描机会

```bash
python3 src/cli.py scan --min-apy 10
```

预期输出：
```
🔍 Scanning BSC for APY ≥ 10.0%...
✅ Found 5 opportunities:

1. CAKE-USDT
   Protocol: PancakeSwap
   APY: 24.5%
   TVL: $2.5M
   Confidence: 85%
```

#### 2.2 查看状态

```bash
python3 src/cli.py status
```

预期输出：
```
🤖 Auto-DeFi Agent Status
========================================
State: IDLE
Running: True
Opportunities Found: 5
Transactions: 0
Last Check: 2026-02-10T20:00:00
```

#### 2.3 风险分析

```bash
python3 src/cli.py risk --chain BSC
```

预期输出：
```
📊 Risk Analysis for CAKE-USDT
Score: 0.75 (LOW)

Factors:
  • TVL: HIGH (+0.3)
  • Protocol: Known (+0.2)
  • APY: Medium (-0.1)

💡 Recommendation: EXECUTE
```

---

### 3. 技术亮点 (1分钟)

#### 3.1 Agent 核心逻辑

```bash
# 显示策略引擎代码
head -50 src/agents/strategy_agent.py
```

#### 3.2 链上交互

```bash
# 显示 BSC 适配器
head -30 src/tools/bsc_adapter.py
```

---

### 4. OpenClaw 集成 (30秒)

```bash
# 显示技能配置
cat SKILL.md | head -30
```

```
# Auto-DeFi Agent Skill 🤖

Smart DeFi Yield Optimization Assistant for BNB Chain

- 📊 Monitor real-time APY
- 🎯 Identify high-yield opportunities
- 📈 Analyze risks
- ⚡ Execute yield strategies
```

---

### 5. 结尾 (30秒)

```
"Auto-DeFi Agent 已经准备好参与 Good Vibes Only: OpenClaw Edition 黑客松。

这是一个完全开源、透明、可验证的 DeFi 工具。

感谢大家！"
```

---

## 备用演示 (如果网络不可用)

如果无法连接 BSC，可以使用本地测试模式：

```python
# 在测试中使用 mock 数据
from agents.strategy_agent import AutoDeFiAgent, StrategyConfig, Opportunity

agent = AutoDeFiAgent()
agent.opportunities = [
    Opportunity("Test Pool", "Test", "BSC", 25.0, 1000000, "A/B", "0x...", 0.8),
]
print(agent.get_best_opportunity())
```

---

## 常见问题

**Q: 需要多少资金开始？**
A: 建议至少 100 USDT 等值资产

**Q: 安全性如何？**
A: 风险评分系统 + 手动确认 + Gas 监控

**Q: 支持哪些链？**
A: BSC + opBNB
