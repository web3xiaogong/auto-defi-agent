"""
Copy Trading System
跟单交易系统

Good Vibes Only: OpenClaw Edition Hackathon
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from collections import defaultdict


class OrderType(Enum):
    """订单类型"""
    BUY = "BUY"
    SELL = "SELL"
    SWAP = "SWAP"


@dataclass
class Trader:
    """交易者"""
    address: str
    name: str
    total_trades: int = 0
    win_rate: float = 0.0
    avg_return: float = 0.0
    followers: int = 0
    is_verified: bool = False
    strategies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CopyOrder:
    """跟单订单"""
    order_id: str
    trader_address: str
    follower_address: str
    pool_address: str
    pool_name: str
    order_type: OrderType
    amount_usd: float
    leverage: float = 1.0
    status: str = "PENDING"  # PENDING, EXECUTED, CANCELLED
    executed_at: datetime = None
    pnl: float = 0.0
    pnl_percent: float = 0.0


@dataclass
class StrategyConfig:
    """策略配置"""
    pool_address: str
    pool_name: str
    min_apy: float = 5.0
    max_slippage: float = 1.0
    auto_copy: bool = True
    max_investment: float = 1000.0
    risk_level: str = "MEDIUM"


@dataclass
class Follower:
    """跟随者"""
    address: str
    trader_address: str
    allocation_percent: float = 100.0
    min_investment: float = 10.0
    max_investment: float = 1000.0
    last_copy: datetime = None
    total_copied: float = 0.0


class CopyTradingManager:
    """
    跟单交易管理器
    
    功能:
    - 跟随交易者
    - 自动复制交易
    - 收益分成
    - 风险控制
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 数据存储
        self.traders: Dict[str, Trader] = {}
        self.followers: Dict[str, List[Follower]] = defaultdict(list)
        self.orders: Dict[str, CopyOrder] = {}
        self.strategies: Dict[str, StrategyConfig] = {}
        
        # 回调函数
        self.on_order_callback: Optional[Callable] = None
        
        # 统计
        self.stats = {
            "total_traders": 0,
            "total_followers": 0,
            "total_volume": 0.0,
            "total_pnl": 0.0,
        }
    
    # ===== 交易者管理 =====
    
    def register_trader(
        self,
        address: str,
        name: str,
        strategies: List[str] = None
    ) -> Trader:
        """注册交易者"""
        trader = Trader(
            address=address,
            name=name,
            strategies=strategies or []
        )
        
        self.traders[address] = trader
        self.stats["total_traders"] += 1
        
        # 保存
        self._save_traders()
        
        return trader
    
    def update_trader_stats(
        self,
        address: str,
        total_trades: int = None,
        win_rate: float = None,
        avg_return: float = None,
        followers: int = None
    ):
        """更新交易者统计"""
        if address not in self.traders:
            return
        
        trader = self.traders[address]
        
        if total_trades is not None:
            trader.total_trades = total_trades
        if win_rate is not None:
            trader.win_rate = win_rate
        if avg_return is not None:
            trader.avg_return = avg_return
        if followers is not None:
            trader.followers = followers
    
    def get_trader(self, address: str) -> Optional[Trader]:
        """获取交易者"""
        return self.traders.get(address)
    
    def get_top_traders(self, limit: int = 10) -> List[Trader]:
        """获取顶级交易者 (按收益率)"""
        sorted_traders = sorted(
            self.traders.values(),
            key=lambda x: x.avg_return,
            reverse=True
        )
        return sorted_traders[:limit]
    
    # ===== 跟随者管理 =====
    
    def follow_trader(
        self,
        follower_address: str,
        trader_address: str,
        allocation_percent: float = 100.0,
        min_investment: float = 10.0,
        max_investment: float = 1000.0
    ) -> Follower:
        """跟随交易者"""
        follower = Follower(
            address=follower_address,
            trader_address=trader_address,
            allocation_percent=allocation_percent,
            min_investment=min_investment,
            max_investment=max_investment
        )
        
        self.followers[trader_address].append(follower)
        self.stats["total_followers"] += 1
        
        # 更新交易者 followers 数量
        if trader_address in self.traders:
            self.traders[trader_address].followers = len(self.followers[trader_address])
        
        return follower
    
    def unfollow_trader(self, follower_address: str, trader_address: str) -> bool:
        """取消跟随"""
        followers = self.followers.get(trader_address, [])
        
        for i, f in enumerate(followers):
            if f.address == follower_address:
                followers.pop(i)
                self.stats["total_followers"] -= 1
                return True
        
        return False
    
    def get_followers(self, trader_address: str) -> List[Follower]:
        """获取交易者的所有跟随者"""
        return self.followers.get(trader_address, [])
    
    # ===== 策略管理 =====
    
    def add_strategy(
        self,
        follower_address: str,
        strategy: StrategyConfig
    ):
        """添加跟随策略"""
        key = f"{follower_address}:{strategy.pool_address}"
        self.strategies[key] = strategy
    
    def remove_strategy(self, follower_address: str, pool_address: str) -> bool:
        """移除策略"""
        key = f"{follower_address}:{pool_address}"
        if key in self.strategies:
            del self.strategies[key]
            return True
        return False
    
    def get_strategy(self, follower_address: str, pool_address: str) -> Optional[StrategyConfig]:
        """获取策略"""
        key = f"{follower_address}:{pool_address}"
        return self.strategies.get(key)
    
    # ===== 订单复制 =====
    
    def copy_order(
        self,
        trader_address: str,
        pool_address: str,
        pool_name: str,
        order_type: OrderType,
        amount_usd: float
    ) -> List[CopyOrder]:
        """
        复制交易者订单到所有跟随者
        
        Args:
            trader_address: 交易者地址
            pool_address: 池地址
            pool_name: 池名称
            order_type: 订单类型
            amount_usd: 金额 (USD)
        
        Returns:
            生成的订单列表
        """
        followers = self.get_followers(trader_address)
        orders = []
        
        for follower in followers:
            # 检查策略
            strategy = self.get_strategy(follower.address, pool_address)
            if strategy and not strategy.auto_copy:
                continue
            
            # 计算投资金额
            invest_amount = amount_usd * (follower.allocation_percent / 100)
            invest_amount = min(
                invest_amount,
                follower.max_investment
            )
            
            if invest_amount < follower.min_investment:
                continue
            
            # 创建订单
            order = CopyOrder(
                order_id=self._generate_order_id(),
                trader_address=trader_address,
                follower_address=follower.address,
                pool_address=pool_address,
                pool_name=pool_name,
                order_type=order_type,
                amount_usd=invest_amount,
            )
            
            self.orders[order.order_id] = order
            orders.append(order)
            
            # 更新统计
            self.stats["total_volume"] += invest_amount
            
            # 触发回调
            if self.on_order_callback:
                self.on_order_callback(order)
        
        return orders
    
    def execute_order(self, order_id: str) -> bool:
        """执行订单"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        order.status = "EXECUTED"
        order.executed_at = datetime.now()
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        order.status = "CANCELLED"
        
        return True
    
    def get_orders(self, address: str = None, status: str = None) -> List[CopyOrder]:
        """获取订单列表"""
        orders = list(self.orders.values())
        
        if address:
            orders = [o for o in orders if o.follower_address == address]
        
        if status:
            orders = [o for o in orders if o.status == status]
        
        return sorted(orders, key=lambda x: x.order_id, reverse=True)
    
    # ===== 收益计算 =====
    
    def calculate_pnl(
        self,
        order_id: str,
        exit_price: float,
        entry_price: float
    ) -> float:
        """计算盈亏"""
        if order_id not in self.orders:
            return 0.0
        
        order = self.orders[order_id]
        
        # 简化版 PnL 计算
        if order.order_type == OrderType.BUY:
            pnl_percent = (exit_price - entry_price) / entry_price
        else:
            pnl_percent = (entry_price - exit_price) / entry_price
        
        order.pnl_percent = pnl_percent
        order.pnl = order.amount_usd * pnl_percent
        self.stats["total_pnl"] += order.pnl
        
        return order.pnl
    
    def distribute_rewards(self, trader_address: str, total_pnl: float) -> Dict:
        """
        分发收益给交易者 (可选)
        
        Args:
            trader_address: 交易者地址
            total_pnl: 总盈亏
        
        Returns:
            分发记录
        """
        # 简化: 交易者获得 10% 的跟随者利润分成
        reward = total_pnl * 0.10
        
        return {
            "trader_address": trader_address,
            "total_pnl": total_pnl,
            "reward": reward,
            "reward_percent": 10.0,
            "distributed_at": datetime.now().isoformat(),
        }
    
    # ===== 统计和报告 =====
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            **self.stats,
            "active_traders": len(self.traders),
            "active_orders": len([o for o in self.orders.values() if o.status == "PENDING"]),
            "completed_orders": len([o for o in self.orders.values() if o.status == "EXECUTED"]),
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取排行榜"""
        leaders = []
        
        for address, trader in self.traders.items():
            leaders.append({
                "address": address,
                "name": trader.name,
                "total_trades": trader.total_trades,
                "win_rate": trader.win_rate,
                "avg_return": trader.avg_return,
                "followers": trader.followers,
                "is_verified": trader.is_verified,
                "score": self._calculate_score(trader),
            })
        
        return sorted(leaders, key=lambda x: x["score"], reverse=True)[:limit]
    
    def _calculate_score(self, trader: Trader) -> float:
        """计算交易者评分"""
        score = 0.0
        
        # 收益率 (40%)
        score += trader.avg_return * 0.4
        
        # 胜率 (30%)
        score += trader.win_rate * 30 * 0.3
        
        # 交易数量 (10%)
        score += min(trader.total_trades / 100, 1.0) * 10 * 0.1
        
        # 跟随者数量 (10%)
        score += min(trader.followers / 50, 1.0) * 10 * 0.1
        
        # 验证加分 (10%)
        if trader.is_verified:
            score += 10 * 0.1
        
        return score
    
    # ===== 数据持久化 =====
    
    def _save_traders(self):
        """保存交易者数据"""
        data = {
            addr: {
                "address": t.address,
                "name": t.name,
                "total_trades": t.total_trades,
                "win_rate": t.win_rate,
                "avg_return": t.avg_return,
                "followers": t.followers,
                "is_verified": t.is_verified,
                "strategies": t.strategies,
                "created_at": t.created_at.isoformat(),
            }
            for addr, t in self.traders.items()
        }
        
        with open(self.data_dir / "traders.json", 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """加载数据"""
        traders_file = self.data_dir / "traders.json"
        
        if traders_file.exists():
            with open(traders_file) as f:
                data = json.load(f)
            
            for addr, t_data in data.items():
                self.traders[addr] = Trader(
                    address=t_data["address"],
                    name=t_data["name"],
                    total_trades=t_data["total_trades"],
                    win_rate=t_data["win_rate"],
                    avg_return=t_data["avg_return"],
                    followers=t_data["followers"],
                    is_verified=t_data["is_verified"],
                    strategies=t_data["strategies"],
                    created_at=datetime.fromisoformat(t_data["created_at"]),
                )
            
            self.stats["total_traders"] = len(self.traders)
    
    def _generate_order_id(self) -> str:
        """生成订单 ID"""
        import secrets
        return f"order_{secrets.token_hex(8)}"
    
    def export_data(self) -> str:
        """导出所有数据"""
        return json.dumps({
            "traders": {
                addr: {
                    "name": t.name,
                    "total_trades": t.total_trades,
                    "win_rate": t.win_rate,
                    "avg_return": t.avg_return,
                    "followers": t.followers,
                }
                for addr, t in self.traders.items()
            },
            "stats": self.get_stats(),
            "exported_at": datetime.now().isoformat(),
        }, indent=2)


# ===== CLI =====
def main():
    import argparse
    import random
    
    parser = argparse.ArgumentParser(description="Copy Trading CLI")
    parser.add_argument("--register", metavar="NAME", help="Register as trader")
    parser.add_argument("--traders", action="store_true", help="List traders")
    parser.add_argument("--leaderboard", action="store_true", help="Show leaderboard")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    args = parser.parse_args()
    
    manager = CopyTradingManager()
    manager.load_data()
    
    if args.register:
        addr = f"0x{random.hex(20)}"
        trader = manager.register_trader(addr, args.register)
        print(f"✅ 注册成功: {trader.name} ({addr[:10]}...)")
    
    elif args.traders:
        print("\n👥 注册交易者:")
        for addr, trader in manager.traders.items():
            print(f"  • {trader.name}: {trader.total_trades} 交易, {trader.avg_return:.1f}% 收益")
    
    elif args.leaderboard:
        print("\n🏆 排行榜:")
        leaders = manager.get_leaderboard()
        for i, leader in enumerate(leaders[:5], 1):
            print(f"  {i}. {leader['name']}: 评分 {leader['score']:.1f}")
    
    elif args.stats:
        print("\n📊 统计:")
        stats = manager.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif args.demo:
        print("\n" + "="*50)
        print("👥 跟单交易系统演示")
        print("="*50)
        
        # 注册交易者
        trader1 = manager.register_trader("0x1111...", "Trader Alice", ["BSC", "CAKE"])
        trader2 = manager.register_trader("0x2222...", "Trader Bob", ["BSC", "USDT"])
        
        # 更新统计
        manager.update_trader_stats("0x1111...", total_trades=50, win_rate=0.65, avg_return=15.5, followers=10)
        manager.update_trader_stats("0x2222...", total_trades=30, win_rate=0.70, avg_return=12.0, followers=5)
        
        # 跟随者
        manager.follow_trader("0xA001", "0x1111...", allocation_percent=50)
        manager.follow_trader("0xA002", "0x1111...", allocation_percent=100)
        manager.follow_trader("0xA003", "0x2222...", allocation_percent=75)
        
        # 复制订单
        orders = manager.copy_order(
            trader_address="0x1111...",
            pool_address="0xPOOL...",
            pool_name="CAKE-USDT",
            order_type=OrderType.BUY,
            amount_usd=100.0
        )
        
        print(f"\n📤 复制的订单数: {len(orders)}")
        for order in orders:
            print(f"  • {order.order_id}: {order.amount_usd:.2f} USD")
        
        print("\n🏆 排行榜:")
        for i, leader in enumerate(manager.get_leaderboard()[:3], 1):
            print(f"  {i}. {leader['name']}: 评分 {leader['score']:.1f}")
        
        print("\n📊 统计:")
        stats = manager.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    else:
        print("使用 --help 查看选项")
        print("使用 --demo 运行演示")


if __name__ == "__main__":
    main()
