@echo off
echo 🚀 Setting up Geo-Regulation Compliance System...
echo ================================================

REM --- Check Python ---
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3 not found. Please install Python 3.8+ and try again.
    exit /b 1
)

REM --- Create venv ---
if not exist venv (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
)
call venv\Scripts\activate.bat

REM --- Upgrade pip & install dependencies ---
python -m pip install --upgrade pip
IF EXIST requirements.txt (
    pip install -r requirements.txt
    echo [SUCCESS] Python dependencies installed
) ELSE (
    echo [ERROR] requirements.txt not found
)

REM --- Setup Node.js ---
where node >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo [INFO] Installing Node.js dependencies...
    IF EXIST package.json (
        npm install
        echo [SUCCESS] Node.js dependencies installed
    ) ELSE (
        echo [WARNING] package.json not found, skipping frontend setup
    )
) ELSE (
    echo [WARNING] Node.js not found, frontend will not run
)

REM --- Setup .env ---
IF NOT EXIST .env (
    IF EXIST .env.template (
        copy .env.template .env
        echo [SUCCESS] .env created from template
    ) ELSE (
        echo OPENAI_API_KEY=your_api_key_here > .env
        echo DEBUG=True >> .env
        echo LOG_LEVEL=INFO >> .env
        echo API_HOST=0.0.0.0 >> .env
        echo API_PORT=8000 >> .env
        echo [SUCCESS] Basic .env file created
    )
)

REM --- Run demo if available ---
IF EXIST run_demo.py (
    echo [INFO] Running demo...
    python run_demo.py
)

echo.
echo 🎉 Setup Complete!
echo ==================
echo To start backend:  
echo   call venv\Scripts\activate.bat
echo   python main.py
echo   -> http://localhost:8000
echo.
echo To start frontend:
echo   npm start
echo   -> http://localhost:3000
echo.
