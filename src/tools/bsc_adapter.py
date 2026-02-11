"""
BSC (BNB Smart Chain) Network Adapter
Handle all BSC blockchain interactions

Good Vibes Only: OpenClaw Edition Hackathon

Features:
- RPC connections (BSC, opBNB, Ethereum, Arbitrum)
- BscScan API integration for real-time data
- Multi-chain DeFi protocol support
- Real-time pool data fetching
"""

import json
import time
import asyncio
import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import httpx

from eth_typing import Address
from web3 import Web3
from web3.contract import Contract
from web3.types import TxParams, Wei

logger = logging.getLogger(__name__)


# ============== Configuration ==============

@dataclass
class ChainConfig:
    """Blockchain network configuration"""
    name: str
    chain_id: int
    rpc_url: str
    explorer_url: str
    scan_api_url: str
    native_symbol: str
    scan_api_key: str = ""


# Pre-configured chains
CHAINS = {
    "bsc": ChainConfig(
        name="BNB Smart Chain",
        chain_id=56,
        rpc_url="https://bsc-dataseed1.binance.org",
        explorer_url="https://bscscan.com",
        scan_api_url="https://api.bscscan.com/api",
        native_symbol="BNB",
    ),
    "opbnb": ChainConfig(
        name="opBNB",
        chain_id=204,
        rpc_url="https://opbnb-mainnet-rpc.bnbchain.org",
        explorer_url="https://opbnbscan.com",
        scan_api_url="https://api.opbnbscan.com/api",
        native_symbol="BNB",
    ),
    "ethereum": ChainConfig(
        name="Ethereum",
        chain_id=1,
        rpc_url="https://eth.llamarpc.com",
        explorer_url="https://etherscan.io",
        scan_api_url="https://api.etherscan.io/api",
        native_symbol="ETH",
    ),
    "arbitrum": ChainConfig(
        name="Arbitrum",
        chain_id=42161,
        rpc_url="https://arb1.arbitrum.io/rpc",
        explorer_url="https://arbiscan.io",
        scan_api_url="https://api.arbiscan.io/api",
        native_symbol="ETH",
    ),
}


# ============== Data Classes ==============

@dataclass
class WalletInfo:
    """Wallet information"""
    address: str
    balance_bnb: Decimal
    balance_usdt: Decimal
    nonce: int


@dataclass
class PoolInfo:
    """DeFi Pool Information"""
    name: str
    protocol: str
    chain: str
    pool_address: str
    token0_address: str = ""
    token1_address: str = ""
    token0_symbol: str = ""
    token1_symbol: str = ""
    tvl: Decimal = Decimal(0)
    tvl_usd: Decimal = Decimal(0)
    apr: Decimal = Decimal(0)
    volume_24h: Decimal = Decimal(0)
    fee: Decimal = Decimal(0)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "protocol": self.protocol,
            "chain": self.chain,
            "pool_address": self.pool_address,
            "token0": self.token0_symbol,
            "token1": self.token1_symbol,
            "tvl": float(self.tvl_usd),
            "apr": float(self.apr),
            "volume_24h": float(self.volume_24h),
        }


@dataclass
class MarketData:
    """Real-time market data from BscScan"""
    token_address: str
    token_symbol: str
    price_usd: Decimal
    price_change_24h: Decimal
    volume_24h: Decimal
    tvl: Decimal
    holders: int = 0
    market_cap: Decimal = Decimal(0)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "token_address": self.token_address,
            "token_symbol": self.token_symbol,
            "price_usd": float(self.price_usd),
            "price_change_24h": float(self.price_change_24h),
            "volume_24h": float(self.volume_24h),
            "tvl": float(self.tvl),
            "holders": self.holders,
            "market_cap": float(self.market_cap),
            "last_updated": self.last_updated.isoformat(),
        }


# ============== Main Adapter ==============

