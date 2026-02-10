"""
Multi-Chain Adapter
支持 BSC, opBNB, Ethereum, Arbitrum 等多链

Good Vibes Only: OpenClaw Edition Hackathon
"""

import json
import random
import secrets
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
from web3 import Web3
from eth_account import Account
from datetime import datetime


class ChainType(Enum):
    """支持的链类型"""
    BSC = "bsc"
    OPBNB = "opbnb"
    ETHEREUM = "ethereum"
    ARBITRUM = "arbitrum"


@dataclass
class ChainConfig:
    """链配置"""
    name: str
    chain_id: int
    native_currency: Dict[str, str]
    rpc_url: str
    explorer_url: str
    router_address: str
    factory_address: str


# 链配置模板
CHAIN_CONFIGS: Dict[ChainType, ChainConfig] = {
    ChainType.BSC: ChainConfig(
        name="BSC",
        chain_id=56,
        native_currency={"name": "BNB", "symbol": "BNB", "decimals": 18},
        rpc_url="https://bsc-dataseed.binance.org/",
        explorer_url="https://bscscan.com",
        router_address="0x10ED43C718714eb63d5aA57B78B54704E256024E",
        factory_address="0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
    ),
    ChainType.OPBNB: ChainConfig(
        name="opBNB",
        chain_id=204,
        native_currency={"name": "BNB", "symbol": "BNB", "decimals": 18},
        rpc_url="https://opbnb-mainnet-rpc.bnbchain.org/",
        explorer_url="https://opbnbscan.com",
        router_address="0x4f30c9d36efc3fe17d8b0e84edc1609953d37369",
        factory_address="0x02D01A8eE0B0d0aC8ebc7b86f05C1dB7b77f2d51",
    ),
    ChainType.ETHEREUM: ChainConfig(
        name="Ethereum",
        chain_id=1,
        native_currency={"name": "Ether", "symbol": "ETH", "decimals": 18},
        rpc_url="https://eth.llamarpc.com/",
        explorer_url="https://etherscan.io",
        router_address="0xE592427A0AEce92De3Edee1F18E0157C05861564",
        factory_address="0x1F98431c8aD98523631AE4a59f267346ea31F984",
    ),
    ChainType.ARBITRUM: ChainConfig(
        name="Arbitrum",
        chain_id=42161,
        native_currency={"name": "Ether", "symbol": "ETH", "decimals": 18},
        rpc_url="https://arb1.arbitrum.io/rpc",
        explorer_url="https://arbiscan.io",
        router_address="0xE592427A0AEce92De3Edee1F18E0157C05861564",
        factory_address="0x1F98431c8aD98523631AE4a59f267346ea31F984",
    ),
}


@dataclass
class TokenInfo:
    """代币信息"""
    symbol: str
    name: str
    address: str
    decimals: int
    chain: ChainType


@dataclass
class PoolInfo:
    """池信息"""
    name: str
    address: str
    token0: str
    token1: str
    factory: str
    chain: ChainType
    tvl: float
    volume_24h: float
    apy: float
    fee: float


