"""
BSC (BNB Smart Chain) Network Adapter
Handle all BSC blockchain interactions
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from dataclasses import dataclass
from eth_typing import Address
from web3 import Web3
from web3.contract import Contract
from web3.types import TxParams, Wei


@dataclass
class WalletInfo:
    """Wallet information"""
    address: str
    balance_bnb: Decimal
    balance_usdt: Decimal
    nonce: int


class BSCAdapter:
    """BSC Network Adapter"""
    
    # PancakeSwap Router ABI (simplified)
    ROUTER_ABI = [
        {
            "name": "swapExactETHForTokens",
            "type": "function",
            "inputs": [
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "outputs": [{"name": "amounts", "type": "uint256[]"}]
        },
        {
            "name": "swapExactTokensForETH",
            "type": "function", 
            "inputs": [
                {"name": "amountIn", "type": "uint256"},
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "outputs": [{"name": "amounts", "type": "uint256[]"}]
        },
        {
            "name": "swapExactTokensForTokens",
            "type": "function",
            "inputs": [
                {"name": "amountIn", "type": "uint256"},
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "outputs": [{"name": "amounts", "type": "uint256[]"}]
        },
        {
            "name": "WETH",
            "type": "function",
            "outputs": [{"name": "", "type": "address"}]
        }
    ]
    
    # ERC20 ABI (simplified)
    ERC20_ABI = [
        {
            "name": "balanceOf",
            "type": "function",
            "inputs": [{"name": "owner", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}]
        },
        {
            "name": "approve",
            "type": "function",
            "inputs": [
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": [{"name": "", "type": "bool"}]
        },
        {
            "name": "allowance",
            "type": "function",
            "inputs": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"}
            ],
            "outputs": [{"name": "", "type": "uint256"}]
        },
        {
            "name": "transfer",
            "type": "function",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": [{"name": "", "type": "bool"}]
        }
    ]
    
    def __init__(self, rpc_url: str, private_key: str = None):
        """
        Initialize BSC Adapter
        
        Args:
            rpc_url: BSC RPC endpoint
            private_key: Wallet private key (optional)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        
        # Get address from private key
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.address = None
            self.account = None
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to BSC"""
        return self.w3.is_connected()
    
    def get_block_number(self) -> int:
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_balance(self, address: str = None) -> Decimal:
        """
        Get BNB balance
        
        Args:
            address: Wallet address (uses self.address if not provided)
        """
        addr = address or self.address
        if not addr:
            raise ValueError("No address provided")
        
        balance_wei = self.w3.eth.get_balance(addr)
        return Decimal(balance_wei) / Decimal(10**18)
    
    def get_token_balance(self, token_address: str, holder_address: str = None) -> Decimal:
        """
        Get ERC20 token balance
        
        Args:
            token_address: Token contract address
            holder_address: Token holder address
        """
        holder = holder_address or self.address
        if not holder:
            raise ValueError("No address provided")
        
        token = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=self.ERC20_ABI
        )
        
        balance_wei = token.functions.balanceOf(holder).call()
        return Decimal(balance_wei) / Decimal(10**18)
    
    def get_nonce(self, address: str = None) -> int:
        """Get transaction nonce"""
        addr = address or self.address
        return self.w3.eth.get_transaction_count(addr)
    
    def approve_token(self, token_address: str, spender_address: str, amount_wei: int) -> str:
        """
        Approve token spending
        
        Args:
            token_address: Token contract address
            spender_address: Spender contract address
            amount_wei: Amount to approve in wei
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No private key provided")
        
        token = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=self.ERC20_ABI
        )
        
        txn = token.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount_wei
        ).build_transaction({
            'from': self.address,
            'nonce': self.get_nonce(),
            'gas': 100000,
            'gasPrice': int(self.w3.eth.gas_price * 1.1)
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    
    def swap_tokens(
        self,
        token_in: str,
        token_out: str,
        amount_in_wei: int,
        amount_out_min_wei: int,
        deadline_seconds: int = 300
    ) -> str:
        """
        Execute token swap on PancakeSwap
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in_wei: Amount to swap in wei
            amount_out_min_wei: Minimum output amount in wei
            deadline_seconds: Transaction deadline
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No private key provided")
        
        router = self.w3.eth.contract(
            address=Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E"),
            abi=self.ROUTER_ABI
        )
        
        import time
        deadline = int(time.time()) + deadline_seconds
        
        path = [
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out)
        ]
        
        gas_price = int(self.w3.eth.gas_price * 1.1)
        
        txn = router.functions.swapExactTokensForTokens(
            amount_in_wei,
            amount_out_min_wei,
            path,
            self.address,
            deadline
        ).build_transaction({
            'from': self.address,
            'nonce': self.get_nonce(),
            'gas': 300000,
            'gasPrice': gas_price
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    
    def swap_eth_for_tokens(
        self,
        token_out: str,
        amount_out_min_wei: int,
        value_wei: int,
        deadline_seconds: int = 300
    ) -> str:
        """
        Swap BNB for tokens
        
        Args:
            token_out: Output token address
            amount_out_min_wei: Minimum output amount in wei
            value_wei: BNB amount to swap in wei
            deadline_seconds: Transaction deadline
            
        Returns:
            Transaction hash
        """
        if not self.account:
            raise ValueError("No private key provided")
        
        router = self.w3.eth.contract(
            address=Web3.to_checksum_address("0x10ED43C718714eb63d5aA57B78B54704E256024E"),
            abi=self.ROUTER_ABI
        )
        
        import time
        deadline = int(time.time()) + deadline_seconds
        
        path = [
            Web3.to_checksum_address(self.w3.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bd095Bc")),  # WBNB
            Web3.to_checksum_address(token_out)
        ]
        
        gas_price = int(self.w3.eth.gas_price * 1.1)
        
        txn = router.functions.swapExactETHForTokens(
            amount_out_min_wei,
            path,
            self.address,
            deadline
        ).build_transaction({
            'from': self.address,
            'nonce': self.get_nonce(),
            'gas': 300000,
            'gasPrice': gas_price,
            'value': value_wei
        })
        
        signed = self.account.sign_transaction(txn)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt"""
        return self.w3.eth.get_transaction_receipt(tx_hash)
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei"""
        return self.w3.eth.gas_price
