/**
 * COMITIA Blockchain Integration
 * Handles Ethereum blockchain interactions for voting
 */

class BlockchainManager {
    constructor() {
        this.provider = null;
        this.signer = null;
        this.contract = null;
        this.contractAddress = null;
        this.isConnected = false;
        
        // Contract ABI (simplified for demo)
        this.contractABI = [
            "function castVote(string memory electionId, string memory positionId, string memory candidateId, bytes32 voteHash) external",
            "function verifyVote(bytes32 voteHash) external view returns (string memory, string memory, string memory, address, uint256, bool)",
            "function getElection(string memory electionId) external view returns (string memory, string memory, uint256, uint256, bool, bool, uint256, address)",
            "function getCandidateVoteCount(string memory electionId, string memory positionId, string memory candidateId) external view returns (uint256)",
            "function hasVoterVoted(address voter, string memory electionId, string memory positionId) external view returns (bool)",
            "event VoteCast(string indexed electionId, string indexed positionId, string indexed candidateId, address voter, bytes32 voteHash, uint256 timestamp)"
        ];
    }

    async initialize() {
        try {
            // Check if MetaMask is installed
            if (typeof window.ethereum === 'undefined') {
                throw new Error('MetaMask is not installed. Please install MetaMask to use blockchain features.');
            }

            // Initialize provider
            this.provider = new ethers.providers.Web3Provider(window.ethereum);
            
            // Request account access
            await this.connectWallet();
            
            // Get contract address from backend
            await this.loadContractInfo();
            
            // console.log removed ('Blockchain manager initialized successfully');
            return true;
        } catch (error) {
            // console.error removed ('Blockchain initialization error:', error);
            throw error;
        }
    }

    async connectWallet() {
        try {
            // Request account access
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });

            if (accounts.length === 0) {
                throw new Error('No accounts found. Please connect your wallet.');
            }

            this.signer = this.provider.getSigner();
            this.isConnected = true;
            