class MultiChainAdapter:
    """多链适配器"""
    
    COMMON_TOKENS: Dict[ChainType, Dict[str, str]] = {
        ChainType.BSC: {
            "USDT": "0x55d398326f99059fF775485246999027B3197955",
            "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
            "BNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bd095Bc",
            "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        },
        ChainType.ETHEREUM: {
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "ETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        },
    }
    
    def __init__(self, private_key: str = None):
        self.w3 = Web3()
        self.account = Account.from_key(private_key) if private_key else None
        self.current_chain = ChainType.BSC
        self.contracts: Dict[ChainType, Any] = {}
        self._init_all_chains()
    
    def _init_all_chains(self):
        for chain_type, config in CHAIN_CONFIGS.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config.rpc_url))
                if w3.is_connected():
                    self.contracts[chain_type] = w3
                    print(f"✅ {config.name} 已连接")
                else:
                    print(f"⚠️ {config.name} 连接失败")
            except Exception as e:
                print(f"❌ {config.name} 错误: {e}")
    
    def switch_chain(self, chain_type: ChainType) -> bool:
        if chain_type not in self.contracts:
            print(f"❌ {chain_type.value} 未连接")
            return False
        self.current_chain = chain_type
        print(f"🔄 已切换到 {CHAIN_CONFIGS[chain_type].name}")
        return True
    
    def get_w3(self) -> Web3:
        return self.contracts.get(self.current_chain, self.w3)
    
    def get_chain_config(self) -> ChainConfig:
        return CHAIN_CONFIGS[self.current_chain]
    
    def get_native_balance(self, address: str = None) -> float:
        w3 = self.get_w3()
        addr = address or (self.account.address if self.account else None)
        if not addr:
            return 0.0
        balance_wei = w3.eth.get_balance(addr)
        return float(w3.from_wei(balance_wei, 'ether'))
    
    def get_token_balance(self, token_address: str, holder_address: str = None) -> float:
        w3 = self.get_w3()
        addr = holder_address or (self.account.address if self.account else None)
        if not addr:
            return 0.0
        abi = [
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
        ]
        token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        balance_wei = token.functions.balanceOf(addr).call()
        decimals = token.functions.decimals().call()
        return float(balance_wei / (10 ** decimals))
    
    def get_all_balances(self, address: str = None) -> Dict[str, float]:
        balances = {}
        chain = self.current_chain
        config = CHAIN_CONFIGS[chain]
        balances[config.native_currency["symbol"]] = self.get_native_balance(address)
        for symbol, token_address in self.COMMON_TOKENS.get(chain, {}).items():
            try:
                balances[symbol] = self.get_token_balance(token_address, address)
            except Exception:
                balances[symbol] = 0.0
        return balances
    
    def get_chain_info(self) -> Dict:
        config = self.get_chain_config()
        w3 = self.get_w3()
        return {
            "name": config.name,
            "chain_id": config.chain_id,
            "block_number": w3.eth.block_number,
            "gas_price": w3.eth.gas_price / 1e9,
            "connection": w3.is_connected(),
        }
    
    def get_gas_price(self) -> float:
        return self.get_w3().eth.gas_price / 1e9
    
    def get_block_number(self) -> int:
        return self.get_w3().eth.block_number
    
    def get_best_apy(self, chains: List[ChainType] = None, min_tvl: float = 10000) -> List[PoolInfo]:
        if chains is None:
            chains = list(ChainType)
        all_pools = []
        for chain in chains:
            if chain not in self.contracts:
                continue
            self.switch_chain(chain)
            chain_pools = self._get_chain_pools(chain, min_tvl)
            all_pools.extend(chain_pools)
        return sorted(all_pools, key=lambda x: x.apy, reverse=True)
    
    def _get_chain_pools(self, chain: ChainType, min_tvl: float) -> List[PoolInfo]:
        pools = []
        config = CHAIN_CONFIGS[chain]
        sample_pools = [
            ("USDT-BNB", "USDT", "BNB", 0.25),
            ("USDC-USDT", "USDC", "USDT", 0.01),
            ("ETH-USDT", "ETH", "USDT", 0.05),
        ]
        for name, token0, token1, fee in sample_pools:
            tvl = random.uniform(10000, 10000000)
            if tvl < min_tvl:
                continue
            apy = random.uniform(2, 30)
            pool = PoolInfo(
                name=name,
                address=f"0x{secrets.token_hex(20)}",
                token0=self.COMMON_TOKENS.get(chain, {}).get(token0, ""),
                token1=self.COMMON_TOKENS.get(chain, {}).get(token1, ""),
                factory=config.factory_address,
                chain=chain,
                tvl=tvl,
                volume_24h=tvl * random.uniform(0.1, 0.5),
                apy=apy,
                fee=fee,
            )
            pools.append(pool)
        return pools
    
    def get_all_chains(self) -> List[ChainType]:
        return list(self.contracts.keys())


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Multi-Chain Adapter CLI")
    parser.add_argument("--chains", action="store_true", help="List all chains")
    parser.add_argument("--balance", action="store_true", help="Show balances")
    parser.add_argument("--info", action="store_true", help="Show chain info")
    parser.add_argument("--best-apy", action="store_true", help="Find best APY")
    args = parser.parse_args()
    
    adapter = MultiChainAdapter()
    
    if args.chains:
        print("\n📡 已连接的链:")
        for chain in adapter.get_all_chains():
            config = CHAIN_CONFIGS[chain]
            print(f"  • {config.name} (ID: {config.chain_id})")
    elif args.balance:
        print("\n💰 余额查询:")
        balances = adapter.get_all_balances()
        for token, balance in balances.items():
            print(f"  {token}: {balance:.4f}")
    elif args.info:
        print("\nℹ️  当前链信息:")
        info = adapter.get_chain_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
    elif args.best_apy:
        print("\n🔍 查找最佳 APY:")
        pools = adapter.get_best_apy([ChainType.BSC, ChainType.OPBNB])
        for i, pool in enumerate(pools[:5], 1):
            print(f"  {i}. {pool.name} ({pool.chain.value}): {pool.apy:.2f}% (TVL: ${pool.tvl:,.0f})")


if __name__ == "__main__":
    main()
