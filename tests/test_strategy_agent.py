"""
Test for Strategy Agent
"""

import pytest
import sys
from pathlib import Path
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.strategy_agent import (
    AutoDeFiAgent, StrategyConfig, AgentState, 
    RiskLevel, Opportunity, Transaction
)


class TestStrategyConfig:
    """Test cases for StrategyConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = StrategyConfig()
        
        assert config.min_apy == 5.0
        assert config.max_slippage == 1.0
        assert config.gas_threshold_usd == 10.0
        assert config.check_interval_seconds == 300
        assert config.auto_execute == False
        assert config.risk_level == RiskLevel.MEDIUM
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = StrategyConfig(
            min_apy=10.0,
            max_slippage=2.0,
            auto_execute=True,
            risk_level=RiskLevel.HIGH
        )
        
        assert config.min_apy == 10.0
        assert config.max_slippage == 2.0
        assert config.auto_execute == True
        assert config.risk_level == RiskLevel.HIGH


class TestAgentState:
    """Test cases for AgentState enum"""
    
    def test_state_values(self):
        """Test all states exist"""
        assert AgentState.IDLE.value == "idle"
        assert AgentState.MONITORING.value == "monitoring"
        assert AgentState.EXECUTING.value == "executing"
        assert AgentState.ERROR.value == "error"
        assert AgentState.STOPPED.value == "stopped"


class TestOpportunity:
    """Test cases for Opportunity dataclass"""
    
    def test_opportunity_creation(self):
        """Test creating an opportunity"""
        opp = Opportunity(
            pool_name="CAKE-USDT",
            protocol="PancakeSwap",
            chain="BSC",
            apy=25.5,
            tvl=1000000.0,
            token_pair="CAKE/USDT",
            contract_address="0x1234...",
            confidence=0.8
        )
        
        assert opp.pool_name == "CAKE-USDT"
        assert opp.apy == 25.5
        assert opp.tvl == 1000000.0
        assert opp.confidence == 0.8
        assert isinstance(opp.timestamp, datetime)
    
    def test_opportunity_defaults(self):
        """Test opportunity default values"""
        opp = Opportunity(
            pool_name="Test",
            protocol="Test",
            chain="BSC",
            apy=10.0,
            tvl=50000.0,
            token_pair="T1/T2",
            contract_address="0x..."
        )
        
        assert opp.confidence == 0.0
        assert isinstance(opp.timestamp, datetime)


class TestAutoDeFiAgent:
    """Test cases for AutoDeFiAgent"""
    
    def test_agent_initialization(self):
        """Test agent creation"""
        config = StrategyConfig(min_apy=10.0)
        agent = AutoDeFiAgent(config=config)
        
        assert agent.config.min_apy == 10.0
        assert agent.state == AgentState.IDLE
        assert agent.running == False
        assert len(agent.opportunities) == 0
        assert len(agent.transactions) == 0
    
    def test_start_stop(self):
        """Test agent start/stop"""
        agent = AutoDeFiAgent()
        
        agent.start()
        assert agent.running == True
        assert agent.state == AgentState.IDLE
        
        agent.stop()
        assert agent.running == False
        assert agent.state == AgentState.STOPPED
    
    def test_scan_opportunities(self):
        """Test opportunity scanning with mock data"""
        from src.tools.defi_service import PoolInfo
        
        agent = AutoDeFiAgent(config=StrategyConfig(min_apy=10.0))
        
        # Mock pools
        mock_pools = [
            PoolInfo("Low APY", "Proto1", "BSC", "0x1", "A", "B", 100000, 5.0, 100000, 0.25),
            PoolInfo("High APY", "Proto2", "BSC", "0x2", "A", "B", 100000, 25.0, 100000, 0.25),
            PoolInfo("Medium APY", "Proto3", "BSC", "0x3", "A", "B", 100000, 15.0, 100000, 0.25),
        ]
        
        opportunities = agent.scan_opportunities(mock_pools)
        
        # Should find 2 opportunities (APY >= 10)
        assert len(opportunities) == 2
        assert all(o.apy >= 10.0 for o in opportunities)
        
        # Should be sorted by APY descending
        assert opportunities[0].apy >= opportunities[1].apy
    
    def test_get_best_opportunity(self):
        """Test getting best opportunity"""
        agent = AutoDeFiAgent()
        
        # No opportunities yet
        assert agent.get_best_opportunity() is None
        
        # Add mock opportunities (already sorted by APY)
        agent.opportunities = [
            Opportunity("Pool B", "P2", "BSC", 25.0, 100000, "C/D", "0x2", 0.8),  # Highest APY first
            Opportunity("Pool C", "P3", "BSC", 20.0, 100000, "E/F", "0x3", 0.6),
            Opportunity("Pool A", "P1", "BSC", 15.0, 100000, "A/B", "0x1", 0.7),
        ]
        
        best = agent.get_best_opportunity()
        assert best is not None
        assert best.apy == 25.0  # Highest APY first
    
    def test_analyze_risk(self):
        """Test risk analysis"""
        agent = AutoDeFiAgent()
        
        opp = Opportunity(
            pool_name="Test Pool",
            protocol="PancakeSwap",  # Known protocol
            chain="BSC",
            apy=25.0,
            tvl=1000000.0,  # High TVL
            token_pair="A/B",
            contract_address="0x..."
        )
        
        analysis = agent.analyze_risk(opp)
        
        assert "score" in analysis
        assert "risk_level" in analysis
        assert "factors" in analysis
        assert "recommendation" in analysis
        
        # Should be LOW risk (high TVL + known protocol)
        assert analysis["risk_level"] in ["LOW", "MEDIUM"]
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        agent = AutoDeFiAgent()
        
        assert agent.metrics["checks"] == 0
        assert agent.metrics["opportunities_found"] == 0
        assert agent.metrics["executed"] == 0
        
        # Trigger some metrics
        agent.metrics["checks"] = 5
        agent.metrics["opportunities_found"] = 10
        agent.metrics["executed"] = 2
        
        assert agent.metrics["checks"] == 5
        assert agent.metrics["opportunities_found"] == 10
        assert agent.metrics["executed"] == 2
    
    def test_get_status(self):
        """Test status retrieval"""
        agent = AutoDeFiAgent()
        agent.start()
        
        status = agent.get_status()
        
        assert "state" in status
        assert "running" in status
        assert "opportunities_count" in status
        assert "transactions_count" in status
        assert "metrics" in status
        
        agent.stop()


class TestTransaction:
    """Test cases for Transaction dataclass"""
    
    def test_transaction_creation(self):
        """Test creating a transaction"""
        tx = Transaction(
            tx_hash="0x1234...",
            action="SWAP",
            from_token="USDT",
            to_token="WBNB",
            amount_usd=100.0,
            gas_used=0.5,
            status="PENDING"
        )
        
        assert tx.tx_hash == "0x1234..."
        assert tx.action == "SWAP"
        assert tx.amount_usd == 100.0
        assert tx.status == "PENDING"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
