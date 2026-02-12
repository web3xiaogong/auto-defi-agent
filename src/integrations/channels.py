"""
Multi-Channel Message Integration

Good Vibes Only: OpenClaw Edition Hackathon

Features:
- Unified message interface for Telegram, Discord, WhatsApp
- Cross-platform context preservation
- Channel-specific formatting
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class Channel(Enum):
    """Supported message channels"""
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    IMESSAGE = "imessage"
    EMAIL = "email"
    WEB = "web"


@dataclass
class Message:
    """Unified message format"""
    channel: Channel
    content: str
    sender_id: str
    sender_name: str
    chat_id: str
    message_id: str = ""
    timestamp: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "channel": self.channel.value,
            "content": self.content,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "chat_id": self.chat_id,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class UserProfile:
    """User profile across channels"""
    user_id: str
    channels: Dict[Channel, str] = field(default_factory=dict)  # channel -> identifier
    preferences: Dict[str, Any] = field(default_factory=dict)
    wallet_address: str = ""
    risk tolerance: str = "MEDIUM"
    defi_experience: str = "INTERMEDIATE"
    
    def get_channel_id(self, channel: Channel) -> Optional[str]:
        return self.channels.get(channel)
    
    def add_channel(self, channel: Channel, identifier: str):
        self.channels[channel] = identifier


class MessageFormatter:
    """Format messages for specific channels"""
    
    @staticmethod
    def format_for_channel(message: str, channel: Channel) -> str:
        """Format message for specific channel"""
        if channel == Channel.TELEGRAM:
            return MessageFormatter._format_telegram(message)
        elif channel == Channel.DISCORD:
            return MessageFormatter._format_discord(message)
        elif channel == Channel.WHATSAPP:
            return MessageFormatter._format_whatsapp(message)
        elif channel == Channel.IMESSAGE:
            return MessageFormatter._format_imessage(message)
        else:
            return message
    
    @staticmethod
    def _format_telegram(message: str) -> str:
        """Format for Telegram (Markdown support)"""
        # Convert **bold** to *bold*
        formatted = message.replace("**", "*")
        return formatted
    
    @staticmethod
    def _format_discord(message: str) -> str:
        """Format for Discord (Markdown support)"""
        # Discord uses **bold** natively
        return message
    
    @staticmethod
    def _format_whatsapp(message: str) -> str:
        """Format for WhatsApp (basic formatting)"""
        # WhatsApp: *bold*, _italic_
        formatted = message.replace("**", "*")
        formatted = formatted.replace("__", "_")
        return formatted
    
    @staticmethod
    def _format_imessage(message: str) -> str:
        """Format for iMessage (basic text only)"""
        # iMessage: limited formatting
        import re
        # Remove markdown
        formatted = re.sub(r"\*\*([^*]+)\*\*", r"\1", message)  # bold
        formatted = re.sub(r"\*([^*]+)\*", r"\1", formatted)  # italic
        formatted = re.sub(r"__([^_]+)__", r"\1", formatted)  # underline
        return formatted
    
    @staticmethod
    def format_defi_result(data: Dict, channel: Channel) -> str:
        """Format DeFi result for channel"""
        
        if channel == Channel.TELEGRAM:
            return MessageFormatter._format_telegram_defi(data)
        elif channel == Channel.DISCORD:
            return MessageFormatter._format_discord_defi(data)
        else:
            return MessageFormatter._format_basic_defi(data)
    
    @staticmethod
    def _format_telegram_defi(data: Dict) -> str:
        """Format DeFi result for Telegram"""
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
    def _format_discord_defi(data: Dict) -> str:
        """Format DeFi result for Discord"""
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
    def _format_basic_defi(data: Dict) -> str:
        """Format DeFi result for basic text"""
        lines = ["DeFi Results"]
        
        if "pools" in data:
            lines.append("")
            lines.append("Top Opportunities:")
            for i, pool in enumerate(data["pools"][:5], 1):
                lines.append(f"{i}. {pool['name']}")
                lines.append(f"   APY: {pool['apy']:.1f}%")
                lines.append(f"   TVL: ${pool['tvl']:,.0f}")
        
        return "\n".join(lines)


class ChannelAdapter(ABC):
    """Abstract base class for channel adapters"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.channel = Channel.TELEGRAM  # Override in subclass
    
    @abstractmethod
    def send_message(self, message: str, chat_id: str, **kwargs) -> str:
        """Send message to channel"""
        pass
    
    @abstractmethod
    def get_messages(self, chat_id: str, limit: int = 100) -> List[Message]:
        """Get messages from channel"""
        pass
    
    @abstractmethod
    def handle_callback(self, callback_data: str) -> Dict:
        """Handle inline button callback"""
        pass


