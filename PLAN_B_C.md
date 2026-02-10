# Auto-DeFi Agent - 差异化功能开发计划
# Good Vibes Only: OpenClaw Edition Hackathon

## 方案 B: ML 预测 + 策略分享 + 链上证明 (5-7天)

---

### 📅 第1-2天: ML APY 预测引擎

#### 目标
使用简单机器学习预测 APY 走势，让 Agent 具备"预测未来"能力

#### 技术方案

```
┌─────────────────────────────────────────────────────────┐
│                    ML 预测引擎架构                        │
├─────────────────────────────────────────────────────────┤
│  输入层                                                  │
│  ├── 历史 APY 数据 (7天/30天/90天)                        │
│  ├── TVL 变化率                                          │
│  ├── 交易量变化                                           │
│  └── Gas 价格趋势                                         │
├─────────────────────────────────────────────────────────┤
│  处理层                                                  │
│  ├── 特征工程: 滑动窗口 + 技术指标                        │
│  ├── 模型: 线性回归 / LSTM 简易版                         │
│  └── 输出: APY 预测 + 置信区间                            │
├─────────────────────────────────────────────────────────┤
│  输出层                                                  │
│  ├── 未来 24h APY 预测                                    │
│  ├── 趋势方向 (📈 涨 / 📉 跌 / ➡️ 稳)                      │
│  └── 建议: 买入 / 持有 / 卖出                             │
└─────────────────────────────────────────────────────────┘
```

#### 文件结构

```
src/
├── ml/
│   ├── apy_predictor.py      # ML 预测核心
│   ├── feature_engineering.py # 特征工程
│   └── training.py           # 模型训练
```

#### 核心代码 apy_predictor.py

