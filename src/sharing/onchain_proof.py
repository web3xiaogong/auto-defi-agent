"""
链上决策证明调用模块
将 Agent 决策记录到 BSC 链上

Good Vibes Only: OpenClaw Edition Hackathon
"""

import json
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class OnChainProof:
    """
    链上决策证明
    
    功能:
    - 将决策记录到链上
    - 验证决策真实性
    - 查询历史决策
    """
    
    # 默认合约地址 (部署后更新)
    DEFAULT_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000"
    
    # 默认 ABI (简化版)
    CONTRACT_ABI = [
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "decisionId", "type": "uint256"},
                {"indexed": True, "name": "agentAddress", "type": "address"},
                {"indexed": False, "name": "decisionHash", "type": "bytes32"},
                {"indexed": False, "name": "apy", "type": "uint256"},
                {"indexed": False, "name": "recommendation", "type": "string"},
                {"indexed": False, "name": "poolName", "type": "string"}
            ],
            "name": "DecisionRecorded",
            "type": "event"
        },
        {
            "inputs": [
                {"name": "decisionHash", "type": "bytes32"},
                {"name": "apy", "type": "uint256"},
                {"name": "riskScore", "type": "uint256"},
                {"name": "recommendation", "type": "string"},
                {"name": "poolAddress", "type": "string"},
                {"name": "poolName", "type": "string"},
                {"name": "agentVersion", "type": "string"},
                {"name": "signature", "type": "bytes"}
            ],
            "name": "recordDecision",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "decisionId", "type": "uint256"}],
            "name": "getDecision",
            "outputs": [
                {"name": "timestamp", "type": "uint256"},
                {"name": "agentAddress", "type": "address"},
                {"name": "decisionHash", "type": "bytes32"},
                {"name": "apy", "type": "uint256"},
                {"name": "riskScore", "type": "uint256"},
                {"name": "recommendation", "type": "string"},
                {"name": "poolAddress", "type": "string"},
                {"name": "poolName", "type": "string"},
                {"name": "agentVersion", "type": "string"},
                {"name": "signature", "type": "bytes"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getDecisionCount",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    def __init__(
        self,
        rpc_url: str,
        contract_address: str = None,
        private_key: str = None,
        agent_name: str = "AutoDeFiAgent",
        agent_version: str = "1.0.0"
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.agent_name = agent_name
        self.agent_version = agent_version
        
        # 设置钱包
        if private_key:
            self.account = Account.from_key(private_key)
            self.contract_address = Web3.to_checksum_address(
                contract_address or self.DEFAULT_CONTRACT_ADDRESS
            )
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.CONTRACT_ABI
            )
        else:
            self.account = None
            self.contract = None
    
    def set_contract(self, contract_address: str, abi_path: str = None):
        """设置合约"""
        self.contract_address = Web3.to_checksum_address(contract_address)
        
        if abi_path and Path(abi_path).exists():
            with open(abi_path) as f:
                abi = json.load(f)
        else:
            abi = self.CONTRACT_ABI
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=abi
        )
    
    def create_decision_hash(
        self,
        pool_address: str,
        apy: float,
        risk_score: float,
        recommendation: str
    ) -> str:
        """
        创建决策哈希
        
        Args:
            pool_address: 池地址
            apy: 当前 APY
            risk_score: 风险评分 (0-1)
            recommendation: 建议 (BUY/HOLD/SELL)
        
        Returns:
            决策哈希 (hex)
        """
        # 构建决策数据
        decision_data = {
            "pool_address": pool_address.lower(),
            "apy": round(apy, 2),
            "risk_score": round(risk_score, 2),
            "recommendation": recommendation.upper(),
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "version": self.agent_version,
        }
        
        # 计算哈希
        data_str = json.dumps(decision_data, sort_keys=True)
        hash_bytes = Web3.keccak(text=data_str)
        
        return hash_bytes.hex()
    
    def sign_decision(self, decision_hash: str) -> bytes:
        """
        签名决策
        
        Args:
            decision_hash: 决策哈希
        
        Returns:
            签名 (bytes)
        """
        if not self.account:
            raise ValueError("No private key configured")
        
        # Ethereum 签名消息
        message = encode_defunct(hexstr=decision_hash)
        signed = self.account.sign_message(message)
        
        return signed.signature
    
    def record_decision(
        self,
        pool_address: str,
        pool_name: str,
        apy: float,
        risk_score: float,
        recommendation: str
    ) -> Dict:
        """
        记录决策到链上
        
        Args:
            pool_address: 池地址
            pool_name: 池名称
            apy: 当前 APY
            risk_score: 风险评分 (0-1)
            recommendation: 建议
        
        Returns:
            交易结果
        """
        if not self.contract:
            return {
                "status": "error",
                "message": "Contract not configured"
            }
        
        try:
            # 创建哈希
            decision_hash = self.create_decision_hash(
                pool_address, apy, risk_score, recommendation
            )
            
            # 签名
            signature = self.sign_decision(decision_hash)
            
            # 转换数据类型
            apy_int = int(apy * 100)  # 乘以100存储
            risk_int = int(risk_score * 100)  # 乘以100存储
            
            # 构建交易
            tx = self.contract.functions.recordDecision(
                decision_hash,
                apy_int,
                risk_int,
                recommendation.upper(),
                Web3.to_checksum_address(pool_address),
                pool_name,
                self.agent_version,
                signature
            ).build_transaction({
                "from": self.account.address,
                "nonce": self.w3.eth.get_transaction_count(self.account.address),
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
            })
            
            # 发送交易
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待确认
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # 解析决策 ID (从事件中)
            decision_id = 0
            if receipt.logs:
                # 简化处理 - 返回交易哈希
                pass
            
            return {
                "status": "success",
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "decision_hash": decision_hash,
                "gas_used": receipt.gasUsed,
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def batch_record_decisions(
        self,
        decisions: List[Dict]
    ) -> List[Dict]:
        """
        批量记录决策
        
        Args:
            decisions: 决策列表
        
        Returns:
            结果列表
        """
        results = []
        for decision in decisions:
            result = self.record_decision(
                pool_address=decision["pool_address"],
                pool_name=decision["pool_name"],
                apy=decision["apy"],
                risk_score=decision.get("risk_score", 0.5),
                recommendation=decision["recommendation"]
            )
            results.append(result)
        return results
    
    def get_decision(self, decision_id: int) -> Optional[Dict]:
        """
        获取决策
        
        Args:
            decision_id: 决策 ID
        
        Returns:
            决策数据 或 None
        """
        if not self.contract:
            return None
        
        try:
            decision = self.contract.functions.getDecision(decision_id).call()
            
            return {
                "decision_id": decision_id,
                "timestamp": datetime.fromtimestamp(decision[0]).isoformat(),
                "agent_address": decision[1],
                "decision_hash": decision[2],
                "apy": decision[3] / 100.0,
                "risk_score": decision[4] / 100.0,
                "recommendation": decision[5],
                "pool_address": decision[6],
                "pool_name": decision[7],
                "agent_version": decision[8],
            }
        except Exception:
            return None
    
    def get_decision_count(self) -> int:
        """获取决策总数"""
        if not self.contract:
            return 0
        
        try:
            return self.contract.functions.getDecisionCount().call()
        except Exception:
            return 0
    
    def verify_on_chain(self, decision_id: int, original_data: str) -> bool:
        """
        链上验证决策
        
        Args:
            decision_id: 决策 ID
            original_data: 原始数据 (JSON)
        
        Returns:
            是否验证成功
        """
        if not self.contract:
            return False
        
        try:
            return self.contract.functions.verifyDecision(
                decision_id, original_data
            ).call()
        except Exception:
            return False
    
    def generate_proof_url(self, decision_id: int) -> str:
        """
        生成证明链接
        
        Args:
            decision_id: 决策 ID
        
        Returns:
            BSCScan 链接
        """
        if not self.contract_address:
            return ""
        
        return f"https://bscscan.com/tx/0x...#{decision_id}"
    
    def export_decisions(self) -> str:
        """
        导出所有决策 (JSON)
        
        Returns:
            JSON 字符串
        """
        count = self.get_decision_count()
        decisions = []
        
        for i in range(min(count, 100)):  # 限制数量
            decision = self.get_decision(i)
            if decision:
                decisions.append(decision)
        
        return json.dumps({
            "exported_at": datetime.now().isoformat(),
            "total_decisions": count,
            "decisions": decisions,
        }, indent=2)


# ===== 演示代码 =====
def demo():
    """演示链上证明功能"""
    print("\n" + "="*50)
    print("⛓️  链上决策证明演示")
    print("="*50)
    print("")
    print("此功能需要:")
    print("1. 部署 DecisionRegistry.sol 到 BSC")
    print("2. 注册 Agent 地址")
    print("3. 配置私钥")
    print("")
    print("使用流程:")
    print("├── 1. Agent 做出决策")
    print("├── 2. 创建决策哈希")
    print("├── 3. 签名决策")
    print("├── 4. 发送到链上")
    print("└── 5. 永久保存，可验证")
    print("")
    print("优势:")
    print("✅ 完全透明 - 任何人都可以查看")
    print("✅ 不可篡改 - 链上数据无法修改")
    print("✅ 可追溯 - 查看完整历史")
    print("")


# ===== CLI =====
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="On-Chain Proof CLI")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--rpc", default="https://bsc-dataseed.binance.org/", help="BSC RPC")
    args = parser.parse_args()
    
    if args.demo:
        demo()
    else:
        print("Use --demo to see demonstration")


if __name__ == "__main__":
    main()
