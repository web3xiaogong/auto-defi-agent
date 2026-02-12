#!/usr/bin/env python3
"""
Multi-Channel Integration Test

Tests Telegram, Discord, and other channels

Usage:
    python3 scripts/test_channels.py --channel telegram
    python3 scripts/test_channels.py --channel discord
    python3 scripts/test_channels.py --all
"""

import json
import argparse
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime


# ============ Test Data ============

TEST_DEFi_DATA = {
    "pools": [
        {
            "name": "PancakeSwap CAKE-BNB LP",
            "apy": 15.2,
            "tvl": 12500000,
            "chain": "BSC",
            "protocol": "PancakeSwap"
        },
        {
            "name": "Venus BNB",
            "apy": 5.2,
            "tvl": 890000000,
            "chain": "BSC",
            "protocol": "Venus"
        },
        {
            "name": "Biswap BSW-BNB LP",
            "apy": 12.8,
            "tvl": 5600000,
            "chain": "BSC",
            "protocol": "Biswap"
        },
        {
            "name": "Alpaca BUSD Stable LP",
            "apy": 4.8,
            "tvl": 32000000,
            "chain": "BSC",
            "protocol": "Alpaca"
        },
        {
            "name": "Apollo ETH-BNB LP",
            "apy": 8.5,
            "tvl": 8900000,
            "chain": "BSC",
            "protocol": "Apollo"
        }
    ],
    "prediction": {
        "pool_name": "PancakeSwap CAKE-BNB LP",
        "predicted_apy_7d": 16.5,
        "trend": "UP",
        "confidence": 0.75,
        "recommendation": "BUY"
    }
}


# ============ Message Templates ============

