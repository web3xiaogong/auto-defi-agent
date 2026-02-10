// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title DecisionRegistry
 * @notice 记录 Agent 所有决策到链上，实现透明可验证
 * @dev Good Vibes Only: OpenClaw Edition Hackathon
 */
contract DecisionRegistry {
    
    // ===== 数据结构 =====
    
    struct Decision {
        uint256 timestamp;           // 决策时间
        address agentAddress;        // Agent 地址
        bytes32 decisionHash;        // 决策内容哈希
        uint256 apy;                 // 当前 APY (乘以100)
        uint256 riskScore;           // 风险评分 (0-100)
        string recommendation;       // 建议 (BUY/HOLD/SELL)
        string poolAddress;          // 池地址
        string poolName;             // 池名称
        string agentVersion;         // Agent 版本
        bytes signature;             // 签名
    }
    
    struct AgentInfo {
        string name;                 // Agent 名称
        string version;              // 版本
        bool isRegistered;           // 是否注册
        uint256 decisionsCount;      // 决策数量
    }
    
    // ===== 状态变量 =====
    
    Decision[] public decisions;              // 所有决策
    mapping(address => AgentInfo) public agents;  // Agent 信息
    mapping(address => bool) public authorizedSigners;  // 授权签名者
    
    address public owner;                     // 合约所有者
    
    // ===== 事件 =====
    
    event DecisionRecorded(
        uint256 indexed decisionId,
        address indexed agentAddress,
        bytes32 decisionHash,
        uint256 apy,
        string recommendation,
        string poolName
    );
    
    event AgentRegistered(
        address indexed agentAddress,
        string name,
        string version
    );
    
    event SignerAuthorized(
        address indexed signer,
        bool authorized
    );
    
    // ===== 修饰符 =====
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            authorizedSigners[msg.sender] || agents[msg.sender].isRegistered,
            "Not authorized"
        );
        _;
    }
    
    // ===== 构造函数 =====
    
    constructor() {
        owner = msg.sender;
    }
    
    // ===== 管理员函数 =====
    
    /**
     * @notice 授权签名者
     */
    function authorizeSigner(address signer, bool authorized) external onlyOwner {
        authorizedSigners[signer] = authorized;
        emit SignerAuthorized(signer, authorized);
    }
    
    /**
     * @notice 注册 Agent
     */
    function registerAgent(
        address agentAddress,
        string memory name,
        string memory version
    ) external onlyOwner {
        agents[agentAddress] = AgentInfo({
            name: name,
            version: version,
            isRegistered: true,
            decisionsCount: 0
        });
        emit AgentRegistered(agentAddress, name, version);
    }
    
    // ===== 核心函数 =====
    
    /**
     * @notice 记录决策
     * @param decisionHash 决策内容的哈希
     * @param apy 当前 APY (乘以100, 例如 25.5% = 2550)
     * @param riskScore 风险评分 (0-100)
     * @param recommendation 建议 (BUY/HOLD/SELL)
     * @param poolAddress 池地址
     * @param poolName 池名称
     * @param agentVersion Agent 版本
     * @param signature 签名
     */
    function recordDecision(
        bytes32 decisionHash,
        uint256 apy,
        uint256 riskScore,
        string memory recommendation,
        string memory poolAddress,
        string memory poolName,
        string memory agentVersion,
        bytes memory signature
    ) external onlyAuthorized returns (uint256) {
        // 验证签名
        require(_verifySignature(
            decisionHash,
            msg.sender,
            signature
        ), "Invalid signature");
        
        // 创建决策记录
        Decision memory decision = Decision({
            timestamp: block.timestamp,
            agentAddress: msg.sender,
            decisionHash: decisionHash,
            apy: apy,
            riskScore: riskScore,
            recommendation: recommendation,
            poolAddress: poolAddress,
            poolName: poolName,
            agentVersion: agentVersion,
            signature: signature
        });
        
        // 存储
        uint256 decisionId = decisions.length;
        decisions.push(decision);
        
        // 更新 Agent 统计
        agents[msg.sender].decisionsCount++;
        
        // 触发事件
        emit DecisionRecorded(
            decisionId,
            msg.sender,
            decisionHash,
            apy,
            recommendation,
            poolName
        );
        
        return decisionId;
    }
    
    /**
     * @notice 批量记录决策 (节省 Gas)
     */
    function batchRecordDecisions(
        bytes32[] memory decisionHashes,
        uint256[] memory apys,
        uint256[] memory riskScores,
        string[] memory recommendations,
        string[] memory poolAddresses,
        string[] memory poolNames,
        string memory agentVersion,
        bytes[] memory signatures
    ) external onlyAuthorized returns (uint256[] memory) {
        require(
            decisionHashes.length == apys.length &&
            apys.length == riskScores.length &&
            riskScores.length == recommendations.length &&
            recommendations.length == poolAddresses.length &&
            poolAddresses.length == poolNames.length &&
            poolNames.length == signatures.length,
            "Array length mismatch"
        );
        
        uint256[] memory decisionIds = new uint256[](decisionHashes.length);
        
        for (uint256 i = 0; i < decisionHashes.length; i++) {
            decisionIds[i] = this.recordDecision(
                decisionHashes[i],
                apys[i],
                riskScores[i],
                recommendations[i],
                poolAddresses[i],
                poolNames[i],
                agentVersion,
                signatures[i]
            );
        }
        
        return decisionIds;
    }
    
    // ===== 查询函数 =====
    
    /**
     * @notice 获取决策数量
     */
    function getDecisionCount() external view returns (uint256) {
        return decisions.length;
    }
    
    /**
     * @notice 获取决策 (按 ID)
     */
    function getDecision(uint256 decisionId) external view returns (Decision memory) {
        require(decisionId < decisions.length, "Invalid ID");
        return decisions[decisionId];
    }
    
    /**
     * @notice 获取 Agent 的所有决策 (分页)
     */
    function getAgentDecisions(
        address agentAddress,
        uint256 startId,
        uint256 limit
    ) external view returns (Decision[] memory) {
        AgentInfo memory agent = agents[agentAddress];
        require(agent.isRegistered, "Agent not registered");
        
        uint256 count = 0;
        for (uint256 i = startId; i < decisions.length && count < limit; i++) {
            if (decisions[i].agentAddress == agentAddress) {
                count++;
            }
        }
        
        Decision[] memory result = new Decision[](count);
        uint256 resultIndex = 0;
        
        for (uint256 i = startId; i < decisions.length && resultIndex < count; i++) {
            if (decisions[i].agentAddress == agentAddress) {
                result[resultIndex] = decisions[i];
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @notice 获取 Agent 统计
     */
    function getAgentStats(address agentAddress) external view returns (
        string memory name,
        string memory version,
        uint256 decisionsCount
    ) {
        AgentInfo memory agent = agents[agentAddress];
        return (agent.name, agent.version, agent.decisionsCount);
    }
    
    // ===== 验证函数 =====
    
    /**
     * @notice 链下验证决策
     */
    function verifyDecision(
        uint256 decisionId,
        string memory originalData
    ) external view returns (bool) {
        require(decisionId < decisions.length, "Invalid ID");
        
        bytes32 hash = keccak256(abi.encodePacked(originalData));
        return decisions[decisionId].decisionHash == hash;
    }
    
    /**
     * @notice 验证签名
     */
    function _verifySignature(
        bytes32 decisionHash,
        address signer,
        bytes memory signature
    ) internal view returns (bool) {
        if (signature.length != 65) return false;
        
        bytes32 hash = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", decisionHash));
        
        bytes32 r;
        bytes32 s;
        uint8 v;
        
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        
        address recovered = ecrecover(hash, v, r, s);
        return recovered == signer || authorizedSigners[recovered];
    }
    
    // ===== 工具函数 =====
    
    /**
     * @notice 计算决策哈希
     */
    function computeDecisionHash(
        string memory poolAddress,
        uint256 apy,
        uint256 riskScore,
        string memory recommendation,
        string memory agentVersion
    ) external pure returns (bytes32) {
        return keccak256(abi.encode(
            poolAddress,
            apy,
            riskScore,
            recommendation,
            agentVersion
        ));
    }
    
    /**
     * @notice 紧急提取 ETH
     */
    function emergencyWithdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
    
    /**
     * @notice 接收 ETH
     */
    receive() external payable {}
}

// ===== 测试部署脚本 =====
// npx hardhat run scripts/deploy.js --network bscTestnet
