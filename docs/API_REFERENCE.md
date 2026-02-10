# API Reference

## CLI Commands

### scan
扫描 DeFi 池寻找机会。

```bash
python3 src/cli.py scan --chain BSC --min-apy 10
```

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--chain` | string | BSC | 要扫描的链 |
| `--min-apy` | number | 5.0 | 最小 APY 百分比 |

### status
显示 Agent 状态。

```bash
python3 src/cli.py status
```

输出：
- Agent 状态 (IDLE/MONITORING/EXECUTING)
- 运行时间
- 发现的机会数
- 交易历史
- 性能指标

### strategy
生成收益率优化策略。

```bash
python3 src/cli.py strategy --chain BSC
```

返回：
- 最佳机会
- 风险分析
- 建议操作
- 预期收益

### risk
分析特定机会的风险。

```bash
python3 src/cli.py risk --chain BSC
```

风险因素：
- TVL（越高越安全）
- 协议声誉
- APY 稳定性
- 历史表现

### execute
执行策略（需要手动批准）。

```bash
python3 src/cli.py execute --chain BSC --approve
```

---

## Python API

### AutoDeFiAgent

```python
from agents.strategy_agent import AutoDeFiAgent, StrategyConfig

# 创建 Agent
config = StrategyConfig(
    min_apy=10.0,
    max_slippage=1.0,
    auto_execute=False
)
agent = AutoDeFiAgent(config=config)

# 启动
agent.start()

# 扫描机会
pools = defi_service.get_bsc_pancake_pools()
opportunities = agent.scan_opportunities(pools)

# 获取最佳机会
best = agent.get_best_opportunity()

# 分析风险
risk = agent.analyze_risk(best)

# 生成策略
strategy = agent.generate_strategy()

# 停止
agent.stop()
```

### BSCAdapter

```python
from tools.bsc_adapter import BSCAdapter

# 创建适配器
adapter = BSCAdapter(
    rpc_url="https://bsc-dataseed.binance.org/",
    private_key="0x..."  # 可选
)

# 检查连接
adapter.is_connected

# 获取余额
balance = adapter.get_balance(address)

# 获取代币余额
token_balance = adapter.get_token_balance(token_address, holder_address)

# 执行 Swap
tx_hash = adapter.swap_tokens(
    token_in="0x...",
    token_out="0x...",
    amount_in_wei=1000000,
    amount_out_min_wei=900000
)

# 获取 Gas 价格
gas_price = adapter.get_gas_price()
```

### DeFiService

```python
from tools.defi_service import DeFiService

# 创建服务
service = DeFiService(bsc_api_key="...")

# 获取池列表
pools = service.get_bsc_pancake_pools()

# 获取高 APY 池
high_apy = service.get_high_apy_pools(chain="BSC", min_tvl=10000)

# 获取 Gas 价格
gas = service.get_gas_price_bsc()

# 计算策略
strategy = service.calculate_yield_strategy(
    principal_usd=1000,
    risk_level="medium"
)
```

---

## 配置

### 环境变量

```bash
# BSC RPC
BSC_RPC=https://bsc-dataseed.binance.org/

# 钱包
WALLET_PRIVATE_KEY=0x...
WALLET_ADDRESS=0x...

# PancakeSwap Router
PANCAKE_ROUTER=0x10ED43C718714eb63d5aA57B78B54704E256024E
```

---

## 风险评分

风险评分范围 0-1：

| 分数 | 风险等级 | 建议 |
|------|----------|------|
| 0.7-1.0 | LOW | 建议执行 |
| 0.4-0.7 | MEDIUM | 谨慎操作 |
| 0-0.4 | HIGH | 不建议 |

---

## 错误码

| 代码 | 含义 | 解决方案 |
|------|------|----------|
| 401 | 无效 Token | 检查 API Key |
| 403 | 无权限 | 确认钱包余额 |
| 409 | Token 已使用 | 重新获取 |
| 410 | 挑战过期 | 重新开始流程 |
