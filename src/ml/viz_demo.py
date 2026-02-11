#!/usr/bin/env python3
"""
APY 预测可视化演示
展示 ML 预测结果的图表

Good Vibes Only: OpenClaw Edition Hackathon

运行方式:
    python3 src/ml/viz_demo.py
"""

import sys
sys.path.insert(0, '.')

from src.ml.viz import APYVisualizer, VisualizationConfig
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_predictions():
    """生成模拟预测数据"""
    pools = [
        {
            "pool_name": "PancakeSwap CAKE-BNB LP",
            "pool_address": "0x...",
            "current_apy": 7.5,
            "predicted_apy_24h": 7.8,
            "predicted_apy_7d": 8.2,
            "trend": "UP",
            "confidence": 0.75,
            "recommendation": "BUY",
            "factors": ["TVL increasing", "Volume up 20%"],
            "risk_warning": "Moderate volatility"
        },
        {
            "pool_name": "Venus BNB",
            "pool_address": "0x...",
            "current_apy": 5.2,
            "predicted_apy_24h": 5.3,
            "predicted_apy_7d": 5.5,
            "trend": "UP",
            "confidence": 0.82,
            "recommendation": "BUY",
            "factors": ["Stablecoin lending", "Low risk"],
            "risk_warning": "Low volatility"
        },
        {
            "pool_name": "Alpaca BUSD Stable LP",
            "pool_address": "0x...",
            "current_apy": 4.8,
            "predicted_apy_24h": 4.7,
            "predicted_apy_7d": 4.5,
            "trend": "DOWN",
            "confidence": 0.68,
            "recommendation": "SELL",
            "factors": ["Stablecoin peg risk", "TVL decreasing"],
            "risk_warning": "Stablecoin depeg risk"
        },
        {
            "pool_name": "Apollo ETH-BNB LP",
            "pool_address": "0x...",
            "current_apy": 6.1,
            "predicted_apy_24h": 6.4,
            "predicted_apy_7d": 6.8,
            "trend": "UP",
            "confidence": 0.71,
            "recommendation": "BUY",
            "factors": ["ETH moving up", "Correlation with ETH"],
            "risk_warning": "Moderate volatility"
        },
        {
            "pool_name": "Biswap BNB-BUSD LP",
            "pool_address": "0x...",
            "current_apy": 8.2,
            "predicted_apy_24h": 8.0,
            "predicted_apy_7d": 7.9,
            "trend": "DOWN",
            "confidence": 0.65,
            "recommendation": "HOLD",
            "factors": ["High APY", "Volume stable"],
            "risk_warning": "High impermanent loss risk"
        },
    ]
    return pools


def demo_charts():
    """演示各种图表生成"""
    viz = APYVisualizer()
    pools = generate_mock_predictions()
    
    print("=" * 60)
    print("🤖 Auto-DeFi Agent - ML Prediction Visualization Demo")
    print("=" * 60)
    print()
    
    # 1. 单池预测趋势图
    print("📈 1. Generating APY prediction chart...")
    dates = [datetime.now() - timedelta(days=i) for i in range(14, -1, -1)]
    actual_apy = [5.2, 5.5, 5.3, 5.8, 6.0, 5.9, 6.2, 6.5, 6.3, 6.8, 7.0, 6.9, 7.2, 7.5, 7.3]
    predicted_apy = [5.3, 5.4, 5.5, 5.7, 6.1, 6.0, 6.3, 6.4, 6.5, 6.7, 7.1, 7.0, 7.3, 7.4, 7.6]
    confidence = [0.1 * (1 + i*0.03) for i in range(15)]
    recommendations = ["HOLD", "HOLD", "HOLD", "BUY", "BUY", "HOLD", "BUY", "BUY", "HOLD", 
                       "BUY", "BUY", "HOLD", "BUY", "BUY", "HOLD"]
    
    viz.plot_apy_prediction(
        pool_name="PancakeSwap CAKE-BNB LP",
        dates=dates,
        actual_apy=actual_apy,
        predicted_apy=predicted_apy,
        confidence=confidence,
        recommendations=recommendations,
        save_path="docs/apy_prediction.png"
    )
    print("   ✅ saved: docs/apy_prediction.png")
    
    # 2. 多池对比图
    print("📊 2. Generating pool comparison chart...")
    pools_dict = {p["pool_name"]: {
        "current_apy": p["current_apy"],
        "predicted_apy_7d": p["predicted_apy_7d"]
    } for p in pools}
    viz.plot_multi_pool_comparison(pools_dict, save_path="docs/pool_comparison.png")
    print("   ✅ saved: docs/pool_comparison.png")
    
    # 3. 仪表盘
    print("🎛️ 3. Generating dashboard...")
    viz.plot_dashboard(pools, save_path="docs/dashboard.png")
    print("   ✅ saved: docs/dashboard.png")
    
    # 4. HTML 交互仪表盘
    print("🌐 4. Generating interactive HTML dashboard...")
    html_path = viz.generate_html_dashboard(pools, save_path="docs/dashboard.html")
    print(f"   ✅ saved: {html_path}")
    print(f"   🌐 Open in browser to see interactive charts!")
    
    print()
    print("=" * 60)
    print("✅ Demo complete! All charts saved to docs/")
    print("=" * 60)


def demo_realtime_prediction():
    """
    实时预测演示脚本
    
    这个函数展示如何将真实 API 数据接入可视化
    """
    print("\n" + "=" * 60)
    print("🔮 Realtime Prediction Demo")
    print("=" * 60)
    
    # TODO: 接入真实 API
    # from src.tools.bsc_adapter import BSCAdapter
    # adapter = BSCAdapter()
    # pools = adapter.get_top_pools(limit=10)
    
    # 使用模拟数据演示
    pools = generate_mock_predictions()
    
    viz = APYVisualizer()
    
    # 生成交互式仪表盘
    html_path = viz.generate_html_dashboard(pools, save_path="docs/realtime_dashboard.html")
    
    print(f"\n📊 Dashboard generated: {html_path}")
    print("💡 Open in browser to see:")
    print("   - Real-time APY rankings")
    print("   - ML prediction trends")
    print("   - Confidence scores")
    print("   - Strategy recommendations")
    
    return html_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="APY Prediction Visualization Demo")
    parser.add_argument("--demo", type=str, default="all",
                       choices=["charts", "dashboard", "all"],
                       help="Demo type")
    parser.add_argument("--realtime", action="store_true",
                       help="Generate realtime dashboard")
    
    args = parser.parse_args()
    
    if args.realtime:
        demo_realtime_prediction()
    elif args.demo == "all":
        demo_charts()
        demo_realtime_prediction()
    elif args.demo == "charts":
        demo_charts()
    elif args.demo == "dashboard":
        demo_realtime_prediction()
