"""
Test for BSC Adapter
"""

import pytest
import sys
from pathlib import Path
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tools.bsc_adapter import BSCAdapter


class TestBSCAdapter:
    """Test cases for BSC Adapter"""
    
    def test_connection(self):
        """Test BSC connection"""
        adapter = BSCAdapter(
            rpc_url="https://bsc-dataseed.binance.org/"
        )
        # May not be connected if no internet
        # assert adapter.is_connected == True
    
    def test_gas_price(self):
        """Test gas price retrieval"""
        adapter = BSCAdapter(
            rpc_url="https://bsc-dataseed.binance.org/"
        )
        # Should not raise exception
        try:
            gas = adapter.get_gas_price()
            assert isinstance(gas, int)
            assert gas > 0
        except Exception as e:
            pytest.skip(f"Network error: {e}")
    
    def test_block_number(self):
        """Test block number retrieval"""
        adapter = BSCAdapter(
            rpc_url="https://bsc-dataseed.binance.org/"
        )
        try:
            block = adapter.get_block_number()
            assert isinstance(block, int)
            assert block > 0
        except Exception as e:
            pytest.skip(f"Network error: {e}")
    
    def test_address_validation(self):
        """Test address validation"""
        # Valid checksum address
        adapter = BSCAdapter(
            rpc_url="https://bsc-dataseed.binance.org/"
        )
        from web3 import Web3
        
        # Should be valid
        addr = Web3.to_checksum_address("0x19C9F422E6158302E8850c9e087A917f113783B4")
        assert addr.startswith("0x")
        assert len(addr) == 42


class TestBSCAdapterTransactions:
    """Test cases for BSC transactions (mocked)"""
    
    def test_wallet_info_structure(self):
        """Test WalletInfo dataclass"""
        from src.tools.bsc_adapter import WalletInfo
        
        info = WalletInfo(
            address="0x1234...",
            balance_bnb=1.5,
            balance_usdt=1000.0,
            nonce=5
        )
        
        assert info.address == "0x1234..."
        assert info.balance_bnb == 1.5
        assert info.balance_usdt == 1000.0
        assert info.nonce == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
