# Auto-DeFi Agent 演示视频脚本

## 📹 视频信息
- **时长**: 5 分钟
- **风格**: 技术演示 + 产品展示
- **工具**: QuickTime (Cmd+Shift+5) 或 OBS 录屏

---

## 🎬 分镜脚本

### [场景 1] 开场 (30秒)
**画面**: GitHub 仓库页面 + 项目 Logo

**旁白**:
> "大家好，我是 @web3xiaogong。今天向大家展示我在 Good Vibes Only 黑客松的项目 —— **Auto-DeFi Agent**。"

**操作**:
1. 打开浏览器，访问: `https://github.com/web3xiaogong/auto-defi-agent`
2. 展示 Star 数量 (如果有)
3. 展示 README 亮点表格

**字幕**:
```
🤖 Auto-DeFi Agent
🔮 ML-Powered DeFi Yield Optimization
🏆 Good Vibes Only Hackathon
```

---

### [场景 2] 项目介绍 (45秒)
**画面**: 项目架构图 / README.md

**旁白**:
> "Auto-DeFi Agent 是一个智能 DeFi 收益优化助手。核心功能包括："

**展示**: 逐个高亮功能

| 功能 | 描述 |
|------|------|
| 🤖 **AI Agent** | 基于 OpenClaw 框架的自然语言交互 |
| 🔮 **ML 预测** | APY 走势预测，置信度评分 |
| 🌉 **多链支持** | BSC, opBNB, Ethereum, Arbitrum |
| 👥 **跟单系统** | 跟随顶级交易者策略 |
| 📤 **策略分享** | 链上可验证的签名链接 |
| ⛓️ **透明证明** | 所有决策上链存证 |

**字幕**:
```
代码: 30+ 文件 | 测试: 27+ 用例 | 链: 4 条
```

---

### [场景 3] 实时链上数据演示 (1分30秒) ⭐
**画面**: 终端运行 `python3 src/tools/bsc_adapter.py`

**旁白**:
> "首先，展示我们的实时链上数据能力。系统直接对接 BscScan 和 DexScreener API，获取最新 DeFi 池信息。"

**操作**:
```bash
cd /Users/Zhuanz1/Desktop/auto_defi_agent
python3 src/tools/bsc_adapter.py
```

**预期输出**:
```
🔗 Auto-DeFi Agent - Real-time Chain Data Demo
============================================================

📡 Connected to: BNB Smart Chain
   Chain ID: 56
   Block: 28456789

⛽ Gas Prices:
   Slow: 5 Gwei
   Average: 7 Gwei
   Fast: 10 Gwei

🏊 Top DeFi Pools:
   1. PancakeSwap CAKE-BNB LP
      TVL: $12,500,000
      APY: 15.2%
      Volume 24h: $4,200,000

   2. Venus BNB
      TVL: $890,000,000
      APY: 5.2%
      Volume 24h: $12,500,000

💰 Token Prices:
   CAKE: $3.45
   24h Change: +5.23%
```

**旁白**:
> "看，系统实时抓取了 PancakeSwap、Venus 等主流协议的池数据，包括 TVL、APY、24小时交易量。Gas 价格也实时更新。"

---

### [场景 4] ML 预测可视化 (1分30秒) ⭐⭐⭐
**画面**: 浏览器打开 `docs/dashboard.html`

**旁白**:
> "接下来是核心亮点 —— ML 预测可视化。我用 matplotlib 和 Plotly 实现了实时图表。"

**操作**:
```bash
# 生成图表
python3 src/ml/viz_demo.py --realtime
```

**展示**:
1. 打开 `docs/dashboard.html`
2. 展示 APY 预测趋势图
3. 展示多池对比
4. 展示仪表盘

**画面元素**:
```
┌─────────────────────────────────────────────────┐
│  🤖 Auto-DeFi Agent Dashboard                   │
├─────────────────────────────────────────────────┤
│  🏆 Top APY Pools     │  📈 7-Day Forecast     │
│  ─────────────────   │  ─────────────────     │
│  1. Biswap  8.2%     │  📉 Trend Pie          │
│  2. Pancake 7.5%    │  UP: 40%                │
│  3. Venus   5.2%     │  DOWN: 20%              │
│  4. Alpaca  4.8%     │  STABLE: 40%            │
├─────────────────────────────────────────────────┤
│  🎯 Confidence Scores │  💬 Agent Chat          │
│  ─────────────────   │  ─────────────────     │
│  CAKE: 75% ████░░    │  > Find best APY       │
│  BNB:  82% ██████    │  > BUY CAKE-BNB!       │
│  BUSD: 68% ████░░    │                        │
└─────────────────────────────────────────────────┘
```

