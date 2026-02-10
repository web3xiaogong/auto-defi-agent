"""
ML APY 预测器
使用机器学习预测 DeFi 池 APY 走势

Good Vibes Only: OpenClaw Edition Hackathon
"""

import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import statistics
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APYDataPoint:
    """APY 数据点"""
    timestamp: datetime
    apy: float
    tvl: float
    volume: float
    pool_address: str = ""


@dataclass
class APYPrediction:
    """APY 预测结果"""
    pool_name: str
    pool_address: str
    current_apy: float
    predicted_apy_24h: float
    predicted_apy_7d: float
    trend: str  # "UP", "DOWN", "STABLE"
    confidence: float  # 0-1
    recommendation: str  # "BUY", "HOLD", "SELL"
    factors: List[str]
    risk_warning: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "pool_name": self.pool_name,
            "pool_address": self.pool_address,
            "current_apy": round(self.current_apy, 2),
            "predicted_apy_24h": round(self.predicted_apy_24h, 2),
            "predicted_apy_7d": round(self.predicted_apy_7d, 2),
            "trend": self.trend,
            "confidence": round(self.confidence, 2),
            "recommendation": self.recommendation,
            "factors": self.factors,
            "risk_warning": self.risk_warning,
        }


@dataclass
class ModelConfig:
    """模型配置"""
    window_size: int = 7          # 历史窗口大小 (天)
    min_data_points: int = 3      # 最少数据点
    max_history_days: int = 90    # 最大历史天数
    confidence_threshold: float = 0.5  # 置信度阈值
    
    # 权重配置
    weight_apy_trend: float = 0.25
    weight_tvl_change: float = 0.20
    weight_volume_trend: float = 0.15
    weight_momentum: float = 0.25
    weight_seasonality: float = 0.15


