"""
Tests for Strategy Sharing
"""

import pytest
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sharing.strategy_share import (
    StrategySharer, create_simple_strategy, generate_strategy_card
)


class TestStrategySharer:
    """Test cases for Strategy Sharer"""
    
    def test_initialization(self):
        """Test sharer initialization"""
        sharer = StrategySharer()
        assert sharer.CODE_LENGTH == 12
    
    def test_create_share_code(self):
        """Test share code creation"""
        sharer = StrategySharer()
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        share_code, verify_code = sharer.create_share_code(strategy)
        assert share_code is not None
        assert verify_code is not None
    
    def test_verify_share_code(self):
        """Test share code verification"""
        sharer = StrategySharer()
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        share_code, _ = sharer.create_share_code(strategy)
        verified = sharer.verify_share_code(share_code)
        assert verified is not None
        assert verified is not None
    
    def test_generate_share_url(self):
        """Test share URL generation"""
        sharer = StrategySharer()
        url = sharer.generate_share_url("TEST1234-XYZ1")
        assert "s=TEST1234" in url
    
    def test_import_strategy(self):
        """Test strategy import"""
        sharer = StrategySharer()
        strategy = create_simple_strategy("CAKE-USDT", 15.0)
        share_code, _ = sharer.create_share_code(strategy)
        imported = sharer.import_strategy(share_code)
        assert imported is not None
    
    def test_create_simple_strategy(self):
        """Test simple strategy creation"""
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        assert strategy["pool_name"] == "CAKE-USDT"
        assert strategy["min_apy"] == 15.0
    
    def test_generate_strategy_card(self):
        """Test strategy card generation"""
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        card = generate_strategy_card(strategy)
        assert "CAKE-USDT" in card


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
