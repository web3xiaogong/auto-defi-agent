"""
Tests for Strategy Sharing
"""

import pytest
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sharing.strategy_share import (
    StrategySharer, ShareableStrategy, create_simple_strategy, generate_strategy_card
)


class TestStrategySharer:
    """Test cases for Strategy Sharer"""
    
    def test_initialization(self):
        """Test sharer initialization"""
        sharer = StrategySharer()
        
        assert sharer.CODE_LENGTH == 12
        assert len(sharer.share_codes) == 0
    
    def test_create_share_code(self):
        """Test share code creation"""
        sharer = StrategySharer()
        
        strategy = {
            "pool_name": "CAKE-USDT",
            "protocol": "PancakeSwap",
            "chain": "BSC",
            "min_apy": 15.0,
            "max_slippage": 1.0,
            "risk_level": "MEDIUM",
        }
        
        share_code, verify_code = sharer.create_share_code(
            strategy,
            creator_address="0x1234...",
            creator_name="TestUser"
        )
        
        assert share_code is not None
        assert verify_code is not None
        assert share_code in sharer.share_codes
    
    def test_verify_share_code(self):
        """Test share code verification"""
        sharer = StrategySharer()
        
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        
        share_code, _ = sharer.create_share_code(strategy)
        
        verified = sharer.verify_share_code(share_code)
        
        assert verified is not None
        assert verified.get("verified") is True
        assert verified.get("pool_name") == "CAKE-USDT"
    
    def test_generate_share_url(self):
        """Test share URL generation"""
        sharer = StrategySharer()
        
        url = sharer.generate_share_url("TEST1234-XYZ1")
        
        assert "s=TEST1234" in url
        assert "autodefi.ai" in url
    
    def test_import_strategy(self):
        """Test strategy import"""
        sharer = StrategySharer()
        
        strategy = create_simple_strategy("CAKE-USDT", 15.0)
        share_code, _ = sharer.create_share_code(strategy)
        
        imported = sharer.import_strategy(share_code)
        
        assert imported is not None
        assert imported.get("pool_name") == "CAKE-USDT"
    
    def test_different_strategies(self):
        """Test different strategies get different codes"""
        sharer = StrategySharer()
        
        strategy1 = create_simple_strategy("CAKE-USDT", 10.0)
        strategy2 = create_simple_strategy("CAKE-USDT", 15.0)
        
        code1, _ = sharer.create_share_code(strategy1)
        code2, _ = sharer.create_share_code(strategy2)
        
        assert code1 != code2


class TestCreateSimpleStrategy:
    """Test convenience functions"""
    
    def test_create_simple_strategy(self):
        """Test simple strategy creation"""
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        
        assert strategy["pool_name"] == "CAKE-USDT"
        assert strategy["min_apy"] == 15.0
        assert strategy["chain"] == "BSC"
    
    def test_create_simple_strategy_defaults(self):
        """Test default values"""
        strategy = create_simple_strategy("CAKE-USDT", 10.0)
        
        assert strategy["chain"] == "BSC"
        assert strategy["protocol"] == "PancakeSwap"


class TestGenerateStrategyCard:
    """Test strategy card generation"""
    
    def test_generate_strategy_card(self):
        """Test card generation"""
        strategy = create_simple_strategy("CAKE-USDT", 15.0, "BSC")
        
        card = generate_strategy_card(strategy)
        
        assert "CAKE-USDT" in card
        assert "15.0%" in card
    
    def test_generate_strategy_card_with_prediction(self):
        """Test card with prediction"""
        strategy = create_simple_strategy("CAKE-USDT", 15.0)
        
        prediction = {
            "current_apy": 15.5,
            "predicted_apy_24h": 16.0,
            "trend": "UP",
            "recommendation": "BUY",
        }
        
        card = generate_strategy_card(strategy, prediction)
        
        assert "15.50%" in card
        assert "BUY" in card


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
