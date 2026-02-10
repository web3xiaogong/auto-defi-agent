#!/usr/bin/env python3
"""
Auto-DeFi Agent - Main Entry Point
Smart DeFi Yield Optimization Assistant for BNB Chain

Good Vibes Only: OpenClaw Edition Hackathon
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, get_config
from tools.defi_service import DeFiService
from agents.strategy_agent import AutoDeFiAgent, StrategyConfig


def setup_logging(log_file: str = None, level: int = logging.INFO):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )


def main():
    """Main entry point"""
    # Load configuration
    config = get_config()
    
    # Setup logging
    setup_logging(
        log_file=config.logging.file,
        level=getattr(logging, config.logging.level.upper(), logging.INFO)
    )
    
    logger = logging.getLogger("AutoDeFiAgent")
    
    # Welcome message
    logger.info("=" * 60)
    logger.info("Auto-DeFi Agent - BNB Chain Hackathon")
    logger.info("Good Vibes Only: OpenClaw Edition")
    logger.info("=" * 60)
    
    try:
        # Initialize services
        logger.info("Initializing DeFi Service...")
        defi_service = DeFiService()
        
        logger.info("Initializing Agent...")
        strategy_config = StrategyConfig(
            min_apy=config.agent.min_transaction_value,
            max_slippage=config.agent.max_slippage,
            auto_execute=False  # Require manual approval
        )
        
        agent = AutoDeFiAgent(
            config=strategy_config,
            wallet_address=config.wallet.address
        )
        
        # Start agent
        agent.start()
        
        # Main loop
        logger.info("Starting main monitoring loop...")
        
        # Check pools
        logger.info("Fetching BSC pools...")
        pools = defi_service.get_bsc_pancake_pools()
        logger.info(f"Found {len(pools)} pools")
        
        if pools:
            # Scan for opportunities
            opportunities = agent.scan_opportunities(pools)
            
            # Get strategy
            strategy = agent.generate_strategy()
            
            # Display results
            logger.info("\n" + "=" * 40)
            logger.info("STRATEGY RECOMMENDATION")
            logger.info("=" * 40)
            
            print("\n" + json.dumps(strategy, indent=2, default=str))
            
            # Get best opportunity
            best = agent.get_best_opportunity()
            if best:
                risk = agent.analyze_risk(best)
                logger.info(f"\nBest Opportunity: {best.pool_name}")
                logger.info(f"  APY: {best.apy:.2f}%")
                logger.info(f"  TVL: ${best.tvl:,.0f}")
                logger.info(f"  Risk: {risk['risk_level']}")
                logger.info(f"  Recommendation: {risk['recommendation']}")
        
        # Display status
        logger.info("\n" + "=" * 40)
        logger.info("AGENT STATUS")
        logger.info("=" * 40)
        status = agent.get_status()
        print(json.dumps(status, indent=2, default=str))
        
        # Save state
        agent.save_state("agent_state.json")
        
        # Stop
        agent.stop()
        
        logger.info("\nAgent execution complete!")
        logger.info("Ready for next iteration or manual approval.")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
