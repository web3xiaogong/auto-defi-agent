"""
Multi-Chain Copy Trading Integration
多链跟单交易集成

Good Vibes Only: OpenClaw Edition Hackathon

整合:
- MultiChainAdapter: 多链访问
- CopyTradingManager: 跟单管理
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_chain_adapter import MultiChainAdapter, ChainType, PoolInfo
from copy_trading.copy_trading_manager import CopyTradingManager, Trader, OrderType, StrategyConfig
from typing import List, Dict, Optional
import json
import random
from datetime import datetime


class MultiChainCopyTrader:
    """
    多链跟单交易器
    
    结合多链访问和跟单功能
    """
    
    def __init__(self, private_key: str = None):
        self.chain_adapter = MultiChainAdapter(private_key)
        self.copy_manager = CopyTradingManager()
        
        # 加载数据
        self.copy_manager.load_data()
    
    # ===== 链操作 =====
    
    def switch_chain(self, chain: ChainType) -> bool:
        """切换链"""
        return self.chain_adapter.switch_chain(chain)
    
    def get_chain_info(self) -> Dict:
        """获取当前链信息"""
        return self.chain_adapter.get_chain_info()
    
    def get_all_chains(self) -> List[ChainType]:
        """获取所有链"""
        return self.chain_adapter.get_all_chains()
    
    # ===== 跨链搜索 =====
    
    def scan_all_chains(
        self,
        min_apy: float = 5.0,
        min_tvl: float = 10000
    ) -> List[PoolInfo]:
        """扫描所有链的池"""
        chains = [ChainType.BSC, ChainType.OPBNB]
        return self.chain_adapter.get_best_apy(chains, min_tvl)
    
    def get_best_pool(self, min_apy: float = 5.0) -> Optional[PoolInfo]:
        """获取最佳池"""
        pools = self.scan_all_chains(min_apy)
        return pools[0] if pools else None
    
    # ===== 交易者发现 =====
    
    def discover_traders(self, chain: ChainType = None) -> List[Dict]:
        """发现链上活跃交易者"""
        self.switch_chain(chain or ChainType.BSC)
        
        # 模拟发现逻辑
        return [
            {
                "address": "0x1111...",
                "name": "YieldMaster",
                "chain": (chain or ChainType.BSC).value,
                "avg_apy": 18.5,
                "followers": 45,
                "verified": True,
            },
            {
                "address": "0x2222...",
                "name": "DeFi Hunter",
                "chain": (chain or ChainType.BSC).value,
                "avg_apy": 15.2,
                "followers": 32,
                "verified": False,
            },
        ]
    
    def get_top_traders(self) -> List[Dict]:
        """获取顶级交易者"""
        return self.copy_manager.get_leaderboard()
    
    # ===== 跟单操作 =====
    
    def follow_trader(
        self,
        trader_address: str,
        allocation_percent: float = 100.0,
        min_investment: float = 10.0,
        max_investment: float = 1000.0
    ):
        """跟随交易者"""
        # 获取跟随者地址 (这里简化处理)
        follower_address = f"0x{random.hex(20)}" if not self.copy_manager.traders else list(self.copy_manager.traders.keys())[0]
        
        return self.copy_manager.follow_trader(
            follower_address=follower_address,
            trader_address=trader_address,
            allocation_percent=allocation_percent,
            min_investment=min_investment,
            max_investment=max_investment
        )
    
    def copy_trader_order(
        self,
        trader_address: str,
        pool_address: str,
        pool_name: str,
        order_type: OrderType,
        amount_usd: float
    ) -> List:
        """复制交易者订单"""
        return self.copy_manager.copy_order(
            trader_address=trader_address,
            pool_address=pool_address,
            pool_name=pool_name,
            order_type=order_type,
            amount_usd=amount_usd
        )
    
    def get_copy_orders(self, address: str = None) -> List:
        """获取跟单订单"""
        return self.copy_manager.get_orders(address)
    
    # ===== 策略管理 =====
    
    def add_strategy(
        self,
        pool_address: str,
        pool_name: str,
        min_apy: float = 5.0,
        auto_copy: bool = True
    ):
        """添加策略"""
        config = StrategyConfig(
            pool_address=pool_address,
            pool_name=pool_name,
            min_apy=min_apy,
            auto_copy=auto_copy
        )
        
        # 获取地址
        follower_address = list(self.copy_manager.traders.keys())[0] if self.copy_manager.traders else "0x0"
        
        self.copy_manager.add_strategy(follower_address, config)
        return config
    
    # ===== 统计 =====
    
    def get_stats(self) -> Dict:
        """获取综合统计"""
        return {
            "chains": {
                "connected": len(self.get_all_chains()),
                "current": self.chain_adapter.current_chain.value,
            },
            "copy_trading": self.copy_manager.get_stats(),
        }
    
    def export(self) -> str:
        """导出数据"""
        return json.dumps({
            "chains": [c.value for c in self.get_all_chains()],
            "traders": self.copy_manager.export_data(),
            "exported_at": datetime.now().isoformat(),
        }, indent=2)


# ===== 便捷函数 =====
def create_multi_chain_trader(private_key: str = None) -> MultiChainCopyTrader:
    """创建多链跟单交易器"""
    return MultiChainCopyTrader(private_key)


# ===== CLI =====
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Chain Copy Trading CLI")
    parser.add_argument("--scan", action="store_true", help="Scan all chains")
    parser.add_argument("--traders", action="store_true", help="Show traders")
    parser.add_argument("--chains", action="store_true", help="Show chains")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    args = parser.parse_args()
    
    trader = MultiChainCopyTrader()
    
    if args.scan:
        print("\n🔍 扫描所有链...")
        pools = trader.scan_all_chains(min_apy=5.0)
        print(f"找到 {len(pools)} 个池")
        for p in pools[:5]:
            print(f"  • {p.name} ({p.chain.value}): {p.apy:.1f}% APY")
    
    elif args.traders:
        print("\n👥 顶级交易者:")
        for i, t in enumerate(trader.get_top_traders()[:5], 1):
            print(f"  {i}. {t['name']}: 评分 {t['score']:.1f}")
    
    elif args.chains:
        print("\n📡 连接的链:")
        for chain in trader.get_all_chains():
            print(f"  • {chain.value}")
    
    elif args.stats:
        print("\n📊 统计:")
        stats = trader.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif args.demo:
        print("\n" + "="*50)
        print("🌉 多链跟单交易演示")
        print("="*50)
        
        # 扫描
        pools = trader.scan_all_chains(min_apy=5.0)
        print(f"\n🔍 发现 {len(pools)} 个机会")
        if pools:
            best = pools[0]
            print(f"  最佳: {best.name} ({best.chain.value}): {best.apy:.1f}%")
        
        # 交易者
        print("\n👥 交易者排行榜:")
        leaders = trader.get_top_traders()
        for i, l in enumerate(leaders[:3], 1):
            print(f"  {i}. {l['name']}: 评分 {l['score']:.1f}")
        
        # 统计
        print("\n📊 统计:")
        stats = trader.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    else:
        print("使用 --help 查看选项")
        print("使用 --demo 运行演示")


if __name__ == "__main__":
    import random
    main()
