---
name: auto-defi-agent
description: Smart DeFi Yield Optimization Assistant for BNB Chain. Monitor APY, analyze risks, and execute yield strategies on BSC and opBNB.
metadata:
  {
    "openclaw": {
      "emoji": "🤖",
      "requires": {
        "bins": ["python3"]
      },
      "install": [
        {
          "id": "pip-deps",
          "kind": "pip",
          "packages": ["web3", "pandas", "python-dotenv", "requests"],
          "label": "Install Python dependencies (web3, pandas, requests)"
        }
      ],
      "skills": {
        "description": "Auto-DeFi Agent for BSC/opBNB yield optimization",
        "parameters": {
          "properties": {
            "action": {
              "enum": ["scan", "status", "strategy", "risk", "execute"],
              "description": "Action to perform"
            },
            "chain": {
              "enum": ["BSC", "opBNB"],
              "description": "Blockchain network"
            },
            "min_apy": {
              "description": "Minimum APY threshold",
              "type": "number"
            },
            "auto_execute": {
              "description": "Automatically execute trades",
              "type": "boolean"
            }
          },
          "required": ["action"]
        }
      }
    },
    "author": "OpenClaw Agent",
    "version": "1.0.0",
    "license": "MIT",
    "repository": ""
  }
---

# Auto-DeFi Agent Skill 🤖

Smart DeFi Yield Optimization Assistant for BNB Chain

## Description

This skill integrates the **Auto-DeFi Agent** for BSC and opBNB networks. It helps you:

- 📊 **Monitor** real-time APY across DeFi protocols
- 🎯 **Identify** high-yield opportunities
- 📈 **Analyze** risks with automated scoring
- ⚡ **Execute** yield optimization strategies (with approval)

## Quick Start

```bash
# Scan for opportunities
/auto-defi-agent scan --chain BSC --min-apy 10

# Check agent status
/auto-defi-agent status

# Get strategy recommendation
/auto-defi-agent strategy --chain BSC

# Analyze risk of best opportunity
/auto-defi-agent risk --chain BSC

# Execute strategy (requires approval)
/auto-defi-agent execute --chain BSC
```

## Examples

### Scan for High-APY Pools

```
You: Scan for DeFi opportunities on BSC with minimum 15% APY
Agent: 
> Fetching pools from DeFi Llama...
> Found 23 pools meeting criteria
> Top opportunity: CAKE-USDT at 24.5% APY
> TVL: $2.5M | Risk Score: 0.72 (LOW)
> Recommendation: EXECUTE
```

### Check Current Status

```
You: What's the agent status?
Agent:
> State: IDLE
> Running: True
> Opportunities Found: 47
> Transactions: 3
> Last Check: 2026-02-10T20:00:00
> Total Profit: $15.42
```

### Get Strategy

```
You: Generate a strategy for BSC
Agent:
> Best: PANCAKE-WBNB at 18.2% APY
> Risk Analysis:
>   - TVL Score: HIGH (+0.3)
>   - Protocol: Known (+0.2)
>   - APY Factor: Medium (-0.1)
> Overall: 0.75 (LOW RISK)
> Recommendation: SWAP 100 USDT → WBNB → Stake in Pool
```

## Configuration

### Required Environment Variables

```bash
# BSC RPC
BSC_RPC=https://bsc-dataseed.binance.org/

# Wallet (optional - for transactions)
WALLET_ADDRESS=0x...
WALLET_PRIVATE_KEY=0x...

# Telegram notifications (optional)
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

### OpenClaw Integration

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "auto-defi-agent": {
      "enabled": true,
      "config": {
        "chain": "BSC",
        "min_apy": 5.0,
        "auto_execute": false
      }
    }
  }
}
```

## Technical Architecture

```
┌─────────────────────────────────────────┐
│         OpenClaw Agent Skill             │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │ Scanner │→ │Strategy │→ │ Analyzer││
│  └─────────┘  └─────────┘  └─────────┘│
│       │              │            │      │
│       └─────────────┼────────────┘      │
│                     │                   │
│       ┌─────────────▼────────────┐       │
│       │   BSC / opBNB Adapter   │       │
│       │   (web3.py)             │       │
│       └─────────────────────────┘       │
└─────────────────────────────────────────┘
```

## Commands

### scan
Scan DeFi pools for opportunities.

```
/auto-defi-agent scan --chain BSC --min-apy 10 [--auto-execute]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chain` | string | BSC | Network to scan |
| `min-apy` | number | 5.0 | Minimum APY % |
| `auto-execute` | boolean | false | Auto-execute best strategy |

### status
Show current agent status and metrics.

```
/auto-defi-agent status
```

Output:
- Agent state (IDLE/MONITORING/EXECUTING)
- Opportunities found
- Transaction history
- Performance metrics

### strategy
Generate yield optimization strategy.

```
/auto-defi-agent strategy --chain BSC
```

Returns:
- Best opportunity
- Risk analysis
- Recommended action
- Expected return

### risk
Analyze risk of specific or best opportunity.

```
/auto-defi-agent risk --chain BSC [--pool POOL_ADDRESS]
```

Risk Factors:
- TVL (higher = safer)
- Protocol reputation
- APY stability
- Historical performance

### execute
Execute a yield strategy (requires approval).

```
/auto-defi-agent execute --chain BSC --pool ADDRESS --amount 100
```

Safety:
- Requires explicit approval
- Shows transaction details before signing
- Estimates gas costs
- Allows setting slippage

## Use Cases

### 1. Daily APY Monitoring

```
You: Check for any pools above 20% APY
Agent scans, finds 3 opportunities, shows details
```

### 2. Portfolio Rebalancing

```
You: Rebalance my stablecoin holdings
Agent finds best yield, suggests swap strategy
```

### 3. Gas-Optimized Trading

```
You: Execute when gas < 10 gwei
Agent monitors gas, executes when optimal
```

## Safety Features

| Feature | Description |
|----------|-------------|
| 🛡️ Risk Scoring | 0-1 risk score for each opportunity |
| 💰 Slippage Control | Max 1% by default, configurable |
| ⛽ Gas Monitoring | Wait for low gas periods |
| 📊 Position Limits | Max position size configurable |
| 🔔 Notifications | Telegram alerts for opportunities |

## Hackathon Context

This skill was built for **Good Vibes Only: OpenClaw Edition** hackathon.

- **Track**: Agent (AI Agent x Onchain Actions)
- **Chain**: BSC + opBNB
- **Category**: DeFi Automation

## Files

- `src/main.py` - Entry point
- `src/config.py` - Configuration
- `src/agents/strategy_agent.py` - Core logic
- `src/tools/bsc_adapter.py` - BSC integration
- `src/tools/defi_service.py` - DeFi data

## Requirements

- Python 3.10+
- web3.py
- pandas
- requests
- python-dotenv

## Installation

```bash
# Install dependencies
pip install web3 pandas requests python-dotenv

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

## License

MIT License - OpenClaw Ecosystem

---

**Built with 🤖 OpenClaw Agent Framework**