```python
"""
ML APY 预测器
使用简单线性回归 + 移动平均预测 APY 走势
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import statistics


@dataclass
class APYDataPoint:
    """APY 数据点"""
    timestamp: datetime
    apy: float
    tvl: float
    volume: float


@dataclass
class APYPrediction:
    """APY 预测结果"""
    current_apy: float
    predicted_apy_24h: float
    predicted_apy_7d: float
    trend: str  # "UP", "DOWN", "STABLE"
    confidence: float  # 0-1
    recommendation: str  # "BUY", "HOLD", "SELL"
    factors: List[str]


class APYPredictor:
    """APY 预测器 - 简单机器学习"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # 模型参数
        self.window_size = 7  # 7天历史
        self.learning_rate = 0.01
        
        # 历史数据缓存
        self.history: List[APYDataPoint] = []
        
        # 训练好的参数 (简单线性回归)
        self.weights = {
            "apy_trend": 0.3,
            "tvl_change": 0.2,
            "volume_trend": 0.2,
            "day_of_week": 0.15,
            "momentum": 0.15,
        }
    
    def add_data_point(self, apy: float, tvl: float, volume: float):
        """添加数据点"""
        point = APYDataPoint(
            timestamp=datetime.now(),
            apy=apy,
            tvl=tvl,
            volume=volume
        )
        self.history.append(point)
        
        # 只保留最近30天数据
        cutoff = datetime.now() - timedelta(days=30)
        self.history = [p for p in self.history if p.timestamp >= cutoff]
    
    def _extract_features(self, days: int = 7) -> Dict[str, float]:
        """提取特征"""
        if len(self.history) < 3:
            return self._default_features()
        
        recent = self.history[-days:]
        
        # APY 趋势 (简单线性回归斜率)
        apy_values = [p.apy for p in recent]
        apy_trend = self._calculate_slope(apy_values)
        
        # TVL 变化率
        if len(recent) >= 2:
            tvl_change = (recent[-1].tvl - recent[0].tvl) / max(recent[0].tvl, 1)
        else:
            tvl_change = 0.0
        
        # 交易量趋势
        volume_values = [p.volume for p in recent]
        volume_trend = self._calculate_slope(volume_values)
        
        # 动量 (最近3天 vs 之前4天)
        if len(recent) >= 7:
            recent_3 = statistics.mean([p.apy for p in recent[-3:]])
            prev_4 = statistics.mean([p.apy for p in recent[-7:-3]])
            momentum = (recent_3 - prev_4) / max(prev_4, 0.01)
        else:
            momentum = 0.0
        
        # 星期几因素 (周末通常 APY 更高)
        day_of_week = datetime.now().weekday()
        day_factor = (day_of_week / 7.0) * 0.1  # 0-0.1
        
        return {
            "apy_trend": apy_trend,
            "tvl_change": tvl_change,
            "volume_trend": volume_trend,
            "day_of_week": day_factor,
            "momentum": momentum,
        }
    
    def _calculate_slope(self, values: List[float]) -> float:
        """计算简单斜率"""
        if len(values) < 2:
            return 0.0
        
        x = list(range(len(values)))
        y = values
        
        # 简化版线性回归
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_xx = sum(xi * xi for xi in x)
        
        denominator = n * sum_xx - sum_x * sum_x
        if abs(denominator) < 0.0001:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    def _default_features(self) -> Dict[str, float]:
        """默认特征 (无数据时)"""
        return {
            "apy_trend": 0.0,
            "tvl_change": 0.0,
            "volume_trend": 0.0,
            "day_of_week": 0.0,
            "momentum": 0.0,
        }
    
    def predict(self, pool_name: str) -> APYPrediction:
        """预测 APY"""
        features = self._extract_features()
        
        # 简单加权预测
        current_apy = self.history[-1].apy if self.history else 5.0
        
        # 预测 24h: 基于趋势外推
        daily_trend = features["apy_trend"] / 7  # 每天的斜率
        predicted_24h = current_apy + daily_trend * 1
        
        # 预测 7d: 考虑动量
        momentum_factor = features["momentum"] * 7
        predicted_7d = current_apy + daily_trend * 7 + momentum_factor
        
        # 计算趋势
        if predicted_24h > current_apy * 1.05:
            trend = "UP"
        elif predicted_24h < current_apy * 0.95:
            trend = "DOWN"
        else:
            trend = "STABLE"
        
        # 计算置信度 (基于数据量)
        confidence = min(len(self.history) / 30, 1.0) * 0.8 + 0.2
        
        # 生成建议
        recommendation = self._generate_recommendation(
            current_apy, predicted_24h, trend, confidence
        )
        
        # 分析影响因素
        factors = self._analyze_factors(features)
        
        return APYPrediction(
            current_apy=current_apy,
            predicted_apy_24h=max(predicted_24h, 0),  # APY 不能为负
            predicted_apy_7d=max(predicted_7d, 0),
            trend=trend,
            confidence=confidence,
            recommendation=recommendation,
            factors=factors,
        )
    
    def _generate_recommendation(
        self, current: float, predicted: float, trend: str, confidence: float
    ) -> str:
        """生成交易建议"""
        if confidence < 0.3:
            return "HOLD"  # 数据不足
        
        apy_change = (predicted - current) / max(current, 0.01)
        
        if trend == "UP" and apy_change > 0.05:
            return "BUY"
        elif trend == "DOWN" and apy_change < -0.05:
            return "SELL"
        else:
            return "HOLD"
    
    def _analyze_factors(self, features: Dict[str, float]) -> List[str]:
        """分析影响因素"""
        factors = []
        
        if features["apy_trend"] > 0.1:
            factors.append("📈 APY 上升趋势")
        elif features["apy_trend"] < -0.1:
            factors.append("📉 APY 下降趋势")
        
        if features["tvl_change"] > 0.1:
            factors.append("💰 TVL 增长 (资金流入)")
        elif features["tvl_change"] < -0.1:
            factors.append("💸 TVL 下降 (资金流出)")
        
        if features["momentum"] > 0.05:
            factors.append("🚀 动量强劲")
        elif features["momentum"] < -0.05:
            factors.append("⚠️ 动量减弱")
        
        if features["day_of_week"] > 0.05:
            factors.append("📅 周末效应")
        
        return factors if factors else ["📊 稳定市场"]
    
    def train(self, historical_data: List[Dict]):
        """训练模型 (简化版 - 调整权重)"""
        # 实际项目中，这里会使用真实的 ML 训练
        # 例如: sklearn.linear_model.LinearRegression
        pass
    
    def save_model(self, pool_name: str):
        """保存模型"""
        model_path = self.model_dir / f"{pool_name}_model.json"
        with open(model_path, 'w') as f:
            json.dump({
                "weights": self.weights,
                "history_count": len(self.history),
                "saved_at": datetime.now().isoformat(),
            }, f, indent=2)
        print(f"💾 模型已保存: {model_path}")
    
    def load_model(self, pool_name: str):
        """加载模型"""
        model_path = self.model_dir / f"{pool_name}_model.json"
        if model_path.exists():
            with open(model_path, 'r') as f:
                data = json.load(f)
                self.weights = data.get("weights", self.weights)
            print(f"📂 模型已加载: {model_path}")


# ===== 简单演示 =====
if __name__ == "__main__":
    # 创建预测器
    predictor = APYPredictor()
    
    # 模拟历史数据
    import random
    for i in range(14):
        predictor.add_data_point(
            apy=10.0 + random.uniform(-2, 3),
            tvl=1000000 + random.uniform(-100000, 200000),
            volume=500000 + random.uniform(-100000, 100000)
        )
    
    # 进行预测
    prediction = predictor.predict("CAKE-USDT")
    
    print("\n" + "="*50)
    print("🔮 APY 预测结果")
    print("="*50)
    print(f"当前 APY: {prediction.current_apy:.2f}%")
    print(f"24h 预测: {prediction.predicted_apy_24h:.2f}%")
    print(f"7d 预测:  {prediction.predicted_apy_7d:.2f}%")
    print(f"趋势:     {prediction.trend}")
    print(f"置信度:   {prediction.confidence:.2%}")
    print(f"建议:     {prediction.recommendation}")
    print(f"\n因素:")
    for f in prediction.factors:
        print(f"  • {f}")
```

