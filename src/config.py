"""
Configuration Management Module
Load settings from .env file
"""

import os
from pathlib import Path
from dotenv import dotenv_values
from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    """Network configuration"""
    bsc_rpc: str = "https://bsc-dataseed.binance.org/"
    opbnb_rpc: str = "https://opbnb-mainnet-rpc.bnbchain.org/"
    bsc_testnet_rpc: str = "https://data-seed-prebsc-1-s1.binance.org:8545/"


class WalletConfig(BaseModel):
    """Wallet configuration"""
    private_key: str = ""
    address: str = ""


class DeFiConfig(BaseModel):
    """DeFi protocol addresses"""
    pancake_router: str = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    pancake_router_opbnb: str = "0x7b28e12F7a6aE55d3Fa1f86cF25C2fddC5E7fC4"
    venus_comptroller: str = "0xfD36E2c2a678ae518C46e91eC0F07bdE4eE4e5d2"


class NotificationConfig(BaseModel):
    """Notification settings"""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


class AgentConfig(BaseModel):
    """Agent behavior settings"""
    gas_multiplier: float = 1.1
    min_transaction_value: float = 0.001
    max_slippage: float = 1.0
    apy_check_interval: int = 300  # seconds


class LoggingConfig(BaseModel):
    """Logging settings"""
    level: str = "INFO"
    file: str = "logs/auto_defi_agent.log"


class Config(BaseModel):
    """Main configuration container"""
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    wallet: WalletConfig = Field(default_factory=WalletConfig)
    defi: DeFiConfig = Field(default_factory=DeFiConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: str = None) -> Config:
    """
    Load configuration from .env file
    
    Args:
        config_path: Path to .env file. If None, looks for .env in current directory
        
    Returns:
        Config object with all settings
    """
    env_file = None
    
    if config_path:
        path = Path(config_path)
        if path.exists():
            env_file = str(path)
    else:
        # Look for .env in current directory or project root
        candidates = [
            Path(".env"),
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]
        for path in candidates:
            if path.exists():
                env_file = str(path)
                break
    
    # Load from .env file
    env_values = {}
    if env_file:
        env_values = dotenv_values(env_file)
    
    # Also allow environment variables to override
    config_dict = {
        **env_values,
        **os.environ,
    }
    
    return Config(
        network=NetworkConfig(
            bsc_rpc=config_dict.get("BSC_RPC", "https://bsc-dataseed.binance.org/"),
            opbnb_rpc=config_dict.get("OPBNB_RPC", "https://opbnb-mainnet-rpc.bnbchain.org/"),
            bsc_testnet_rpc=config_dict.get("BSC_TESTNET_RPC", ""),
        ),
        wallet=WalletConfig(
            private_key=config_dict.get("WALLET_PRIVATE_KEY", ""),
            address=config_dict.get("WALLET_ADDRESS", ""),
        ),
        defi=DeFiConfig(
            pancake_router=config_dict.get("PANCAKE_ROUTER", "0x10ED43C718714eb63d5aA57B78B54704E256024E"),
            pancake_router_opbnb=config_dict.get("PANCAKE_ROUTER_OPBNB", ""),
            venus_comptroller=config_dict.get("VENUS_COMPTROLLER", ""),
        ),
        notification=NotificationConfig(
            telegram_bot_token=config_dict.get("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=config_dict.get("TELEGRAM_CHAT_ID", ""),
        ),
        agent=AgentConfig(
            gas_multiplier=float(config_dict.get("GAS_MULTIPLIER", 1.1)),
            min_transaction_value=float(config_dict.get("MIN_TRANSACTION_VALUE", 0.001)),
            max_slippage=float(config_dict.get("MAX_SLIPPAGE", 1.0)),
            apy_check_interval=int(config_dict.get("APY_CHECK_INTERVAL", 300)),
        ),
        logging=LoggingConfig(
            level=config_dict.get("LOG_LEVEL", "INFO"),
            file=config_dict.get("LOG_FILE", "logs/auto_defi_agent.log"),
        ),
    )


# Global config instance
_config: Config = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config():
    """Reset configuration (useful for testing)"""
    global _config
    _config = None
