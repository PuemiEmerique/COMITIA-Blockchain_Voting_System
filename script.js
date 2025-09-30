/**
 * COMITIA Main Application Script
 * Handles UI interactions, authentication, and dashboard management
 */

class ComitiaApp {
    constructor() {
        this.currentUser = null;
        this.isInitialized = false;
        this.activeModal = null;
    }

    async initialize() {
        if (this.isInitialized) return;

        try {
            // Check if user is already logged in
            if (window.comitiaAPI.isAuthenticated()) {
                this.currentUser = window.comitiaAPI.getCurrentUser();
                this.showDashboard();
            } else {
                this.showPublicView();
            }

            this.setupEventListeners();
            this.isInitialized = true;
            
            // console.log removed ('COMITIA App initialized');
        } catch (error) {
            // console.error removed ('App initialization error:', error);
        }
    }

    setupEventListeners() {
        // Modal functionality
        this.setupModalEvents();
        
        // Authentication forms
        this.setupAuthForms();
        
        // Dashboard interactions
        this.setupDashboardEvents();
        
        // Navigation events
        this.setupNavigationEvents();
    }

    setupModalEvents() {
        const modalOverlay = document.getElementById('modalOverlay');
        
        // Open modal buttons
        document.getElementById('openRegister')?.addEventListener('click', () => this.openModal('registerModal'));
        document.getElementById('heroRegister')?.addEventListener('click', () => this.openModal('registerModal'));
        document.getElementById('openLogin')?.addEventListener('click', () => this.openModal('loginModal'));
        document.getElementById('heroLogin')?.addEventListener('click', () => this.openModal('loginModal'));
        
        // Close modal functionality
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                const modalId = e.target.getAttribute('data-close');
                this.closeModal(modalId);
            });
        });
        
        modalOverlay?.addEventListener('click', () => {
            this.closeAllModals();
        });
    }

    setupAuthForms() {
        // Registration form
        document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegistration(e);
        });
        
        // Login form
        document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin(e);
        });
    }

    setupNavigationEvents() {
        // User navigation
        document.getElementById('userDashboard')?.addEventListener('click', () => {
            this.showDashboard();
        });
        
        document.getElementById('userLogout')?.addEventListener('click', async () => {
            await this.handleLogout();
        });
    }

    setupDashboardEvents() {
        // Citizen Dashboard Events
        document.getElementById('applyVoterBtn')?.addEventListener('click', () => this.handleVoterApplication());
        document.getElementById('applyCandidateBtn')?.addEventListener('click', () => this.handleCandidateApplication());
        
        // Voter Dashboard Events
        document.getElementById('verifyVotesBtn')?.addEventListener('click', () => this.handleVoteVerification());
        document.getElementById('updateBiometricBtn')?.addEventListener('click', () => this.handleBiometricUpdate());
        
        // Candidate Dashboard Events
        document.getElementById('createCampaignBtn')?.addEventListener('click', () => this.handleCreateCampaign());
        document.getElementById('voterFeedbackBtn')?.addEventListener('click', () => this.handleVoterFeedback());
        
        // Voter Official Dashboard Events
        document.getElementById('reviewRegistrationsBtn')?.addEventListener('click', () => this.handleReviewRegistrations());
        document.getElementById('captureBiometricBtn')?.addEventListener('click', () => this.handleBiometricCapture());
        
        // Electoral Commission Dashboard Events
        document.getElementById('createElectionBtn')?.addEventListener('click', () => this.handleCreateElection());
        document.getElementById('reviewCandidatesBtn')?.addEventListener('click', () => this.handleReviewCandidates());
        document.getElementById('manageOfficialsBtn')?.addEventListener('click', () => this.handleManageOfficials());
        document.getElementById('securityAuditBtn')?.addEventListener('click', () => this.handleSecurityAudit());
        
        // Biometric Events
        document.getElementById('startBiometricBtn')?.addEventListener('click', () => this.startBiometricAuth());
        document.getElementById('captureBiometricBtn')?.addEventListener('click', () => this.captureBiometric());
    }

    // Modal Management
    openModal(modalId) {
        const modalOverlay = document.getElementById('modalOverlay');
        const modal = document.getElementById(modalId);
        
        if (modalOverlay && modal) {
            modalOverlay.style.display = 'block';
            modal.style.display = 'block';
            this.activeModal = modalId;
        }
    }
    
    closeModal(modalId) {
        const modalOverlay = document.getElementById('modalOverlay');
        const modal = document.getElementById(modalId);
        
        if (modalOverlay && modal) {
            modalOverlay.style.display = 'none';
            modal.style.display = 'none';
            this.activeModal = null;
        }
    }
    
    closeAllModals() {
        const modalOverlay = document.getElementById('modalOverlay');
        modalOverlay.style.display = 'none';
        
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
        
        this.activeModal = null;
    }

    // Authentication Handlers
    async handleRegistration(e) {
        const form = e.target;
        const statusDiv = document.getElementById('registerStatus');
        
        try {
            const userData = {
                username: form.regUsername.value,
                email: form.regEmail.value,
                first_name: form.regFirstName.value,
                last_name: form.regLastName.value,
                phone_number: form.regPhone.value,
                national_id: form.regNationalId.value,
                date_of_birth: form.regDateOfBirth.value,
                address: form.regAddress.value,
                password: form.regPassword.value,
                password_confirm: form.regConfirm.value
            };

            // Validate passwords match
            if (userData.password !== userData.password_confirm) {
                throw new Error('Passwords do not match');
            }

            statusDiv.textContent = 'Creating account...';
            statusDiv.className = 'status info';

            const response = await window.comitiaAPI.register(userData);
            
            statusDiv.textContent = 'Registration successful! You can now log in.';
            statusDiv.className = 'status success';
            
            // Clear form
            form.reset();
            
            // Switch to login modal after delay
            setTimeout(() => {
                this.closeModal('registerModal');
                this.openModal('loginModal');
            }, 2000);

        } catch (error) {
            statusDiv.textContent = error.message;
            statusDiv.className = 'status error';
        }
    }

    async handleLogin(e) {
        const form = e.target;
        const statusDiv = document.getElementById('loginStatus');
        
        try {
            const username = form.loginUsername.value;
            const password = form.loginPassword.value;

            statusDiv.textContent = 'Logging in...';
            statusDiv.className = 'status info';

            const response = await window.comitiaAPI.login(username, password);
            
            this.currentUser = response.user;
            
            statusDiv.textContent = 'Login successful! Loading dashboard...';
            statusDiv.className = 'status success';
            
            // Clear form
            form.reset();
            
            setTimeout(() => {
                this.closeAllModals();
                this.showDashboard();
            }, 1500);

        } catch (error) {
            statusDiv.textContent = error.message;
            statusDiv.className = 'status error';
        }
    }

    async handleLogout() {
        try {
            await window.comitiaAPI.logout();
            this.currentUser = null;
            this.showPublicView();
        } catch (error) {
            // console.error removed ('Logout error:', error);
            // Force logout even if API call fails
            this.currentUser = null;
            this.showPublicView();
        }
    }

    // View Management
    showPublicView() {
        document.getElementById('heroSection').style.display = 'flex';
        document.getElementById('dashboardContainer').style.display = 'none';
        document.getElementById('publicNav').style.display = 'block';
        document.getElementById('userNav').style.display = 'none';
    }

    showDashboard() {
        if (!this.currentUser) {
            this.showPublicView();
            return;
        }

        document.getElementById('heroSection').style.display = 'none';
        document.getElementById('dashboardContainer').style.display = 'block';
        document.getElementById('publicNav').style.display = 'none';
        document.getElementById('userNav').style.display = 'block';

        // Update user welcome message
        const userWelcome = document.getElementById('userWelcome');
        if (userWelcome) {
            userWelcome.textContent = `Welcome, ${this.currentUser.first_name}!`;
        }

        // Hide all dashboards first
        document.querySelectorAll('.dashboard').forEach(dashboard => {
            dashboard.style.display = 'none';
        });

        // Show appropriate dashboard based on user type
        const userType = this.currentUser.user_type;
        const dashboardId = `${userType}Dashboard`;
        const dashboard = document.getElementById(dashboardId);
        
        if (dashboard) {
            dashboard.style.display = 'block';
            this.loadDashboardData(userType);
        } else {
            // console.error removed ('Dashboard not found for user type:', userType);
        }
    }

    async loadDashboardData(userType) {
        try {
            switch (userType) {
                case 'citizen':
                    await this.loadCitizenData();
                    break;
                case 'voter':
                    await this.loadVoterData();
                    break;
                case 'candidate':
                    await this.loadCandidateData();
                    break;
                case 'voter_official':
                    await this.loadVoterOfficialData();
                    break;
                case 'electoral_commission':
                    await this.loadElectoralCommissionData();
                    break;
            }
        } catch (error) {
            // console.error removed ('Error loading dashboard data:', error);
        }
    }

    async loadCitizenData() {
        try {
            // Load voter enrollment status
            const enrollmentStatus = await window.comitiaAPI.getVoterApplicationStatus();
            this.updateEnrollmentStatus(enrollmentStatus);
            
            // Load active elections
            const elections = await window.comitiaAPI.getElections({ active: true });
            this.displayElections(elections, 'activeElectionsList');
        } catch (error) {
            // console.error removed ('Error loading citizen data:', error);
        }
    }

    async loadVoterData() {
        try {
            // Load voter profile
            const profile = await window.comitiaAPI.getProfile();
            this.displayVoterInfo(profile);
            
            // Load elections for voting
            const elections = await window.comitiaAPI.getElections({ active: true });
            this.displayVotingElections(elections);
            
            // Load biometric status
            const biometricStatus = await window.comitiaAPI.getBiometricStatus();
            this.displayBiometricStatus(biometricStatus);
        } catch (error) {
            // console.error removed ('Error loading voter data:', error);
        }
    }

    async loadCandidateData() {
        try {
            // Load campaigns
            const campaigns = await window.comitiaAPI.getMyCampaigns();
            this.displayCampaigns(campaigns);
            
            // Load candidacy applications
            const applications = await window.comitiaAPI.getCandidacyApplications();
            this.displayCandidateApplications(applications);
        } catch (error) {
            // console.error removed ('Error loading candidate data:', error);
        }
    }

    async loadVoterOfficialData() {
        try {
            // Load pending registrations
            const pendingRegistrations = await window.comitiaAPI.getPendingRegistrations();
            this.displayPendingRegistrations(pendingRegistrations);
        } catch (error) {
            // console.error removed ('Error loading voter official data:', error);
        }
    }

    async loadElectoralCommissionData() {
        try {
            // Load elections
            const elections = await window.comitiaAPI.getElections();
            this.displayCommissionElections(elections);
            
            // Load pending candidates
            const pendingCandidates = await window.comitiaAPI.getPendingCandidates();
            this.displayPendingCandidates(pendingCandidates);
            
            // Load statistics
            const stats = await window.comitiaAPI.getElectionStatistics();
            this.displayElectionStatistics(stats);
        } catch (error) {
            // console.error removed ('Error loading electoral commission data:', error);
        }
    }

    // Dashboard Action Handlers
    async handleVoterApplication() {
        try {
            this.openModal('biometricModal');
            // Implementation for voter application with biometric capture
        } catch (error) {
            // console.error removed ('Voter application error:', error);
        }
    }

    async handleCandidateApplication() {
        // Implementation for candidate application
        alert('Candidate application feature coming soon!');
    }

    async handleVoteVerification() {
        try {
            const votes = await window.comitiaAPI.getMyVotes();
            // Display vote verification interface
            // console.log removed ('User votes:', votes);
        } catch (error) {
            // console.error removed ('Vote verification error:', error);
        }
    }

    async handleBiometricUpdate() {
        this.openModal('biometricModal');
    }

    async handleCreateCampaign() {
        alert('Create campaign feature coming soon!');
    }

    async handleVoterFeedback() {
        alert('Voter feedback feature coming soon!');
    }

    async handleReviewRegistrations() {
        alert('Review registrations feature coming soon!');
    }

    async handleBiometricCapture() {
        this.openModal('biometricModal');
    }

    async handleCreateElection() {
        alert('Create election feature coming soon!');
    }

    async handleReviewCandidates() {
        alert('Review candidates feature coming soon!');
    }

    async handleManageOfficials() {
        alert('Manage officials feature coming soon!');
    }

    async handleSecurityAudit() {
        alert('Security audit feature coming soon!');
    }

    // Biometric Handlers
    async startBiometricAuth() {
        try {
            await window.biometricAuth.initialize();
            await window.biometricAuth.startCamera();
            
            document.getElementById('startBiometricBtn').style.display = 'none';
            document.getElementById('captureBiometricBtn').style.display = 'inline-block';
        } catch (error) {
            // console.error removed ('Biometric start error:', error);
            window.biometricAuth.updateStatus(`Error: ${error.message}`, 'error');
        }
    }

    async captureBiometric() {
        try {
            const result = await window.biometricAuth.registerBiometric();
            // console.log removed ('Biometric registration result:', result);
            
            setTimeout(() => {
                this.closeModal('biometricModal');
            }, 2000);
        } catch (error) {
            // console.error removed ('Biometric capture error:', error);
        }
    }

    // Display Helper Methods
    updateEnrollmentStatus(status) {
        const statusElement = document.getElementById('voterEnrollmentStatus');
        if (statusElement && status) {
            const badge = statusElement.querySelector('.status-badge');
            if (badge) {
                badge.textContent = status.status || 'Not Applied';
                badge.className = `status-badge ${status.status?.toLowerCase() || 'pending'}`;
            }
        }
    }

    displayElections(elections, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!elections || elections.length === 0) {
            container.innerHTML = '<p>No active elections</p>';
            return;
        }

        container.innerHTML = elections.map(election => `
            <div class="election-item">
                <h4>${election.title}</h4>
                <p>${election.description}</p>
                <p><strong>Voting:</strong> ${new Date(election.voting_start_date).toLocaleDateString()} - ${new Date(election.voting_end_date).toLocaleDateString()}</p>
            </div>
        `).join('');
    }

    displayVoterInfo(profile) {
        if (profile.voter_profile) {
            const voterProfile = profile.voter_profile;
            
            document.getElementById('voterIdDisplay').textContent = voterProfile.voter_id || 'N/A';
            document.getElementById('pollingStationDisplay').textContent = voterProfile.polling_station || 'Not Assigned';
            document.getElementById('constituencyDisplay').textContent = voterProfile.constituency || 'Not Assigned';
        }
    }

    displayBiometricStatus(status) {
        const statusElement = document.getElementById('biometricStatus');
        if (statusElement && status) {
            const badge = statusElement.querySelector('.status-badge');
            if (badge) {
                badge.textContent = status.is_registered ? 'Verified' : 'Not Registered';
                badge.className = `status-badge ${status.is_registered ? 'verified' : 'pending'}`;
            }
        }
    }

    displayVotingElections(elections) {
        this.displayElections(elections, 'voterElectionsList');
    }

    displayCampaigns(campaigns) {
        const container = document.getElementById('candidateCampaignsList');
        if (!container) return;

        if (!campaigns || campaigns.length === 0) {
            container.innerHTML = '<p>No campaigns created</p>';
            return;
        }

        container.innerHTML = campaigns.map(campaign => `
            <div class="campaign-item">
                <h4>${campaign.name}</h4>
                <p>${campaign.description}</p>
            </div>
        `).join('');
    }

    displayCandidateApplications(applications) {
        const statusElement = document.getElementById('candidateApplicationStatus');
        if (statusElement && applications && applications.length > 0) {
            const latestApp = applications[0];
            const badge = statusElement.querySelector('.status-badge');
            if (badge) {
                badge.textContent = latestApp.status;
                badge.className = `status-badge ${latestApp.status.toLowerCase()}`;
            }
        }
    }

    displayPendingRegistrations(registrations) {
        const countElement = document.getElementById('pendingRegistrationsCount');
        if (countElement) {
            countElement.textContent = registrations?.length || 0;
        }
    }

    displayCommissionElections(elections) {
        this.displayElections(elections, 'commissionElectionsList');
    }

    displayPendingCandidates(candidates) {
        const countElement = document.getElementById('pendingCandidatesCount');
        if (countElement) {
            countElement.textContent = candidates?.length || 0;
        }
    }

    displayElectionStatistics(stats) {
        if (stats) {
            document.getElementById('totalElections').textContent = stats.total_elections || 0;
            document.getElementById('totalVoters').textContent = stats.total_voters || 0;
            document.getElementById('totalCandidates').textContent = stats.total_candidates || 0;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    window.comitiaApp = new ComitiaApp();
    await window.comitiaApp.initialize();
});
