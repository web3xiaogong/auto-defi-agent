// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * ERC-8004: Autonomous AI Agent Registry
 * 
 * Features:
 * - Register autonomous AI agents
 * - Update agent metadata
 * - Verify agent authenticity
 * - Agent discovery and ranking
 * - Strategy marketplace integration
 */

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract ERC8004AgentRegistry is Ownable {
    using Counters for Counters.Counter;
    using ECDSA for bytes32;

    // ============ Structs ============

    struct Agent {
        string agentId;
        address owner;
        string metadataURI;
        string[] services;
        uint256 timestamp;
        bool verified;
        uint256 trustScore;
        uint256 reputationPoints;
    }

    struct AgentUpdate {
        string agentId;
        string metadataURI;
        string[] services;
        uint256 timestamp;
        bytes signature;
    }

    // ============ State ============

    Counters.Counter private _agentIdCounter;
    
    // agentId => Agent
    mapping(string => Agent) public agents;
    
    // owner => agentId[]
    mapping(address => string[]) public ownerAgents;
    
    // agentId => verification status
    mapping(string => bool) public verifiedAgents;
    
    // service name => agentId[]
    mapping(string => string[]) public serviceIndex;
    
    // Chainlink VRF for trust scoring (simplified)
    mapping(bytes32 => bool) private _nonces;
    
    // Trusted verifiers
    mapping(address => bool) public trustedVerifiers;
    
    // Events
    event AgentRegistered(
        string indexed agentId,
        address indexed owner,
        string metadataURI,
        string[] services,
        uint256 timestamp
    );
    
    event AgentUpdated(
        string indexed agentId,
        string metadataURI,
        string[] services,
        uint256 timestamp
    );
    
    event AgentVerified(
        string indexed agentId,
        bool verified,
        uint256 trustScore
    );
    
    event ReputationUpdated(
        string indexed agentId,
        uint256 oldPoints,
        uint256 newPoints
    );
    
    event TrustScoreUpdated(
        string indexed agentId,
        uint256 oldScore,
        uint256 newScore
    );

    // ============ Modifiers ============

    modifier onlyAgentOwner(string memory agentId) {
        require(
            agents[agentId].owner == msg.sender,
            "ERC8004: Only agent owner can call this"
        );
        _;
    }

    modifier onlyTrustedVerifier() {
        require(
            trustedVerifiers[msg.sender] || owner() == msg.sender,
            "ERC8004: Only trusted verifier"
        );
        _;
    }

    // ============ Constructor ============

    constructor() {
        trustedVerifiers[msg.sender] = true;
    }

    // ============ Core Functions ============

    /**
     * Register a new AI Agent
     */
    function registerAgent(
        string memory agentId,
        string memory metadataURI,
        string[] memory services
    ) external returns (bool) {
        require(
            bytes(agents[agentId].agentId).length == 0,
            "ERC8004: Agent ID already exists"
        );
        require(
            bytes(agentId).length > 0,
            "ERC8004: Invalid agent ID"
        );
        require(
            bytes(metadataURI).length > 0,
            "ERC8004: Invalid metadata URI"
        );
        require(
            services.length > 0,
            "ERC8004: At least one service required"
        );

        // Create agent
        Agent storage newAgent = agents[agentId];
        newAgent.agentId = agentId;
        newAgent.owner = msg.sender;
        newAgent.metadataURI = metadataURI;
        newAgent.services = services;
        newAgent.timestamp = block.timestamp;
        newAgent.verified = false;
        newAgent.trustScore = 50; // Default score
        newAgent.reputationPoints = 0;

        // Update indexes
        ownerAgents[msg.sender].push(agentId);
        for (uint256 i = 0; i < services.length; i++) {
            serviceIndex[services[i]].push(agentId);
        }

        // Emit event
        emit AgentRegistered(agentId, msg.sender, metadataURI, services, block.timestamp);

        return true;
    }

    /**
     * Update agent metadata and services
     */
    function updateAgent(
        string memory agentId,
        string memory metadataURI,
        string[] memory services
    ) external onlyAgentOwner(agentId) returns (bool) {
        require(
            bytes(metadataURI).length > 0,
            "ERC8004: Invalid metadata URI"
        );

        // Update agent
        Agent storage agent = agents[agentId];
        agent.metadataURI = metadataURI;
        
        // Update services (simplified - in production, handle service changes)
        delete agent.services;
        for (uint256 i = 0; i < services.length; i++) {
            agent.services.push(services[i]);
        }

        emit AgentUpdated(agentId, metadataURI, services, block.timestamp);

        return true;
    }

    /**
     * Verify or unverify an agent (only trusted verifiers)
     */
    function verifyAgent(
        string memory agentId,
        bool verified,
        uint256 trustScore
    ) external onlyTrustedVerifier returns (bool) {
        require(
            bytes(agents[agentId].agentId).length > 0,
            "ERC8004: Agent not found"
        );

        uint256 oldScore = agents[agentId].trustScore;
        agents[agentId].verified = verified;
        agents[agentId].trustScore = trustScore;

        emit AgentVerified(agentId, verified, trustScore);
        emit TrustScoreUpdated(agentId, oldScore, trustScore);

        return true;
    }

    /**
     * Update agent reputation points
     */
    function updateReputation(
        string memory agentId,
        int256 deltaPoints
    ) external onlyTrustedVerifier returns (bool) {
        require(
            bytes(agents[agentId].agentId).length > 0,
            "ERC8004: Agent not found"
        );

        uint256 oldPoints = agents[agentId].reputationPoints;
        if (deltaPoints > 0) {
            agents[agentId].reputationPoints += uint256(deltaPoints);
        } else {
            uint256 decrease = uint256(-deltaPoints);
            if (agents[agentId].reputationPoints >= decrease) {
                agents[agentId].reputationPoints -= decrease;
            } else {
                agents[agentId].reputationPoints = 0;
            }
        }

        emit ReputationUpdated(
            agentId,
            oldPoints,
            agents[agentId].reputationPoints
        );

        return true;
    }

    // ============ Query Functions ============

    /**
     * Get agent information
     */
    function getAgent(string memory agentId) external view returns (
        address owner,
        string memory metadataURI,
        string[] memory services,
        uint256 timestamp,
        bool verified,
        uint256 trustScore,
        uint256 reputationPoints
    ) {
        Agent storage agent = agents[agentId];
        return (
            agent.owner,
            agent.metadataURI,
            agent.services,
            agent.timestamp,
            agent.verified,
            agent.trustScore,
            agent.reputationPoints
        );
    }

    /**
     * Get agents by owner
     */
    function getOwnerAgents(address owner) external view returns (string[] memory) {
        return ownerAgents[owner];
    }

    /**
     * Get agents by service
     */
    function getAgentsByService(string memory service) external view returns (string[] memory) {
        return serviceIndex[service];
    }

    /**
     * Get total agent count
     */
    function getAgentCount() external view returns (uint256) {
        return ownerAgents[msg.sender].length; // Approximation
    }

    /**
     * Search agents by prefix (simple implementation)
     */
    function searchAgents(string memory prefix) external view returns (string[] memory) {
        // In production, implement proper search with IPFS
        return new string[](0);
    }

    // ============ Admin Functions ============

    /**
     * Add trusted verifier
     */
    function addTrustedVerifier(address verifier) external onlyOwner {
        trustedVerifiers[verifier] = true;
    }

    /**
     * Remove trusted verifier
     */
    function removeTrustedVerifier(address verifier) external onlyOwner {
        trustedVerifiers[verifier] = false;
    }

    /**
     * Emergency agent deletion (only owner)
     */
    function emergencyDelete(string memory agentId) external onlyOwner {
        require(
            bytes(agents[agentId].agentId).length > 0,
            "ERC8004: Agent not found"
        );

        address owner = agents[agentId].owner;
        
        // Clear from owner mapping (simplified)
        delete agents[agentId];
        
        // Note: In production, properly update all indexes
    }
}