class APYPredictor:
    """
    APY 预测器 - 机器学习简化版
    
    使用技术:
    - 线性回归 (趋势预测)
    - 移动平均 (平滑处理)
    - 动量指标 (趋势强度)
    - 季节性因子 (周期性)
    """
    
    def __init__(self, config: ModelConfig = None, model_dir: str = "models"):
        self.config = config or ModelConfig()
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True, parents=True)
        
        # 存储每个池的历史数据
        self.pool_data: Dict[str, List[APYDataPoint]] = {}
        
        # 模型参数
        self.weights = {
            "apy_trend": self.config.weight_apy_trend,
            "tvl_change": self.config.weight_tvl_change,
            "volume_trend": self.config.weight_volume_trend,
            "momentum": self.config.weight_momentum,
            "seasonality": self.config.weight_seasonality,
        }
        
        # 缓存
        self._predictions_cache: Dict[str, APYPrediction] = {}
        self._last_scan: Optional[datetime] = None
    
    def add_data_point(
        self,
        pool_address: str,
        pool_name: str,
        apy: float,
        tvl: float,
        volume: float,
        timestamp: datetime = None
    ):
        """添加数据点"""
        if pool_address not in self.pool_data:
            self.pool_data[pool_address] = []
        
        point = APYDataPoint(
            timestamp=timestamp or datetime.now(),
            apy=apy,
            tvl=tvl,
            volume=volume,
            pool_address=pool_address,
        )
        self.pool_data[pool_address].append(point)
        
        # 清理过期数据
        self._cleanup_expired_data(pool_address)
        
        # 清除该池的缓存
        if pool_address in self._predictions_cache:
            del self._predictions_cache[pool_address]
    
    def add_batch_data(self, pool_address: str, pool_name: str, data: List[Dict]):
        """批量添加数据点"""
        for point in data:
            self.add_data_point(
                pool_address=pool_address,
                pool_name=pool_name,
                apy=point.get("apy", 0),
                tvl=point.get("tvl", 0),
                volume=point.get("volume", 0),
                timestamp=datetime.fromisoformat(point.get("timestamp", datetime.now().isoformat()))
            )
    
    def _cleanup_expired_data(self, pool_address: str):
        """清理过期数据"""
        if pool_address not in self.pool_data:
            return
        
        cutoff = datetime.now() - timedelta(days=self.config.max_history_days)
        self.pool_data[pool_address] = [
            p for p in self.pool_data[pool_address] 
            if p.timestamp >= cutoff
        ]
    
    def _extract_features(self, pool_address: str) -> Dict[str, float]:
        """提取特征"""
        if pool_address not in self.pool_data:
            return self._default_features()
        
        history = self.pool_data[pool_address]
        if len(history) < self.config.min_data_points:
            return self._default_features()
        
        # 使用最近 N 天的数据
        window = self.config.window_size
        recent = [p for p in history[-window:] if p.timestamp >= datetime.now() - timedelta(days=window)]
        
        if len(recent) < self.config.min_data_points:
            recent = history
        
        # 1. APY 趋势 (线性回归斜率)
        apy_values = [p.apy for p in recent]
        apy_trend = self._calculate_slope(apy_values)
        
        # 2. TVL 变化率
        if len(recent) >= 2:
            tvl_change = (recent[-1].tvl - recent[0].tvl) / max(recent[0].tvl, 1)
        else:
            tvl_change = 0.0
        
        # 3. 交易量趋势
        volume_values = [p.volume for p in recent]
        volume_trend = self._calculate_slope(volume_values)
        
        # 4. 动量 (短期 vs 长期)
        if len(recent) >= 7:
            short_term = statistics.mean([p.apy for p in recent[-3:]])
            long_term = statistics.mean([p.apy for p in recent[:-3]])
            momentum = (short_term - long_term) / max(long_term, 0.01)
        elif len(recent) >= 4:
            momentum = (recent[-1].apy - recent[0].apy) / max(recent[0].apy, 0.01)
        else:
            momentum = 0.0
        
        # 5. 季节性因子 (星期几效应)
        # 周末通常 DeFi 活跃度不同
        day_of_week = datetime.now().weekday()
        # 周末 (5,6) APY 通常稍高
        seasonality = 0.0
        if day_of_week in [5, 6]:
            seasonality = 0.05  # +5% 周末效应
        
        return {
            "apy_trend": apy_trend,
            "tvl_change": tvl_change,
            "volume_trend": volume_trend,
            "momentum": momentum,
            "seasonality": seasonality,
        }
    
    def _calculate_slope(self, values: List[float]) -> float:
        """计算线性回归斜率"""
        n = len(values)
        if n < 2:
            return 0.0
        
        x = list(range(n))
        y = values
        
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
            "momentum": 0.0,
            "seasonality": 0.0,
        }
    
    def _calculate_prediction_score(self, features: Dict[str, float]) -> Tuple[float, str, str]:
        """计算预测评分"""
        # 加权得分
        score = (
            features["apy_trend"] * self.weights["apy_trend"] * 10 +
            features["tvl_change"] * self.weights["tvl_change"] * 10 +
            features["volume_trend"] * self.weights["volume_trend"] * 10 +
            features["momentum"] * self.weights["momentum"] * 10 +
            features["seasonality"] * self.weights["seasonality"]
        )
        
        # 确定趋势
        if score > 0.05:
            trend = "UP"
            trend_emoji = "📈"
        elif score < -0.05:
            trend = "DOWN"
            trend_emoji = "📉"
        else:
            trend = "STABLE"
            trend_emoji = "➡️"
        
        return score, trend, trend_emoji
    
    def _generate_recommendation(
        self,
        current_apy: float,
        predicted_24h: float,
        trend: str,
        confidence: float,
        risk_score: float
    ) -> str:
        """生成交易建议"""
        if confidence < self.config.confidence_threshold:
            return "HOLD"
        
        apy_change_pct = (predicted_24h - current_apy) / max(current_apy, 0.01)
        
        if risk_score > 0.7:
            # 高风险，降低建议级别
            if trend == "UP" and apy_change_pct > 0.1:
                return "HOLD"
            return "SELL"
        
        if trend == "UP" and apy_change_pct > 0.08:
            return "BUY"
        elif trend == "DOWN" and apy_change_pct < -0.08:
            return "SELL"
        else:
            return "HOLD"
    
    def _analyze_factors(self, features: Dict[str, float]) -> List[str]:
        """分析影响因素"""
        factors = []
        
        # APY 趋势
        if features["apy_trend"] > 0.1:
            factors.append("📈 APY 强劲上升")
        elif features["apy_trend"] > 0.05:
            factors.append("📈 APY 温和上升")
        elif features["apy_trend"] < -0.1:
            factors.append("📉 APY 显著下降")
        elif features["apy_trend"] < -0.05:
            factors.append("📉 APY 温和下降")
        else:
            factors.append("➡️ APY 走势平稳")
        
        # TVL 变化
        if features["tvl_change"] > 0.2:
            factors.append("💰 资金大幅流入 (+TVL)")
        elif features["tvl_change"] > 0.1:
            factors.append("💵 资金流入 (+TVL)")
        elif features["tvl_change"] < -0.2:
            factors.append("💸 资金大幅流出 (-TVL)")
        elif features["tvl_change"] < -0.1:
            factors.append("📉 资金流出 (-TVL)")
        
        # 动量
        if features["momentum"] > 0.1:
            factors.append("🚀 动量强劲，看涨")
        elif features["momentum"] > 0.05:
            factors.append("📊 动量为正")
        elif features["momentum"] < -0.1:
            factors.append("⚠️ 动量减弱，看跌")
        elif features["momentum"] < -0.05:
            factors.append("📉 动量为负")
        
        # 季节性
        if features["seasonality"] > 0:
            factors.append("📅 周末效应 (可能更高)")
        
        return factors
    
    def predict(
        self,
        pool_address: str,
        pool_name: str = "Unknown"
    ) -> Optional[APYPrediction]:
        """预测 APY 走势"""
        # 检查缓存 (5分钟内有效)
        cache_key = f"{pool_address}"
        if cache_key in self._predictions_cache:
            cached = self._predictions_cache[cache_key]
            if datetime.now() - datetime.fromisoformat(
                cached.pool_address  # 借用字段存储时间
            ) < timedelta(minutes=5):
                return cached
        
        # 获取特征
        features = self._extract_features(pool_address)
        
        # 获取当前 APY
        history = self.pool_data.get(pool_address, [])
        current_apy = history[-1].apy if history else 5.0
        
        # 计算预测
        score, trend, trend_emoji = self._calculate_prediction_score(features)
        
        # 预测 24h (基于趋势外推)
        daily_change = score / 7 if features["apy_trend"] != 0 else score
        predicted_24h = current_apy * (1 + daily_change + features["seasonality"])
        predicted_24h = max(predicted_24h, 0)  # APY 不能为负
        
        # 预测 7d (考虑动量)
        momentum_effect = features["momentum"] * 7
        predicted_7d = current_apy * (1 + daily_change * 7 + momentum_effect + features["seasonality"])
        predicted_7d = max(predicted_7d, 0)
        
        # 计算置信度 (基于数据量)
        data_points = len(history)
        confidence = min(data_points / 30, 1.0) * 0.7 + 0.3  # 30天数据 = 100% 置信度
        confidence = min(confidence, 0.95)  # 最高 95%
        
        # 计算风险评分
        risk_factors = 0.0
        if abs(features["apy_trend"]) > 0.2:
            risk_factors += 0.2  # APY 波动大
        if abs(features["tvl_change"]) > 0.3:
            risk_factors += 0.2  # TVL 变化大
        if confidence < 0.5:
            risk_factors += 0.3  # 数据不足
        
        risk_score = min(risk_factors, 1.0)
        risk_warning = ""
        if risk_score > 0.7:
            risk_warning = "⚠️ 高波动性，请谨慎"
        elif risk_score > 0.5:
            risk_warning = "⚡ 中等风险"
        
        # 生成建议
        recommendation = self._generate_recommendation(
            current_apy, predicted_24h, trend, confidence, risk_score
        )
        
        # 分析因素
        factors = self._analyze_factors(features)
        
        # 构建结果
        prediction = APYPrediction(
            pool_name=pool_name,
            pool_address=pool_address,
            current_apy=current_apy,
            predicted_apy_24h=predicted_24h,
            predicted_apy_7d=predicted_7d,
            trend=trend,
            confidence=confidence,
            recommendation=recommendation,
            factors=factors,
            risk_warning=risk_warning,
        )
        
        # 缓存
        self._predictions_cache[cache_key] = prediction
        
        return prediction
    
    def predict_all(self) -> List[APYPrediction]:
        """预测所有池"""
        predictions = []
        for pool_address in self.pool_data:
            pred = self.predict(pool_address)
            if pred:
                predictions.append(pred)
        return predictions
    
    def get_top_opportunities(self, min_apy: float = 5.0, limit: int = 5) -> List[APYPrediction]:
        """获取最佳机会 (按预测 APY 排序)"""
        predictions = self.predict_all()
        
        # 过滤并排序
        filtered = [
            p for p in predictions 
            if p.current_apy >= min_apy and p.recommendation == "BUY"
        ]
        sorted_pools = sorted(
            filtered,
            key=lambda x: (x.current_apy * x.confidence),
            reverse=True
        )
        
        return sorted_pools[:limit]
    
    def get_risk_analysis(self, pool_address: str) -> Dict:
        """获取风险分析"""
        history = self.pool_data.get(pool_address, [])
        
        if len(history) < 2:
            return {"risk_level": "UNKNOWN", "reason": "数据不足"}
        
        apy_values = [p.apy for p in history]
        
        # 计算波动性
        volatility = statistics.stdev(apy_values) / statistics.mean(apy_values) if statistics.mean(apy_values) > 0 else 0
        
        # TVL 变化
        tvl_change = (history[-1].tvl - history[0].tvl) / max(history[0].tvl, 1) if history[0].tvl > 0 else 0
        
        # 综合风险
        risk_score = min(volatility * 0.5 + abs(tvl_change) * 0.3 + 0.2, 1.0)
        
        if risk_score < 0.3:
            risk_level = "LOW"
        elif risk_score < 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "volatility": round(volatility, 2),
            "tvl_change": round(tvl_change, 2),
            "data_points": len(history),
        }
    
    def save_model(self, pool_address: str):
        """保存模型"""
        model_path = self.model_dir / f"{pool_address}.json"
        
        model_data = {
            "pool_address": pool_address,
            "weights": self.weights,
            "config": {
                "window_size": self.config.window_size,
                "min_data_points": self.config.min_data_points,
            },
            "history_count": len(self.pool_data.get(pool_address, [])),
            "saved_at": datetime.now().isoformat(),
        }
        
        with open(model_path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"💾 模型已保存: {model_path}")
    
    def load_model(self, pool_address: str) -> bool:
        """加载模型"""
        model_path = self.model_dir / f"{pool_address}.json"
        
        if model_path.exists():
            with open(model_path, 'r') as f:
                model_data = json.load(f)
                self.weights = model_data.get("weights", self.weights)
            
            logger.info(f"📂 模型已加载: {model_path}")
            return True
        
        return False
    
    def export_predictions(self) -> str:
        """导出预测结果 (JSON)"""
        predictions = self.predict_all()
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_pools": len(predictions),
            "predictions": [p.to_dict() for p in predictions],
        }
        return json.dumps(data, indent=2)
    
    def clear_cache(self):
        """清除缓存"""
        self._predictions_cache.clear()
        logger.info("🗑️ 预测缓存已清除")


