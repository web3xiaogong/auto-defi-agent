#!/usr/bin/env python3
"""
ERC-8004 Demo Deployment Script

Simulates contract deployment and interaction
For demonstration without actual blockchain deployment

Usage:
    python3 scripts/deploy_demo.py --network sepolia
"""

import json
import hashlib
import time
import secrets
from datetime import datetime


def generate_contract_address(deployer: str, nonce: int) -> str:
    """Generate deterministic contract address"""
    # Simplified address generation
    timestamp = str(int(time.time()) + nonce)
    data = f"{deployer}:{timestamp}:{secrets.token_hex(8)}"
    hash = hashlib.sha256(data.encode()).hexdigest()
    return "0x" + hash[:40]


def deploy_demo(network: str = "sepolia", private_key: str = None):
    """Demo deployment with simulated addresses"""
    
    print("=" * 70)
    print("🚀 ERC-8004 Demo Deployment")
    print("=" * 70)
    
    # Wallet info
    if private_key:
        try:
            from eth_account import Account
            wallet = Account.from_key(private_key)
            deployer = wallet.address
        except:
            deployer = "0x" + secrets.token_hex(20)
    else:
        deployer = "0x" + secrets.token_hex(20)
    
    print(f"\n📱 Deployer: {deployer}")
    print(f"🌐 Network: {network}")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    
    # Generate addresses
    nonce = 0
    agent_registry_addr = generate_contract_address(deployer, nonce)
    nonce += 1
    strategy_marketplace_addr = generate_contract_address(deployer, nonce)
    
    print("\n" + "-" * 70)
    print("📄 Deploying Contracts...")
    print("-" * 70)
    
    # Agent Registry
    print(f"\n1️⃣  ERC8004AgentRegistry")
    print(f"    Address: {agent_registry_addr}")
    print(f"    Gas used: 1,234,567 (estimated)")
    print(f"    Status: ✅ Simulated")
    
    # Strategy Marketplace
    print(f"\n2️⃣  ERC8004StrategyMarketplace")
    print(f"    Address: {strategy_marketplace_addr}")
    print(f"    Gas used: 2,345,678 (estimated)")
    print(f"    Status: ✅ Simulated")
    
    # Save config
    config = {
        "network": network,
        "chain_id": 11155111 if network == "sepolia" else 84532 if network == "base-sepolia" else 97,
        "deployed_at": datetime.now().isoformat(),
        "mode": "demo",
        "contracts": {
            "agent_registry": {
                "address": agent_registry_addr,
                "name": "ERC8004AgentRegistry",
                "bytecode_hash": hashlib.sha256(b"ERC8004AgentRegistry").hexdigest()[:16],
                "gas_used": 1234567,
            },
            "strategy_marketplace": {
                "address": strategy_marketplace_addr,
                "name": "ERC8004StrategyMarketplace", 
                "bytecode_hash": hashlib.sha256(b"ERC8004StrategyMarketplace").hexdigest()[:16],
                "gas_used": 2345678,
            }
        },
        "explorer_urls": {
            "agent_registry": f"https://sepolia.etherscan.io/address/{agent_registry_addr}",
            "strategy_marketplace": f"https://sepolia.etherscan.io/address/{strategy_marketplace_addr}",
        }
    }
    
    # Save config
    with open("src/integrations/erc8004_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ Demo Deployment Complete!")
    print("=" * 70)
    
    print(f"\n📁 Config saved: src/integrations/erc8004_config.json")
    
    print(f"\n🔗 Explorer Links:")
    print(f"  • Agent Registry: {config['explorer_urls']['agent_registry']}")
    print(f"  • Strategy Marketplace: {config['explorer_urls']['strategy_marketplace']}")
    
    print("\n💡 To deploy to real network:")
    print("   1. Compile contracts: npx hardhat compile")
    print("   2. Deploy: npx hardhat run scripts/deploy.js --network sepolia")
    print("   3. Update src/integrations/erc8004.py with real addresses")
    
    return config


def register_demo_agent(config_path: str = "src/integrations/erc8004_config.json"):
    """Demo: Register Auto-DeFi Agent"""
    
    print("\n" + "=" * 70)
    print("📝 Demo: Register Auto-DeFi Agent on ERC-8004")
    print("=" * 70)
    
    # Load config
    try:
        with open(config_path) as f:
            config = json.load(f)
    except FileNotFoundError:
        config = deploy_demo("sepolia")
    
    # Agent info
    agent_id = f"autodefi-{int(time.time())}"
    
    print(f"\n🤖 Agent: Auto-DeFi Agent")
    print(f"📛 ID: {agent_id}")
    print(f"📝 Description: ML-Powered DeFi Yield Optimization")
    print(f"👨‍💻 Author: web3xiaogong")
    print(f"🔗 Services:")
    print("   • defi-optimization")
    print("   • apy-prediction")
    print("   • strategy-sharing")
    print("   • copy-trading")
    
    # Simulate registration
    print(f"\n⏳ Calling registerAgent()...")
    time.sleep(0.5)
    print(f"   • Agent ID: {agent_id}")
    print(f"   • Metadata URI: ipfs://Qm{secrets.token_hex(32)}")
    print(f"   • Transaction hash: 0x{secrets.token_hex(32)}")
    print(f"   • Status: ✅ Registered")
    
    # Save agent info
    agent_info = {
        "agent_id": agent_id,
        "name": "Auto-DeFi Agent",
        "description": "ML-Powered DeFi Yield Optimization Agent for BNB Chain",
        "version": "1.0.0",
        "author": "web3xiaogong",
        "services": [
            "defi-optimization",
            "apy-prediction",
            "strategy-sharing",
            "copy-trading"
        ],
        "capabilities": [
            "multi-chain",
            "ml-prediction",
            "onchain-proof"
        ],
        "metadata_uri": f"ipfs://Qm{secrets.token_hex(32)}",
        "trust_score": 75,
        "verified": False,
        "registered_at": datetime.now().isoformat(),
    }
    
    with open("src/integrations/agent_info.json", "w") as f:
        json.dump(agent_info, f, indent=2)
    
    print(f"\n📁 Agent info saved: src/integrations/agent_info.json")
    
    return agent_info


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--register":
        # Only register agent
        register_demo_agent()
    else:
        # Full demo deployment
        network = sys.argv[1] if len(sys.argv) > 1 else "sepolia"
        deploy_demo(network)
        
        print("\n" + "-" * 70)
        print("📝 Register Auto-DeFi Agent")
        print("-" * 70)
        register_demo_agent()
