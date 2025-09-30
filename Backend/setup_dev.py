#!/usr/bin/env python3
"""
COMITIA Development Environment Setup Script
This script helps set up the Django development environment
"""

import os
import sys
import subprocess
import platform
def run_command(command, description):
    """Run a command and handle errors"""
    logging.info(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"{description} completed successfully")
        if result.stdout:
            logging.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{description} failed")
        logging.info(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    logging.info("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        logging.info(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        logging.error(f"Python {version.major}.{version.minor}.{version.micro} is not compatible. Please use Python 3.8+")
        return False

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = "venv"
    if os.path.exists(venv_path):
        logging.info(f"Virtual environment already exists at {venv_path}")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_virtual_environment():
{{ ... }}
    """Install Python requirements"""
    activate_cmd = activate_virtual_environment()
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        logging.info("requirements.txt not found. Creating basic requirements...")
        create_requirements_file()
    
    if platform.system().lower() == "windows":
        command = f"venv\\Scripts\\pip install -r requirements.txt"
    else:
{{ ... }}
numpy==1.24.3
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    logging.info("Created requirements.txt")

def create_env_file():
    """Create a .env file with default settings"""
    env_content = """# Django Settings
SECRET_KEY=django-insecure-change-me-in-production-comitia-blockchain-voting
{{ ... }}
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        logging.info("Created .env file with default settings")
    else:
        logging.info(".env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
{{ ... }}
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")

def run_migrations():
    """Run Django migrations"""
    if platform.system().lower() == "windows":
        python_cmd = "venv\\Scripts\\python"
{{ ... }}
    
    return run_command(f"{python_cmd} manage.py collectstatic --noinput", "Collecting static files")

def create_superuser():
    """Create a superuser account"""
    logging.info("Creating superuser account...")
    logging.info("You'll be prompted to enter superuser details.")
    
    if platform.system().lower() == "windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    try:
        subprocess.run(f"{python_cmd} manage.py createsuperuser", shell=True, check=True)
        logging.info("Superuser created successfully")
        return True
    except subprocess.CalledProcessError:
        logging.warning("Superuser creation skipped or failed")
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    logging.info("Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        logging.info("MongoDB is running and accessible")
        return True
    except Exception as e:
        logging.error(f"MongoDB connection failed: {e}")
        logging.info("Please make sure MongoDB is installed and running on localhost:27017")
        return False

def check_redis():
    """Check if Redis is running"""
    logging.info("Checking Redis connection...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
        logging.info("Redis is running and accessible")
        return True
    except Exception as e:
        logging.error(f"Redis connection failed: {e}")
        logging.info("Please make sure Redis is installed and running on localhost:6379")
        return False

def main():
    """Main setup function"""
    logging.info("COMITIA Django Development Environment Setup")
    logging.info("=" * 50)
    
    # Change to the Backend directory
    if os.path.basename(os.getcwd()) != "Backend":
        if os.path.exists("Backend"):
            os.chdir("Backend")
            logging.info("Changed to Backend directory")
        else:
            logging.error("Backend directory not found. Please run this script from the project root.")
            return False
    
    # Check Python version
    if not check_python_version():
        return False
{{ ... }}
    # Check external services
    mongodb_ok = check_mongodb()
    redis_ok = check_redis()
    
    if not mongodb_ok:
        logging.warning("MongoDB is required for the application to work properly.")
        logging.info("Please install and start MongoDB before proceeding.")
    
    if not redis_ok:
        logging.info("Redis is recommended for caching and Celery tasks.")
        logging.info("Please install and start Redis for optimal performance.")
    
    # Run Django setup commands
    if mongodb_ok:
        if not run_migrations():
            logging.warning("Migration failed. You may need to fix database issues.")
        
        collect_static_files()
        
        # Offer to create superuser
        create_superuser()
    
    # Print final instructions
    logging.info("\n" + "=" * 50)
    logging.info("Setup completed!")
    logging.info("Next steps:")
    logging.info(f"1. Activate virtual environment: {activate_virtual_environment()}")
    
    if mongodb_ok:
        logging.info("2. Start the development server: python manage.py runserver")
        logging.info("3. Open your browser to: http://localhost:8000")
        logging.info("4. Admin panel available at: http://localhost:8000/admin")
    else:
        logging.info("2. Install and start MongoDB")
        logging.info("3. Run migrations: python manage.py migrate")
        logging.info("4. Start the development server: python manage.py runserver")
    
    logging.info("Optional services:")
    if not redis_ok:
        logging.info("- Install Redis for caching and background tasks")
    logging.info("- Set up Ethereum testnet connection (update .env file)")
    logging.info("- Configure email settings in .env file")
    
    logging.info("Documentation:")
    logging.info("- API docs: http://localhost:8000/swagger/")
    logging.info("- System status: http://localhost:8000/status/")
    
    return True

{{ ... }}
    success = main()
    sys.exit(0 if success else 1)
