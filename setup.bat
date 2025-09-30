@echo off
echo ========================================
echo COMITIA Django Development Setup
echo ========================================
echo.

cd Backend

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Running setup script...
python setup_dev.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Setup completed successfully!
    echo ========================================
    echo.
    echo To start development:
    echo 1. cd Backend
    echo 2. venv\Scripts\activate
    echo 3. python manage.py runserver
    echo.
    echo Then open: http://localhost:8000
    echo.
) else (
    echo.
    echo Setup failed. Please check the error messages above.
    echo.
)

pause
