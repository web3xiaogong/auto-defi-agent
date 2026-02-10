"""
DeFi Service Module
Fetch DeFi protocol data from BSC/opBNB
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import requests


@dataclass
class PoolInfo:
    """DeFi Pool Information"""
    name: str
    protocol: str
    chain: str
    pool_address: str
    token0: str
    token1: str
    tvl: float  # Total Value Locked in USD
    apy: float  # Annual Percentage Yield
    volume_24h: float
    fee: float  # Trading fee percentage


@dataclass
class TokenPrice:
    """Token Price Information"""
    symbol: str
    address: str
    price_usd: float
    price_change_24h: float
    volume_24h: float


class DeFiService:
    """DeFi Protocol Service"""
    
    # BSC Scan API
    BSCSCAN_API = "https://api.bscscan.com/api"
    
    # DeFi API (using DeFi Llama as data source)
    DEFILLAMA_API = "https://api.llama.fi"
    
    # Common token addresses (BSC)
    TOKENS = {
        "BNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bd095Bc",
        "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        "USDC": "0x8AC76a51cc950d9822D34b9d4159482fF67C89eC",
        "CAKE": "0x0E09FaBB73Bd3Ad0F69FD3E0b3877C61c7eE2136",
        "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bd095Bc",
    }
    
    def __init__(self, bsc_api_key: str = None):
        """
        Initialize DeFi Service
        
        Args:
            bsc_api_key: BSCScan API key (optional, increases rate limit)
        """
        self.bsc_api_key = bsc_api_key
    
    def get_bsc_pancake_pools(self) -> List[PoolInfo]:
        """
        Get PancakeSwap pools on BSC
        
        Returns:
            List of PoolInfo objects
        """
        # Using DeFi Llama for pool data
        try:
            response = requests.get(
                f"{self.DEFILLAMA_API}/protocols",
                params={"chain": "BSC"},
                timeout=30
            )
            data = response.json()
            
            pools = []
            for protocol in data:
                if "pancake" in protocol.get("name", "").lower():
                    for pool in protocol.get("poolDetails", [])[:10]:  # Top 10 pools
                        pools.append(PoolInfo(
                            name=pool.get("poolName", "Unknown"),
                            protocol="PancakeSwap",
                            chain="BSC",
                            pool_address=pool.get("poolAddress", ""),
                            token0=pool.get("token0", ""),
                            token1=pool.get("token1", ""),
                            tvl=pool.get("tvl", 0),
                            apy=pool.get("apy", 0),
                            volume_24h=pool.get("volume24h", 0),
                            fee=pool.get("fee", 0.25)
                        ))
            
            return pools
        except Exception as e:
            print(f"Error fetching pools: {e}")
            return []
    
    def get_token_price(self, token_address: str) -> Optional[TokenPrice]:
        """
        Get token price from DeFi Llama
        
        Args:
            token_address: Token contract address
            
        Returns:
            TokenPrice object or None
        """
        try:
            # Try DeFi Llama price API
            response = requests.get(
                f"https://api.llama.fi/tokenPrice/{token_address}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return TokenPrice(
                    symbol="Unknown",
                    address=token_address,
                    price_usd=data.get("price", 0),
                    price_change_24h=data.get("priceChange24h", 0),
                    volume_24h=data.get("volume24h", 0)
                )
        except Exception as e:
            print(f"Error fetching price: {e}")
        
        return None
    
    def get_high_apy_pools(self, chain: str = "BSC", min_tvl: float = 10000) -> List[PoolInfo]:
        """
        Get pools with high APY, filtered by minimum TVL
        
        Args:
            chain: Chain name (BSC, opBNB)
            min_tvl: Minimum TVL in USD
            
        Returns:
            Sorted list of PoolInfo by APY (descending)
        """
        pools = self.get_bsc_pancake_pools()
        
        # Filter by chain and TVL
        filtered = [
            p for p in pools
            if p.chain == chain and p.tvl >= min_tvl
        ]
        
        # Sort by APY descending
        sorted_pools = sorted(filtered, key=lambda x: x.apy, reverse=True)
        
        return sorted_pools[:10]  # Top 10
    
    def get_protocol_stats(self, protocol: str = "pancakeswap") -> Dict[str, Any]:
        """
        Get protocol statistics
        
        Args:
            protocol: Protocol name
            
        Returns:
            Dictionary with protocol stats
        """
        try:
            response = requests.get(
                f"{self.DEFILLAMA_API}/protocol/{protocol}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "tvl": data.get("tvl", 0),
                    "volume_24h": data.get("volume24h", 0),
                    "apy": data.get("apy", 0),
                    "chain": data.get("chain"),
                    "category": data.get("category"),
                }
        except Exception as e:
            print(f"Error fetching protocol stats: {e}")
        
        return {}
    
    def get_gas_price_bsc(self) -> Dict[str, int]:
        """
        Get current gas prices on BSC
        
        Returns:
            Dictionary with standard, fast, urgent gas prices in Gwei
        """
        try:
            response = requests.get(
                "https://api.bscscan.com/api",
                params={
                    "module": "gastracker",
                    "action": "gasoracle",
                    "apikey": self.bsc_api_key or ""
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data.get("result", {})
                    return {
                        "safe_gas": int(result.get("SafeGasPrice", 5)),
                        "propose_gas": int(result.get("ProposeGasPrice", 10)),
                        "fast_gas": int(result.get("FastGasPrice", 15))
                    }
        except Exception as e:
            print(f"Error fetching gas price: {e}")
        
        # Default values
        return {"safe_gas": 5, "propose_gas": 10, "fast_gas": 15}
    
    def get_venus_yields(self) -> List[Dict[str, Any]]:
        """
        Get Venus lending yields
        
        Returns:
            List of market yields
        """
        try:
            response = requests.get(
                "https://api.llama.fi/lends?chain=BSC",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                venus_markets = []
                for market in data:
                    if "venus" in market.get("protocol", "").lower():
                        venus_markets.append({
                            "token": market.get("underlyingSymbol"),
                            "supply_apy": market.get("supplyAPY", 0),
                            "borrow_apy": market.get("borrowAPY", 0),
                            "tvl": market.get("tvlUsd", 0),
                            "collateral_factor": market.get("collateralFactor", 0)
                        })
                
                return venus_markets
        except Exception as e:
            print(f"Error fetching Venus yields: {e}")
        
        return []
    
    def calculate_yield_strategy(
        self,
        principal_usd: float,
        risk_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Calculate optimal yield strategy based on risk level
        
        Args:
            principal_usd: Investment amount in USD
            risk_level: low, medium, high
            
        Returns:
            Strategy recommendation
        """
        pools = self.get_high_apy_pools(min_tvl=10000)
        
        if not pools:
            return {"error": "No pools available"}
        
        # Filter based on risk
        if risk_level == "low":
            filtered = [p for p in pools if p.fee <= 0.3 and p.tvl >= 100000]
        elif risk_level == "high":
            filtered = [p for p in pools if p.apy >= 50]
        else:  # medium
            filtered = [p for p in pools if p.tvl >= 50000]
        
        if not filtered:
            filtered = pools[:5]
        
        # Calculate expected returns
        for pool in filtered:
            pool.annual_return = principal_usd * (pool.apy / 100)
        
        return {
            "principal_usd": principal_usd,
            "risk_level": risk_level,
            "recommended_pools": [
                {
                    "name": p.name,
                    "protocol": p.protocol,
                    "apy": f"{p.apy:.2f}%",
                    "tvl": f"${p.tvl:,.0f}",
                    "expected_annual_return": f"${pool.annual_return:,.2f}"
                }
                for p, pool in zip(filtered[:3], filtered[:3])
            ],
            "best_pool": filtered[0].name if filtered else None,
            "best_apy": f"{filtered[0].apy:.2f}%" if filtered else "N/A"
        }


# Example usage
if __name__ == "__main__":
    service = DeFiService()
    
    # Get top pools
    print("Top 5 High APY Pools:")
    pools = service.get_high_apy_pools()
    for i, pool in enumerate(pools[:5], 1):
        print(f"{i}. {pool.name}: {pool.apy:.2f}% APY (TVL: ${pool.tvl:,.0f})")
    
    # Get gas prices
    print("\nGas Prices (Gwei):")
    gas = service.get_gas_price_bsc()
    print(f"  Safe: {gas['safe_gas']}")
    print(f"  Fast: {gas['fast_gas']}")
