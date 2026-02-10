"""
Auto-DeFi Agent Core
Main agent logic for DeFi yield optimization
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AgentState(Enum):
    """Agent execution state"""
    IDLE = "idle"
    MONITORING = "monitoring"
    EXECUTING = "executing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class StrategyConfig:
    """Strategy configuration"""
    min_apy: float = 5.0  # Minimum APY to consider
    max_slippage: float = 1.0  # Maximum slippage %
    gas_threshold_usd: float = 10.0  # Max gas cost in USD
    check_interval_seconds: int = 300  # 5 minutes
    auto_execute: bool = False  # Require manual approval
    risk_level: RiskLevel = RiskLevel.MEDIUM


@dataclass
class Opportunity:
    """Yield opportunity"""
    pool_name: str
    protocol: str
    chain: str
    apy: float
    tvl: float
    token_pair: str
    contract_address: str
    confidence: float = 0.0  # 0-1 confidence score
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Transaction:
    """Transaction record"""
    tx_hash: str
    action: str
    from_token: str
    to_token: str
    amount_usd: float
    gas_used: float
    status: str
    timestamp: datetime = field(default_factory=datetime.now)


class AutoDeFiAgent:
    """
    Auto-DeFi Agent for BSC/opBNB
    
    Monitors DeFi opportunities and executes yield optimization strategies
    """
    
    def __init__(
        self,
        config: StrategyConfig = None,
        wallet_address: str = None,
        log_level: int = logging.INFO
    ):
        """
        Initialize the Auto-DeFi Agent
        
        Args:
            config: Strategy configuration
            wallet_address: Wallet address for tracking
            log_level: Logging level
        """
        self.config = config or StrategyConfig()
        self.wallet_address = wallet_address
        
        # Setup logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("AutoDeFiAgent")
        
        # State
        self.state = AgentState.IDLE
        self.opportunities: List[Opportunity] = []
        self.transactions: List[Transaction] = []
        self.last_check: Optional[datetime] = None
        self.running = False
        
        # Performance tracking
        self.metrics = {
            "checks": 0,
            "opportunities_found": 0,
            "executed": 0,
            "errors": 0,
            "total_profit_usd": 0.0
        }
    
    def start(self):
        """Start the agent"""
        if self.running:
            self.logger.warning("Agent is already running")
            return
        
        self.running = True
        self.state = AgentState.IDLE
        self.logger.info("Auto-DeFi Agent started")
        self.logger.info(f"Config: min_apy={self.config.min_apy}%, "
                        f"auto_execute={self.config.auto_execute}")
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        self.state = AgentState.STOPPED
        self.logger.info("Auto-DeFi Agent stopped")
        self.logger.info(f"Metrics: {self.metrics}")
    
    def scan_opportunities(self, pools: List) -> List[Opportunity]:
        """
        Scan for yield opportunities
        
        Args:
            pools: List of DeFi pools from DeFi service
            
        Returns:
            List of Opportunity objects
        """
        self.logger.info(f"Scanning {len(pools)} pools for opportunities...")
        
        opportunities = []
        
        for pool in pools:
            # Skip if APY below threshold
            if pool.apy < self.config.min_apy:
                continue
            
            # Skip if TVL too low
            if pool.tvl < 10000:  # $10k minimum
                continue
            
            # Calculate confidence based on TVL and APY
            confidence = min(1.0, (pool.tvl / 1000000) * 0.5 + (pool.apy / 100) * 0.5)
            
            opp = Opportunity(
                pool_name=pool.name,
                protocol=pool.protocol,
                chain=pool.chain,
                apy=pool.apy,
                tvl=pool.tvl,
                token_pair=f"{pool.token0}/{pool.token1}",
                contract_address=pool.pool_address,
                confidence=confidence
            )
            
            opportunities.append(opp)
        
        # Sort by APY
        opportunities.sort(key=lambda x: x.apy, reverse=True)
        
        self.opportunities = opportunities
        self.metrics["checks"] += 1
        self.metrics["opportunities_found"] += len(opportunities)
        
        self.logger.info(f"Found {len(opportunities)} opportunities")
        
        return opportunities
    
    def get_best_opportunity(self) -> Optional[Opportunity]:
        """
        Get the best yield opportunity
        
        Returns:
            Highest APY opportunity or None
        """
        if not self.opportunities:
            return None
        
        return self.opportunities[0]
    
    def analyze_risk(self, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Analyze risk of an opportunity
        
        Args:
            opportunity: Opportunity to analyze
            
        Returns:
            Risk analysis dictionary
        """
        score = 0.0
        factors = []
        
        # TVL factor (higher TVL = lower risk)
        if opportunity.tvl >= 1000000:
            factors.append(("TVL", "Low", "+0.3"))
            score += 0.3
        elif opportunity.tvl >= 100000:
            factors.append(("TVL", "Medium", "+0.2"))
            score += 0.2
        else:
            factors.append(("TVL", "High", "+0.0"))
        
        # APY factor (extreme APY = higher risk)
        if opportunity.apy >= 100:
            factors.append(("APY", "High Risk", "-0.2"))
            score -= 0.2
        elif opportunity.apy >= 50:
            factors.append(("APY", "Medium", "-0.1"))
            score -= 0.1
        else:
            factors.append(("APY", "Low", "+0.1"))
            score += 0.1
        
        # Protocol factor (known protocols = lower risk)
        known_protocols = ["pancakeswap", "venus", "alpaca"]
        if any(p.lower() in opportunity.protocol.lower() for p in known_protocols):
            factors.append(("Protocol", "Known", "+0.2"))
            score += 0.2
        else:
            factors.append(("Protocol", "Unknown", "-0.1"))
            score -= 0.1
        
        # Normalize score
        score = max(0.0, min(1.0, score))
        
        # Determine risk level
        if score >= 0.7:
            risk = "LOW"
        elif score >= 0.4:
            risk = "MEDIUM"
        else:
            risk = "HIGH"
        
        return {
            "opportunity": opportunity.pool_name,
            "score": score,
            "risk_level": risk,
            "factors": factors,
            "recommendation": "EXECUTE" if score >= 0.5 else "WAIT"
        }
    
    def generate_strategy(self) -> Dict[str, Any]:
        """
        Generate current strategy based on market conditions
        
        Returns:
            Strategy recommendation
        """
        if not self.opportunities:
            return {"status": "NO_OPPORTUNITIES"}
        
        best = self.get_best_opportunity()
        risk_analysis = self.analyze_risk(best)
        
        strategy = {
            "timestamp": datetime.now().isoformat(),
            "best_opportunity": {
                "name": best.pool_name,
                "protocol": best.protocol,
                "chain": best.chain,
                "apy": f"{best.apy:.2f}%",
                "tvl": f"${best.tvl:,.0f}",
                "confidence": f"{best.confidence:.1%}"
            },
            "risk_analysis": risk_analysis,
            "recommendation": risk_analysis["recommendation"],
            "next_action": "SCAN" if risk_analysis["recommendation"] == "WAIT" else "EXECUTE"
        }
        
        return strategy
    
    def execute_strategy(self, opportunity: Opportunity) -> Optional[Transaction]:
        """
        Execute a yield strategy
        
        Args:
            opportunity: Opportunity to execute
            
        Returns:
            Transaction record or None
        """
        if not self.config.auto_execute:
            self.logger.info("Auto-execute disabled. Manual approval required.")
            return None
        
        self.logger.info(f"Executing strategy for {opportunity.pool_name}")
        self.state = AgentState.EXECUTING
        
        # Simulate transaction (in real implementation, call BSC adapter)
        tx = Transaction(
            tx_hash="0x" + "".join(["%02x" % 0 for _ in range(32)]),
            action="SWAP",
            from_token=opportunity.token_pair.split("/")[0],
            to_token=opportunity.token_pair.split("/")[1],
            amount_usd=100.0,  # Example amount
            gas_used=0.5,  # Example gas in BNB
            status="PENDING"
        )
        
        self.transactions.append(tx)
        self.metrics["executed"] += 1
        
        self.state = AgentState.IDLE
        self.logger.info(f"Transaction submitted: {tx.tx_hash}")
        
        return tx
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status
        
        Returns:
            Status dictionary
        """
        return {
            "state": self.state.value,
            "running": self.running,
            "opportunities_count": len(self.opportunities),
            "transactions_count": len(self.transactions),
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "metrics": self.metrics
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export agent state as dictionary"""
        return {
            "state": self.state.value,
            "config": {
                "min_apy": self.config.min_apy,
                "max_slippage": self.config.max_slippage,
                "auto_execute": self.config.auto_execute,
                "risk_level": self.config.risk_level.value
            },
            "opportunities": [
                {
                    "pool": o.pool_name,
                    "apy": o.apy,
                    "tvl": o.tvl,
                    "confidence": o.confidence
                }
                for o in self.opportunities[:10]
            ],
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_state(self, filepath: str = "agent_state.json"):
        """Save agent state to file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        self.logger.info(f"State saved to {filepath}")
    
    def load_state(self, filepath: str = "agent_state.json"):
        """Load agent state from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.metrics = data.get("metrics", {})
            self.logger.info(f"State loaded from {filepath}")
        except FileNotFoundError:
            self.logger.warning(f"State file {filepath} not found")


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = AutoDeFiAgent(
        config=StrategyConfig(
            min_apy=10.0,
            auto_execute=False
        )
    )
    
    # Start
    agent.start()
    
    # Get status
    print(json.dumps(agent.get_status(), indent=2, default=str))
    
    # Stop
    agent.stop()
