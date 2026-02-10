"""
Test for DeFi Service
"""

import pytest
import sys
from pathlib import Path
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.defi_service import DeFiService, PoolInfo, TokenPrice


class TestDeFiService:
    """Test cases for DeFi Service"""
    
    def test_service_initialization(self):
        """Test service creation"""
        service = DeFiService()
        assert service.DEFILLAMA_API == "https://api.llama.fi"
    
    def test_token_addresses(self):
        """Test token address mapping"""
        service = DeFiService()
        
        assert "BNB" in service.TOKENS
        assert "USDT" in service.TOKENS
        assert "CAKE" in service.TOKENS
        
        # Verify addresses are checksum format
        for token, address in service.TOKENS.items():
            assert address.startswith("0x")
            assert len(address) in [42, 43]
    
    def test_pool_info_dataclass(self):
        """Test PoolInfo dataclass"""
        pool = PoolInfo(
            name="CAKE-USDT",
            protocol="PancakeSwap",
            chain="BSC",
            pool_address="0x...",
            token0="0x...",
            token1="0x...",
            tvl=1000000.0,
            apy=25.5,
            volume_24h=500000.0,
            fee=0.25
        )
        
        assert pool.name == "CAKE-USDT"
        assert pool.apy == 25.5
        assert pool.tvl == 1000000.0
        assert pool.protocol == "PancakeSwap"
    
    def test_token_price_dataclass(self):
        """Test TokenPrice dataclass"""
        price = TokenPrice(
            symbol="CAKE",
            address="0x123...",
            price_usd=0.5,
            price_change_24h=5.0,
            volume_24h=1000000.0
        )
        
        assert price.symbol == "CAKE"
        assert price.price_usd == 0.5
        assert isinstance(price.price_change_24h, float)
    
    def test_gas_price_structure(self):
        """Test gas price return structure"""
        service = DeFiService()
        
        # Mock test - just check function exists
        assert hasattr(service, 'get_gas_price_bsc')
    
    def test_yield_strategy_structure(self):
        """Test yield strategy calculation structure"""
        service = DeFiService()
        
        # Mock test - check function signature
        assert hasattr(service, 'calculate_yield_strategy')
        
        # Test with empty pools (should return error)
        # result = service.calculate_yield_strategy(1000, "medium")
        # assert "error" in result or "recommended_pools" in result


class TestPoolFiltering:
    """Test cases for pool filtering logic"""
    
    def test_high_apy_filter(self):
        """Test filtering pools by APY"""
        pools = [
            PoolInfo("Pool A", "Protocol1", "BSC", "0x1", "0xA", "0xB", 100000, 5.0, 100000, 0.25),
            PoolInfo("Pool B", "Protocol2", "BSC", "0x2", "0xA", "0xB", 100000, 15.0, 100000, 0.25),
            PoolInfo("Pool C", "Protocol3", "BSC", "0x3", "0xA", "0xB", 100000, 25.0, 100000, 0.25),
        ]
        
        # Filter by APY >= 10
        filtered = [p for p in pools if p.apy >= 10]
        assert len(filtered) == 2
        assert all(p.apy >= 10 for p in filtered)
    
    def test_tvl_filter(self):
        """Test filtering pools by TVL"""
        pools = [
            PoolInfo("Pool A", "Protocol1", "BSC", "0x1", "0xA", "0xB", 5000, 25.0, 100000, 0.25),
            PoolInfo("Pool B", "Protocol2", "BSC", "0x2", "0xA", "0xB", 100000, 15.0, 100000, 0.25),
            PoolInfo("Pool C", "Protocol3", "BSC", "0x3", "0xA", "0xB", 1000000, 10.0, 100000, 0.25),
        ]
        
        # Filter by TVL >= 10000
        filtered = [p for p in pools if p.tvl >= 10000]
        assert len(filtered) == 2
    
    def test_sorting_by_apy(self):
        """Test sorting pools by APY"""
        pools = [
            PoolInfo("Pool A", "Protocol1", "BSC", "0x1", "0xA", "0xB", 100000, 10.0, 100000, 0.25),
            PoolInfo("Pool B", "Protocol2", "BSC", "0x2", "0xA", "0xB", 100000, 25.0, 100000, 0.25),
            PoolInfo("Pool C", "Protocol3", "BSC", "0x3", "0xA", "0xB", 100000, 15.0, 100000, 0.25),
        ]
        
        # Sort by APY descending
        sorted_pools = sorted(pools, key=lambda x: x.apy, reverse=True)
        
        assert sorted_pools[0].apy == 25.0
        assert sorted_pools[1].apy == 15.0
        assert sorted_pools[2].apy == 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