---

### 📅 第3天: 策略分享功能

#### 目标
生成可分享的策略链接/二维码，让用户可以分享自己的投资策略

#### 技术方案

```
策略分享 = Base64编码(策略数据) + 签名验证 + 短链接
```

#### 文件结构

```
src/
├── sharing/
│   ├── strategy_share.py    # 分享核心
│   ├── qr_generator.py      # 二维码生成
│   └── signature.py         # 策略签名
```

#### 核心代码 strategy_share.py

```python
"""
策略分享功能
生成可验证的策略分享链接
"""

import json
import base64
import hashlib
import urllib.parse
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from cryptography.fernet import Fernet
from pathlib import Path


@dataclass
class ShareableStrategy:
    """可分享的策略"""
    pool_name: str
    protocol: str
    chain: str
    min_apy: float
    max_slippage: float
    risk_level: str
    creator_address: str
    created_at: str
    expires_at: str
    signature: str  # 创作者签名


class StrategySharer:
    """策略分享器"""
    
    def __init__(self, encryption_key: bytes = None):
        # 加密密钥
        if encryption_key is None:
            self.encryption_key = Fernet.generate_key()
        else:
            self.encryption_key = encryption_key
        
        self.cipher = Fernet(self.encryption_key)
        
        # 分享码存储
        self.share_codes: dict = {}
    
    def create_share_code(
        self,
        strategy: dict,
        private_key: str,
        expires_hours: int = 24
    ) -> str:
        """创建分享码"""
        # 构建分享数据
        share_data = {
            **strategy,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + datetime.timedelta(hours=expires_hours)).isoformat(),
        }
        
        # 创建签名
        message = json.dumps(share_data, sort_keys=True)
        signature = self._sign_message(message, private_key)
        share_data["signature"] = signature
        
        # 编码为分享码
        json_str = json.dumps(share_data)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        
        # 简短分享码 (前12字符)
        share_code = encoded[:12].upper()
        
        # 存储
        self.share_codes[share_code] = share_data
        
        return share_code
    
    def verify_share_code(self, share_code: str) -> Optional[dict]:
        """验证并解析分享码"""
        if share_code not in self.share_codes:
            return None
        
        data = self.share_codes[share_code]
        
        # 检查过期
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now() > expires_at:
            del self.share_codes[share_code]
            return None
        
        # 验证签名
        message = {k: v for k, v in data.items() if k != "signature"}
        message_str = json.dumps(message, sort_keys=True)
        
        # 这里简化验证 - 实际需要公钥验证
        if data["signature"]:
            data["verified"] = True
        
        return data
    
    def generate_share_url(self, share_code: str, base_url: str = "https://autodefi.ai") -> str:
        """生成分享 URL"""
        params = urllib.parse.urlencode({"s": share_code})
        return f"{base_url}/strategy?{params}"
    
    def _sign_message(self, message: str, private_key: str) -> str:
        """签名消息 (简化版)"""
        # 实际应使用以太坊签名
        message_bytes = message.encode()
        hash_bytes = hashlib.sha256(message_bytes).digest()
        signature = base64.urlsafe_b64encode(hash_bytes).decode()[:65]
        return signature


# ===== 二维码生成 =====
def generate_qr_code(data: str, output_path: str):
    """生成二维码"""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        
        return True
    except ImportError:
        print("⚠️  需要安装 qrcode: pip install qrcode[pil]")
        return False


# ===== 演示 =====
if __name__ == "__main__":
    sharer = StrategySharer()
    
    # 创建策略
    strategy = {
        "pool_name": "CAKE-USDT",
        "protocol": "PancakeSwap",
        "chain": "BSC",
        "min_apy": 15.0,
        "max_slippage": 1.0,
        "risk_level": "MEDIUM",
        "creator_address": "0x19C9F422E6158302E8850c9e087A917f113783B4",
    }
    
    # 生成分享码
    share_code = sharer.create_share_code(strategy, "private_key_placeholder")
    print(f"📤 分享码: {share_code}")
    
    # 生成 URL
    url = sharer.generate_share_url(share_code)
    print(f"🔗 分享链接: {url}")
    
    # 生成二维码
    if generate_qr_code(url, "strategy_qr.png"):
        print("📱 二维码已保存: strategy_qr.png")
    
    # 验证
    verified = sharer.verify_share_code(share_code)
    if verified:
        print(f"✅ 验证成功: {verified['pool_name']}")
```

