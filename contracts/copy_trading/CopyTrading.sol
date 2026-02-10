// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title CopyTradingRegistry
 * @notice 跟单交易注册表 - 管理交易者和跟随者关系
 * @dev Good Vibes Only: OpenClaw Edition Hackathon
 */
contract CopyTradingRegistry {
    
    // ===== 结构体 =====
    
    struct Trader {
        string name;
        bool isRegistered;
        uint256 totalFollowers;
        uint256 totalVolume;
        int256 totalPnl;
        uint256 createdAt;
    }
    
    struct Follower {
        address traderAddress;
        uint256 allocationPercent;  // 0-100
        uint256 minInvestment;
        uint256 maxInvestment;
        bool isActive;
        uint256 joinedAt;
    }
    
    struct CopyOrder {
        address trader;
        address follower;
        address poolAddress;
        string poolName;
        uint8 orderType;  // 0=BUY, 1=SELL, 2=SWAP
        uint256 amountUsd;
        uint256 executedAt;
        bool isExecuted;
        int256 pnl;
    }
    
    // ===== 状态变量 =====
    
    mapping(address => Trader) public traders;
    mapping(address => Follower[]) public followers;
    mapping(bytes32 => CopyOrder) public orders;
    
    address[] public traderList;
    uint256 public orderCount;
    
    // 事件
    event TraderRegistered(address indexed trader, string name);
    event TraderUpdated(address indexed trader, uint256 totalFollowers, int256 totalPnl);
    event FollowerJoined(address indexed follower, address indexed trader, uint256 allocation);
    event FollowerLeft(address indexed follower, address indexed trader);
    event OrderCreated(bytes32 indexed orderId, address indexed trader, address indexed follower);
    event OrderExecuted(bytes32 indexed orderId, int256 pnl);
    event RewardsDistributed(address indexed trader, uint256 reward);
    
    // ===== 修饰符 =====
    
    modifier onlyRegisteredTrader() {
        require(traders[msg.sender].isRegistered, "Not registered trader");
        _;
    }
    
    // ===== 交易者函数 =====
    
    /**
     * @notice 注册为交易者
     */
    function registerTrader(string memory name) external {
        require(!traders[msg.sender].isRegistered, "Already registered");
        
        traders[msg.sender] = Trader({
            name: name,
            isRegistered: true,
            totalFollowers: 0,
            totalVolume: 0,
            totalPnl: 0,
            createdAt: block.timestamp
        });
        
        traderList.push(msg.sender);
        
        emit TraderRegistered(msg.sender, name);
    }
    
    /**
     * @notice 更新交易者统计
     */
    function updateTraderStats(uint256 additionalVolume, int256 pnl) external onlyRegisteredTrader {
        Trader storage trader = traders[msg.sender];
        trader.totalVolume += additionalVolume;
        trader.totalPnl += pnl;
        
        emit TraderUpdated(msg.sender, trader.totalFollowers, trader.totalPnl);
    }
    
    /**
     * @notice 获取交易者
     */
    function getTrader(address traderAddress) external view returns (
        string memory name,
        uint256 totalFollowers,
        uint256 totalVolume,
        int256 totalPnl,
        bool isRegistered
    ) {
        Trader storage t = traders[traderAddress];
        return (t.name, t.totalFollowers, t.totalVolume, t.totalPnl, t.isRegistered);
    }
    
    // ===== 跟随者函数 =====
    
    /**
     * @notice 跟随交易者
     */
    function followTrader(
        address traderAddress,
        uint256 allocationPercent,
        uint256 minInvestment,
        uint256 maxInvestment
    ) external {
        require(traders[traderAddress].isRegistered, "Trader not registered");
        require(msg.sender != traderAddress, "Cannot follow yourself");
        require(allocationPercent > 0 && allocationPercent <= 100, "Invalid allocation");
        
        Follower memory newFollower = Follower({
            traderAddress: traderAddress,
            allocationPercent: allocationPercent,
            minInvestment: minInvestment,
            maxInvestment: maxInvestment,
            isActive: true,
            joinedAt: block.timestamp
        });
        
        followers[traderAddress].push(newFollower);
        traders[traderAddress].totalFollowers++;
        
        emit FollowerJoined(msg.sender, traderAddress, allocationPercent);
    }
    
    /**
     * @notice 取消跟随
     */
    function unfollowTrader(address traderAddress) external {
        Follower[] storage followerList = followers[traderAddress];
        
        for (uint256 i = 0; i < followerList.length; i++) {
            if (followerList[i].traderAddress == msg.sender) {
                followerList[i].isActive = false;
                traders[traderAddress].totalFollowers--;
                emit FollowerLeft(msg.sender, traderAddress);
                return;
            }
        }
    }
    
    /**
     * @notice 获取跟随者数量
     */
    function getFollowerCount(address traderAddress) external view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < followers[traderAddress].length; i++) {
            if (followers[traderAddress][i].isActive) {
                count++;
            }
        }
        return count;
    }
    
    // ===== 订单函数 =====
    
    /**
     * @notice 创建复制订单 (由交易者调用)
     */
    function createCopyOrder(
        address follower,
        address poolAddress,
        string memory poolName,
        uint8 orderType,
        uint256 amountUsd
    ) external returns (bytes32 orderId) {
        require(traders[msg.sender].isRegistered, "Not registered trader");
        
        // 生成订单 ID
        orderId = keccak256(abi.encodePacked(
            msg.sender,
            follower,
            poolAddress,
            orderCount,
            block.timestamp
        ));
        
        orders[orderId] = CopyOrder({
            trader: msg.sender,
            follower: follower,
            poolAddress: poolAddress,
            poolName: poolName,
            orderType: orderType,
            amountUsd: amountUsd,
            executedAt: 0,
            isExecuted: false,
            pnl: 0
        });
        
        orderCount++;
        
        emit OrderCreated(orderId, msg.sender, follower);
        
        return orderId;
    }
    
    /**
     * @notice 执行订单 (由跟随者或合约调用)
     */
    function executeOrder(bytes32 orderId, int256 pnl) external {
        CopyOrder storage order = orders[orderId];
        require(order.trader != address(0), "Invalid order");
        require(!order.isExecuted, "Already executed");
        require(order.follower == msg.sender, "Not the follower");
        
        order.isExecuted = true;
        order.executedAt = block.timestamp;
        order.pnl = pnl;
        
        // 更新交易者统计
        traders[order.trader].totalVolume += order.amountUsd;
        traders[order.trader].totalPnl += pnl;
        
        emit OrderExecuted(orderId, pnl);
    }
    
    /**
     * @notice 获取订单
     */
    function getOrder(bytes32 orderId) external view returns (
        address trader,
        address follower,
        address poolAddress,
        string memory poolName,
        uint8 orderType,
        uint256 amountUsd,
        bool isExecuted,
        int256 pnl
    ) {
        CopyOrder storage order = orders[orderId];
        return (
            order.trader,
            order.follower,
            order.poolAddress,
            order.poolName,
            order.orderType,
            order.amountUsd,
            order.isExecuted,
            order.pnl
        );
    }
    
    // ===== 收益分成 =====
    
    /**
     * @notice 分配收益给交易者
     */
    function distributeRewards(bytes32[] memory orderIds, uint256 rewardPercent) external {
        require(rewardPercent <= 20, "Max 20% reward");
        
        for (uint256 i = 0; i < orderIds.length; i++) {
            CopyOrder storage order = orders[orderIds[i]];
            if (!order.isExecuted || order.pnl <= 0) continue;
            
            uint256 reward = uint256(order.pnl) * rewardPercent / 100;
            
            // 奖励交易者
            // 注意: 这里应该发送 ETH 或代币
            emit RewardsDistributed(order.trader, reward);
        }
    }
    
    // ===== 查询函数 =====
    
    /**
     * @notice 获取排行榜
     */
    function getLeaderboard(uint256 start, uint256 limit) external view returns (
        address[] memory traderAddresses,
        int256[] memory scores
    ) {
        uint256 end = start + limit;
        if (end > traderList.length) end = traderList.length;
        
        address[] memory result = new address[](end - start);
        int256[] memory scoresResult = new int256[](end - start);
        
        for (uint256 i = start; i < end; i++) {
            address traderAddr = traderList[i];
            Trader storage t = traders[traderAddr];
            
            // 简单评分: Pnl * 10 + Followers * 100
            result[i - start] = traderAddr;
            scoresResult[i - start] = t.totalPnl * 10 + int256(t.totalFollowers) * 100;
        }
        
        return (result, scoresResult);
    }
    
    /**
     * @notice 获取交易者总数
     */
    function getTraderCount() external view returns (uint256) {
        return traderList.length;
    }
}

