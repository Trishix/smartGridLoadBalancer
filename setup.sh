#!/bin/bash

# Smart Grid Load-Balancer - Setup Script
# Run this script to set up the complete environment

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Smart Grid Load-Balancer - Setup Script                   ║"
echo "║     Demand Response + Storage Trigger with LangGraph + Groq    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment
echo ""
echo "📍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ℹ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "📍 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || {
    echo "   ⚠️  Could not auto-activate. Please run:"
    echo "   source venv/bin/activate  (Linux/Mac)"
    echo "   venv\\Scripts\\activate  (Windows)"
}

# Upgrade pip
echo ""
echo "📍 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✓ pip upgraded"

# Install dependencies
echo ""
echo "📍 Installing dependencies..."
pip install -r requirements.txt -q

# Check installation
echo "   ✓ Dependencies installed"
python -c "import langgraph; import langchain_groq; print('   ✓ LangGraph and Groq verified')" 2>/dev/null || echo "   ⚠️  Some dependencies may need to be verified"

# Setup environment file
echo ""
echo "📍 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ Created .env file from template"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY"
    echo "   Get it at: https://console.groq.com"
else
    echo "   ℹ .env file already exists"
fi

# Display next steps
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✓ SETUP COMPLETE                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. Configure Groq API Key:"
echo "   $ nano .env  (or edit .env in your editor)"
echo "   Add: GROQ_API_KEY=your_api_key_from_console.groq.com"
echo ""
echo "2. Get Groq API Key (Free):"
echo "   Visit: https://console.groq.com"
echo "   Sign up → Settings → API Keys → Create API Key"
echo ""
echo "3. Run the demonstration:"
echo "   $ python main.py"
echo ""
echo "4. Run the quick start:"
echo "   $ python QUICKSTART.py"
echo ""
echo "5. Run tests:"
echo "   $ python test_validation.py"
echo ""
echo "📚 Documentation:"
echo "   - INDEX.md          ← Start here for navigation"
echo "   - README.md         ← Project overview"
echo "   - QUICKSTART.py     ← 5-minute examples"
echo "   - ARCHITECTURE.md   ← Technical deep-dive"
echo ""
echo "💡 Common Commands:"
echo "   python main.py              Run all demonstrations"
echo "   python QUICKSTART.py        Run quick start examples"
echo "   python -c \"from main import *; demo...\"   Custom scenarios"
echo ""
echo "🔗 Integration:"
echo "   See integration_examples.py for real-world patterns:"
echo "   - SCADA system integration"
echo "   - Smart thermostat APIs"
echo "   - Real-time event processing"
echo "   - Database persistence"
echo ""
