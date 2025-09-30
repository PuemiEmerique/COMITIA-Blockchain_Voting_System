# COMITIA - Blockchain Voting System

A secure, transparent, and decentralized electronic voting system powered by blockchain technology and biometric authentication.

## 🌟 Features

### Core Functionality
- **5 User Types**: Citizens, Voters, Candidates, Voter Officials, Electoral Commission
- **Blockchain Security**: All votes recorded on Ethereum blockchain
- **Biometric Authentication**: Face recognition and fingerprint verification
- **Real-time Results**: Live election results with transparent counting
- **Mobile Responsive**: Works seamlessly across all devices
- **Complete Audit Trail**: Full transparency and accountability

### User Roles & Capabilities

#### 👥 Citizens
- Account registration and identity verification
- Apply for voter registration with biometric data
- Apply for candidacy in elections
- Access civic education resources

#### 🗳️ Voters
- Secure voting with biometric verification
- Vote verification on blockchain
- View voting history and receipts
- Real-time election results access

#### 🏛️ Candidates
- Campaign management and digital assets
- Performance analytics and voter feedback
- Event scheduling and management
- Social media integration

#### 👮 Voter Officials
- Review and approve voter registrations
- Capture and verify biometric data
- Process identity verification
- Generate registration statistics

#### 🏢 Electoral Commission
- Create and manage elections
- Approve candidate applications
- System-wide analytics and reporting
- Security auditing and monitoring

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: MongoDB with Djongo
- **Authentication**: JWT with SimpleJWT
- **Caching**: Redis
- **Task Queue**: Celery
- **API Documentation**: drf-yasg (Swagger/OpenAPI)

### Frontend
- **Templates**: Django Templates with Jinja2
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Icons**: Font Awesome 6
- **Charts**: Chart.js (for analytics)

### Blockchain
- **Network**: Ethereum (Sepolia testnet for development)
- **Smart Contracts**: Solidity
- **Web3 Integration**: Ethers.js
- **Wallet**: MetaMask integration

### Biometric Authentication
- **Face Recognition**: face-api.js with TensorFlow.js
- **Fingerprint**: WebAuthn API
- **Image Processing**: OpenCV (Python backend)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for blockchain tools)
- MongoDB 5.0+
- Redis 6.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd COMITIA-Blockchain_Voting_System
   ```

2. **Run the setup script**
   ```bash
   cd Backend
   python setup_dev.py
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Start the development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API docs: http://localhost:8000/swagger/

### Manual Setup (if script fails)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

## 📁 Project Structure

```
COMITIA-Blockchain_Voting_System/
├── Backend/                          # Django backend
│   ├── comitia/                     # Main project settings
│   │   ├── settings.py              # Django settings
│   │   ├── urls.py                  # URL configuration
│   │   └── views.py                 # Main views
│   ├── accounts/                    # User management app
│   ├── elections/                   # Election management app
│   ├── voting/                      # Voting functionality app
│   ├── blockchain/                  # Blockchain integration app
│   ├── biometrics/                  # Biometric authentication app
│   ├── campaigns/                   # Campaign management app
│   ├── templates/                   # Django templates
│   │   ├── base.html               # Base template
│   │   ├── home.html               # Home page
│   │   ├── accounts/               # Authentication templates
│   │   └── dashboards/             # Role-based dashboards
│   ├── static/                      # Static files
│   │   ├── css/                    # Stylesheets
│   │   ├── js/                     # JavaScript files
│   │   └── images/                 # Images and assets
│   ├── media/                       # User uploaded files
│   ├── requirements.txt             # Python dependencies
│   ├── manage.py                    # Django management script
│   └── setup_dev.py                # Development setup script
├── contracts/                       # Smart contracts (Solidity)
├── docs/                           # Documentation
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
MONGO_DB_NAME=comitia_db
MONGO_HOST=localhost
MONGO_PORT=27017

# Redis
REDIS_URL=redis://localhost:6379/0

# Blockchain
ETHEREUM_NETWORK=sepolia
INFURA_PROJECT_ID=your-infura-project-id
PRIVATE_KEY=your-private-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Setup

1. **Install MongoDB**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb
   
   # macOS
   brew install mongodb-community
   
   # Windows
   # Download from https://www.mongodb.com/try/download/community
   ```

2. **Start MongoDB**
   ```bash
   # Ubuntu/Debian/macOS
   sudo systemctl start mongod
   
   # Windows
   # Start MongoDB service from Services panel
   ```

3. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Windows
   # Download from https://redis.io/download
   ```

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Biometric authentication (face + fingerprint)
- Multi-factor authentication support
- Session management and timeout

### Data Protection
- AES-256 encryption for sensitive data
- HTTPS enforcement in production
- CSRF protection on all forms
- XSS protection with Content Security Policy
- SQL injection prevention with ORM

### Blockchain Security
- Immutable vote recording
- Cryptographic vote verification
- Smart contract auditing
- Private key management
- Transaction monitoring

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/refresh/` - Token refresh

### Election Endpoints
- `GET /api/v1/elections/` - List elections
- `POST /api/v1/elections/` - Create election
- `GET /api/v1/elections/{id}/` - Election details
- `POST /api/v1/elections/{id}/vote/` - Cast vote

### Biometric Endpoints
- `POST /api/v1/biometrics/register/` - Register biometric
- `POST /api/v1/biometrics/verify/` - Verify biometric
- `GET /api/v1/biometrics/status/` - Biometric status

### Blockchain Endpoints
- `POST /api/v1/blockchain/verify-vote/` - Verify vote on blockchain
- `GET /api/v1/blockchain/transaction/{hash}/` - Transaction details
- `GET /api/v1/blockchain/network-info/` - Network information

Full API documentation available at: http://localhost:8000/swagger/

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test elections

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Data
```bash
# Load test fixtures
python manage.py loaddata fixtures/test_data.json

# Create test users
python manage.py shell
>>> from accounts.models import User
>>> User.objects.create_test_users()
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   SECRET_KEY=your-production-secret-key
   ```

2. **Database Configuration**
   ```bash
   # Use MongoDB Atlas or dedicated MongoDB server
   MONGO_HOST=your-mongodb-host
   MONGO_DB_NAME=comitia_production
   ```

3. **Static Files**
   ```bash
   python manage.py collectstatic
   # Configure web server to serve static files
   ```

4. **SSL Certificate**
   ```bash
   # Configure HTTPS with Let's Encrypt or commercial SSL
   ```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write tests for new features
- Update documentation
- Follow semantic versioning

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**MongoDB Connection Error**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

**Redis Connection Error**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis
```

**Migration Errors**
```bash
# Reset migrations
python manage.py migrate --fake-initial
python manage.py migrate
```

### Getting Help
- 📧 Email: support@comitia.com
- 💬 Discord: [COMITIA Community](https://discord.gg/comitia)
- 📖 Documentation: [docs.comitia.com](https://docs.comitia.com)
- 🐛 Issues: [GitHub Issues](https://github.com/comitia/issues)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Ethereum Foundation for blockchain infrastructure
- face-api.js team for biometric authentication
- All contributors and testers

---

**Built with ❤️ for transparent and secure elections**