class BSCAdapter:
    """
    BSC Network Adapter with Multi-Chain Support
    
    Features:
    - Connect to BSC, opBNB, Ethereum, Arbitrum
    - Fetch real-time data from chain scanners (BscScan, Etherscan, etc.)
    - Get DeFi pool information
    - Execute swaps on PancakeSwap and other DEXs
    """
    
    # PancakeSwap Router ABI (simplified)
    ROUTER_ABI = [
        {
            "name": "swapExactETHForTokens",
            "type": "function",
            "inputs": [
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "outputs": [{"name": "amounts", "type": "uint256[]"}]
        },
        {
            "name": "swapExactTokensForETH",
            "type": "function", 
            "inputs": [
                {"name": "amountIn", "type": "uint256"},
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "outputs": [{"name": "amounts", "type": "uint256[]"}]
        },
        {
            "name": "swapExactTokensForTokens",
            "type": "function",
            "inputs": [
                {"name": "amountIn", "type": "uint256"},
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "outputs": [{"name": "amounts", "type": "uint256[]"}]
        },
        {
            "name": "WETH",
            "type": "function",
            "outputs": [{"name": "", "type": "address"}]
        }
    ]
    
    # ERC20 ABI (simplified)
    ERC20_ABI = [
        {
            "name": "balanceOf",
            "type": "function",
            "inputs": [{"name": "owner", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}]
        },
        {
            "name": "approve",
            "type": "function",
            "inputs": [
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": [{"name": "", "type": "bool"}]
        },
        {
            "name": "allowance",
            "type": "function",
            "inputs": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"}
            ],
            "outputs": [{"name": "", "type": "uint256"}]
        },
        {
            "name": "transfer",
            "type": "function",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": [{"name": "", "type": "bool"}]
        }
    ]
    
    # Well-known DeFi pool addresses (BSC)
    KNOWN_POOLS = {
        # PancakeSwap
        "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82": {
            "name": "PancakeSwap CAKE",
            "protocol": "PancakeSwap",
            "token0": "CAKE",
            "token1": "BNB",
            "type": "farm"
        },
        "0x58F876857a02D6762E0101bb5C46D8c51251C071": {
            "name": "PancakeSwap CAKE-BNB LP",
            "protocol": "PancakeSwap",
            "token0": "CAKE",
            "token1": "BNB",
            "type": "lp"
        },
        "0x16b9a82874138c59e9eAb49c8e8a11D9d03f4D7a": {
            "name": "PancakeSwap BUSD-BNB LP",
            "protocol": "PancakeSwap",
            "token0": "BUSD",
            "token1": "BNB",
            "type": "lp"
        },
        # Venus
        "0x95c78222B3D6e52426D182a24093C9626BDA7e89": {
            "name": "Venus BUSD",
            "protocol": "Venus",
            "token0": "BUSD",
            "token1": "vBUSD",
            "type": "lending"
        },
        "0xA7c551e53a63D242d4018bFeCfebdB29C3f1D4c7": {
            "name": "Venus BNB",
            "protocol": "Venus",
            "token0": "BNB",
            "token1": "vBNB",
            "type": "lending"
        },
        # Biswap
        "0x858E3312196C8FEA47584C53d7F93fF8B4dB0C5e": {
            "name": "Biswap BSW-BNB LP",
            "protocol": "Biswap",
            "token0": "BSW",
            "token1": "BNB",
            "type": "lp"
        },
    }
    
    def __init__(
        self, 
        chain: str = "bsc", 
        rpc_url: str = None, 
        private_key: str = None,
        scan_api_key: str = ""
    ):
        """
        Initialize BSC Adapter
        
        Args:
            chain: Chain name ('bsc', 'opbnb', 'ethereum', 'arbitrum')
            rpc_url: RPC endpoint (auto-selected if not provided)
            private_key: Wallet private key (optional)
            scan_api_key: BscScan/Etherscan API key for real-time data
        """
        # Load chain config
        if chain in CHAINS:
            self.chain_config = CHAINS[chain]
        else:
            raise ValueError(f"Unknown chain: {chain}. Supported: {list(CHAINS.keys())}")
        
        # Override RPC if provided
        if rpc_url:
            self.chain_config.rpc_url = rpc_url
        
        # Override API key if provided
        if scan_api_key:
            self.chain_config.scan_api_key = scan_api_key
        
        self.w3 = Web3(Web3.HTTPProvider(self.chain_config.rpc_url))
        self.private_key = private_key
        self.chain = chain
        
        # Async HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Cache for market data
        self._price_cache: Dict[str, MarketData] = {}
        self._cache_ttl = 60  # seconds
        
        # Get address from private key
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.address = None
            self.account = None
        
        logger.info(f"Connected to {self.chain_config.name}")
    
    async def close(self):
        """Close async client"""
        await self.http_client.aclose()
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to network"""
        return self.w3.is_connected()
    
    def get_chain_info(self) -> Dict:
        """Get chain information"""
        return {
            "name": self.chain_config.name,
            "chain_id": self.chain_config.chain_id,
            "native_symbol": self.chain_config.native_symbol,
            "block_number": self.w3.eth.block_number,
            "gas_price": self.w3.eth.gas_price,
            "connected": self.is_connected,
        }
    
    # ============== BscScan API Methods ==============
    
    async def _scan_api_request(self, params: Dict) -> Dict:
        """Make request to block explorer API"""
        if not self.chain_config.scan_api_key:
            logger.warning("No scan API key provided - real-time data limited")
            return {}
        
        params["apikey"] = self.chain_config.scan_api_key
        
        try:
            response = await self.http_client.get(
                self.chain_config.scan_api_url,
                params=params
            )
            data = response.json()
            
            if data.get("status") == "1":
                return data.get("result", {})
            else:
                logger.warning(f"Scan API error: {data.get('message')}")
                return {}
        except Exception as e:
            logger.error(f"Scan API request failed: {e}")
            return {}
    
    async def get_token_price(self, token_address: str) -> Optional[MarketData]:
        """
        Get token price from BscScan API
        
        Args:
            token_address: Token contract address
        
        Returns:
            MarketData with price info
        """
        # Check cache
        if token_address in self._price_cache:
            cached = self._price_cache[token_address]
            if (datetime.now() - cached.last_updated).seconds < self._cache_ttl:
                return cached
        
        # Fetch from API
        result = await self._fetch_price_from_dexscreener(token_address)
        
        if result:
            data = MarketData(
                token_address=token_address,
                token_symbol=result.get("symbol", "???"),
                price_usd=Decimal(str(result.get("price", 0))),
                price_change_24h=Decimal(str(result.get("priceChange24h", 0))),
                volume_24h=Decimal(str(result.get("volume24h", 0))),
                tvl=Decimal(str(result.get("tvl", 0))),
                holders=result.get("holders", 0),
            )
            self._price_cache[token_address] = data
            return data
        
        return None
    
    async def _fetch_price_from_dexscreener(self, token_address: str) -> Optional[Dict]:
        """Fetch price from DexScreener API as fallback"""
        try:
            response = await self.http_client.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            )
            data = response.json()
            
            if data.get("pair"):
                pair = data["pair"]
                return {
                    "symbol": pair["baseToken"]["symbol"],
                    "price": pair["priceUsd"],
                    "priceChange24h": pair["priceChange"]["h24"],
                    "volume24h": pair["volume"]["h24"],
                    "tvl": pair["liquidity"]["usd"],
                }
        except Exception as e:
            logger.error(f"DexScreener API error: {e}")
        
        return None
    
    async def get_top_pools(self, limit: int = 10) -> List[PoolInfo]:
        """
        Get top DeFi pools by TVL
        
        Args:
            limit: Number of pools to return
        
        Returns:
            List of PoolInfo objects
        """
        pools = []
        
        # Known pools with cached data
        for address, info in self.KNOWN_POOLS.items():
            # Get TVL from DexScreener
            dex_data = await self._fetch_price_from_dexscreener(address)
            
            pool = PoolInfo(
                name=info["name"],
                protocol=info["protocol"],
                chain=self.chain_config.name,
                pool_address=address,
                token0_symbol=info["token0"],
                token1_symbol=info["token1"],
                tvl_usd=Decimal(str(dex_data.get("tvl", 0))) if dex_data else Decimal(0),
                apr=Decimal(str(dex_data.get("apy", 0))) if dex_data else Decimal(0),
                volume_24h=Decimal(str(dex_data.get("volume24h", 0))) if dex_data else Decimal(0),
            )
            pools.append(pool)
        
        # Sort by TVL and return top N
        pools.sort(key=lambda x: x.tvl_usd, reverse=True)
        return pools[:limit]
    
    async def get_gas_price(self) -> Dict[str, Decimal]:
        """
        Get current gas prices from multiple sources
        
        Returns:
            Dict with gas prices in Gwei
        """
        # Try chain scanner first
        result = await self._scan_api_request({
            "module": "gastracker",
            "action": "gasoracle"
        })
        
        if result:
            return {
                "slow": Decimal(str(result.get("SafeGasPrice", 0))),
                "average": Decimal(str(result.get("ProposeGasPrice", 0))),
                "fast": Decimal(str(result.get("FastGasPrice", 0))),
            }
        
        # Fallback to web3
        gas_wei = self.w3.eth.gas_price
        gas_gwei = Decimal(gas_wei) / Decimal(10**9)
        
        return {
            "average": gas_gwei,
            "slow": gas_gwei * Decimal("0.8"),
            "fast": gas_gwei * Decimal("1.2"),
        }
    
    async def estimate_swap_gas(
        self, 
        token_in: str, 
        token_out: str, 
        amount_wei: int
    ) -> int:
        """
        Estimate gas for a swap transaction
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_wei: Amount to swap in wei
        
        Returns:
            Estimated gas units
        """
        router_address = "0x10ED43C718714eb63d5aA57B78B54704E256024E"  # PancakeSwap
        
        router = self.w3.eth.contract(
            address=Web3.to_checksum_address(router_address),
            abi=self.ROUTER_ABI
        )
        
        try:
            txn = router.functions.swapExactTokensForTokens(
                amount_wei,
                0,
                [Web3.to_checksum_address(token_in), Web3.to_checksum_address(token_out)],
                self.address or Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
                int(time.time()) + 300
            ).build_transaction({
                'from': self.address or Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
                'nonce': 0,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            return self.w3.eth.estimate_gas(txn)
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            return 300000
    
    # ============== Web3 Methods ==============
    
    def get_block_number(self) -> int:
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_balance(self, address: str = None) -> Decimal:
        """
        Get native token balance
        
        Args:
            address: Wallet address (uses self.address if not provided)
        """
        addr = address or self.address
        if not addr:
            raise ValueError("No address provided")
        
        balance_wei = self.w3.eth.get_balance(addr)
        return Decimal(balance_wei) / Decimal(10**18)
    
    def get_token_balance(self, token_address: str, holder_address: str = None) -> Decimal:
        """
        Get ERC20 token balance
        
        Args:
            token_address: Token contract address
            holder_address: Token holder address
        """
        holder = holder_address or self.address
        if not holder:
            raise ValueError("No address provided")
        
        token = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=self.ERC20_ABI
        )
        
        balance_wei = token.functions.balanceOf(holder).call()
        return Decimal(balance_wei) / Decimal(10**18)
    
    def get_nonce(self, address: str = None) -> int:
        """Get transaction nonce"""
        addr = address or self.address
        return self.w3.eth.get_transaction_count(addr)
    
    def approve_token(self, token_address: str, spender_address: str, amount_wei: int) -> str:
        """
        Approve token spending
        
        Args:
            token_address: Token contract address
            spender_address: Spender contract address
            amount_wei: Amount to approve in wei
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No private key provided")
        
        token = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=self.ERC20_ABI
        )
        
        txn = token.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount_wei
        ).build_transaction({
            'from': self.address,
            'nonce': self.get_nonce(),
            'gas': 100000,
            'gasPrice': int(self.w3.eth.gas_price * 1.1)
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    
    def swap_tokens(
        self,
        token_in: str,
        token_out: str,
        amount_in_wei: int,
        amount_out_min_wei: int,
        deadline_seconds: int = 300
    ) -> str:
        """
        Execute token swap on PancakeSwap
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in_wei: Amount to swap in wei
            amount_out_min_wei: Minimum output amount in wei
            deadline_seconds: Transaction deadline
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No private key provided")
        
        router = self.w3.eth.contract(
            address=Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E"),
            abi=self.ROUTER_ABI
        )
        
        deadline = int(time.time()) + deadline_seconds
        
        path = [
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out)
        ]
        
        gas_price = int(self.w3.eth.gas_price * 1.1)
        
        txn = router.functions.swapExactTokensForTokens(
            amount_in_wei,
            amount_out_min_wei,
            path,
            self.address,
            deadline
        ).build_transaction({
            'from': self.address,
            'nonce': self.get_nonce(),
            'gas': 300000,
            'gasPrice': gas_price
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    
    def swap_eth_for_tokens(
        self,
        token_out: str,
        amount_out_min_wei: int,
        value_wei: int,
        deadline_seconds: int = 300
    ) -> str:
        """
        Swap BNB for tokens
        
        Args:
            token_out: Output token address
            amount_out_min_wei: Minimum output amount in wei
            value_wei: BNB amount to swap in wei
            deadline_seconds: Transaction deadline
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No private key provided")
        
        router = self.w3.eth.contract(
            address=Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E"),
            abi=self.ROUTER_ABI
        )
        
        deadline = int(time.time()) + deadline_seconds
        
        path = [
            Web3.to_checksum_address(self.w3.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bd095Bc")),
            Web3.to_checksum_address(token_out)
        ]
        
        gas_price = int(self.w3.eth.gas_price * 1.1)
        
        txn = router.functions.swapExactETHForTokens(
            amount_out_min_wei,
            path,
            self.address,
            deadline
        ).build_transaction({
            'from': self.address,
            'nonce': self.get_nonce(),
            'gas': 300000,
            'gasPrice': gas_price,
            'value': value_wei
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt"""
        return self.w3.eth.get_transaction_receipt(tx_hash)


# ============== Demo ==============

async def demo_realtime_data():
    """Demo: Fetch real-time DeFi data from BscScan"""
    print("=" * 60)
    print("🔗 Auto-DeFi Agent - Real-time Chain Data Demo")
    print("=" * 60)
    
    # Initialize adapter
    adapter = BSCAdapter(chain="bsc")
    
    print(f"\n📡 Connected to: {adapter.chain_config.name}")
    print(f"   Chain ID: {adapter.chain_config.chain_id}")
    print(f"   Block: {adapter.get_block_number()}")
    
    # Get gas prices
    print("\n⛽ Gas Prices:")
    gas = await adapter.get_gas_price()
    print(f"   Slow: {gas['slow']} Gwei")
    print(f"   Average: {gas['average']} Gwei")
    print(f"   Fast: {gas['fast']} Gwei")
    
    # Get top pools
    print("\n🏊 Top DeFi Pools:")
    pools = await adapter.get_top_pools(limit=5)
    for i, pool in enumerate(pools, 1):
        print(f"   {i}. {pool.name}")
        print(f"      TVL: ${pool.tvl_usd:,.0f}")
        print(f"      APY: {pool.apr:.1f}%")
        print(f"      Volume 24h: ${pool.volume_24h:,.0f}")
    
    # Get token price
    print("\n💰 Token Prices:")
    cake_price = await adapter.get_token_price("0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82")
    if cake_price:
        print(f"   CAKE: ${cake_price.price_usd:.4f}")
        print(f"   24h Change: {cake_price.price_change_24h:+.2f}%")
    
    await adapter.close()
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_realtime_data())
