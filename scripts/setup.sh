#!/bin/bash

echo "======================================================"
echo "🧠 SECOND BRAIN AGENT - SETUP SCRIPT"
echo "======================================================"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi
echo "✅ Python found"
echo ""

# Create virtual environment
echo "2️⃣  Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "4️⃣  Installing dependencies..."
pip install --upgrade pip
python scripts/install_dependencies.py
if [ $? -ne 0 ]; then
    echo "❌ Dependency installation failed"
    exit 1
fi
echo ""

# Create .env file
echo "5️⃣  Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✅ .env file already exists"
fi
echo ""

# Create data directories
echo "6️⃣  Creating data directories..."
mkdir -p data/audio data/exports data/vector_db data/temp
echo "✅ Data directories created"
echo ""

# Setup database
echo "7️⃣  Setting up database..."
echo "ℹ️  Make sure PostgreSQL is running!"
read -p "Press Enter when PostgreSQL is ready..."
python scripts/setup_database.py
echo ""

# Seed sample data
echo "8️⃣  Adding sample data..."
read -p "Add sample test data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/seed_data.py
fi
echo ""

echo "======================================================"
echo "✅ SETUP COMPLETE!"
echo "======================================================"
echo ""
echo "📋 Next Steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Run: python run.py"
echo "   3. Open: http://localhost:8501"
echo ""
echo "📚 Setup Guides:"
echo "   • Google APIs: python scripts/setup_google_apis.py"
echo "   • Telegram Bot: python scripts/setup_telegram_bot.py"
echo ""
echo "======================================================"