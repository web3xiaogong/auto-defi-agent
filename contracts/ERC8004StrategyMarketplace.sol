// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * ERC-8004 Strategy Marketplace
 * 
 * Features:
 * - Publish strategies for sale
 * - Buy strategies
 * - Track sales and royalties
 * - Ratings and reviews
 */

contract ERC8004StrategyMarketplace is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    // ============ Structs ============

    struct Strategy {
        string strategyId;
        address creator;
        string metadataURI;
        string name;
        string description;
        string poolName;
        string chain;
        uint256 price; // in wei
        uint256 royaltyPercent;
        uint256 salesCount;
        uint256 totalRevenue;
        uint256 ratingSum;
        uint256 ratingCount;
        uint256 timestamp;
        bool active;
    }

    struct Rating {
        string strategyId;
        address rater;
        uint8 rating; // 1-5
        string review;
        uint256 timestamp;
    }

    // ============ State ============

    Counters.Counter private _strategyIdCounter;
    
    // strategyId => Strategy
    mapping(string => Strategy) public strategies;
    
    // creator => strategyId[]
    mapping(address => string[]) public creatorStrategies;
    
    // strategyId => Rating[]
    mapping(string => Rating[]) public ratings;
    
    // buyer => strategyId[]
    mapping(address => string[]) public purchases;
    
    // Strategy sale event
    event StrategyPublished(
        string indexed strategyId,
        address indexed creator,
        string name,
        uint256 price,
        uint256 timestamp
    );
    
    event StrategySold(
        string indexed strategyId,
        address indexed buyer,
        uint256 price,
        uint256 timestamp
    );
    
    event RatingAdded(
        string indexed strategyId,
        address indexed rater,
        uint8 rating,
        uint256 timestamp
    );
    
    event StrategyStatusChanged(
        string indexed strategyId,
        bool active
    );

    // ============ Constructor ============

    constructor() {}

    // ============ Core Functions ============

    /**
     * Publish a new strategy
     */
    function publishStrategy(
        string memory strategyId,
        string memory metadataURI,
        string memory name,
        string memory description,
        string memory poolName,
        string memory chain,
        uint256 price,
        uint256 royaltyPercent
    ) external nonReentrant returns (bool) {
        require(
            bytes(strategies[strategyId].strategyId).length == 0,
            "ERC8004: Strategy ID already exists"
        );
        require(
            bytes(name).length > 0,
            "ERC8004: Invalid strategy name"
        );
        require(
            price > 0,
            "ERC8004: Price must be greater than 0"
        );
        require(
            royaltyPercent <= 50,
            "ERC8004: Royalty cannot exceed 50%"
        );

        // Create strategy
        Strategy storage newStrategy = strategies[strategyId];
        newStrategy.strategyId = strategyId;
        newStrategy.creator = msg.sender;
        newStrategy.metadataURI = metadataURI;
        newStrategy.name = name;
        newStrategy.description = description;
        newStrategy.poolName = poolName;
        newStrategy.chain = chain;
        newStrategy.price = price;
        newStrategy.royaltyPercent = royaltyPercent;
        newStrategy.salesCount = 0;
        newStrategy.totalRevenue = 0;
        newStrategy.ratingSum = 0;
        newStrategy.ratingCount = 0;
        newStrategy.timestamp = block.timestamp;
        newStrategy.active = true;

        // Update indexes
        creatorStrategies[msg.sender].push(strategyId);

        emit StrategyPublished(strategyId, msg.sender, name, price, block.timestamp);

        return true;
    }

    /**
     * Buy a strategy
     */
    function buyStrategy(string memory strategyId) external payable nonReentrant returns (bool) {
        require(
            bytes(strategies[strategyId].strategyId).length > 0,
            "ERC8004: Strategy not found"
        );
        require(
            strategies[strategyId].active,
            "ERC8004: Strategy is not active"
        );
        require(
            msg.value >= strategies[strategyId].price,
            "ERC8004: Insufficient payment"
        );

        Strategy storage strategy = strategies[strategyId];
        address creator = strategy.creator;
        uint256 price = strategy.price;
        uint256 royalty = (price * strategy.royaltyPercent) / 100;

        // Transfer payment
        payable(creator).transfer(price - (price - royalty)); // Simplified
        
        // Update strategy stats
        strategy.salesCount++;
        strategy.totalRevenue += price;

        // Record purchase
        purchases[msg.sender].push(strategyId);

        emit StrategySold(strategyId, msg.sender, price, block.timestamp);

        // Refund excess
        if (msg.value > price) {
            payable(msg.sender).transfer(msg.value - price);
        }

        return true;
    }

    /**
     * Add rating and review
     */
    function addRating(
        string memory strategyId,
        uint8 rating,
        string memory review
    ) external returns (bool) {
        require(
            bytes(strategies[strategyId].strategyId).length > 0,
            "ERC8004: Strategy not found"
        );
        require(
            rating >= 1 && rating <= 5,
            "ERC8004: Rating must be 1-5"
        );

        // Check if buyer has purchased (simplified - in production, verify ownership)
        
        Rating memory newRating = Rating({
            strategyId: strategyId,
            rater: msg.sender,
            rating: rating,
            review: review,
            timestamp: block.timestamp
        });
        
        ratings[strategyId].push(newRating);
        
        // Update strategy rating
        Strategy storage strategy = strategies[strategyId];
        strategy.ratingSum += rating;
        strategy.ratingCount++;

        emit RatingAdded(strategyId, msg.sender, rating, block.timestamp);

        return true;
    }

    // ============ Query Functions ============

    /**
     * Get strategy details
     */
    function getStrategy(string memory strategyId) external view returns (
        address creator,
        string memory metadataURI,
        string memory name,
        string memory description,
        string memory poolName,
        string memory chain,
        uint256 price,
        uint256 royaltyPercent,
        uint256 salesCount,
        uint256 totalRevenue,
        uint256 averageRating,
        bool active
    ) {
        Strategy storage strategy = strategies[strategyId];
        uint256 avgRating = strategy.ratingCount > 0 
            ? strategy.ratingSum / strategy.ratingCount 
            : 0;
        
        return (
            strategy.creator,
            strategy.metadataURI,
            strategy.name,
            strategy.description,
            strategy.poolName,
            strategy.chain,
            strategy.price,
            strategy.royaltyPercent,
            strategy.salesCount,
            strategy.totalRevenue,
            avgRating,
            strategy.active
        );
    }

    /**
     * Get creator's strategies
     */
    function getCreatorStrategies(address creator) external view returns (string[] memory) {
        return creatorStrategies[creator];
    }

    /**
     * Get buyer's purchases
     */
    function getPurchases(address buyer) external view returns (string[] memory) {
        return purchases[buyer];
    }

    /**
     * Get strategy ratings
     */
    function getStrategyRatings(string memory strategyId) external view returns (Rating[] memory) {
        return ratings[strategyId];
    }

    /**
     * Search strategies by name
     */
    function searchStrategies(string memory query) external view returns (string[] memory) {
        // In production, implement proper search
        return new string[](0);
    }

    /**
     * Get top strategies by sales
     */
    function getTopStrategies(uint256 limit) external view returns (string[] memory) {
        // Simplified - in production, implement proper sorting
        return new string[](limit);
    }

    // ============ Admin Functions ============

    /**
     * Toggle strategy active status
     */
    function toggleStrategyStatus(string memory strategyId) external returns (bool) {
        require(
            bytes(strategies[strategyId].strategyId).length > 0,
            "ERC8004: Strategy not found"
        );

        require(
            strategies[strategyId].creator == msg.sender || owner() == msg.sender,
            "ERC8004: Only creator or owner can toggle"
        );

        strategies[strategyId].active = !strategies[strategyId].active;

        emit StrategyStatusChanged(strategyId, strategies[strategyId].active);

        return true;
    }

    /**
     * Emergency withdrawal (only owner)
     */
    function emergencyWithdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}