class TelegramAdapter(ChannelAdapter):
    """Telegram channel adapter"""
    
    def __init__(self, bot_token: str):
        super().__init__({"bot_token": bot_token})
        self.channel = Channel.TELEGRAM
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str, chat_id: str, **kwargs) -> str:
        """Send message via Telegram"""
        import requests
        
        formatted = MessageFormatter.format_for_channel(message, Channel.TELEGRAM)
        
        data = {
            "chat_id": chat_id,
            "text": formatted,
            "parse_mode": "Markdown",
            "reply_markup": kwargs.get("reply_markup")
        }
        
        response = requests.post(
            f"{self.base_url}/sendMessage",
            json=data
        )
        
        result = response.json()
        if result.get("ok"):
            return result["result"]["message_id"]
        else:
            raise Exception(f"Telegram error: {result}")
    
    def get_messages(self, chat_id: str, limit: int = 100) -> List[Message]:
        """Get messages from Telegram"""
        import requests
        
        response = requests.get(
            f"{self.base_url}/getChatHistory",
            params={
                "chat_id": chat_id,
                "limit": limit
            }
        )
        
        messages = []
        for msg in response.json().get("result", []):
            messages.append(Message(
                channel=Channel.TELEGRAM,
                content=msg.get("text", ""),
                sender_id=str(msg.get("from", {}).get("id", "")),
                sender_name=msg.get("from", {}).get("username", ""),
                chat_id=chat_id,
                message_id=str(msg.get("message_id", "")),
                timestamp=msg.get("date", 0)
            ))
        
        return messages
    
    def handle_callback(self, callback_data: str) -> Dict:
        """Handle callback from inline keyboard"""
        # Parse callback data (format: action:param)
        parts = callback_data.split(":", 1)
        if len(parts) == 2:
            return {"action": parts[0], "params": parts[1]}
        return {"action": callback_data, "params": ""}