// ===== 收益分成合约 =====
contract CopyTradingRewards {
    
    struct Reward {
        uint256 period;
        uint256 totalRewards;
        uint256 distributed;
        mapping(address => uint256) traderRewards;
    }
    
    mapping(uint256 => Reward) public rewards;
    uint256 public currentPeriod;
    
    address public registry;
    
    event RewardsAdded(uint256 period, uint256 amount);
    event RewardsClaimed(uint256 period, address trader, uint256 amount);
    
    constructor(address _registry) {
        registry = _registry;
        currentPeriod = 1;
    }
    
    /**
     * @notice 添加奖励
     */
    function addRewards() external payable {
        require(msg.value > 0, "No rewards");
        
        Reward storage r = rewards[currentPeriod];
        r.totalRewards += msg.value;
        
        emit RewardsAdded(currentPeriod, msg.value);
    }
    
    /**
     * @notice 交易者领取奖励
     */
    function claimRewards(uint256 period) external {
        // 需要与 Registry 合约交互验证
        // 简化版: 直接领取
        require(period < currentPeriod, "Period not ended");
        
        // 计算奖励逻辑...
        emit RewardsClaimed(period, msg.sender, 0);
    }
    
    /**
     * @notice 结束当前周期
     */
    function endPeriod() external {
        currentPeriod++;
    }
}
