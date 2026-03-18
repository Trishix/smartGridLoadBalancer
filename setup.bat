@echo off

REM Smart Grid Load-Balancer - Setup Script for Windows
REM Run this script to set up the complete environment

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     Smart Grid Load-Balancer - Setup Script (Windows)         ║
echo ║     Demand Response + Storage Trigger with LangGraph + Groq    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check Python version
echo 📍 Checking Python version...
python --version
echo.

REM Create virtual environment
echo 📍 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo    ✓ Virtual environment created
) else (
    echo    ℹ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo 📍 Activating virtual environment...
call venv\Scripts\activate.bat
echo    ✓ Virtual environment activated
echo.

REM Upgrade pip
echo 📍 Upgrading pip...
python -m pip install --upgrade pip > nul 2>&1
echo    ✓ pip upgraded
echo.

REM Install dependencies
echo 📍 Installing dependencies...
pip install -r requirements.txt -q
echo    ✓ Dependencies installed
echo.

REM Setup environment file
echo 📍 Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo    ✓ Created .env file from template
    echo.
    echo    ⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY
    echo    Get it at: https://console.groq.com
) else (
    echo    ℹ .env file already exists
)
echo.

REM Display next steps
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ✓ SETUP COMPLETE                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📝 NEXT STEPS:
echo.
echo 1. Configure Groq API Key:
echo    - Open .env in a text editor
echo    - Add: GROQ_API_KEY=your_api_key_from_console.groq.com
echo.
echo 2. Get Groq API Key (Free):
echo    Visit: https://console.groq.com
echo    Sign up ^-> Settings ^-> API Keys ^-> Create API Key
echo.
echo 3. Run the demonstration:
echo    python main.py
echo.
echo 4. Run the quick start:
echo    python QUICKSTART.py
echo.
echo 5. Run tests:
echo    python test_validation.py
echo.
echo 📚 Documentation:
echo    - INDEX.md          (Start here for navigation)
echo    - README.md         (Project overview)
echo    - QUICKSTART.py     (5-minute examples)
echo    - ARCHITECTURE.md   (Technical deep-dive)
echo.
echo 💡 Common Commands:
echo    python main.py              (Run all demonstrations)
echo    python QUICKSTART.py        (Run quick start examples)
echo    python test_validation.py   (Run tests)
echo.
echo 🔗 Integration:
echo    See integration_examples.py for real-world patterns:
echo    - SCADA system integration
echo    - Smart thermostat APIs
echo    - Real-time event processing
echo    - Database persistence
echo.
pause