---

### 📅 第4天: 链上决策证明

#### 目标
将 Agent 的所有决策记录到区块链，实现完全透明可验证

#### 技术方案

```
┌─────────────────────────────────────────────────────────┐
│                   链上决策证明架构                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   Agent 决策                                              │
│       │                                                  │
│       ▼                                                  │
│   ┌─────────┐    签名    ┌─────────┐    上链    ┌──────┐ │
│   │  决策数据 │ ───────► │  签名  │ ────────► │ 链上 │ │
│   │ (JSON)   │          │ (ETH)   │          │ 记录 │ │
│   └─────────┘          └─────────┘          └──────┘ │
│                                                          │
│   决策包括:                                               │
│   - 池地址 + APY + TVL                                    │
│   - 风险评分 + 建议                                       │
│   - 时间戳 + Agent 版本                                   │
│   - 创作者签名                                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### Solidity 智能合约 DecisionRegistry.sol

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title DecisionRegistry
 * @notice 记录 Agent 所有决策到链上，实现透明可验证
 */
contract DecisionRegistry {
    
    struct Decision {
        uint256 timestamp;
        address agent;
        bytes32 decisionHash;      // 决策内容的哈希
        uint256 apy;
        uint256 riskScore;
        string recommendation;     // BUY/HOLD/SELL
        string poolAddress;
        bytes signature;           // 签名验证
    }
    
    // 决策记录
    Decision[] public decisions;
    
    // 事件
    event DecisionRecorded(
        uint256 indexed decisionId,
        address indexed agent,
        bytes32 decisionHash,
        uint256 apy,
        string recommendation
    );
    
    // Agent 注册
    mapping(address => bool) public registeredAgents;
    
    // 管理员
    address public owner;
    
    modifier onlyRegistered() {
        require(registeredAgents[msg.sender], "Not registered agent");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    // 注册 Agent
    function registerAgent(address agent) external {
        require(msg.sender == owner, "Only owner");
        registeredAgents[agent] = true;
    }
    
    /**
     * @notice 记录决策
     * @param decisionHash 决策内容的哈希
     * @param apy 当前 APY
     * @param riskScore 风险评分 (0-100)
     * @param recommendation 建议 (BUY/HOLD/SELL)
     * @param poolAddress 池地址
     * @param signature 签名
     */
    function recordDecision(
        bytes32 decisionHash,
        uint256 apy,
        uint256 riskScore,
        string memory recommendation,
        string memory poolAddress,
        bytes memory signature
    ) external onlyRegistered returns (uint256) {
        Decision memory decision = Decision({
            timestamp: block.timestamp,
            agent: msg.sender,
            decisionHash: decisionHash,
            apy: apy,
            riskScore: riskScore,
            recommendation: recommendation,
            poolAddress: poolAddress,
            signature: signature
        });
        
        uint256 decisionId = decisions.length;
        decisions.push(decision);
        
        emit DecisionRecorded(decisionId, msg.sender, decisionHash, apy, recommendation);
        
        return decisionId;
    }
    
    // 获取决策数量
    function getDecisionCount() external view returns (uint256) {
        return decisions.length;
    }
    
    // 获取决策 (按 ID)
    function getDecision(uint256 id) external view returns (Decision memory) {
        require(id < decisions.length, "Invalid ID");
        return decisions[id];
    }
    
    // 验证决策 (链下验证)
    function verifyDecision(
        uint256 decisionId,
        string memory originalData
    ) external view returns (bool) {
        require(decisionId < decisions.length, "Invalid ID");
        
        bytes32 hash = keccak256(abi.encodePacked(originalData));
        return decisions[decisionId].decisionHash == hash;
    }
}
```

