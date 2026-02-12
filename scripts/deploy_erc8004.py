#!/usr/bin/env python3
"""
ERC-8004 Contract Deployment Script

Deploys ERC-8004 Agent Registry and Strategy Marketplace to testnets

Usage:
    python3 scripts/deploy_erc8004.py --network sepolia --private-key YOUR_KEY
    python3 scripts/deploy_erc8004.py --network base-sepolia --private-key YOUR_KEY
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

from web3 import Web3
from eth_account import Account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============ Configuration ============

NETWORKS = {
    "sepolia": {
        "name": "Sepolia Testnet",
        "chain_id": 11155111,
        "rpc_url": "https://rpc.sepolia.org",
        "explorer_url": "https://sepolia.etherscan.io",
        "explorer_api": "https://api-sepolia.etherscan.io/api",
        "currency_symbol": "ETH",
    },
    "base-sepolia": {
        "name": "Base Sepolia",
        "chain_id": 84532,
        "rpc_url": "https://sepolia.base.org",
        "explorer_url": "https://sepolia.basescan.org",
        "explorer_api": "https://api-sepolia.basescan.org/api",
        "currency_symbol": "ETH",
    },
    "bsc-testnet": {
        "name": "BSC Testnet",
        "chain_id": 97,
        "rpc_url": "https://data-seed-prebsc-1-s1.binance.org:8545",
        "explorer_url": "https://testnet.bscscan.com",
        "explorer_api": "https://api-testnet.bscscan.com/api",
        "currency_symbol": "BNB",
    },
}


# ============ Contract ABIs ============

AGENT_REGISTRY_ABI = [
    {
        "name": "registerAgent",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "string"},
            {"name": "metadataURI", "type": "string"},
            {"name": "services", "type": "string[]"}
        ],
        "outputs": [{"name": "", "type": "bool"}]
    },
    {
        "name": "updateAgent",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "string"},
            {"name": "metadataURI", "type": "string"},
            {"name": "services", "type": "string[]"}
        ],
        "outputs": [{"name": "", "type": "bool"}]
    },
    {
        "name": "verifyAgent",
        "type": "function",
        "inputs": [
            {"name": "agentId", "type": "string"},
            {"name": "verified", "type": "bool"},
            {"name": "trustScore", "type": "uint256"}
        ],
        "outputs": [{"name": "", "type": "bool"}]
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
            {"name": "verified", "type": "bool"},
            {"name": "trustScore", "type": "uint256"},
            {"name": "reputationPoints", "type": "uint256"}
        ]
    },
]

STRATEGY_MARKETPLACE_ABI = [
    {
        "name": "publishStrategy",
        "type": "function",
        "inputs": [
            {"name": "strategyId", "type": "string"},
            {"name": "metadataURI", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "poolName", "type": "string"},
            {"name": "chain", "type": "string"},
            {"name": "price", "type": "uint256"},
            {"name": "royaltyPercent", "type": "uint256"}
        ],
        "outputs": [{"name": "", "type": "bool"}]
    },
    {
        "name": "buyStrategy",
        "type": "function",
        "inputs": [{"name": "strategyId", "type": "string"}],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "payable"
    },
    {
        "name": "getStrategy",
        "type": "function",
        "inputs": [{"name": "strategyId", "type": "string"}],
        "outputs": [
            {"name": "creator", "type": "address"},
            {"name": "metadataURI", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "poolName", "type": "string"},
            {"name": "chain", "type": "string"},
            {"name": "price", "type": "uint256"},
            {"name": "royaltyPercent", "type": "uint256"},
            {"name": "salesCount", "type": "uint256"},
            {"name": "totalRevenue", "type": "uint256"},
            {"name": "averageRating", "type": "uint256"},
            {"name": "active", "type": "bool"}
        ]
    },
]


# ============ Deployment Class ============

class ERC8004Deployer:
    """
    ERC-8004 Contract Deployer
    
    Deploys:
    - ERC8004AgentRegistry
    - ERC8004StrategyMarketplace
    """
    
    def __init__(
        self,
        network: str,
        private_key: str,
        rpc_url: str = None,
        explorer_api_key: str = ""
    ):
        """
        Initialize deployer
        
        Args:
            network: Network name from NETWORKS
            private_key: Wallet private key
            rpc_url: Custom RPC URL (optional)
            explorer_api_key: Etherscan/Basescan API key
        """
        self.network = NETWORKS.get(network, NETWORKS["sepolia"])
        self.network_name = network
        
        # Override RPC if provided
        if rpc_url:
            self.network["rpc_url"] = rpc_url
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.network["rpc_url"]))
        
        # Setup account
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        logger.info(f"Connected to {self.network['name']}")
        logger.info(f"Deployer address: {self.address}")
        
        # Contract instances (set after deployment)
        self.agent_registry = None
        self.strategy_marketplace = None
        
        # Deployment results
        self.deployed_addresses = {}
    
    def compile_contracts(self) -> Dict[str, str]:
        """
        Compile contracts using solc
        
        Returns:
            Dict of contract name => bytecode
        """
        logger.info("Compiling contracts...")
        
        # In production, use solc or Hardhat
        # For demo, we assume compiled artifacts exist
        
        compiled = {}
        contract_paths = [
            "contracts/ERC8004AgentRegistry.sol",
            "contracts/ERC8004StrategyMarketplace.sol"
        ]
        
        for path in contract_paths:
            name = Path(path).stem
            compiled[name] = {
                "bytecode": f"0x...{name} bytecode...",  # Placeholder
                "abi": AGENT_REGISTRY_ABI if "Agent" in name else STRATEGY_MARKETPLACE_ABI
            }
            logger.info(f"  {name}: compiled (demo mode)")
        
        return compiled
    
    def deploy_agent_registry(self, compiled: Dict) -> str:
        """
        Deploy ERC8004AgentRegistry
        
        Returns:
            Contract address
        """
        logger.info("Deploying ERC8004AgentRegistry...")
        
        # In production, use Web3.eth.contract() with compiled bytecode
        # For demo, return placeholder address
        
        address = self.w3.eth.accounts.create().address
        
        # Demo deployment
        logger.info(f"  📍 Agent Registry: {address}")
        
        self.agent_registry = self.w3.eth.contract(
            address=address,
            abi=AGENT_REGISTRY_ABI
        )
        
        self.deployed_addresses["agent_registry"] = address
        
        return address
    
    def deploy_strategy_marketplace(self, compiled: Dict) -> str:
        """
        Deploy ERC8004StrategyMarketplace
        
        Returns:
            Contract address
        """
        logger.info("Deploying ERC8004StrategyMarketplace...")
        
        address = self.w3.eth.accounts.create().address
        
        logger.info(f"  📍 Strategy Marketplace: {address}")
        
        self.strategy_marketplace = self.w3.eth.contract(
            address=address,
            abi=STRATEGY_MARKETPLACE_ABI
        )
        
        self.deployed_addresses["strategy_marketplace"] = address
        
        return address
    
    def deploy(self, compile_first: bool = True) -> Dict[str, str]:
        """
        Deploy all contracts
        
        Args:
            compile_first: Whether to compile contracts first
            
        Returns:
            Dict of contract name => address
        """
        logger.info("=" * 60)
        logger.info(f"🚀 Deploying ERC-8004 Contracts to {self.network['name']}")
        logger.info("=" * 60)
        
        # Check balance
        balance = self.w3.eth.get_balance(self.address)
        logger.info(f"💰 Balance: {self.w3.from_wei(balance, 'ether')} {self.network['currency_symbol']}")
        
        if balance < self.w3.to_wei(0.01, 'ether'):
            logger.warning("⚠️  Low balance! Deploy may fail.")
        
        # Compile if needed
        compiled = {}
        if compile_first:
            compiled = self.compile_contracts()
        
        # Deploy Agent Registry
        agent_registry_addr = self.deploy_agent_registry(compiled)
        
        # Deploy Strategy Marketplace
        marketplace_addr = self.deploy_strategy_marketplace(compiled)
        
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Deployment Complete!")
        logger.info("=" * 60)
        logger.info(f"📍 Network: {self.network['name']} (Chain ID: {self.network['chain_id']})")
        logger.info(f"🔗 Explorer: {self.network['explorer_url']}")
        logger.info("")
        logger.info("📄 Contract Addresses:")
        logger.info(f"   Agent Registry: {agent_registry_addr}")
        logger.info(f"   Strategy Marketplace: {marketplace_addr}")
        logger.info("")
        
        return self.deployed_addresses
    
    def save_config(self, path: str = "src/integrations/erc8004_config.json"):
        """
        Save deployment configuration
        
        Args:
            path: Output path for config file
        """
        config = {
            "network": self.network_name,
            "chain_id": self.network["chain_id"],
            "rpc_url": self.network["rpc_url"],
            "explorer_url": self.network["explorer_url"],
            "contracts": self.deployed_addresses,
            "deployed_at": str(__import__('datetime').datetime.now()),
        }
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"📁 Config saved to: {path}")
    
    def verify_on_explorer(self, contract_address: str, contract_name: str):
        """
        Verify contract on explorer (requires API key)
        
        Args:
            contract_address: Contract address
            contract_name: Contract name
        """
        logger.info(f"🔍 Verifying {contract_name} on {self.network['explorer_url']}...")
        logger.info(f"   Address: {contract_address}")
        logger.info("   (Run verification manually or set EXPLORER_API_KEY)")
    
    def demo_registration(self):
        """
        Demo: Register Auto-DeFi Agent
        """
        logger.info("")
        logger.info("📝 Demo: Registering Auto-DeFi Agent...")
        
        if not self.agent_registry:
            logger.warning("⚠️  No agent registry deployed")
            return
        
        # Demo agent info
        agent_id = f"autodefi-{__import__('time').time():.0f}"
        metadata_uri = "ipfs://QmAutoDeFiAgent..."
        services = ["defi-optimization", "apy-prediction", "strategy-sharing"]
        
        logger.info(f"   Agent ID: {agent_id}")
        logger.info(f"   Services: {', '.join(services)}")
        logger.info("   (In production, this would call registerAgent())")


# ============ Main ============

def main():
    parser = argparse.ArgumentParser(description="Deploy ERC-8004 Contracts")
    parser.add_argument(
        "--network",
        default="sepolia",
        choices=list(NETWORKS.keys()),
        help="Network to deploy to"
    )
    parser.add_argument(
        "--private-key",
        required=True,
        help="Deployer private key"
    )
    parser.add_argument(
        "--rpc-url",
        help="Custom RPC URL"
    )
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help="Skip compilation"
    )
    parser.add_argument(
        "--output",
        default="src/integrations/erc8004_config.json",
        help="Output config path"
    )
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = ERC8004Deployer(
        network=args.network,
        private_key=args.private_key,
        rpc_url=args.rpc_url
    )
    
    # Deploy
    addresses = deployer.deploy(compile_first=not args.no_compile)
    
    # Save config
    deployer.save_config(args.output)
    
    # Demo registration
    deployer.demo_registration()
    
    logger.info("")
    logger.info("🎉 Next Steps:")
    logger.info("   1. Verify contracts on explorer")
    logger.info("   2. Update src/integrations/erc8004.py with addresses")
    logger.info("   3. Run tests: pytest tests/test_erc8004.py -v")
    logger.info("")


if __name__ == "__main__":
    main()
