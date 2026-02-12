"""
ERC-8004 Agent Registry Integration

Good Vibes Only: OpenClaw Edition Hackathon

Features:
- Register autonomous AI agents on ERC-8004
- Publish strategies to marketplace
- Agent discovery and verification
"""

import json
import hashlib
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from eth_typing import Address
from web3 import Web3
import logging

logger = logging.getLogger(__name__)


# ============== ERC-8004 Contract ABIs ==============

AGENT_REGISTRY_ABI = [
    {
        "name": "registerAgent",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "string"},
            {"name": "metadataURI", "type": "string"},
            {"name": "services", "type": "string[]"}
        ],
        "outputs": []
    },
    {
        "name": "updateAgent",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "string"},
            {"name": "metadataURI", "type": "string"},
            {"name": "services", "type": "string[]"}
        ],
        "outputs": []
    },
    {
        "name": "getAgent",
        "type": "function",
        "inputs": [{"name": "agentId", "type": "string"}],
        "outputs": [
            {"name": "owner", "type": "address"},
            {"name": "metadataURI", "type": "string"},
            {"name": "services", "type": "string[]"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "verified", "type": "bool"}
        ]
    },
    {
        "name": "verifyAgent",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "string"},
            {"name": "verified", "type": "bool"}
        ],
        "outputs": []
    },
    {
        "name": "getAllAgents",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "", "type": "string[]"}]
    },
    {
        "name": "agentCount",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}]
    }
]

STRATEGY_MARKETPLACE_ABI = [
    {
        "name": "publishStrategy",
        "type": "function",
        "inputs": [
            {"name": "strategyId", "type": "string"},
            {"name": "metadataURI", "type": "string"},
            {"name": "price", "type": "uint256"},
            {"name": " royaltyPercent", "type": "uint256"}
        ],
        "outputs": []
    },
    {
        "name": "buyStrategy",
        "type": "function",
        "inputs": [{"name": "strategyId", "type": "string"}],
        "outputs": []
    },
    {
        "name": "getStrategy",
        "type": "function",
        "inputs": [{"name": "strategyId", "type": "string"}],
        "outputs": [
            {"name": "creator", "type": "address"},
            {"name": "metadataURI", "type": "string"},
            {"name": "price", "type": "uint256"},
            {"name": "salesCount", "type": "uint256"}
        ]
    },
    {
        "name": "getStrategiesByCreator",
        "type": "function",
        "inputs": [{"name": "creator", "type": "address"}],
        "outputs": [{"name": "", "type": "string[]"}]
    }
]


# ============== Data Classes ==============

@dataclass
class AgentInfo:
    """Agent information for ERC-8004 registration"""
    agent_id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    services: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    trust_score: float = 0.0
    verified: bool = False
    created_at: int = 0
    metadata_uri: str = ""
    
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
    strategy_id: str
    name: str
    description: str
    pool_name: str
    chain: str
    apy_estimate: float
    risk_level: str  # LOW, MEDIUM, HIGH
    creator: str
    price_eth: float
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


# ============== ERC-8004 Registry ==============

