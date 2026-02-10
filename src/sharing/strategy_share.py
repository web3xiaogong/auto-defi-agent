"""
策略分享功能
生成可验证的策略分享链接和二维码

Good Vibes Only: OpenClaw Edition Hackathon
"""

import json
import base64
import hashlib
import urllib.parse
import hmac
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Tuple
from pathlib import Path


@dataclass
class ShareableStrategy:
    """可分享的策略"""
    pool_name: str
    protocol: str
    chain: str
    min_apy: float
    max_slippage: float
    risk_level: str
    description: str = ""
    creator_name: str = ""
    creator_address: str = ""
    created_at: str = ""
    expires_at: str = ""
    signature: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "pool_name": self.pool_name,
            "protocol": self.protocol,
            "chain": self.chain,
            "min_apy": self.min_apy,
            "max_slippage": self.max_slippage,
            "risk_level": self.risk_level,
            "description": self.description,
            "creator_name": self.creator_name,
            "creator_address": self.creator_address,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "signature": self.signature,
        }


class StrategySharer:
    """
    策略分享器
    
    功能:
    - 生成短分享码
    - 创建可验证的签名
    - 生成分享链接
    - 生成二维码
    """
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or self._generate_secret()
        self.share_codes: Dict[str, dict] = {}
        
        # 分享码长度
        self.CODE_LENGTH = 12
    
    def _generate_secret(self) -> str:
        """生成密钥"""
        import secrets
        return secrets.token_hex(32)
    
    def _encode_share_code(self, data: dict) -> str:
        """编码为分享码"""
        # 添加时间戳防止重放
        data["_ts"] = datetime.now().timestamp()
        
        # JSON 编码
        json_str = json.dumps(data, sort_keys=True)
        
        # Base64 编码
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        
        # 生成校验码
        checksum = self._generate_checksum(encoded)
        
        # 返回格式: CODE-CHECKSUM
        return f"{encoded[:self.CODE_LENGTH].upper()}-{checksum[:4].upper()}"
    
    def _generate_checksum(self, data: str) -> str:
        """生成校验码"""
        message = f"{data}{self.secret_key}".encode()
        hash_bytes = hashlib.sha256(message).digest()
        return base64.urlsafe_b64encode(hash_bytes).decode()[:8]
    
    def _verify_checksum(self, code: str, data: str) -> bool:
        """验证校验码"""
        if "-" not in code:
            return False
        
        parts = code.split("-")
        if len(parts) != 2:
            return False
        
        stored_checksum = parts[1]
        expected_checksum = self._generate_checksum(data)[:4]
        
        return hmac.compare_digest(stored_checksum, expected_checksum)
    
    def create_share_code(
        self,
        strategy: Dict,
        creator_address: str = "",
        creator_name: str = "",
        expires_hours: int = 24
    ) -> Tuple[str, str]:
        """
        创建分享码
        
        Args:
            strategy: 策略参数
            creator_address: 创作者地址
            creator_name: 创作者名称
            expires_hours: 过期时间 (小时)
        
        Returns:
            (share_code, verification_code)
        """
        # 构建分享数据
        share_data = {
            "pool_name": strategy.get("pool_name", ""),
            "protocol": strategy.get("protocol", ""),
            "chain": strategy.get("chain", "BSC"),
            "min_apy": strategy.get("min_apy", 5.0),
            "max_slippage": strategy.get("max_slippage", 1.0),
            "risk_level": strategy.get("risk_level", "MEDIUM"),
            "description": strategy.get("description", ""),
            "creator_name": creator_name,
            "creator_address": creator_address,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=expires_hours)).isoformat(),
        }
        
        # 创建签名
        message = self._create_signable_message(share_data)
        signature = self._sign_message(message)
        share_data["signature"] = signature
        
        # 生成分享码
        share_code = self._encode_share_code(share_data)
        
        # 存储
        self.share_codes[share_code] = share_data
        
        # 生成验证码 (用于确认分享真实性)
        verification_code = self._generate_verification_code(share_data)
        
        return share_code, verification_code
    
    def _create_signable_message(self, data: dict) -> str:
        """创建可签名消息"""
        # 排除签名本身
        signable = {k: v for k, v in data.items() if k != "signature"}
        return json.dumps(signable, sort_keys=True)
    
    def _sign_message(self, message: str) -> str:
        """签名消息 (简化版)"""
        hash_bytes = hashlib.sha256(f"{message}{self.secret_key}".encode()).digest()
        signature = base64.urlsafe_b64encode(hash_bytes).decode()[:65]
        return signature
    
    def _generate_verification_code(self, data: dict) -> str:
        """生成验证码"""
        summary = f"{data.get('pool_name','')}{data.get('min_apy',0)}{data.get('chain','')}"
        return hashlib.sha256(summary.encode()).hexdigest()[:8].upper()
    
    def verify_share_code(self, share_code: str) -> Optional[dict]:
        """验证并解析分享码"""
        if share_code not in self.share_codes:
            return None
        
        data = self.share_codes[share_code]
        
        # 检查过期
        try:
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                del self.share_codes[share_code]
                return {"error": "EXPIRED", "message": "分享码已过期"}
        except (KeyError, ValueError):
            pass
        
        # 验证签名
        message = self._create_signable_message(data)
        expected_sig = self._sign_message(message)
        
        if data.get("signature") == expected_sig:
            data["verified"] = True
        else:
            data["verified"] = False
        
        return data
    
    def generate_share_url(
        self,
        share_code: str,
        base_url: str = "https://autodefi.ai/share"
    ) -> str:
        """生成分享 URL"""
        params = urllib.parse.urlencode({"s": share_code})
        return f"{base_url}?{params}"
    
    def generate_strategy_qr(
        self,
        share_code: str,
        output_path: str = None,
        base_url: str = "https://autodefi.ai/share"
    ) -> Optional[str]:
        """
        生成策略二维码
        
        Args:
            share_code: 分享码
            output_path: 输出路径
            base_url: 基础 URL
        
        Returns:
            输出文件路径 或 None
        """
        url = self.generate_share_url(share_code, base_url)
        
        if output_path is None:
            output_path = f"strategy_{share_code[:8]}.png"
        
        try:
            import qrcode
            from qrcode.image.styledpil import StyledPilImage
            from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
            from qrcode.image.styles.colormasks import SolidFillColorMask
            
            # 创建 QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # 生成图像
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(back_color=(255, 255, 255)),
            )
            
            # 保存
            img.save(output_path)
            return output_path
            
        except ImportError:
            # 备用: 简单版本
            import qrcode as qr
            q = qr.QRCode(
                version=1,
                error_correction=qr.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            q.add_data(url)
            q.make(fit=True)
            img = q.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            return output_path
    
    def import_strategy(self, share_code: str) -> Optional[Dict]:
        """导入策略"""
        verified = self.verify_share_code(share_code)
        
        if not verified:
            return None
        
        if "error" in verified:
            return verified
        
        # 返回策略参数
        return {
            "pool_name": verified.get("pool_name"),
            "protocol": verified.get("protocol"),
            "chain": verified.get("chain"),
            "min_apy": verified.get("min_apy"),
            "max_slippage": verified.get("max_slippage"),
            "risk_level": verified.get("risk_level"),
            "creator_address": verified.get("creator_address"),
            "creator_name": verified.get("creator_name"),
        }
    
    def get_popular_strategies(self, limit: int = 10) -> list:
        """获取热门策略 (模拟)"""
        # 实际项目中应查询数据库
        return [
            {
                "rank": i + 1,
                "pool_name": f"Pool {i+1}",
                "apy": f"{10 + i * 2}%",
                "followers": 100 - i * 10,
            }
            for i in range(min(limit, 10))
        ]


# ===== 便利函数 =====
def create_simple_strategy(
    pool_name: str,
    min_apy: float,
    chain: str = "BSC"
) -> Dict:
    """创建简单策略"""
    return {
        "pool_name": pool_name,
        "min_apy": min_apy,
        "chain": chain,
        "protocol": "PancakeSwap",
        "max_slippage": 1.0,
        "risk_level": "MEDIUM",
    }


def generate_strategy_card(strategy: Dict, prediction: Dict = None) -> str:
    """
    生成策略卡片 (Markdown 格式)
    
    用于 Telegram/Discord 分享
    """
    card = f"""
╔══════════════════════════════════════╗
║     🤖 Auto-DeFi 策略分享            ║
╠══════════════════════════════════════╣
║ 池名称:     {strategy.get('pool_name', 'N/A'):<20}║
║ 协议:       {strategy.get('protocol', 'N/A'):<20}║
║ 链:         {strategy.get('chain', 'N/A'):<20}║
║ 最小 APY:   {strategy.get('min_apy', 0):.1f}%{'':<15}║
║ 风险等级:   {strategy.get('risk_level', 'N/A'):<20}║
"""
    
    if prediction:
        card += f"""╠══════════════════════════════════════╣
║ 🔮 预测                              ║
║ 当前 APY:  {prediction.get('current_apy', 0):.2f}%{'':<14}║
║ 24h 预测:  {prediction.get('predicted_apy_24h', 0):.2f}%{'':<14}║
║ 趋势:      {prediction.get('trend', 'N/A'):<20}║
║ 建议:      {prediction.get('recommendation', 'N/A'):<20}║
"""
    
    card += """╚══════════════════════════════════════╝
"""
    
    return card


# ===== CLI 接口 =====
def main():
    import argparse
    import random
    
    parser = argparse.ArgumentParser(description="Strategy Sharing CLI")
    parser.add_argument("--pool", default="CAKE-USDT", help="Pool name")
    parser.add_argument("--apy", type=float, default=15.0, help="Min APY")
    parser.add_argument("--chain", default="BSC", help="Chain")
    parser.add_argument("--qr", action="store_true", help="Generate QR code")
    args = parser.parse_args()
    
    # 创建分享器
    sharer = StrategySharer()
    
    # 创建策略
    strategy = create_simple_strategy(args.pool, args.apy, args.chain)
    
    # 生成分享码
    share_code, verify_code = sharer.create_share_code(
        strategy,
        creator_address="0x19C9F422E6158302E8850c9e087A917f113783B4",
        creator_name="AutoDeFi Bot"
    )
    
    print("\n" + "="*50)
    print("📤 策略分享")
    print("="*50)
    print(f"分享码:   {share_code}")
    print(f"验证码:   {verify_code}")
    print(f"池名称:   {args.pool}")
    print(f"最小 APY: {args.apy}%")
    print(f"链:       {args.chain}")
    
    # 生成 URL
    url = sharer.generate_share_url(share_code)
    print(f"\n🔗 分享链接: {url}")
    
    # 生成二维码
    if args.qr:
        qr_path = sharer.generate_strategy_qr(share_code)
        if qr_path:
            print(f"📱 二维码: {qr_path}")
    
    # 显示卡片
    card = generate_strategy_card(strategy)
    print(f"\n{card}")
    
    # 验证
    verified = sharer.verify_share_code(share_code)
    if verified and verified.get("verified"):
        print("✅ 验证成功")


if __name__ == "__main__":
    main()
