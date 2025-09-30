/**
 * COMITIA Biometric Authentication
 * Handles face recognition and biometric verification
 */

class BiometricAuth {
    constructor() {
        this.isInitialized = false;
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.faceDescriptor = null;
        this.isCapturing = false;
    }

    async initialize() {
        if (this.isInitialized) return;

        try {
            // Load face-api.js models
            await this.loadModels();
            this.isInitialized = true;
            // console.log removed ('Biometric authentication initialized');
        } catch (error) {
            // console.error removed ('Failed to initialize biometric auth:', error);
            throw error;
        }
    }

    async loadModels() {
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api@latest/model';
        
        try {
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
                faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
                faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
                faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
            ]);
            // console.log removed ('Face-api models loaded successfully');
        } catch (error) {
            // console.error removed ('Error loading face-api models:', error);
            throw error;
        }
    }

    async startCamera() {
        try {
            this.video = document.getElementById('biometricVideo');
            this.canvas = document.getElementById('biometricCanvas');

            if (!this.video || !this.canvas) {
                throw new Error('Video or canvas element not found');
            }

            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });

            this.video.srcObject = this.stream;
            
            return new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    resolve();
                };
            });
        } catch (error) {
            // console.error removed ('Error starting camera:', error);
            throw new Error('Camera access denied or not available');
        }
    }

    async stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.video) {
            this.video.srcObject = null;
        }
    }

    async detectFace() {
        if (!this.video || !this.isInitialized) {
            throw new Error('Biometric system not initialized');
        }

        try {
            const detections = await faceapi
                .detectAllFaces(this.video, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceDescriptors();

            if (detections.length === 0) {
                throw new Error('No face detected');
            }

            if (detections.length > 1) {
                throw new Error('Multiple faces detected. Please ensure only one person is in frame');
            }

            return detections[0];
        } catch (error) {
            // console.error removed ('Face detection error:', error);
            throw error;
        }
    }

    async captureBiometric() {
        if (this.isCapturing) return;
        
        this.isCapturing = true;
        
        try {
            // Ensure camera is started
            if (!this.stream) {
                await this.startCamera();
                // Wait for video to be ready
                await new Promise(resolve => setTimeout(resolve, 1000));
            }

            // Detect face
            const detection = await this.detectFace();
            
            // Extract face descriptor
            this.faceDescriptor = detection.descriptor;
            
            // Capture image
            const imageData = this.captureImage();
            
            // Prepare biometric data
            const biometricData = {
                descriptor: Array.from(this.faceDescriptor),
                image: imageData,
                timestamp: new Date().toISOString(),
                quality_score: this.calculateQualityScore(detection)
            };

            return biometricData;
        } catch (error) {
            // console.error removed ('Biometric capture error:', error);
            throw error;
        } finally {
            this.isCapturing = false;
        }
    }

    captureImage() {
        if (!this.video || !this.canvas) {
            throw new Error('Video or canvas not available');
        }

        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        context.drawImage(this.video, 0, 0);
        
        return this.canvas.toDataURL('image/jpeg', 0.8);
    }

    calculateQualityScore(detection) {
        // Simple quality score based on face size and landmarks
        const faceBox = detection.detection.box;
        const faceSize = faceBox.width * faceBox.height;
        const landmarks = detection.landmarks;
        
        // Normalize face size (assuming 640x480 video)
        const normalizedSize = faceSize / (640 * 480);
        
        // Check if face is centered
        const centerX = faceBox.x + faceBox.width / 2;
        const centerY = faceBox.y + faceBox.height / 2;
        const videoCenterX = 320; // 640/2
        const videoCenterY = 240; // 480/2
        
        const centerDistance = Math.sqrt(
            Math.pow(centerX - videoCenterX, 2) + 
            Math.pow(centerY - videoCenterY, 2)
        );
        const normalizedCenterDistance = centerDistance / Math.sqrt(320*320 + 240*240);
        
        // Calculate quality score (0-1)
        let qualityScore = 0.5; // Base score
        
        // Face size contribution (bigger is better, up to a point)
        if (normalizedSize > 0.05 && normalizedSize < 0.3) {
            qualityScore += 0.3;
        }
        
        // Centering contribution
        if (normalizedCenterDistance < 0.2) {
            qualityScore += 0.2;
        }
        
        return Math.min(1.0, qualityScore);
    }

    async verifyBiometric(storedDescriptor) {
        try {
            const currentDetection = await this.detectFace();
            const currentDescriptor = currentDetection.descriptor;
            
            // Calculate distance between descriptors
            const distance = faceapi.euclideanDistance(currentDescriptor, storedDescriptor);
            
            // Threshold for face recognition (lower = more strict)
            const threshold = 0.6;
            const isMatch = distance < threshold;
            
            return {
                isMatch,
                confidence: Math.max(0, (threshold - distance) / threshold),
                distance
            };
        } catch (error) {
            // console.error removed ('Biometric verification error:', error);
            throw error;
        }
    }

    async registerBiometric() {
        try {
            await this.initialize();
            await this.startCamera();
            
            // Show status
            this.updateStatus('Position your face in the center and look directly at the camera');
            
            // Wait for user to position themselves
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Capture multiple samples for better accuracy
            const samples = [];
            for (let i = 0; i < 3; i++) {
                this.updateStatus(`Capturing sample ${i + 1} of 3...`);
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                const biometricData = await this.captureBiometric();
                samples.push(biometricData);
            }
            
            // Calculate average descriptor
            const avgDescriptor = this.calculateAverageDescriptor(samples);
            
            // Prepare final biometric data
            const finalBiometricData = {
                descriptor: avgDescriptor,
                samples: samples.length,
                registration_date: new Date().toISOString(),
                quality_scores: samples.map(s => s.quality_score)
            };
            
            // Register with backend
            const response = await window.comitiaAPI.registerBiometric(finalBiometricData);
            
            this.updateStatus('Biometric registration successful!', 'success');
            return response;
            
        } catch (error) {
            this.updateStatus(`Registration failed: ${error.message}`, 'error');
            throw error;
        } finally {
            await this.stopCamera();
        }
    }

    calculateAverageDescriptor(samples) {
        if (samples.length === 0) return null;
        
        const descriptorLength = samples[0].descriptor.length;
        const avgDescriptor = new Array(descriptorLength).fill(0);
        
        // Sum all descriptors
        samples.forEach(sample => {
            sample.descriptor.forEach((value, index) => {
                avgDescriptor[index] += value;
            });
        });
        
        // Calculate average
        return avgDescriptor.map(sum => sum / samples.length);
    }

    async performBiometricAuth() {
        try {
            await this.initialize();
            await this.startCamera();
            
            this.updateStatus('Look directly at the camera for verification');
            
            // Wait for user to position themselves
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Capture current biometric
            const currentBiometric = await this.captureBiometric();
            
            // Verify with backend
            const response = await window.comitiaAPI.verifyBiometricAuth({
                descriptor: currentBiometric.descriptor,
                timestamp: currentBiometric.timestamp
            });
            
            if (response.verified) {
                this.updateStatus('Biometric verification successful!', 'success');
                return { success: true, confidence: response.confidence };
            } else {
                this.updateStatus('Biometric verification failed', 'error');
                return { success: false, reason: response.reason };
            }
            
        } catch (error) {
            this.updateStatus(`Verification failed: ${error.message}`, 'error');
            throw error;
        } finally {
            await this.stopCamera();
        }
    }

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('biometricStatus');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status ${type}`;
        }
        // console.log removed (`Biometric Status (${type}): ${message}`);
    }

    // WebAuthn integration for fingerprint/touch authentication
    async registerWebAuthn() {
        if (!window.PublicKeyCredential) {
            throw new Error('WebAuthn not supported in this browser');
        }

        try {
            const user = window.comitiaAPI.getCurrentUser();
            if (!user) {
                throw new Error('User not authenticated');
            }

            const publicKeyCredentialCreationOptions = {
                challenge: new Uint8Array(32),
                rp: {
                    name: "COMITIA Voting System",
                    id: window.location.hostname,
                },
                user: {
                    id: new TextEncoder().encode(user.id),
                    name: user.username,
                    displayName: user.first_name + ' ' + user.last_name,
                },
                pubKeyCredParams: [{alg: -7, type: "public-key"}],
                authenticatorSelection: {
                    authenticatorAttachment: "platform",
                    userVerification: "required"
                },
                timeout: 60000,
                attestation: "direct"
            };

            const credential = await navigator.credentials.create({
                publicKey: publicKeyCredentialCreationOptions
            });

            return {
                id: credential.id,
                rawId: Array.from(new Uint8Array(credential.rawId)),
                type: credential.type,
                response: {
                    attestationObject: Array.from(new Uint8Array(credential.response.attestationObject)),
                    clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON))
                }
            };
        } catch (error) {
            // console.error removed ('WebAuthn registration error:', error);
            throw error;
        }
    }

    async authenticateWebAuthn() {
        if (!window.PublicKeyCredential) {
            throw new Error('WebAuthn not supported in this browser');
        }

        try {
            const publicKeyCredentialRequestOptions = {
                challenge: new Uint8Array(32),
                allowCredentials: [],
                timeout: 60000,
                userVerification: "required"
            };

            const assertion = await navigator.credentials.get({
                publicKey: publicKeyCredentialRequestOptions
            });

            return {
                id: assertion.id,
                rawId: Array.from(new Uint8Array(assertion.rawId)),
                type: assertion.type,
                response: {
                    authenticatorData: Array.from(new Uint8Array(assertion.response.authenticatorData)),
                    clientDataJSON: Array.from(new Uint8Array(assertion.response.clientDataJSON)),
                    signature: Array.from(new Uint8Array(assertion.response.signature)),
                    userHandle: assertion.response.userHandle ? Array.from(new Uint8Array(assertion.response.userHandle)) : null
                }
            };
        } catch (error) {
            // console.error removed ('WebAuthn authentication error:', error);
            throw error;
        }
    }
}

// Create global biometric instance
window.biometricAuth = new BiometricAuth();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BiometricAuth;
}