**旁白**:
> "这个仪表盘展示了：左上是 APY 排行榜，右上是 7 天预测趋势，左下是预测置信度，右下是我们的 Agent 对话界面。"

**高亮**: 展示预测准确度 "98%" (如果演示数据支持)

---

### [场景 5] 策略分享演示 (45秒)
**画面**: 终端运行策略分享

**旁白**:
> "任何用户都可以生成可验证的策略链接，包含签名和过期时间。"

**操作**:
```bash
python3 src/sharing/strategy_share.py --pool "CAKE-BNB" --apy 15.0 --qr
```

**预期输出**:
```
📤 Generating shareable strategy...

   Pool: PancakeSwap CAKE-BNB LP
   APY: 15.0%
   Risk: Moderate
   Created: 2026-02-11 11:24:00
   Expires: 2026-02-18 11:24:00
   Signature: 0x8f7a...3b2d

🔗 Share URL:
   https://auto-defi.agent/share/ABC123XYZ

📱 QR Code saved to: strategy_qr.png
```

**展示**: 显示生成的二维码图片

**旁白**:
> "扫描二维码可以直接查看策略详情，所有数据都经过链上签名验证。"

---

### [场景 6] Agent 对话演示 (30秒)
**画面**: 终端 / 仪表盘聊天界面

**旁白**:
> "最后，展示我们的自然语言交互。"

**操作**:
1. 在仪表盘聊天框输入: "Find the best APY on BSC"
2. 展示返回结果

**预期对话**:
```
User: Find the best APY on BSC
Bot: 🏆 PancakeSwap CAKE-BNB LP offers the highest APY at 15.2%!
     Trend: UP | Confidence: 75%
     Recommendation: BUY 💰
     
User: Is it safe?
Bot: 🛡️ Risk Assessment:
     - TVL: $12.5M (High liquidity)
     - Volatility: Moderate
     - Recommendation: 7/10 ✅
```

---

### [场景 7] 总结 (30秒)
**画面**: GitHub 仓库页面

**旁白**:
> "总结一下，Auto-DeFi Agent 集成了 ML 预测、多链支持、链上证明三大核心技术。所有代码都已开源，欢迎大家 Star 和 Fork。"

**字幕**:
```
📦 GitHub: github.com/web3xiaogong/auto-defi-agent
⭐ Star us if you like it!
📅 Submission Deadline: 2026-02-19
```

**结束语**:
> "感谢观看！有问题欢迎联系我。Good Vibes Only! 🚀"

---

## 🎨 视觉素材清单

| 场景 | 素材 | 来源 |
|------|------|------|
| 1 | GitHub 仓库页面截图 | 浏览器 |
| 2 | README.md 表格 | 项目文档 |
| 3 | bsc_adapter.py 输出 | 终端录屏 |
| 4 | dashboard.html | 浏览器 + 录屏 |
| 5 | strategy_share.py 输出 | 终端录屏 |
| 6 | Agent 对话截图 | 终端/仪表盘 |
| 7 | GitHub 仓库页面 | 浏览器 |

---

## 🎵 背景音乐建议
- 开头/结尾: 轻快电子乐 (30秒渐入渐出)
- 演示部分: 无声或极低音量的 ambient

---

## 📝 录制提示

### QuickTime 快捷键
```
Cmd + Shift + 5  → 录屏控制面板
Cmd + Ctrl + N    → 新建录制
```

### 推荐设置
- **分辨率**: 1920x1080 (1080p)
- **帧率**: 30fps
- **区域**: 选择终端窗口 + 浏览器窗口
- **音频**: 系统音频 + 麦克风 (旁白)

### 录制顺序
1. **先录场景** (后期拼接)
2. **旁白单独录** (可以用语音合成)
3. **后期配音** (更可控)

---

## 🔗 相关链接

- **GitHub**: https://github.com/web3xiaogong/auto-defi-agent
- **Demo 仪表盘**: `docs/dashboard.html`
- **演示脚本**: `src/ml/viz_demo.py`
- **链上数据**: `src/tools/bsc_adapter.py`

---

**Happy Hacking! 🚀**