class DiscordAdapter(ChannelAdapter):
    """Discord channel adapter"""
    
    def __init__(self, bot_token: str, guild_id: str):
        super().__init__({"bot_token": bot_token, "guild_id": guild_id})
        self.channel = Channel.DISCORD
        self.base_url = "https://discord.com/api/v10"
        self.headers = {"Authorization": f"Bot {bot_token}"}
    
    def send_message(self, message: str, channel_id: str, **kwargs) -> str:
        """Send message via Discord"""
        import requests
        
        formatted = MessageFormatter.format_for_channel(message, Channel.DISCORD)
        
        data = {
            "content": formatted,
            "embeds": kwargs.get("embeds")
        }
        
        response = requests.post(
            f"{self.base_url}/channels/{channel_id}/messages",
            headers=self.headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["id"]
        else:
            raise Exception(f"Discord error: {response.text}")
    
    def get_messages(self, channel_id: str, limit: int = 100) -> List[Message]:
        """Get messages from Discord"""
        import requests
        
        response = requests.get(
            f"{self.base_url}/channels/{channel_id}/messages",
            headers=self.headers,
            params={"limit": min(limit, 100)}
        )
        
        messages = []
        for msg in response.json():
            messages.append(Message(
                channel=Channel.DISCORD,
                content=msg.get("content", ""),
                sender_id=str(msg.get("author", {}).get("id", "")),
                sender_name=msg.get("author", {}).get("username", ""),
                chat_id=channel_id,
                message_id=str(msg.get("id", "")),
                timestamp=int(msg.get("timestamp", 0))
            ))
        
        return messages
    
    def handle_callback(self, callback_data: str) -> Dict:
        """Handle Discord interaction callback"""
        return {"action": callback_data, "params": ""}


class ChannelManager:
    """
    Multi-channel message manager
    
    Features:
    - Unified message interface
    - Channel-specific formatting
    - Context preservation across channels
    """
    
    def __init__(self):
        self.adapters: Dict[Channel, ChannelAdapter] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.message_history: List[Message] = []
    
    def add_adapter(self, channel: Channel, adapter: ChannelAdapter):
        """Add channel adapter"""
        self.adapters[channel] = adapter
        logger.info(f"Added adapter for {channel.value}")
    
    def get_adapter(self, channel: Channel) -> Optional[ChannelAdapter]:
        """Get adapter for channel"""
        return self.adapters.get(channel)
    
    def send_defi_result(
        self,
        data: Dict,
        channel: Channel,
        chat_id: str,
        **kwargs
    ) -> str:
        """
        Send formatted DeFi result to channel
        
        Args:
            data: DeFi data to send
            channel: Target channel
            chat_id: Channel/chat ID
            **kwargs: Additional options
            
        Returns:
            Message ID
        """
        adapter = self.get_adapter(channel)
        if not adapter:
            raise ValueError(f"No adapter for channel: {channel}")
        
        # Format message
        message = MessageFormatter.format_defi_result(data, channel)
        
        # Send
        return adapter.send_message(message, chat_id, **kwargs)
    
    def create_inline_keyboard(
        self,
        buttons: List[List[Dict]],
        channel: Channel
    ) -> Dict:
        """Create channel-specific inline keyboard"""
        
        if channel == Channel.TELEGRAM:
            return {
                "inline_keyboard": [
                    [
                        {"text": btn.get("text", ""), "callback_data": btn.get("action", "")}
                        for btn in row
                    ]
                    for row in buttons
                ]
            }
        elif channel == Channel.DISCORD:
            # Discord uses components
            return {
                "components": [
                    {
                        "type": 1,  # Action row
                        "components": [
                            {
                                "type": 2,  # Button
                                "label": btn.get("text", ""),
                                "style": 1,  # Primary
                                "custom_id": btn.get("action", "")
                            }
                            for btn in row
                        ]
                    }
                    for row in buttons
                ]
            }
        else:
            return {}
    
    def sync_user_profile(
        self,
        user_id: str,
        channel: Channel,
        channel_id: str,
        profile_data: Dict = None
    ) -> UserProfile:
        """Sync user profile across channels"""
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        profile = self.user_profiles[user_id]
        profile.add_channel(channel, channel_id)
        
        if profile_data:
            profile.preferences.update(profile_data)
        
        return profile
    
    def get_user_context(self, user_id: str) -> Dict:
        """Get user's context across all channels"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {}
        
        return {
            "channels": {c.value: i for c, i in profile.channels.items()},
            "wallet": profile.wallet_address,
            "risk_tolerance": profile.risk_tolerance,
            "experience": profile.defi_experience,
            "preferences": profile.preferences
        }


# ============== Demo ==============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = ChannelManager()
    
    # Add Telegram adapter (demo)
    # manager.add_adapter(Channel.TELEGRAM, TelegramAdapter("YOUR_BOT_TOKEN"))
    
    print("=" * 60)
    print("📡 Multi-Channel Message Integration Demo")
    print("=" * 60)
    
    # Demo message formatting
    demo_data = {
        "pools": [
            {"name": "PancakeSwap CAKE-BNB", "apy": 15.2, "tvl": 12500000},
            {"name": "Venus BNB", "apy": 5.2, "tvl": 890000000},
            {"name": "Biswap BSW-BNB", "apy": 12.8, "tvl": 5600000},
        ],
        "prediction": {
            "predicted_apy_7d": 16.5,
            "trend": "UP",
            "confidence": 0.75
        }
    }
    
    print("\n📱 Telegram Format:")
    print(MessageFormatter.format_for_channel(
        MessageFormatter._format_telegram_defi(demo_data),
        Channel.TELEGRAM
    ))
    
    print("\n💬 Discord Format:")
    print(MessageFormatter.format_for_channel(
        MessageFormatter._format_discord_defi(demo_data),
        Channel.DISCORD
    ))
    
    print("\n📲 Basic Format:")
    print(MessageFormatter._format_basic_defi(demo_data))
    
    print("\n✅ Demo complete!")