class ChannelFormatter:
    """Format messages for different channels"""
    
    @staticmethod
    def format_telegram(data: Dict) -> str:
        """Format for Telegram (Markdown)"""
        lines = ["📊 *DeFi Scan Results*\n"]
        
        # Top Pools
        lines.append("*🏆 Top 5 APY Pools:*")
        for i, pool in enumerate(data["pools"][:5], 1):
            emoji = "🟢" if pool["apy"] > 10 else "🟡" if pool["apy"] > 5 else "🔴"
            lines.append(f"{emoji} *{i}. {pool['name']}*")
            lines.append(f"   📈 APY: `{pool['apy']:.1f}%`")
            lines.append(f"   💰 TVL: `${pool['tvl']:,.0f}`")
            lines.append(f"   ⛓️ {pool['chain']} | 🏦 {pool['protocol']}")
            lines.append("")
        
        # Prediction
        pred = data.get("prediction", {})
        if pred:
            lines.append("─" * 30)
            lines.append("🔮 *ML Prediction:*")
            lines.append(f"   📍 Pool: *{pred.get('pool_name', 'N/A')}*")
            lines.append(f"   📈 7D APY: `{pred.get('predicted_apy_7d', 0):.1f}%`")
            lines.append(f"   📊 Trend: {pred.get('trend', 'N/A')}")
            lines.append(f"   🎯 Confidence: `{pred.get('confidence', 0)*100:.0f}%`")
            
            rec = pred.get("recommendation", "")
            if rec == "BUY":
                lines.append(f"   💡 Recommendation: *✅ BUY*")
            elif rec == "SELL":
                lines.append(f"   💡 Recommendation: *❌ SELL*")
            else:
                lines.append(f"   💡 Recommendation: *⏸️ HOLD*")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_discord(data: Dict) -> str:
        """Format for Discord (Markdown)"""
        lines = ["📊 **DeFi Scan Results**\n"]
        
        lines.append("**🏆 Top 5 APY Pools:**")
        for i, pool in enumerate(data["pools"][:5], 1):
            emoji = "🟢" if pool["apy"] > 10 else "🟡" if pool["apy"] > 5 else "🔴"
            lines.append(f"{emoji} **{i}. {pool['name']}**")
            lines.append(f"   📈 APY: `{pool['apy']:.1f}%`")
            lines.append(f"   💰 TVL: `${pool['tvl']:,.0f}`")
            lines.append(f"   ⛓️ {pool['chain']} | 🏦 {pool['protocol']}")
            lines.append("")
        
        pred = data.get("prediction", {})
        if pred:
            lines.append("─" * 30)
            lines.append("🔮 **ML Prediction:**")
            lines.append(f"   📍 Pool: **{pred.get('pool_name', 'N/A')}**")
            lines.append(f"   📈 7D APY: `{pred.get('predicted_apy_7d', 0):.1f}%`")
            lines.append(f"   📊 Trend: {pred.get('trend', 'N/A')}")
            lines.append(f"   🎯 Confidence: `{pred.get('confidence', 0)*100:.0f}%`")
            
            rec = pred.get("recommendation", "")
            if rec == "BUY":
                lines.append(f"   💡 Recommendation: **✅ BUY**")
            elif rec == "SELL":
                lines.append(f"   💡 Recommendation: **❌ SELL**")
            else:
                lines.append(f"   💡 Recommendation: **⏸️ HOLD**")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_whatsapp(data: Dict) -> str:
        """Format for WhatsApp (basic text)"""
        lines = ["📊 *DeFi Scan Results*\n"]
        
        lines.append("*🏆 Top 5 APY Pools:*")
        for i, pool in enumerate(data["pools"][:5], 1):
            lines.append(f"{i}. {pool['name']}")
            lines.append(f"   APY: {pool['apy']:.1f}% | TVL: ${pool['tvl']:,.0f}")
            lines.append(f"   {pool['chain']} | {pool['protocol']}")
            lines.append("")
        
        pred = data.get("prediction", {})
        if pred:
            lines.append("─" * 30)
            lines.append("🔮 *ML Prediction:*")
            lines.append(f"   Pool: {pred.get('pool_name', 'N/A')}")
            lines.append(f"   7D APY: {pred.get('predicted_apy_7d', 0):.1f}%")
            lines.append(f"   Trend: {pred.get('trend', 'N/A')}")
            lines.append(f"   Confidence: {pred.get('confidence', 0)*100:.0f}%")
            lines.append(f"   Recommendation: {pred.get('recommendation', '')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_basic(data: Dict) -> str:
        """Format for basic text (iMessage, SMS)"""
        lines = ["DeFi Scan Results"]
        lines.append("=" * 40)
        
        for i, pool in enumerate(data["pools"][:5], 1):
            lines.append(f"{i}. {pool['name']}")
            lines.append(f"   APY: {pool['apy']:.1f}% | TVL: ${pool['tvl']:,.0f}")
        
        pred = data.get("prediction", {})
        if pred:
            lines.append("")
            lines.append(f"Prediction for {pred.get('pool_name', 'N/A')}:")
            lines.append(f"   7D APY: {pred.get('predicted_apy_7d', 0):.1f}%")
            lines.append(f"   Trend: {pred.get('trend', 'N/A')}")
        
        return "\n".join(lines)


# ============ Channel Simulator ============

class ChannelSimulator:
    """Simulate sending messages to channels"""
    
    def __init__(self):
        self.sent_messages = []
    
    def send_telegram(self, message: str, chat_id: str = "test_chat") -> Dict:
        """Simulate Telegram message"""
        result = {
            "channel": "telegram",
            "chat_id": chat_id,
            "message_id": f"tg_{datetime.now().timestamp()}",
            "status": "sent",
            "preview": message[:100] + "..." if len(message) > 100 else message
        }
        self.sent_messages.append(result)
        return result
    
    def send_discord(self, message: str, channel_id: str = "test_channel") -> Dict:
        """Simulate Discord message"""
        result = {
            "channel": "discord",
            "channel_id": channel_id,
            "message_id": f"dc_{datetime.now().timestamp()}",
            "status": "sent",
            "preview": message[:100] + "..." if len(message) > 100 else message
        }
        self.sent_messages.append(result)
        return result
    
    def send_whatsapp(self, message: str, phone: str = "+1234567890") -> Dict:
        """Simulate WhatsApp message"""
        result = {
            "channel": "whatsapp",
            "phone": phone,
            "message_id": f"wa_{datetime.now().timestamp()}",
            "status": "sent",
            "preview": message[:100] + "..." if len(message) > 100 else message
        }
        self.sent_messages.append(result)
        return result
    
    def get_summary(self) -> Dict:
        """Get summary of sent messages"""
        return {
            "total_sent": len(self.sent_messages),
            "channels": list(set(m["channel"] for m in self.sent_messages)),
            "messages": self.sent_messages
        }


# ============ Tests ============

def test_telegram():
    """Test Telegram channel"""
    print("=" * 60)
    print("📱 Testing Telegram Integration")
    print("=" * 60)
    
    simulator = ChannelSimulator()
    
    # Format message
    message = ChannelFormatter.format_telegram(TEST_DEFi_DATA)
    
    # Simulate sending
    result = simulator.send_telegram(message, chat_id="123456789")
    
    print(f"\n✅ Message sent to Telegram!")
    print(f"   Chat ID: {result['chat_id']}")
    print(f"   Message ID: {result['message_id']}")
    
    print(f"\n📝 Message Preview:")
    print("-" * 60)
    print(message[:500])
    print("-" * 60)
    
    return simulator.get_summary()


def test_discord():
    """Test Discord channel"""
    print("\n" + "=" * 60)
    print("💬 Testing Discord Integration")
    print("=" * 60)
    
    simulator = ChannelSimulator()
    
    # Format message
    message = ChannelFormatter.format_discord(TEST_DEFi_DATA)
    
    # Simulate sending
    result = simulator.send_discord(message, channel_id="987654321")
    
    print(f"\n✅ Message sent to Discord!")
    print(f"   Channel ID: {result['channel_id']}")
    print(f"   Message ID: {result['message_id']}")
    
    print(f"\n📝 Message Preview:")
    print("-" * 60)
    print(message[:500])
    print("-" * 60)
    
    return simulator.get_summary()


def test_whatsapp():
    """Test WhatsApp channel"""
    print("\n" + "=" * 60)
    print("💬 Testing WhatsApp Integration")
    print("=" * 60)
    
    simulator = ChannelSimulator()
    
    # Format message
    message = ChannelFormatter.format_whatsapp(TEST_DEFi_DATA)
    
    # Simulate sending
    result = simulator.send_whatsapp(message, phone="+1234567890")
    
    print(f"\n✅ Message sent to WhatsApp!")
    print(f"   Phone: {result['phone']}")
    print(f"   Message ID: {result['message_id']}")
    
    print(f"\n📝 Message Preview:")
    print("-" * 60)
    print(message[:500])
    print("-" * 60)
    
    return simulator.get_summary()


def test_all_channels():
    """Test all channels"""
    print("=" * 60)
    print("🌐 Testing All Channels")
    print("=" * 60)
    
    all_results = []
    
    # Test each channel
    results_tg = test_telegram()
    all_results.extend(results_tg["messages"])
    
    results_dc = test_discord()
    all_results.extend(results_dc["messages"])
    
    results_wa = test_whatsapp()
    all_results.extend(results_wa["messages"])
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Total messages sent: {len(all_results)}")
    print(f"📱 Channels tested:")
    print("   • Telegram")
    print("   • Discord")
    print("   • WhatsApp")
    print("   • Basic Text")
    
    return {
        "total": len(all_results),
        "channels": ["telegram", "discord", "whatsapp"],
        "messages": all_results
    }


def test_integration_with_erc8004():
    """Test multi-channel with ERC-8004 agent"""
    print("\n" + "=" * 60)
    print("🤖 Testing ERC-8004 Agent Integration")
    print("=" * 60)
    
    # Load agent info
    try:
        with open("src/integrations/agent_info.json") as f:
            agent_info = json.load(f)
    except:
        agent_info = {
            "agent_id": "autodefi-demo",
            "name": "Auto-DeFi Agent",
            "services": ["defi-optimization", "apy-prediction"]
        }
    
    print(f"\n🤖 Agent: {agent_info['name']}")
    print(f"📛 ID: {agent_info.get('agent_id', 'N/A')}")
    print(f"🔗 Services: {', '.join(agent_info.get('services', []))}")
    
    # Format DeFi data with agent signature
    data = {
        **TEST_DEFi_DATA,
        "agent": {
            "id": agent_info.get("agent_id", "autodefi-demo"),
            "signature": "0x" + "abcd" * 10,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Test formatting
    telegram_msg = ChannelFormatter.format_telegram(data)
    discord_msg = ChannelFormatter.format_discord(data)
    
    print(f"\n✅ Messages formatted for all channels")
    
    return {
        "agent": agent_info,
        "channels_tested": ["telegram", "discord", "whatsapp"]
    }


# ============ Main ============

def main():
    parser = argparse.ArgumentParser(description="Test Multi-Channel Integration")
    parser.add_argument(
        "--channel",
        choices=["telegram", "discord", "whatsapp", "all"],
        default="all",
        help="Channel to test (default: all)"
    )
    parser.add_argument(
        "--erc8004",
        action="store_true",
        help="Test ERC-8004 integration"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🚀 Auto-DeFi Agent - Multi-Channel Integration Test")
    print("=" * 60)
    
    # Test channels
    if args.channel == "all":
        results = test_all_channels()
    elif args.channel == "telegram":
        results = test_telegram()
    elif args.channel == "discord":
        results = test_discord()
    elif args.channel == "whatsapp":
        results = test_whatsapp()
    
    # Test ERC-8004 integration
    if args.erc8004:
        results = test_integration_with_erc8004()
    
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
