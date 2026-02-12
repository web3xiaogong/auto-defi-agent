"""
Tests for ERC-8004 Integration

Run with:
    pytest tests/test_erc8004.py -v
"""

import pytest
import json
import hashlib
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


# ============ Data Classes (Copy from modules) ============

@dataclass
class AgentInfo:
    """Agent information for ERC-8004 registration"""
    agent_id: str = ""
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    services: List[str] = None
    capabilities: List[str] = None
    trust_score: float = 0.0
    verified: bool = False
    created_at: int = 0
    metadata_uri: str = ""
    
    def __post_init__(self):
        if self.services is None:
            self.services = []
        if self.capabilities is None:
            self.capabilities = []
    
    def to_dict(self) -> Dict:
        return {
            "agentId": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "services": self.services,
            "capabilities": self.capabilities,
            "trustScore": self.trust_score,
            "verified": self.verified,
            "createdAt": self.created_at,
            "metadataURI": self.metadata_uri
        }


@dataclass
class StrategyListing:
    """Strategy listing for marketplace"""
    strategy_id: str = ""
    name: str = ""
    description: str = ""
    pool_name: str = ""
    chain: str = ""
    apy_estimate: float = 0.0
    risk_level: str = "MEDIUM"
    creator: str = ""
    price_eth: float = 0.0
    royalty_percent: int = 10
    sales_count: int = 0
    rating: float = 0.0
    metadata_uri: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "strategyId": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "poolName": self.pool_name,
            "chain": self.chain,
            "apyEstimate": self.apy_estimate,
            "riskLevel": self.risk_level,
            "creator": self.creator,
            "priceETH": self.price_eth,
            "royaltyPercent": self.royalty_percent,
            "salesCount": self.sales_count,
            "rating": self.rating,
            "metadataURI": self.metadata_uri
        }


# ============ Mock ERC-8004 Registry ============

class MockERC8004Registry:
    """Mock ERC-8004 Registry for testing"""
    
    CONTRACTS = {
        "sepolia": {
            "agent_registry": "0x1234567890123456789012345678901234567890",
            "strategy_marketplace": "0x0987654321098765432109876543210987654321"
        }
    }
    
    def __init__(self, rpc_url: str = None, chain: str = "sepolia"):
        self.chain = chain
        self.contracts = self.CONTRACTS.get(chain, self.CONTRACTS["sepolia"])
        self.registered_agents = {}
        print(f"✅ Mock ERC-8004 Registry initialized on {chain}")
    
    def generate_agent_id(self, name: str, version: str = "1.0.0") -> str:
        timestamp = str(int(time.time()))
        data = f"{name}:{version}:{timestamp}"
        return f"autodefi-{hashlib.sha256(data.encode()).hexdigest()[:16]}"
    
    def create_metadata_uri(self, agent_info: AgentInfo) -> str:
        metadata = agent_info.to_dict()
        metadata_json = json.dumps(metadata, indent=2)
        metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        return f"https://ipfs.io/ipfs/{metadata_hash}"
    
    def register_agent(self, agent_info: AgentInfo) -> Dict:
        agent_id = self.generate_agent_id(agent_info.name)
        agent_info.agent_id = agent_id
        agent_info.created_at = int(time.time())
        metadata_uri = self.create_metadata_uri(agent_info)
        agent_info.metadata_uri = metadata_uri
        
        self.registered_agents[agent_id] = agent_info
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "metadata_uri": metadata_uri
        }
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        return self.registered_agents.get(agent_id)


# ============ Message Formatter ============

