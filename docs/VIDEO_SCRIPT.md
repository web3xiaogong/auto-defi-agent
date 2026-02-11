# Auto-DeFi Agent - 演示视频脚本

## 🎬 视频信息
- **时长**: 5 分钟
- **场景**: 屏幕录制 + 旁白
- **工具**: QuickTime Player (Cmd+Shift+5 录屏)

---

## 📍 场景 1: 开场 (30秒)

### 旁白:
```
大家好！我是 Auto-DeFi Agent，今天要展示一个智能 DeFi 收益优化助手。

这个项目解决什么问题？
• DeFi 机会发现困难
• 投资决策缺乏数据支持
• 策略分享不方便
• 透明度不足

我会展示 4 个核心功能...
```

### 画面:
- 显示项目 README.md
- 展示 GitHub stars (如果有了)

---

## 📍 场景 2: ML 预测演示 (1分钟)

### 旁白:
```
首先来看看我们的 ML 预测引擎。

它能预测 APY 走势，给出买卖建议。
```

### 命令:
```bash
cd /Users/Zhuanz1/Desktop/auto_defi_agent
python3 src/ml/apy_predictor.py --pool "CAKE-USDT" --points 14
```

### 画面:
- 运行命令
- 展示预测结果
- highlight 置信度和建议

### 旁白:
```
看到了吗？系统预测 CAKE-USDT 会下跌，建议卖出。
置信度达到 63%，这是一个相当可靠的信号。
```

---

## 📍 场景 3: 策略分享演示 (1分钟)

### 旁白:
```
现在来看看策略分享功能。

我可以创建一个策略，然后生成分享链接和二维码。
```

### 命令:
```bash
python3 src/sharing/strategy_share.py --pool "CAKE-USDT" --apy 15.0 --chain BSC --qr
```

### 画面:
- 运行命令
- 展示分享码和二维码
- 打开二维码图片

### 旁白:
```
生成了分享码和二维码！
其他人可以扫描二维码或输入分享码来使用这个策略。
```

---

## 📍 场景 4: 多链扫描演示 (1分钟)

### 旁白:
```
接下来是跨链能力。

我们的系统支持 4 条链：BSC、opBNB、Ethereum、Arbitrum。
```

### 命令:
```bash
python3 src/multi_chain/__init__.py --scan
```

### 画面:
- 运行命令
- 展示扫描结果
- 展示每条链的最佳 APY

### 旁白:
```
扫描完成！系统发现 6 个机会，最佳在 opBNB 上，APY 达到 27%！

这就是多链聚合的价值——找到最佳收益。
```

---

## 📍 场景 5: 跟单系统演示 (1分钟)

### 旁白:
```
最后来看看跟单交易系统。

我可以跟随顶级交易者，自动复制他们的操作。
```

### 命令:
```bash
python3 src/copy_trading/copy_trading_manager.py --demo
```

### 画面:
- 运行命令
- 展示交易者排行榜
- 展示已复制的订单

### 旁白:
```
这里展示了排行榜和复制订单。
用户可以选择跟随评分最高的交易者，系统会自动复制他们的操作。
```

---

## 📍 场景 6: 总结 (30秒)

### 旁白:
```
总结一下 Auto-DeFi Agent 的核心价值：

1. AI 自动化 - 减少人工监控
2. ML 预测 - 数据驱动的决策
3. 多链访问 - 发现最佳收益
4. 跟单系统 - 复制成功策略
5. 链上证明 - 透明可验证

感谢观看！项目已在 GitHub 开源，欢迎贡献代码！

GitHub: https://github.com/[YOUR_USERNAME]/auto-defi-agent
```

### 画面:
- 显示 GitHub 链接
- 联系方式

---

## 🎬 录制提示

### 工具:
- **Mac**: QuickTime Player (Cmd+Shift+5)
- **Windows**: OBS Studio
- **Linux**: OBS Studio

### 设置:
- 分辨率: 1920x1080
- 帧率: 30fps
- 音频: 内置麦克风

### 技巧:
1. 先演练 2-3 遍
2. 说话慢一点，清楚一点
3. 暂停 2-3 秒再切换场景
4. 保持光线充足，背景整洁

---

## 📁 输出文件

- **演示视频**: demo_video.mp4
- **幻灯片**: presentation.pdf
- **项目链接**: https://github.com/[YOUR_USERNAME]/auto-defi-agent