class ERC8004Registry:
    """
    ERC-8004 Agent Registry Integration
    
    Features:
    - Register AI agents on ERC-8004
    - Update agent metadata
    - Verify agent authenticity
    - Discover agents
    """
    
    # Official ERC-8004 Contracts (example addresses)
    CONTRACTS = {
        "base": {
            "agent_registry": "0x...",  # TBD when mainnet deployed
            "strategy_marketplace": "0x..."
        },
        "sepolia": {
            "agent_registry": "0x...",  # Testnet address
            "strategy_marketplace": "0x..."
        }
    }
    
    def __init__(
        self, 
        rpc_url: str, 
        private_key: str = None,
        chain: str = "base"
    ):
        """
        Initialize ERC-8004 Registry
        
        Args:
            rpc_url: RPC endpoint
            private_key: Wallet private key (for transactions)
            chain: Network (base, sepolia)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.address = None
            self.account = None
        
        self.chain = chain
        self.contracts = self.CONTRACTS.get(chain, self.CONTRACTS["sepolia"])
        
        # Initialize contract instances
        self.agent_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contracts["agent_registry"]),
            abi=AGENT_REGISTRY_ABI
        )
        
        logger.info(f"ERC-8004 Registry initialized on {chain}")
    
    def generate_agent_id(self, name: str, version: str = "1.0.0") -> str:
        """
        Generate unique agent ID
        
        Args:
            name: Agent name
            version: Agent version
            
        Returns:
            Unique agent ID (hash-based)
        """
        timestamp = str(int(time.time()))
        data = f"{name}:{version}:{timestamp}"
        return f"autodefi-{hashlib.sha256(data.encode()).hexdigest()[:16]}"
    
    def create_metadata_uri(self, agent_info: AgentInfo, ipfs_gateway: str = "https://ipfs.io/ipfs/") -> str:
        """
        Create metadata URI for agent
        
        In production, this would upload to IPFS
        For demo, we use local JSON
        """
        metadata = agent_info.to_dict()
        metadata_json = json.dumps(metadata, indent=2)
        
        # TODO: Upload to IPFS
        # For demo, return local hash
        metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        
        return f"{ipfs_gateway}{metadata_hash}"
    
    def register_agent(self, agent_info: AgentInfo) -> Dict:
        """
        Register agent on ERC-8004
        
        Args:
            agent_info: Agent information
            
        Returns:
            Transaction receipt
        """
        if not self.account:
            raise ValueError("Private key required for registration")
        
        # Generate agent ID
        agent_id = self.generate_agent_id(agent_info.name, agent_info.version)
        agent_info.agent_id = agent_id
        agent_info.created_at = int(time.time())
        
        # Create metadata
        metadata_uri = self.create_metadata_uri(agent_info)
        
        # Build transaction
        txn = self.agent_registry.functions.registerAgent(
            agent_id,
            metadata_uri,
            agent_info.services
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 500000,
            "gasPrice": self.w3.eth.gas_price
        })
        
        # Sign and send
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        logger.info(f"Agent registered: {agent_id}")
        
        return {
            "status": "pending",
            "agent_id": agent_id,
            "tx_hash": tx_hash.hex(),
            "metadata_uri": metadata_uri
        }
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """
        Get agent information from registry
        
        Args:
            agent_id: Agent ID
            
        Returns:
            AgentInfo or None
        """
        try:
            result = self.agent_registry.functions.getAgent(agent_id).call()
            
            return AgentInfo(
                agent_id=agent_id,
                name=result[0],  # metadata is first
                description="",  # Parse from metadata
                owner=result[0],
                services=list(result[1]) if isinstance(result[1], (list, tuple)) else [],
                verified=result[4],
                created_at=result[3]
            )
        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None
    
    def get_all_agents(self) -> List[str]:
        """Get all registered agent IDs"""
        try:
            return self.agent_registry.functions.getAllAgents().call()
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []
    
    def verify_agent(self, agent_id: str, verified: bool = True) -> str:
        """
        Verify or unverify an agent
        
        Args:
            agent_id: Agent ID
            verified: Verification status
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Private key required")
        
        txn = self.agent_registry.functions.verifyAgent(
            agent_id, verified
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 100000,
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        return tx_hash.hex()


# ============== Strategy Marketplace ==============

class StrategyMarketplace:
    """
    ERC-8004 Strategy Marketplace
    
    Features:
    - Publish strategies for sale
    - Buy strategies
    - Track sales and royalties
    """
    
    def __init__(
        self,
        rpc_url: str,
        private_key: str = None,
        chain: str = "base"
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.address = None
            self.account = None
        
        self.chain = chain
        
        # Contract address (placeholder)
        self.contract_address = ERC8004Registry.CONTRACTS.get(chain, {}).get(
            "strategy_marketplace", "0x..."
        )
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=STRATEGY_MARKETPLACE_ABI
        )
    
    def generate_strategy_id(self, name: str, creator: str) -> str:
        """Generate unique strategy ID"""
        timestamp = str(int(time.time()))
        data = f"{name}:{creator}:{timestamp}"
        return f"strategy-{hashlib.sha256(data.encode()).hexdigest()[:16]}"
    
    def publish_strategy(
        self,
        listing: StrategyListing
    ) -> Dict:
        """
        Publish strategy to marketplace
        
        Args:
            listing: Strategy listing information
            
        Returns:
            Transaction receipt
        """
        if not self.account:
            raise ValueError("Private key required")
        
        strategy_id = self.generate_strategy_id(listing.name, self.address)
        listing.strategy_id = strategy_id
        
        # Convert price to wei
        price_wei = int(listing.price_eth * 10**18)
        
        # Build transaction
        txn = self.contract.functions.publishStrategy(
            strategy_id,
            listing.metadata_uri or f"ipfs://{strategy_id}",
            price_wei,
            listing.royalty_percent
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 300000,
            "gasPrice": self.w3.eth.gas_price
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        logger.info(f"Strategy published: {strategy_id}")
        
        return {
            "status": "pending",
            "strategy_id": strategy_id,
            "tx_hash": tx_hash.hex(),
            "price_eth": listing.price_eth
        }
    
    def buy_strategy(self, strategy_id: str, value_eth: float) -> str:
        """
        Buy a strategy from marketplace
        
        Args:
            strategy_id: Strategy ID
            value_eth: Payment amount in ETH
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("Private key required")
        
        value_wei = int(value_eth * 10**18)
        
        txn = self.contract.functions.buyStrategy(strategy_id).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "gas": 300000,
            "gasPrice": self.w3.eth.gas_price,
            "value": value_wei
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        
        return tx_hash.hex()
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyListing]:
        """Get strategy details"""
        try:
            result = self.contract.functions.getStrategy(strategy_id).call()
            
            return StrategyListing(
                strategy_id=strategy_id,
                name="",  # Parse from metadata
                description="",
                pool_name="",
                chain=self.chain,
                apy_estimate=0.0,
                risk_level="MEDIUM",
                creator=result[0],
                price_eth=float(result[2]) / 10**18,
                sales_count=result[3]
            )
        except Exception as e:
            logger.error(f"Failed to get strategy: {e}")
            return None


# ============== Demo ==============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Demo registration
    registry = ERC8004Registry(
        rpc_url="https://base.public.blastapi.io",
        chain="base"
    )
    
    # Create agent info
    agent = AgentInfo(
        name="Auto-DeFi Agent",
        description="ML-Powered DeFi Yield Optimization Agent for BNB Chain",
        author="web3xiaogong",
        services=["defi-optimization", "apy-prediction", "strategy-sharing", "copy-trading"],
        capabilities=["multi-chain", "ml-prediction", "onchain-proof", "strategy-marketplace"]
    )
    
    print("=" * 60)
    print("🤖 ERC-8004 Agent Registry Demo")
    print("=" * 60)
    
    # Generate agent ID
    agent_id = registry.generate_agent_id(agent.name)
    print(f"\n📛 Agent ID: {agent_id}")
    
    # Generate metadata URI
    metadata_uri = registry.create_metadata_uri(agent)
    print(f"🔗 Metadata URI: {metadata_uri}")
    
    print("\n💡 To register on mainnet:")
    print("   1. Deploy ERC-8004 contracts")
    print("   2. Set private key")
    print("   3. Call register_agent()")
    
    print("\n✅ Demo complete!")
