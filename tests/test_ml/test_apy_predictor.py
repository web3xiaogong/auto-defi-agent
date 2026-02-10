"""
Tests for ML APY Predictor
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ml.apy_predictor import APYPredictor, APYPrediction, APYDataPoint, ModelConfig


class TestAPYPredictor:
    """Test cases for APY Predictor"""
    
    def test_initialization(self):
        """Test predictor initialization"""
        config = ModelConfig(window_size=7)
        predictor = APYPredictor(config=config)
        
        assert predictor.config.window_size == 7
        assert len(predictor.pool_data) == 0
    
    def test_add_data_point(self):
        """Test adding data points"""
        predictor = APYPredictor()
        
        predictor.add_data_point(
            pool_address="0x1234...",
            pool_name="CAKE-USDT",
            apy=10.0,
            tvl=1000000,
            volume=500000
        )
        
        assert "0x1234..." in predictor.pool_data
        assert len(predictor.pool_data["0x1234..."]) == 1
    
    def test_predict_with_no_data(self):
        """Test prediction with no data"""
        predictor = APYPredictor()
        
        prediction = predictor.predict("0x9999...", "Test Pool")
        
        assert prediction is not None
        assert prediction.pool_name == "Test Pool"
        assert prediction.trend == "STABLE"
    
    def test_prediction_structure(self):
        """Test prediction dataclass structure"""
        prediction = APYPrediction(
            pool_name="Test",
            pool_address="0x1234",
            current_apy=10.0,
            predicted_apy_24h=10.5,
            predicted_apy_7d=12.0,
            trend="UP",
            confidence=0.8,
            recommendation="BUY",
            factors=["📈 APY 上升"],
        )
        
        assert prediction.pool_name == "Test"
        assert prediction.current_apy == 10.0
        assert prediction.trend == "UP"
        
        data = prediction.to_dict()
        assert data["pool_name"] == "Test"
    
    def test_calculate_slope(self):
        """Test slope calculation"""
        predictor = APYPredictor()
        
        rising = [1.0, 2.0, 3.0, 4.0, 5.0]
        slope = predictor._calculate_slope(rising)
        assert slope > 0
        
        falling = [5.0, 4.0, 3.0, 2.0, 1.0]
        slope = predictor._calculate_slope(falling)
        assert slope < 0
    
    def test_get_risk_analysis(self):
        """Test risk analysis"""
        predictor = APYPredictor()
        
        risk = predictor.get_risk_analysis("0x9999...")
        assert risk["risk_level"] == "UNKNOWN"
    
    def test_clear_cache(self):
        """Test cache clearing"""
        predictor = APYPredictor()
        
        predictor.add_data_point("0x1111...", "Pool", 10.0, 1000000, 500000)
        predictor.predict("0x1111...", "Pool")
        
        assert len(predictor._predictions_cache) == 1
        
        predictor.clear_cache()
        
        assert len(predictor._predictions_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