            // Listen for account changes
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length === 0) {
                    this.disconnect();
                } else {
                    this.signer = this.provider.getSigner();
                }
            });

            // Listen for chain changes
            window.ethereum.on('chainChanged', () => {
                window.location.reload();
            });

            const address = await this.signer.getAddress();
            // console.log removed ('Wallet connected:', address);
            
            return address;
        } catch (error) {
            // console.error removed ('Wallet connection error:', error);
            throw error;
        }
    }

    async loadContractInfo() {
        try {
            // Get contract info from backend
            const contractInfo = await window.comitiaAPI.makeRequest('/blockchain/contract-info/');
            
            if (!contractInfo.address) {
                throw new Error('Voting contract not deployed');
            }

            this.contractAddress = contractInfo.address;
            this.contract = new ethers.Contract(
                this.contractAddress,
                this.contractABI,
                this.signer
            );

            // console.log removed ('Contract loaded:', this.contractAddress);
        } catch (error) {
            // console.error removed ('Contract loading error:', error);
            throw error;
        }
    }

    async getNetworkInfo() {
        try {
            const network = await this.provider.getNetwork();
            const balance = await this.signer.getBalance();
            const address = await this.signer.getAddress();

            return {
                network: network.name,
                chainId: network.chainId,
                address,
                balance: ethers.utils.formatEther(balance)
            };
        } catch (error) {
            // console.error removed ('Network info error:', error);
            throw error;
        }
    }

    async castVoteOnBlockchain(electionId, positionId, candidateId, voteData) {
        try {
            if (!this.isConnected || !this.contract) {
                throw new Error('Blockchain not connected');
            }

            // Create vote hash
            const voteHash = ethers.utils.keccak256(
                ethers.utils.toUtf8Bytes(JSON.stringify(voteData))
            );

            // Estimate gas
            const gasEstimate = await this.contract.estimateGas.castVote(
                electionId,
                positionId,
                candidateId,
                voteHash
            );

            // Add 20% buffer to gas estimate
            const gasLimit = gasEstimate.mul(120).div(100);

            // Cast vote on blockchain
            const transaction = await this.contract.castVote(
                electionId,
                positionId,
                candidateId,
                voteHash,
                { gasLimit }
            );

            // console.log removed ('Vote transaction submitted:', transaction.hash);

            // Wait for confirmation
            const receipt = await transaction.wait();
            
            // console.log removed ('Vote confirmed on blockchain:', receipt.transactionHash);

            return {
                success: true,
                transactionHash: receipt.transactionHash,
                blockNumber: receipt.blockNumber,
                gasUsed: receipt.gasUsed.toString(),
                voteHash: voteHash
            };

        } catch (error) {
            // console.error removed ('Blockchain vote casting error:', error);
            
            // Parse error message
            let errorMessage = error.message;
            if (error.reason) {
                errorMessage = error.reason;
            } else if (error.data && error.data.message) {
                errorMessage = error.data.message;
            }

            throw new Error(`Blockchain vote failed: ${errorMessage}`);
        }
    }

    async verifyVoteOnBlockchain(voteHash) {
        try {
            if (!this.contract) {
                throw new Error('Contract not loaded');
            }

            const voteInfo = await this.contract.verifyVote(voteHash);
            
            return {
                electionId: voteInfo[0],
                positionId: voteInfo[1],
                candidateId: voteInfo[2],
                voter: voteInfo[3],
                timestamp: voteInfo[4].toNumber(),
                isVerified: voteInfo[5]
            };
        } catch (error) {
            // console.error removed ('Vote verification error:', error);
            throw error;
        }
    }

    async getElectionInfo(electionId) {
        try {
            if (!this.contract) {
                throw new Error('Contract not loaded');
            }

            const electionInfo = await this.contract.getElection(electionId);
            
            return {
                title: electionInfo[0],
                description: electionInfo[1],
                startTime: electionInfo[2].toNumber(),
                endTime: electionInfo[3].toNumber(),
                isActive: electionInfo[4],
                resultsPublished: electionInfo[5],
                totalVotes: electionInfo[6].toNumber(),
                creator: electionInfo[7]
            };
        } catch (error) {
            // console.error removed ('Election info error:', error);
            throw error;
        }
    }

    async getCandidateVotes(electionId, positionId, candidateId) {
        try {
            if (!this.contract) {
                throw new Error('Contract not loaded');
            }

            const voteCount = await this.contract.getCandidateVoteCount(
                electionId,
                positionId,
                candidateId
            );

            return voteCount.toNumber();
        } catch (error) {
            // console.error removed ('Candidate votes error:', error);
            throw error;
        }
    }

    async hasUserVoted(electionId, positionId) {
        try {
            if (!this.contract || !this.signer) {
                throw new Error('Contract or signer not available');
            }

            const userAddress = await this.signer.getAddress();
            const hasVoted = await this.contract.hasVoterVoted(
                userAddress,
                electionId,
                positionId
            );

            return hasVoted;
        } catch (error) {
            // console.error removed ('Vote check error:', error);
            throw error;
        }
    }

    async getTransactionStatus(transactionHash) {
        try {
            const transaction = await this.provider.getTransaction(transactionHash);
            const receipt = await this.provider.getTransactionReceipt(transactionHash);

            if (!transaction) {
                return { status: 'not_found' };
            }

            if (!receipt) {
                return { 
                    status: 'pending',
                    transaction: {
                        hash: transaction.hash,
                        from: transaction.from,
                        to: transaction.to,
                        value: ethers.utils.formatEther(transaction.value),
                        gasPrice: ethers.utils.formatUnits(transaction.gasPrice, 'gwei')
                    }
                };
            }

            return {
                status: receipt.status === 1 ? 'confirmed' : 'failed',
                transaction: {
                    hash: transaction.hash,
                    from: transaction.from,
                    to: transaction.to,
                    value: ethers.utils.formatEther(transaction.value),
                    gasPrice: ethers.utils.formatUnits(transaction.gasPrice, 'gwei')
                },
                receipt: {
                    blockNumber: receipt.blockNumber,
                    blockHash: receipt.blockHash,
                    gasUsed: receipt.gasUsed.toString(),
                    effectiveGasPrice: ethers.utils.formatUnits(receipt.effectiveGasPrice, 'gwei')
                }
            };
        } catch (error) {
            // console.error removed ('Transaction status error:', error);
            throw error;
        }
    }

    async listenForVoteEvents(electionId, callback) {
        try {
            if (!this.contract) {
                throw new Error('Contract not loaded');
            }

            // Create filter for VoteCast events
            const filter = this.contract.filters.VoteCast(electionId);
            
            // Listen for events
            this.contract.on(filter, (electionId, positionId, candidateId, voter, voteHash, timestamp, event) => {
                callback({
                    electionId,
                    positionId,
                    candidateId,
                    voter,
                    voteHash,
                    timestamp: timestamp.toNumber(),
                    transactionHash: event.transactionHash,
                    blockNumber: event.blockNumber
                });
            });

            // console.log removed ('Listening for vote events for election:', electionId);
        } catch (error) {
            // console.error removed ('Event listening error:', error);
            throw error;
        }
    }

    async stopListeningForEvents() {
        if (this.contract) {
            this.contract.removeAllListeners();
            // console.log removed ('Stopped listening for blockchain events');
        }
    }

    async switchToCorrectNetwork() {
        try {
            // Get required network from backend
            const networkInfo = await window.comitiaAPI.getNetworkStatus();
            const requiredChainId = networkInfo.chain_id;

            const currentNetwork = await this.provider.getNetwork();
            
            if (currentNetwork.chainId !== requiredChainId) {
                // Request network switch
                await window.ethereum.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: ethers.utils.hexValue(requiredChainId) }]
                });
            }
        } catch (error) {
            // console.error removed ('Network switch error:', error);
            throw error;
        }
    }

    disconnect() {
        this.provider = null;
        this.signer = null;
        this.contract = null;
        this.isConnected = false;
        // console.log removed ('Blockchain disconnected');
    }

    // Utility methods
    formatAddress(address) {
        if (!address) return '';
        return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    }

    formatHash(hash) {
        if (!hash) return '';
        return `${hash.substring(0, 10)}...${hash.substring(hash.length - 8)}`;
    }

    async getGasPrice() {
        try {
            const gasPrice = await this.provider.getGasPrice();
            return ethers.utils.formatUnits(gasPrice, 'gwei');
        } catch (error) {
            // console.error removed ('Gas price error:', error);
            return '0';
        }
    }

    async estimateVotingCost(electionId, positionId, candidateId) {
        try {
            if (!this.contract) {
                throw new Error('Contract not loaded');
            }

            const voteHash = ethers.utils.keccak256(
                ethers.utils.toUtf8Bytes('dummy_vote_data')
            );

            const gasEstimate = await this.contract.estimateGas.castVote(
                electionId,
                positionId,
                candidateId,
                voteHash
            );

            const gasPrice = await this.provider.getGasPrice();
            const cost = gasEstimate.mul(gasPrice);

            return {
                gasEstimate: gasEstimate.toString(),
                gasPrice: ethers.utils.formatUnits(gasPrice, 'gwei'),
                costInEth: ethers.utils.formatEther(cost),
                costInWei: cost.toString()
            };
        } catch (error) {
            // console.error removed ('Cost estimation error:', error);
            throw error;
        }
    }
}

// Create global blockchain manager instance
window.blockchainManager = new BlockchainManager();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BlockchainManager;
}
