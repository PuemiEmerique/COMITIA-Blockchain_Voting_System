/**
 * COMITIA API Integration Layer
 * Handles all communication with the Django backend
 */

class ComitiaAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('comitia_token');
        this.user = JSON.parse(localStorage.getItem('comitia_user') || 'null');
    }

    // Helper method for making authenticated requests
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add authentication token if available
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Authentication Methods
    async register(userData) {
        const response = await this.makeRequest('/accounts/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        return response;
    }

    async login(username, password) {
        const response = await this.makeRequest('/accounts/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.access) {
            this.token = response.access;
            this.user = response.user;
            localStorage.setItem('comitia_token', this.token);
            localStorage.setItem('comitia_user', JSON.stringify(this.user));
        }

        return response;
    }

    async logout() {
        try {
            await this.makeRequest('/accounts/logout/', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.token = null;
            this.user = null;
            localStorage.removeItem('comitia_token');
            localStorage.removeItem('comitia_user');
        }
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('comitia_refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await this.makeRequest('/accounts/token/refresh/', {
            method: 'POST',
            body: JSON.stringify({ refresh: refreshToken })
        });

        this.token = response.access;
        localStorage.setItem('comitia_token', this.token);
        return response;
    }

    // User Profile Methods
    async getProfile() {
        return await this.makeRequest('/accounts/profile/');
    }

    async updateProfile(profileData) {
        return await this.makeRequest('/accounts/profile/', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    async changePassword(passwordData) {
        return await this.makeRequest('/accounts/change-password/', {
            method: 'POST',
            body: JSON.stringify(passwordData)
        });
    }

    // Voter Registration Methods
    async applyForVoterRegistration(applicationData) {
        return await this.makeRequest('/accounts/voter-pre-enrollment/', {
            method: 'POST',
            body: JSON.stringify(applicationData)
        });
    }

    async getVoterApplicationStatus() {
        return await this.makeRequest('/accounts/voter-pre-enrollment/');
    }

    // Candidate Methods
    async applyCandidacy(candidacyData) {
        return await this.makeRequest('/accounts/candidate-application/', {
            method: 'POST',
            body: JSON.stringify(candidacyData)
        });
    }

    async getCandidacyApplications() {
        return await this.makeRequest('/accounts/candidate-application/');
    }

    // Election Methods
    async getElections(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.makeRequest(`/elections/?${params}`);
    }

    async getElection(electionId) {
        return await this.makeRequest(`/elections/${electionId}/`);
    }

    async createElection(electionData) {
        return await this.makeRequest('/elections/create/', {
            method: 'POST',
            body: JSON.stringify(electionData)
        });
    }

    async updateElection(electionId, electionData) {
        return await this.makeRequest(`/elections/${electionId}/update/`, {
            method: 'PUT',
            body: JSON.stringify(electionData)
        });
    }

    async getElectionCandidates(electionId, filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.makeRequest(`/elections/${electionId}/candidates/?${params}`);
    }

    async registerForElection(electionId, candidateData) {
        return await this.makeRequest(`/elections/${electionId}/register-candidate/`, {
            method: 'POST',
            body: JSON.stringify(candidateData)
        });
    }

    async getElectionResults(electionId) {
        return await this.makeRequest(`/elections/${electionId}/results/`);
    }

    async publishResults(electionId) {
        return await this.makeRequest(`/elections/${electionId}/publish-results/`, {
            method: 'POST'
        });
    }

    // Candidate Management (Electoral Commission)
    async getPendingCandidates() {
        return await this.makeRequest('/elections/pending-candidates/');
    }

    async approveCandidate(candidateId) {
        return await this.makeRequest(`/elections/candidates/${candidateId}/approve/`, {
            method: 'POST'
        });
    }

    async rejectCandidate(candidateId, reason) {
        return await this.makeRequest(`/elections/candidates/${candidateId}/reject/`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }

    // Voting Methods
    async checkVoterEligibility(electionId) {
        return await this.makeRequest(`/elections/${electionId}/eligibility/`);
    }

    async getBallot(electionId) {
        return await this.makeRequest(`/elections/${electionId}/ballot/`);
    }

    async startVotingSession(electionId) {
        return await this.makeRequest(`/voting/sessions/start/${electionId}/`, {
            method: 'POST'
        });
    }

    async verifyBiometric(sessionId, biometricData) {
        return await this.makeRequest(`/voting/sessions/${sessionId}/verify-biometric/`, {
            method: 'POST',
            body: JSON.stringify(biometricData)
        });
    }

    async castVote(voteData) {
        return await this.makeRequest('/voting/cast-vote/', {
            method: 'POST',
            body: JSON.stringify(voteData)
        });
    }

    async getMyVotes() {
        return await this.makeRequest('/voting/my-votes/');
    }

    async verifyVote(verificationCode) {
        return await this.makeRequest(`/voting/verify-vote/${verificationCode}/`);
    }

    async getVoteReceipt(voteId) {
        return await this.makeRequest(`/voting/receipt/${voteId}/`);
    }

    // Biometric Methods
    async registerBiometric(biometricData) {
        return await this.makeRequest('/biometrics/register/', {
            method: 'POST',
            body: JSON.stringify(biometricData)
        });
    }

    async verifyBiometricAuth(biometricData) {
        return await this.makeRequest('/biometrics/verify/', {
            method: 'POST',
            body: JSON.stringify(biometricData)
        });
    }

    async getBiometricStatus() {
        return await this.makeRequest('/biometrics/status/');
    }

    // Blockchain Methods
    async getBlockchainStatus(transactionHash) {
        return await this.makeRequest(`/voting/blockchain/status/${transactionHash}/`);
    }

    async verifyOnBlockchain(voteHash) {
        return await this.makeRequest(`/voting/blockchain/verify/${voteHash}/`);
    }

    async getNetworkStatus() {
        return await this.makeRequest('/blockchain/network-status/');
    }

    // Statistics Methods (Electoral Commission)
    async getElectionStatistics() {
        return await this.makeRequest('/elections/statistics/');
    }

    async getVotingStatistics(electionId) {
        return await this.makeRequest(`/voting/statistics/${electionId}/`);
    }

    // Voter Official Methods
    async getPendingRegistrations() {
        return await this.makeRequest('/accounts/pending-voter-registrations/');
    }

    async approveVoterRegistration(userId) {
        return await this.makeRequest(`/accounts/approve-voter/${userId}/`, {
            method: 'POST'
        });
    }

    async rejectVoterRegistration(userId, reason) {
        return await this.makeRequest(`/accounts/reject-voter/${userId}/`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }

    // Campaign Methods
    async getMyCampaigns() {
        return await this.makeRequest('/campaigns/my-campaigns/');
    }

    async createCampaign(campaignData) {
        return await this.makeRequest('/campaigns/create/', {
            method: 'POST',
            body: JSON.stringify(campaignData)
        });
    }

    async updateCampaign(campaignId, campaignData) {
        return await this.makeRequest(`/campaigns/${campaignId}/update/`, {
            method: 'PUT',
            body: JSON.stringify(campaignData)
        });
    }

    async getPublicCampaigns() {
        return await this.makeRequest('/campaigns/public/');
    }

    // Utility Methods
    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    getCurrentUser() {
        return this.user;
    }

    getUserType() {
        return this.user?.user_type || null;
    }

    hasRole(role) {
        return this.user?.user_type === role;
    }

    // Error handling helper
    handleAPIError(error) {
        console.error('API Error:', error);
        
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            // Token expired, try to refresh
            this.refreshToken().catch(() => {
                // Refresh failed, logout user
                this.logout();
                window.location.reload();
            });
        }
        
        return {
            success: false,
            error: error.message
        };
    }
}

// Create global API instance
window.comitiaAPI = new ComitiaAPI();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComitiaAPI;
}