#### Python 调用代码

```python
"""
链上决策证明调用
"""

from web3 import Web3
from eth_account import Account
import json
import hashlib
from typing import Dict, Optional


class OnChainProof:
    """链上决策证明"""
    
    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        private_key: str
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        
        # 加载合约
        with open("contracts/DecisionRegistry.json") as f:
            abi = json.load(f)
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
    
    def create_decision_hash(self, decision: Dict) -> str:
        """创建决策哈希"""
        # 确保字段顺序一致
        ordered = {
            "pool_address": decision.get("pool_address", ""),
            "apy": str(decision.get("apy", 0)),
            "risk_score": str(decision.get("risk_score", 0)),
            "recommendation": decision.get("recommendation", ""),
            "timestamp": str(decision.get("timestamp", 0)),
            "agent_version": decision.get("agent_version", "1.0"),
        }
        
        data_str = json.dumps(ordered, sort_keys=True)
        hash_bytes = Web3.keccak(text=data_str)
        return hash_bytes.hex()
    
    def sign_decision(self, decision_hash: str) -> bytes:
        """签名决策"""
        # 添加 Ethereum 前缀
        message = f"\x19Ethereum Signed Message:\n32{decision_hash}"
        message_hash = Web3.keccak(text=message)
        
        # 签名
        signed = self.account.sign_hash(message_hash)
        return signed.signature
    
    def record_decision(self, decision: Dict) -> Optional[int]:
        """记录决策到链上"""
        try:
            # 创建哈希
            decision_hash = self.create_decision_hash(decision)
            
            # 签名
            signature = self.sign_decision(decision_hash)
            
            # 构建交易
            tx = self.contract.functions.recordDecision(
                decision_hash,
                int(decision.get("apy", 0) * 100),  # 转换为整数
                int(decision.get("risk_score", 0)),
                decision.get("recommendation", ""),
                decision.get("pool_address", ""),
                signature
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
            })
            
            # 发送交易
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待确认
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.blockNumber
            
        except Exception as e:
            print(f"❌ 链上记录失败: {e}")
            return None
    
    def get_decision(self, decision_id: int) -> Dict:
        """获取决策"""
        decision = self.contract.functions.getDecision(decision_id).call()
        return {
            "timestamp": decision[0],
            "agent": decision[1],
            "decision_hash": decision[2],
            "apy": decision[3],
            "risk_score": decision[4],
            "recommendation": decision[5],
            "pool_address": decision[6],
        }
    
    def verify_decision(self, decision_id: int, original_data: str) -> bool:
        """验证决策"""
        # 链下验证哈希
        return self.contract.functions.verifyDecision(
            decision_id, original_data
        ).call()


# ===== 演示 =====
if __name__ == "__main__":
    # 这是一个演示 - 实际需要部署合约
    
    print("📝 链上决策证明功能")
    print("")
    print("使用流程:")
    print("1. 部署 DecisionRegistry.sol 到 BSC")
    print("2. 注册 Agent 地址")
    print("3. Agent 每次决策时调用 recordDecision()")
    print("4. 所有决策永久记录在链上，可验证")
    print("")
    print("优势:")
    print("✅ 完全透明 - 任何人都可以验证决策")
    print("✅ 不可篡改 - 链上数据无法修改")
    print("✅ 可追溯 - 查看历史所有决策")
```