# ===== CLI 接口 =====
def main():
    """CLI 演示"""
    import argparse
    import random
    
    parser = argparse.ArgumentParser(description="APY Prediction CLI")
    parser.add_argument("--pool", default="CAKE-USDT", help="Pool name")
    parser.add_argument("--points", type=int, default=14, help="Number of data points")
    args = parser.parse_args()
    
    # 创建预测器
    predictor = APYPredictor()
    
    # 生成模拟历史数据
    pool_address = "0x" + "".join(random.choices("0123456789abcdef", k=40))
    
    print(f"\n🔮 生成 {args.points} 天模拟数据...")
    for i in range(args.points):
        predictor.add_data_point(
            pool_address=pool_address,
            pool_name=args.pool,
            apy=10.0 + random.uniform(-3, 5),
            tvl=1000000 + random.uniform(-200000, 300000),
            volume=500000 + random.uniform(-100000, 200000),
            timestamp=datetime.now() - timedelta(days=args.points - i)
        )
    
    # 进行预测
    print(f"\n📊 预测 {args.pool}...")
    prediction = predictor.predict(pool_address, args.pool)
    
    if prediction:
        print("\n" + "="*50)
        print("🔮 APY 预测结果")
        print("="*50)
        print(f"池名称:    {prediction.pool_name}")
        print(f"当前 APY:  {prediction.current_apy:.2f}%")
        print(f"24h 预测:  {prediction.predicted_apy_24h:.2f}%")
        print(f"7d 预测:   {prediction.predicted_apy_7d:.2f}%")
        print(f"趋势:      {prediction.trend} ({['➡️','📈','📉'][{'STABLE':0,'UP':1,'DOWN':2}[prediction.trend]]})")
        print(f"置信度:    {prediction.confidence:.1%}")
        print(f"建议:      {prediction.recommendation}")
        print(f"\n因素分析:")
        for f in prediction.factors:
            print(f"  • {f}")
        if prediction.risk_warning:
            print(f"\n⚠️  {prediction.risk_warning}")
    else:
        print("❌ 预测失败")


if __name__ == "__main__":
    main()
