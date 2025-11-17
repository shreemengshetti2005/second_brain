@echo off
echo ======================================================
echo 🧠 SECOND BRAIN AGENT - SETUP SCRIPT
echo ======================================================
echo.

REM Check Python
echo 1️⃣  Checking Python version...
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.12+
    exit /b 1
)
echo ✅ Python found
echo.

REM Create virtual environment
echo 2️⃣  Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo 3️⃣  Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo 4️⃣  Installing dependencies...
python -m pip install --upgrade pip
python scripts\install_dependencies.py
if errorlevel 1 (
    echo ❌ Dependency installation failed
    exit /b 1
)
echo.

REM Create .env file
echo 5️⃣  Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo ✅ Created .env file
    echo ⚠️  Please edit .env and add your API keys
) else (
    echo ✅ .env file already exists
)
echo.

REM Create data directories
echo 6️⃣  Creating data directories...
mkdir data\audio 2>nul
mkdir data\exports 2>nul
mkdir data\vector_db 2>nul
mkdir data\temp 2>nul
echo ✅ Data directories created
echo.

REM Setup database
echo 7️⃣  Setting up database...
echo ℹ️  Make sure PostgreSQL is running!
pause
python scripts\setup_database.py
echo.

REM Seed sample data
echo 8️⃣  Adding sample data...
set /p ADDSAMPLE="Add sample test data? (y/n): "
if /i "%ADDSAMPLE%"=="y" (
    python scripts\seed_data.py
)
echo.

echo ======================================================
echo ✅ SETUP COMPLETE!
echo ======================================================
echo.
echo 📋 Next Steps:
echo    1. Edit .env file with your API keys
echo    2. Run: python run.py
echo    3. Open: http://localhost:8501
echo.
echo 📚 Setup Guides:
echo    • Google APIs: python scripts\setup_google_apis.py
echo    • Telegram Bot: python scripts\setup_telegram_bot.py
echo.
echo ======================================================
pause