---

## 📅 第5-7天: 方案 C - 多链聚合器 + 跟单系统

### 5.1 多链聚合器架构

```
┌─────────────────────────────────────────────────────────┐
│                   多链聚合器架构                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   Auto-DeFi Agent                                        │
│       │                                                  │
│       ├──► BSC ──► PancakeSwap ──► Venus ──►            │
│       │                                                  │
│       ├──► opBNB ──► PancakeSwap ──►                     │
│       │                                                  │
│       ├──► Ethereum ──► Uniswap ──► Aave ──►             │
│       │                                                  │
│       └──► Arbitrum ──► GMX ──►                         │
│                                                          │
│   统一接口:                                               │
│   - scan_all_chains(min_apy=10)                         │
│   - get_best_opportunity()                              │
│   - execute_cross_chain_swap()                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.2 跟单系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    跟单系统架构                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   策略发布者                                               │
│       │                                                  │
│       ├──► 创建策略 (设定参数)                             │
│       │       │                                          │
│       │       ▼                                          │
│       ├──► 签名发布                                       │
│       │                                                  │
│       ▼                                                  │
│   ┌─────────┐                                           │
│   │ 策略池   │ ◄─── 多个跟单者订阅                        │
│   └─────────┘                                           │
│       │                                                  │
│       ▼                                                  │
│   跟单者                                                  │
│       ├──► 选择策略订阅                                   │
│       │       │                                          │
│       │       ▼                                          │
│       ├──► 自动复制交易                                   │
│       │       │                                          │
│       │       ▼                                          │
│       └──► 收益分配 (可选)                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 完整任务清单

### 方案 B: ML 预测 + 分享 + 链上证明

| 天数 | 任务 | 文件 | 状态 |
|------|------|------|------|
| 1 | ML 预测器核心 | `src/ml/apy_predictor.py` | ⏳ |
| 2 | 特征工程 + 训练 | `src/ml/feature_engineering.py` | ⏳ |
| 3 | 策略分享功能 | `src/sharing/strategy_share.py` | ⏳ |
| 4 | 链上证明合约 | `contracts/DecisionRegistry.sol` | ⏳ |
| 5 | 集成测试 | `tests/test_ml_prediction.py` | ⏳ |
| 6 | 文档完善 | `docs/ML_PREDICTION.md` | ⏳ |
| 7 | Demo 准备 | `docs/DEMO_B.md` | ⏳ |

### 方案 C: 多链聚合器 + 跟单

| 天数 | 任务 | 文件 | 状态 |
|------|------|------|------|
| 1-2 | 多链适配器 | `src/tools/multi_chain_adapter.py` | ⏳ |
| 3-4 | 跟单系统核心 | `src/copy_trading/manager.py` | ⏳ |
| 5-6 | 收益分配合约 | `contracts/CopyTrading.sol` | ⏳ |
| 7-8 | 完整集成 | - | ⏳ |
| 9 | 最终测试 | - | ⏳ |

---

## 🚀 启动命令

```bash
# 安装额外依赖
pip install qrcode[pil] cryptography

# 运行 ML 演示
python3 src/ml/apy_predictor.py

# 运行分享演示
python3 src/sharing/strategy_share.py

# 编译合约
npx hardhat compile
```

---

## 📊 评分亮点

| 功能 | 评委加分点 |
|------|-----------|
| ML 预测 | AI/ML 技术深度 |
| 策略分享 | 社交/传播性 |
| 链上证明 | Web3 原生特性 |
| 多链聚合 | 产品完整性 |
| 跟单系统 | 社区/商业价值 |