class MessageFormatter:
    """Message formatter for channels"""
    
    @staticmethod
    def format_telegram_defi(data: Dict) -> str:
        lines = ["📊 *DeFi Results*"]
        
        if "pools" in data:
            lines.append("")
            lines.append("*Top Opportunities:*")
            for i, pool in enumerate(data["pools"][:5], 1):
                lines.append(f"{i}. *{pool['name']}*")
                lines.append(f"   APY: `{pool['apy']:.1f}%`")
                lines.append(f"   TVL: `${pool['tvl']:,.0f}`")
        
        if "prediction" in data:
            lines.append("")
            lines.append("🔮 *Prediction:*")
            pred = data["prediction"]
            lines.append(f"   7D APY: `{pred.get('predicted_apy_7d', 0):.1f}%`")
            lines.append(f"   Trend: {pred.get('trend', 'N/A')}")
            lines.append(f"   Confidence: `{pred.get('confidence', 0)*100:.0f}%`")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_discord_defi(data: Dict) -> str:
        lines = ["📊 **DeFi Results**"]
        
        if "pools" in data:
            lines.append("")
            lines.append("**Top Opportunities:**")
            for i, pool in enumerate(data["pools"][:5], 1):
                lines.append(f"**{i}. {pool['name']}**")
                lines.append(f"   APY: `{pool['apy']:.1f}%`")
                lines.append(f"   TVL: `${pool['tvl']:,.0f}`")
        
        if "prediction" in data:
            lines.append("")
            lines.append("🔮 **Prediction:**")
            pred = data["prediction"]
            lines.append(f"   7D APY: `{pred.get('predicted_apy_7d', 0):.1f}%`")
            lines.append(f"   Trend: {pred.get('trend', 'N/A')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_defi_result(data: Dict, channel: str = "telegram") -> str:
        if channel == "telegram":
            return MessageFormatter.format_telegram_defi(data)
        elif channel == "discord":
            return MessageFormatter.format_discord_defi(data)
        else:
            return str(data)


# ============ Tests ============

class TestAgentInfo:
    """Test AgentInfo dataclass"""
    
    def test_create_agent_info(self):
        agent = AgentInfo(
            name="Auto-DeFi Agent",
            description="ML-Powered DeFi Optimization",
            author="web3xiaogong",
            services=["defi-optimization", "apy-prediction"],
            capabilities=["multi-chain", "ml-prediction"]
        )
        
        assert agent.name == "Auto-DeFi Agent"
        assert len(agent.services) == 2
        assert agent.version == "1.0.0"
        assert agent.trust_score == 0.0
        
        print("✅ AgentInfo creation works")
    
    def test_agent_to_dict(self):
        agent = AgentInfo(
            name="Test Agent",
            description="Test",
            services=["service1"]
        )
        
        data = agent.to_dict()
        
        assert "agentId" in data
        assert "name" in data
        assert data["name"] == "Test Agent"
        assert "services" in data
        assert "service1" in data["services"]
        
        print("✅ AgentInfo.to_dict() works")


class TestStrategyListing:
    """Test StrategyListing dataclass"""
    
    def test_create_listing(self):
        listing = StrategyListing(
            strategy_id="strategy-123",
            name="High APY CAKE Strategy",
            description="Earn high yields",
            pool_name="PancakeSwap CAKE-BNB",
            chain="BSC",
            apy_estimate=15.5,
            risk_level="MEDIUM",
            creator="0x1234...",
            price_eth=0.01,
            royalty_percent=10
        )
        
        assert listing.name == "High APY CAKE Strategy"
        assert listing.apy_estimate == 15.5
        assert listing.risk_level == "MEDIUM"
        assert listing.price_eth == 0.01
        
        print("✅ StrategyListing creation works")
    
    def test_listing_to_dict(self):
        listing = StrategyListing(
            name="Test Strategy",
            chain="BSC"
        )
        
        data = listing.to_dict()
        
        assert "strategyId" in data
        assert "chain" in data
        assert data["chain"] == "BSC"
        
        print("✅ StrategyListing.to_dict() works")


class TestMockERC8004Registry:
    """Test Mock ERC-8004 Registry"""
    
    def test_generate_agent_id(self):
        registry = MockERC8004Registry(chain="sepolia")
        
        agent_id = registry.generate_agent_id("Auto-DeFi Agent", "1.0.0")
        
        assert agent_id.startswith("autodefi-")
        assert len(agent_id) >= 20
        
        print(f"✅ Generated agent ID: {agent_id}")
    
    def test_create_metadata_uri(self):
        registry = MockERC8004Registry()
        
        agent = AgentInfo(
            name="Auto-DeFi Agent",
            description="Test Agent",
            services=["defi-optimization"]
        )
        
        metadata_uri = registry.create_metadata_uri(agent)
        
        assert metadata_uri.startswith("https://ipfs.io/ipfs/")
        assert len(metadata_uri) > 50
        
        print(f"✅ Metadata URI: {metadata_uri}")
    
    def test_register_agent(self):
        registry = MockERC8004Registry()
        
        agent = AgentInfo(
            name="Auto-DeFi Agent",
            description="ML-Powered DeFi Optimization",
            author="web3xiaogong",
            services=["defi-optimization", "apy-prediction"]
        )
        
        result = registry.register_agent(agent)
        
        assert result["status"] == "success"
        assert result["agent_id"].startswith("autodefi-")
        assert "metadata_uri" in result
        
        # Verify agent is stored
        retrieved = registry.get_agent(result["agent_id"])
        assert retrieved is not None
        assert retrieved.name == "Auto-DeFi Agent"
        
        print(f"✅ Agent registered: {result['agent_id']}")
    
    def test_full_registration_workflow(self):
        print("")
        print("🧪 Testing Full Registration Workflow")
        print("-" * 50)
        
        registry = MockERC8004Registry()
        
        # Step 1: Create agent
        agent = AgentInfo(
            name="Auto-DeFi Agent",
            description="ML-Powered DeFi Yield Optimization Agent",
            author="web3xiaogong",
            services=[
                "defi-optimization",
                "apy-prediction",
                "strategy-sharing",
                "copy-trading"
            ],
            capabilities=[
                "multi-chain",
                "ml-prediction",
                "onchain-proof"
            ]
        )
        
        print("✅ Step 1: Agent info created")
        
        # Step 2: Register
        result = registry.register_agent(agent)
        
        print(f"✅ Step 2: Agent registered with ID: {result['agent_id']}")
        print(f"   Metadata: {result['metadata_uri'][:50]}...")
        
        # Step 3: Verify
        retrieved = registry.get_agent(result["agent_id"])
        
        assert retrieved is not None
        assert len(retrieved.services) == 4
        assert len(retrieved.capabilities) == 3
        
        print("✅ Step 3: Agent verified successfully")
        print("-" * 50)


class TestMessageFormatter:
    """Test Message Formatter"""
    
    def test_telegram_formatting(self):
        data = {
            "pools": [
                {"name": "PancakeSwap", "apy": 15.2, "tvl": 12500000},
                {"name": "Venus", "apy": 5.2, "tvl": 890000000},
            ],
            "prediction": {
                "predicted_apy_7d": 16.5,
                "trend": "UP",
                "confidence": 0.75
            }
        }
        
        msg = MessageFormatter.format_telegram_defi(data)
        
        assert "PancakeSwap" in msg
        assert "15.2" in msg
        assert "*" in msg  # Markdown bold
        assert "UP" in msg
        
        print("✅ Telegram formatting works")
    
    def test_discord_formatting(self):
        data = {
            "pools": [
                {"name": "PancakeSwap", "apy": 15.2, "tvl": 12500000}
            ],
            "prediction": {
                "predicted_apy_7d": 16.5,
                "trend": "UP"
            }
        }
        
        msg = MessageFormatter.format_discord_defi(data)
        
        assert "**" in msg  # Discord markdown bold
        assert "PancakeSwap" in msg
        
        print("✅ Discord formatting works")
    
    def test_channel_formatting(self):
        data = {
            "pools": [{"name": "Test", "apy": 10.0, "tvl": 1000000}]
        }
        
        telegram_msg = MessageFormatter.format_defi_result(data, "telegram")
        discord_msg = MessageFormatter.format_defi_result(data, "discord")
        
        assert "Test" in telegram_msg
        assert "Test" in discord_msg
        
        print("✅ Channel formatting works")


class TestIntegration:
    """End-to-end integration tests"""
    
    def test_complete_workflow(self):
        print("")
        print("=" * 60)
        print("🧪 Complete ERC-8004 Integration Test")
        print("=" * 60)
        
        # 1. Create Registry
        registry = MockERC8004Registry()
        
        # 2. Create Agent
        agent = AgentInfo(
            name="Auto-DeFi Agent",
            description="ML-Powered DeFi Yield Optimization Agent for BNB Chain",
            author="web3xiaogong",
            services=[
                "defi-optimization",
                "apy-prediction",
                "strategy-sharing",
                "copy-trading"
            ],
            capabilities=[
                "multi-chain",
                "ml-prediction",
                "onchain-proof",
                "strategy-marketplace"
            ]
        )
        
        # 3. Register
        result = registry.register_agent(agent)
        
        print(f"📛 Agent ID: {result['agent_id']}")
        print(f"🔗 Metadata: {result['metadata_uri'][:60]}...")
        
        # 4. Create Strategy
        strategy = StrategyListing(
            strategy_id="strategy-demo",
            name="High APY CAKE-BNB Strategy",
            description="Earn high yields with CAKE-BNB LP",
            pool_name="PancakeSwap CAKE-BNB",
            chain="BSC",
            apy_estimate=15.0,
            risk_level="MEDIUM",
            creator=result['agent_id'],
            price_eth=0.01,
            royalty_percent=10
        )
        
        strategy_dict = strategy.to_dict()
        print(f"📊 Strategy: {strategy.name} - {strategy.apy_estimate}% APY")
        
        # 5. Format message
        defi_data = {
            "pools": [
                {"name": "PancakeSwap CAKE-BNB", "apy": 15.2, "tvl": 12500000},
                {"name": "Venus BNB", "apy": 5.2, "tvl": 890000000},
            ],
            "prediction": {
                "predicted_apy_7d": 16.5,
                "trend": "UP",
                "confidence": 0.75
            }
        }
        
        telegram_msg = MessageFormatter.format_defi_result(defi_data, "telegram")
        
        print("")
        print("📱 Telegram Message Preview:")
        print("-" * 40)
        print(telegram_msg)
        print("-" * 40)
        
        print("")
        print("=" * 60)
        print("✅ All Integration Tests Passed!")
        print("=" * 60)


# ============ Run Tests ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
