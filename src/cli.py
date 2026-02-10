#!/usr/bin/env python3
"""
OpenClaw Skill Interface for Auto-DeFi Agent
Provides CLI interface for OpenClaw integration
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import load_config
from tools.defi_service import DeFiService
from agents.strategy_agent import AutoDeFiAgent, StrategyConfig, AgentState


def format_opportunity(opp, index=1):
    """Format opportunity for display"""
    return f"""
{index}. {opp.pool_name}
   Protocol: {opp.protocol}
   Chain: {opp.chain}
   APY: {opp.apy:.2f}%
   TVL: ${opp.tvl:,.0f}
   Confidence: {opp.confidence:.0%}
"""


def format_risk(analysis):
    """Format risk analysis for display"""
    lines = [f"\n📊 Risk Analysis for {analysis['opportunity']}"]
    lines.append(f"Score: {analysis['score']:.2f} ({analysis['risk_level']})")
    lines.append("\nFactors:")
    for factor, level, score in analysis['factors']:
        lines.append(f"  • {factor}: {level} {score}")
    lines.append(f"\n💡 Recommendation: {analysis['recommendation']}")
    return "\n".join(lines)


def cmd_scan(args):
    """Scan for opportunities"""
    chain = args.chain.upper()
    min_apy = float(args.min_apy)
    
    print(f"\n🔍 Scanning {chain} for APY ≥ {min_apy}%...")
    
    # Initialize services
    defi_service = DeFiService()
    agent = AutoDeFiAgent(config=StrategyConfig(min_apy=min_apy))
    
    # Fetch pools
    pools = defi_service.get_bsc_pancake_pools() if chain == "BSC" else []
    
    if not pools:
        # Try opBNB pools (same API for now)
        pools = defi_service.get_bsc_pancake_pools()
    
    if pools:
        opportunities = agent.scan_opportunities(pools)
        
        if opportunities:
            print(f"\n✅ Found {len(opportunities)} opportunities:")
            for i, opp in enumerate(opportunities[:10], 1):
                print(format_opportunity(opp, i))
            
            # Best opportunity
            best = agent.get_best_opportunity()
            if best:
                print(f"\n🏆 Best Opportunity:")
                print(format_opportunity(best))
                print(format_risk(agent.analyze_risk(best)))
        else:
            print(f"\n⚠️ No opportunities found with {min_apy}% APY threshold")
    else:
        print("\n❌ Failed to fetch pools")
    
    return 0


def cmd_status(args):
    """Show agent status"""
    config = load_config()
    
    agent = AutoDeFiAgent(
        config=StrategyConfig(),
        wallet_address=config.wallet.address
    )
    
    status = agent.get_status()
    
    print("\n🤖 Auto-DeFi Agent Status")
    print("=" * 40)
    print(f"State: {status['state']}")
    print(f"Running: {status['running']}")
    print(f"Opportunities Found: {status['opportunities_count']}")
    print(f"Transactions: {status['transactions_count']}")
    print(f"Last Check: {status['last_check'] or 'Never'}")
    
    metrics = status['metrics']
    print(f"\n📈 Metrics:")
    print(f"  • Checks: {metrics['checks']}")
    print(f"  • Opportunities: {metrics['opportunities_found']}")
    print(f"  • Executed: {metrics['executed']}")
    print(f"  • Errors: {metrics['errors']}")
    
    return 0


def cmd_strategy(args):
    """Generate strategy"""
    chain = args.chain.upper() if args.chain else "BSC"
    
    print(f"\n🎯 Generating {chain} Strategy...")
    
    defi_service = DeFiService()
    agent = AutoDeFiAgent(config=StrategyConfig())
    
    pools = defi_service.get_bsc_pancake_pools()
    
    if pools:
        agent.scan_opportunities(pools)
        strategy = agent.generate_strategy()
        
        print("\n📋 Strategy Recommendation")
        print("=" * 40)
        print(json.dumps(strategy, indent=2, default=str))
    else:
        print("\n❌ No pools available")
    
    return 0


def cmd_risk(args):
    """Analyze risk"""
    chain = args.chain.upper() if args.chain else "BSC"
    
    print(f"\n📊 Analyzing Risk for {chain}...")
    
    defi_service = DeFiService()
    agent = AutoDeFiAgent(config=StrategyConfig())
    
    pools = defi_service.get_bsc_pancake_pools()
    
    if pools:
        opportunities = agent.scan_opportunities(pools)
        best = agent.get_best_opportunity()
        
        if best:
            analysis = agent.analyze_risk(best)
            print(format_risk(analysis))
        else:
            print("\n⚠️ No opportunities to analyze")
    else:
        print("\n❌ No pools available")
    
    return 0


def cmd_execute(args):
    """Execute strategy"""
    print("\n⚠️ Execution requires manual approval")
    print("Set auto_execute=true in config or call with --approve flag")
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Auto-DeFi Agent CLI for OpenClaw Integration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan for opportunities")
    scan_parser.add_argument("--chain", default="BSC", help="Chain to scan")
    scan_parser.add_argument("--min-apy", default="5.0", help="Minimum APY percentage")
    
    # status
    subparsers.add_parser("status", help="Show agent status")
    
    # strategy
    strategy_parser = subparsers.add_parser("strategy", help="Generate strategy")
    strategy_parser.add_argument("--chain", default="BSC", help="Chain")
    
    # risk
    risk_parser = subparsers.add_parser("risk", help="Analyze risk")
    risk_parser.add_argument("--chain", default="BSC", help="Chain")
    
    # execute
    execute_parser = subparsers.add_parser("execute", help="Execute strategy")
    execute_parser.add_argument("--chain", default="BSC", help="Chain")
    execute_parser.add_argument("--approve", action="store_true", help="Auto-approve")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route commands
    commands = {
        "scan": cmd_scan,
        "status": cmd_status,
        "strategy": cmd_strategy,
        "risk": cmd_risk,
        "execute": cmd_execute,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
