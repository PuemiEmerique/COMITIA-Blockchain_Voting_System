// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title COMITIA Voting Contract
 * @dev Smart contract for secure, transparent voting on the blockchain
 * @author COMITIA Development Team
 */

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract VotingContract is AccessControl, ReentrancyGuard, Pausable {
    
    // Role definitions
    bytes32 public constant ELECTION_ADMIN_ROLE = keccak256("ELECTION_ADMIN_ROLE");
    bytes32 public constant VOTER_ROLE = keccak256("VOTER_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    
    // Election structure
    struct Election {
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        bool isActive;
        bool resultsPublished;
        uint256 totalVotes;
        address creator;
        string[] positionIds;
        mapping(string => Position) positions;
    }
    
    // Position structure
    struct Position {
        string title;
        string description;
        uint256 maxVotesPerVoter;
        uint256 availableSeats;
        string[] candidateIds;
        mapping(string => Candidate) candidates;
        mapping(address => bool) hasVoted;
        mapping(string => uint256) voteCount;
    }
    
    // Candidate structure
    struct Candidate {
        string name;
        string party;
        string manifesto;
        address candidateAddress;
        uint256 voteCount;
        bool isActive;
    }
    
    // Vote structure
    struct Vote {
        string electionId;
        string positionId;
        string candidateId;
        address voter;
        uint256 timestamp;
        bytes32 voteHash;
        bool isVerified;
    }
    
    // Mappings
    mapping(string => Election) public elections;
    mapping(address => mapping(string => mapping(string => bool))) public hasVoted; // voter => election => position => bool
    mapping(bytes32 => Vote) public votes;
    mapping(address => bool) public registeredVoters;
    mapping(string => bool) public electionExists;
    
    // Arrays for iteration
    string[] public electionIds;
    bytes32[] public voteHashes;
    
    // Events
    event ElectionCreated(
        string indexed electionId,
        string title,
        address indexed creator,
        uint256 startTime,
        uint256 endTime
    );
    
    event PositionAdded(
        string indexed electionId,
        string indexed positionId,
        string title,
        uint256 maxVotesPerVoter
    );
    
    event CandidateRegistered(
        string indexed electionId,
        string indexed positionId,
        string indexed candidateId,
        string name,
        address candidateAddress
    );
    
    event VoteCast(
        string indexed electionId,
        string indexed positionId,
        string indexed candidateId,
        address voter,
        bytes32 voteHash,
        uint256 timestamp
    );
    
    event ElectionStarted(string indexed electionId);
    event ElectionEnded(string indexed electionId);
    event ResultsPublished(string indexed electionId);
    event VoterRegistered(address indexed voter);
    event VoterRevoked(address indexed voter);
    
    // Modifiers
    modifier onlyElectionAdmin() {
        require(hasRole(ELECTION_ADMIN_ROLE, msg.sender), "Caller is not an election admin");
        _;
    }
    
    modifier onlyRegisteredVoter() {
        require(registeredVoters[msg.sender], "Caller is not a registered voter");
        _;
    }
    
    modifier electionMustExist(string memory electionId) {
        require(electionExists[electionId], "Election does not exist");
        _;
    }
    
    modifier votingMustBeActive(string memory electionId) {
        require(elections[electionId].isActive, "Voting is not active");
        require(block.timestamp >= elections[electionId].startTime, "Voting has not started");
        require(block.timestamp <= elections[electionId].endTime, "Voting has ended");
        _;
    }
    
    modifier hasNotVoted(string memory electionId, string memory positionId) {
        require(!hasVoted[msg.sender][electionId][positionId], "Already voted for this position");
        _;
    }
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ELECTION_ADMIN_ROLE, msg.sender);
    }
    
    /**
     * @dev Register a new voter
     * @param voter Address of the voter to register
     */
    function registerVoter(address voter) external onlyElectionAdmin {
        require(!registeredVoters[voter], "Voter already registered");
        registeredVoters[voter] = true;
        _grantRole(VOTER_ROLE, voter);
        emit VoterRegistered(voter);
    }
    
    /**
     * @dev Revoke voter registration
     * @param voter Address of the voter to revoke
     */
    function revokeVoter(address voter) external onlyElectionAdmin {
        require(registeredVoters[voter], "Voter not registered");
        registeredVoters[voter] = false;
        _revokeRole(VOTER_ROLE, voter);
        emit VoterRevoked(voter);
    }
    
    /**
     * @dev Create a new election
     * @param electionId Unique identifier for the election
     * @param title Title of the election
     * @param description Description of the election
     * @param startTime Start time of voting (Unix timestamp)
     * @param endTime End time of voting (Unix timestamp)
     */
    function createElection(
        string memory electionId,
        string memory title,
        string memory description,
        uint256 startTime,
        uint256 endTime
    ) external onlyElectionAdmin {
        require(!electionExists[electionId], "Election already exists");
        require(startTime < endTime, "Start time must be before end time");
        require(endTime > block.timestamp, "End time must be in the future");
        
        Election storage newElection = elections[electionId];
        newElection.title = title;
        newElection.description = description;
        newElection.startTime = startTime;
        newElection.endTime = endTime;
        newElection.isActive = false;
        newElection.resultsPublished = false;
        newElection.totalVotes = 0;
        newElection.creator = msg.sender;
        
        electionExists[electionId] = true;
        electionIds.push(electionId);
        
        emit ElectionCreated(electionId, title, msg.sender, startTime, endTime);
    }
    
    /**
     * @dev Add a position to an election
     * @param electionId ID of the election
     * @param positionId Unique identifier for the position
     * @param title Title of the position
     * @param description Description of the position
     * @param maxVotesPerVoter Maximum votes a voter can cast for this position
     * @param availableSeats Number of available seats for this position
     */
    function addPosition(
        string memory electionId,
        string memory positionId,
        string memory title,
        string memory description,
        uint256 maxVotesPerVoter,
        uint256 availableSeats
    ) external onlyElectionAdmin electionMustExist(electionId) {
        require(!elections[electionId].isActive, "Cannot modify active election");
        require(maxVotesPerVoter > 0, "Max votes must be greater than 0");
        require(availableSeats > 0, "Available seats must be greater than 0");
        
        Election storage election = elections[electionId];
        Position storage position = election.positions[positionId];
        
        position.title = title;
        position.description = description;
        position.maxVotesPerVoter = maxVotesPerVoter;
        position.availableSeats = availableSeats;
        
        election.positionIds.push(positionId);
        
        emit PositionAdded(electionId, positionId, title, maxVotesPerVoter);
    }
    
    /**
     * @dev Register a candidate for a position
     * @param electionId ID of the election
     * @param positionId ID of the position
     * @param candidateId Unique identifier for the candidate
     * @param name Name of the candidate
     * @param party Political party of the candidate
     * @param manifesto Candidate's manifesto
     * @param candidateAddress Blockchain address of the candidate
     */
    function registerCandidate(
        string memory electionId,
        string memory positionId,
        string memory candidateId,
        string memory name,
        string memory party,
        string memory manifesto,
        address candidateAddress
    ) external onlyElectionAdmin electionMustExist(electionId) {
        require(!elections[electionId].isActive, "Cannot modify active election");
        require(candidateAddress != address(0), "Invalid candidate address");
        
        Election storage election = elections[electionId];
        Position storage position = election.positions[positionId];
        Candidate storage candidate = position.candidates[candidateId];
        
        candidate.name = name;
        candidate.party = party;
        candidate.manifesto = manifesto;
        candidate.candidateAddress = candidateAddress;
        candidate.voteCount = 0;
        candidate.isActive = true;
        
        position.candidateIds.push(candidateId);
        
        emit CandidateRegistered(electionId, positionId, candidateId, name, candidateAddress);
    }
    
    /**
     * @dev Start an election
     * @param electionId ID of the election to start
     */
    function startElection(string memory electionId) external onlyElectionAdmin electionMustExist(electionId) {
        Election storage election = elections[electionId];
        require(!election.isActive, "Election is already active");
        require(block.timestamp >= election.startTime, "Election start time not reached");
        require(election.positionIds.length > 0, "Election must have at least one position");
        
        election.isActive = true;
        emit ElectionStarted(electionId);
    }
    
    /**
     * @dev End an election
     * @param electionId ID of the election to end
     */
    function endElection(string memory electionId) external onlyElectionAdmin electionMustExist(electionId) {
        Election storage election = elections[electionId];
        require(election.isActive, "Election is not active");
        
        election.isActive = false;
        emit ElectionEnded(electionId);
    }
    
    /**
     * @dev Cast a vote
     * @param electionId ID of the election
     * @param positionId ID of the position
     * @param candidateId ID of the candidate
     * @param voteHash Hash of the vote for verification
     */
    function castVote(
        string memory electionId,
        string memory positionId,
        string memory candidateId,
        bytes32 voteHash
    ) external 
        onlyRegisteredVoter 
        nonReentrant 
        whenNotPaused
        electionMustExist(electionId)
        votingMustBeActive(electionId)
        hasNotVoted(electionId, positionId)
    {
        Election storage election = elections[electionId];
        Position storage position = election.positions[positionId];
        Candidate storage candidate = position.candidates[candidateId];
        
        require(candidate.isActive, "Candidate is not active");
        require(voteHash != bytes32(0), "Invalid vote hash");
        
        // Record the vote
        Vote storage vote = votes[voteHash];
        vote.electionId = electionId;
        vote.positionId = positionId;
        vote.candidateId = candidateId;
        vote.voter = msg.sender;
        vote.timestamp = block.timestamp;
        vote.voteHash = voteHash;
        vote.isVerified = true;
        
        // Update vote counts
        hasVoted[msg.sender][electionId][positionId] = true;
        position.hasVoted[msg.sender] = true;
        position.voteCount[candidateId]++;
        candidate.voteCount++;
        election.totalVotes++;
        
        // Store vote hash for iteration
        voteHashes.push(voteHash);
        
        emit VoteCast(electionId, positionId, candidateId, msg.sender, voteHash, block.timestamp);
    }
    
    /**
     * @dev Publish election results
     * @param electionId ID of the election
     */
    function publishResults(string memory electionId) external onlyElectionAdmin electionMustExist(electionId) {
        Election storage election = elections[electionId];
        require(!election.isActive, "Election must be ended first");
        require(!election.resultsPublished, "Results already published");
        
        election.resultsPublished = true;
        emit ResultsPublished(electionId);
    }
    
    /**
     * @dev Verify a vote using its hash
     * @param voteHash Hash of the vote to verify
     * @return Vote details
     */
    function verifyVote(bytes32 voteHash) external view returns (
        string memory electionId,
        string memory positionId,
        string memory candidateId,
        address voter,
        uint256 timestamp,
        bool isVerified
    ) {
        Vote storage vote = votes[voteHash];
        require(vote.voter != address(0), "Vote not found");
        
        return (
            vote.electionId,
            vote.positionId,
            vote.candidateId,
            vote.voter,
            vote.timestamp,
            vote.isVerified
        );
    }
    
    /**
     * @dev Get election details
     * @param electionId ID of the election
     */
    function getElection(string memory electionId) external view electionMustExist(electionId) returns (
        string memory title,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        bool isActive,
        bool resultsPublished,
        uint256 totalVotes,
        address creator
    ) {
        Election storage election = elections[electionId];
        return (
            election.title,
            election.description,
            election.startTime,
            election.endTime,
            election.isActive,
            election.resultsPublished,
            election.totalVotes,
            election.creator
        );
    }
    
    /**
     * @dev Get candidate vote count
     * @param electionId ID of the election
     * @param positionId ID of the position
     * @param candidateId ID of the candidate
     */
    function getCandidateVoteCount(
        string memory electionId,
        string memory positionId,
        string memory candidateId
    ) external view electionMustExist(electionId) returns (uint256) {
        return elections[electionId].positions[positionId].candidates[candidateId].voteCount;
    }
    
    /**
     * @dev Get total number of elections
     */
    function getElectionCount() external view returns (uint256) {
        return electionIds.length;
    }
    
    /**
     * @dev Get total number of votes cast
     */
    function getTotalVotesCast() external view returns (uint256) {
        return voteHashes.length;
    }
    
    /**
     * @dev Check if a voter has voted in a specific position
     * @param voter Address of the voter
     * @param electionId ID of the election
     * @param positionId ID of the position
     */
    function hasVoterVoted(
        address voter,
        string memory electionId,
        string memory positionId
    ) external view returns (bool) {
        return hasVoted[voter][electionId][positionId];
    }
    
    /**
     * @dev Emergency pause function
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Emergency unpause function
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Get contract version
     */
    function getVersion() external pure returns (string memory) {
        return "1.0.0";
    }
}
