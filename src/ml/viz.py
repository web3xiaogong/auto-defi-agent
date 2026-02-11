"""
APY 预测可视化模块
展示 ML 预测结果的图表

Good Vibes Only: OpenClaw Edition Hackathon
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """可视化配置"""
    figsize: tuple = (12, 8)
    dpi: int = 100
    style: str = "seaborn-v0_8"
    colors: dict = None
    
    def __post_init__(self):
        self.colors = self.colors or {
            "actual": "#2E86AB",      # 蓝色 - 实际数据
            "predicted": "#E94F37",   # 红色 - 预测数据
            "confidence": "#A23B72",  # 紫色 - 置信区间
            "buy": "#28A745",         # 绿色 - 买入信号
            "sell": "#DC3545",        # 红色 - 卖出信号
            "hold": "#FFC107",        # 黄色 - 持有
            "background": "#F8F9FA",  # 背景色
        }


class APYVisualizer:
    """
    APY 预测可视化器
    
    功能:
    - APY 趋势预测图
    - 多池对比图
    - 置信区间图
    - 策略推荐仪表盘
    """
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        plt.style.use(self.config.style)
    
    def plot_apy_prediction(
        self,
        pool_name: str,
        dates: List[datetime],
        actual_apy: List[float],
        predicted_apy: List[float],
        confidence: List[float] = None,
        recommendations: List[str] = None,
        save_path: str = None
    ) -> str:
        """
        绘制 APY 预测对比图
        
        Args:
            pool_name: 池名称
            dates: 日期列表
            actual_apy: 实际 APY 列表
            predicted_apy: 预测 APY 列表
            confidence: 置信度列表
            recommendations: 推荐列表
            save_path: 保存路径
        
        Returns:
            保存的文件路径
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.config.figsize, 
                                        gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_facecolor(self.config.colors["background"])
        
        # 主图：APY 趋势
        ax1.plot(dates, actual_apy, 
                color=self.config.colors["actual"], 
                linewidth=2, 
                label="Actual APY",
                marker='o',
                markersize=4)
        ax1.plot(dates, predicted_apy, 
                color=self.config.colors["predicted"], 
                linewidth=2, 
                linestyle='--',
                label="Predicted APY",
                marker='s',
                markersize=4)
        
        # 置信区间
        if confidence:
            upper = [p * (1 + c) for p, c in zip(predicted_apy, confidence)]
            lower = [p * (1 - c) for p, c in zip(predicted_apy, confidence)]
            ax1.fill_between(dates, lower, upper, 
                           color=self.config.colors["confidence"],
                           alpha=0.2,
                           label="Confidence Interval")
        
        # 标注推荐
        if recommendations:
            for i, (date, rec) in enumerate(zip(dates, recommendations)):
                if rec == "BUY":
                    ax1.scatter([date], [predicted_apy[i]], 
                               color=self.config.colors["buy"], 
                               s=150, marker='^', zorder=5)
                elif rec == "SELL":
                    ax1.scatter([date], [predicted_apy[i]], 
                               color=self.config.colors["sell"], 
                               s=150, marker='v', zorder=5)
        
        ax1.set_title(f"APY Prediction: {pool_name}", fontsize=14, fontweight='bold')
        ax1.set_ylabel("APY (%)", fontsize=11)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        # 副图：预测误差
        if len(actual_apy) == len(predicted_apy):
            errors = [a - p for a, p in zip(actual_apy, predicted_apy)]
            colors = [self.config.colors["buy"] if e > 0 else self.config.colors["sell"] 
                     for e in errors]
            ax2.bar(dates, errors, color=colors, alpha=0.7, width=0.8)
            ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
            ax2.set_ylabel("Error (%)", fontsize=11)
            ax2.set_xlabel("Date", fontsize=11)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi, 
                       facecolor=self.config.colors["background"])
            logger.info(f"Chart saved to: {save_path}")
            plt.close()
            return save_path
        
        plt.show()
        return None
    
    def plot_multi_pool_comparison(
        self,
        pools: Dict[str, Dict],
        metric: str = "apy",
        save_path: str = None
    ) -> str:
        """
        绘制多池对比图
        
        Args:
            pools: {pool_name: {values: [], labels: []}}
            metric: 指标名称
            save_path: 保存路径
        
        Returns:
            保存的文件路径
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.patch.set_facecolor(self.config.colors["background"])
        
        pool_names = list(pools.keys())
        
        # 左图：APY 对比柱状图
        apy_values = [p.get("current_apy", 0) for p in pools.values()]
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(pool_names)))
        
        bars = ax1.barh(pool_names, apy_values, color=colors)
        ax1.set_xlabel("Current APY (%)", fontsize=11)
        ax1.set_title("Current APY Comparison", fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # 添加数值标签
        for bar, val in zip(bars, apy_values):
            ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                    f"{val:.2f}%", va='center', fontsize=10)
        
        # 右图：预测趋势雷达图
        ax2.remove()
        ax2 = fig.add_subplot(122, projection='polar')
        
        # 预测数据
        predicted = [p.get("predicted_apy_7d", 0) for p in pools.values()]
        angles = np.linspace(0, 2 * np.pi, len(pool_names), endpoint=False)
        predicted = np.array(predicted)
        
        ax2.fill(angles, predicted, color=self.config.colors["predicted"], alpha=0.25)
        ax2.plot(angles, predicted, color=self.config.colors["predicted"], 
                linewidth=2, marker='o')
        ax2.set_xticks(angles)
        ax2.set_xticklabels(pool_names, size=9)
        ax2.set_title("7-Day APY Prediction", fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi,
                       facecolor=self.config.colors["background"])
            logger.info(f"Comparison chart saved to: {save_path}")
            plt.close()
            return save_path
        
        plt.show()
        return None
    
    def plot_dashboard(
        self,
        predictions: List[Dict],
        top_n: int = 5,
        save_path: str = None
    ) -> str:
        """
        绘制仪表盘总览
        
        Args:
            predictions: 预测结果列表
            top_n: 显示前 N 个池
            save_path: 保存路径
        
        Returns:
            保存的文件路径
        """
        fig = plt.figure(figsize=(16, 10))
        fig.patch.set_facecolor(self.config.colors["background"])
        
        # 按 APY 排序
        sorted_preds = sorted(predictions, key=lambda x: x.get("current_apy", 0), reverse=True)[:top_n]
        
        # 1. APY 排行榜
        ax1 = fig.add_subplot(2, 2, 1)
        names = [p.get("pool_name", "")[:15] for p in sorted_preds]
        apys = [p.get("current_apy", 0) for p in sorted_preds]
        colors = [self.config.colors["buy"] if p.get("recommendation") == "BUY" 
                 else self.config.colors["sell"] for p in sorted_preds]
        
        bars = ax1.barh(names[::-1], apys[::-1], color=colors[::-1])
        ax1.set_xlabel("APY (%)", fontsize=10)
        ax1.set_title("🏆 Top APY Pools", fontsize=12, fontweight='bold')
        for bar, val in zip(bars, apys[::-1]):
            ax1.text(val + 0.3, bar.get_y() + bar.get_height()/2, 
                    f"{val:.1f}%", va='center', fontsize=9)
        
        # 2. 预测分布
        ax2 = fig.add_subplot(2, 2, 2)
        pred_7d = [p.get("predicted_apy_7d", 0) for p in sorted_preds]
        ax2.bar(names, pred_7d, color=self.config.colors["predicted"], alpha=0.8)
        ax2.set_ylabel("Predicted 7D APY (%)", fontsize=10)
        ax2.set_title("📈 7-Day APY Forecast", fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. 置信度仪表
        ax3 = fig.add_subplot(2, 2, 3)
        confidences = [p.get("confidence", 0) for p in sorted_preds]
        colors_conf = ['green' if c > 0.7 else 'orange' if c > 0.5 else 'red' for c in confidences]
        bars = ax3.barh(names[::-1], confidences[::-1], color=colors_conf[::-1])
        ax3.set_xlabel("Confidence Score", fontsize=10)
        ax3.set_title("🎯 Prediction Confidence", fontsize=12, fontweight='bold')
        ax3.set_xlim(0, 1)
        
        # 4. 趋势饼图
        ax4 = fig.add_subplot(2, 2, 4)
        trends = [p.get("trend", "STABLE") for p in sorted_preds]
        trend_counts = {"UP": trends.count("UP"), "DOWN": trends.count("DOWN"), 
                       "STABLE": trends.count("STABLE")}
        colors_pie = [self.config.colors["buy"], self.config.colors["sell"], 
                     self.config.colors["hold"]]
        ax4.pie(trend_counts.values(), labels=trend_counts.keys(), 
               colors=colors_pie, autopct='%1.0f%%', startangle=90)
        ax4.set_title("📊 Trend Distribution", fontsize=12, fontweight='bold')
        
        plt.suptitle("Auto-DeFi Agent Dashboard", fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.config.dpi,
                       facecolor=self.config.colors["background"])
            logger.info(f"Dashboard saved to: {save_path}")
            plt.close()
            return save_path
        
        plt.show()
        return None
    
    def generate_html_dashboard(self, predictions: List[Dict], save_path: str = None) -> str:
        """
        生成交互式 HTML 仪表盘 (使用 Plotly)
        
        Args:
            predictions: 预测结果列表
            save_path: 保存路径
        
        Returns:
            HTML 文件路径
        """
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        
        # 按 APY 排序
        sorted_preds = sorted(predictions, key=lambda x: x.get("current_apy", 0), reverse=True)[:10]
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Top APY Pools", "7-Day Forecast", 
                          "Confidence Score", "Trend Distribution"),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # 1. APY 排行榜
        names = [p.get("pool_name", "") for p in sorted_preds]
        apys = [p.get("current_apy", 0) for p in sorted_preds]
        colors = ["#28A745" if p.get("recommendation") == "BUY" else "#DC3545" 
                 for p in sorted_preds]
        
        fig.add_trace(
            go.Bar(x=apys, y=names, orientation='h', 
                  marker_color=colors, name="Current APY"),
            row=1, col=1
        )
        
        # 2. 预测趋势
        pred_7d = [p.get("predicted_apy_7d", 0) for p in sorted_preds]
        fig.add_trace(
            go.Bar(x=names, y=pred_7d, 
                  marker_color="#E94F37", name="7D Prediction"),
            row=1, col=2
        )
        
        # 3. 置信度
        confidences = [p.get("confidence", 0) for p in sorted_preds]
        fig.add_trace(
            go.Bar(x=names, y=confidences,
                  marker_color=px.colors.sequential.Viridis,
                  name="Confidence"),
            row=2, col=1
        )
        
        # 4. 趋势饼图
        trends = [p.get("trend", "STABLE") for p in sorted_preds]
        trend_counts = {"UP": trends.count("UP"), "DOWN": trends.count("DOWN"), 
                       "STABLE": trends.count("STABLE")}
        fig.add_trace(
            go.Pie(labels=list(trend_counts.keys()), 
                  values=list(trend_counts.values()),
                  marker_colors=["#28A745", "#DC3545", "#FFC107"],
                  name="Trends"),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="🤖 Auto-DeFi Agent - Real-time Dashboard",
            showlegend=False,
            height=700,
            template="plotly_white"
        )
        
        html_path = save_path or "dashboard.html"
        fig.write_html(html_path)
        logger.info(f"Interactive dashboard saved to: {html_path}")
        
        return html_path


# ============== Demo ==============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 创建可视化器
    viz = APYVisualizer()
    
    # 模拟预测数据
    dates = [datetime.now() - timedelta(days=i) for i in range(14, -1, -1)]
    actual_apy = [5.2, 5.5, 5.3, 5.8, 6.0, 5.9, 6.2, 6.5, 6.3, 6.8, 7.0, 6.9, 7.2, 7.5, 7.3]
    predicted_apy = [5.3, 5.4, 5.5, 5.7, 6.1, 6.0, 6.3, 6.4, 6.5, 6.7, 7.1, 7.0, 7.3, 7.4, 7.6]
    confidence = [0.1, 0.12, 0.15, 0.18, 0.2, 0.22, 0.25, 0.28, 0.3, 0.32, 0.35, 0.38, 0.4, 0.42, 0.45]
    recommendations = ["HOLD", "HOLD", "HOLD", "BUY", "BUY", "HOLD", "BUY", "BUY", "HOLD", "BUY", "BUY", "HOLD", "BUY", "BUY", "HOLD"]
    
    # 1. 预测趋势图
    print("📊 Generating APY prediction chart...")
    viz.plot_apy_prediction(
        pool_name="PancakeSwap CAKE-BNB",
        dates=dates,
        actual_apy=actual_apy,
        predicted_apy=predicted_apy,
        confidence=confidence,
        recommendations=recommendations,
        save_path="apy_prediction.png"
    )
    
    # 2. 多池对比
    print("📊 Generating comparison chart...")
    pools = {
        "PancakeSwap CAKE": {"current_apy": 7.5, "predicted_apy_7d": 8.2},
        "Venus BNB": {"current_apy": 5.2, "predicted_apy_7d": 5.5},
        "Alpaca BUSD": {"current_apy": 4.8, "predicted_apy_7d": 4.5},
        "Apollo ETH": {"current_apy": 6.1, "predicted_apy_7d": 6.8},
        "Biswap BNB": {"current_apy": 8.2, "predicted_apy_7d": 7.9},
    }
    viz.plot_multi_pool_comparison(pools, save_path="pool_comparison.png")
    
    # 3. 仪表盘
    print("📊 Generating dashboard...")
    demo_predictions = [
        {"pool_name": "Pancake CAKE-BNB", "current_apy": 7.5, "predicted_apy_7d": 8.2, 
         "confidence": 0.75, "trend": "UP", "recommendation": "BUY"},
        {"pool_name": "Venus BNB", "current_apy": 5.2, "predicted_apy_7d": 5.5, 
         "confidence": 0.82, "trend": "UP", "recommendation": "BUY"},
        {"pool_name": "Alpaca BUSD", "current_apy": 4.8, "predicted_apy_7d": 4.5, 
         "confidence": 0.68, "trend": "DOWN", "recommendation": "SELL"},
        {"pool_name": "Apollo ETH", "current_apy": 6.1, "predicted_apy_7d": 6.8, 
         "confidence": 0.71, "trend": "UP", "recommendation": "BUY"},
        {"pool_name": "Biswap BNB", "current_apy": 8.2, "predicted_apy_7d": 7.9, 
         "confidence": 0.65, "trend": "DOWN", "recommendation": "HOLD"},
    ]
    viz.plot_dashboard(demo_predictions, save_path="dashboard.png")
    
    # 4. HTML 仪表盘
    print("📊 Generating interactive HTML dashboard...")
    viz.generate_html_dashboard(demo_predictions, save_path="docs/dashboard.html")
    
    print("\n✅ All charts generated successfully!")
    print("   - apy_prediction.png")
    print("   - pool_comparison.png")
    print("   - dashboard.png")
    print("   - docs/dashboard.html (interactive)")
