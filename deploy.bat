@echo off
REM CSReforge Deployment Script for Windows
SETLOCAL EnableDelayedExpansion

echo ======================================
echo CSReforge Deployment Script for Windows
echo ======================================
echo.

REM Check Python installation
python --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check pip
pip --version > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pip is not installed. Please install pip.
    exit /b 1
)

echo Installing required packages...
pip install fastapi uvicorn motor pydantic python-dotenv requests

REM Create necessary directories
if not exist logs mkdir logs
if not exist .env (
    echo Creating default .env file...
    echo MONGO_URL=mongodb://localhost:27017 > .env
    echo DATABASE_NAME=csreforge >> .env
    echo SECRET_KEY=YourSecretKeyHere >> .env
)

echo.
echo Checking MongoDB connection...
python -c "from motor.motor_asyncio import AsyncIOMotorClient; client = AsyncIOMotorClient('mongodb://localhost:27017'); client.server_info()" > nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo MongoDB not found. Please make sure MongoDB is installed and running.
    echo You can use MongoDB Atlas instead by updating the MONGO_URL in the .env file.
    echo Visit https://www.mongodb.com/cloud/atlas for a free MongoDB Atlas cluster.
)

echo.
echo Do you want to set up a custom domain? (Y/N)
set /p domain_choice="> "
if /i "%domain_choice%"=="Y" (
    echo.
    echo Please enter your domain name (e.g., csreforge.lol):
    set /p domain_name="> "
    
    echo.
    echo Creating IIS configuration file...
    echo ^<configuration^> > web.config
    echo    ^<system.webServer^> >> web.config
    echo        ^<handlers^> >> web.config
    echo            ^<add name="Python FastAPI" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/^> >> web.config
    echo        ^</handlers^> >> web.config
    echo        ^<httpPlatform processPath="%%INTERPRETERPATH%%\python.exe" >> web.config
    echo                     arguments="backend\main.py" >> web.config
    echo                     stdoutLogEnabled="true" >> web.config
    echo                     stdoutLogFile="logs\stdout.log" >> web.config
    echo                     startupTimeLimit="60" >> web.config
    echo                     processesPerApplication="1"/^> >> web.config
    echo    ^</system.webServer^> >> web.config
    echo ^</configuration^> >> web.config
    
    echo.
    echo To set up your domain with IIS:
    echo 1. Open IIS Manager
    echo 2. Create a new site pointing to this directory
    echo 3. Bind your domain to the site
    echo 4. Make sure you have installed URL Rewrite module for IIS
) else (
    echo Skipping custom domain setup.
)

echo.
echo Creating Windows service script...
echo @echo off > start_service.bat
echo cd "%%~dp0" >> start_service.bat
echo echo Starting CSReforge API server... >> start_service.bat
echo start /min cmd /c "python backend\main.py > logs\api.log 2^>^&1" >> start_service.bat
echo echo CSReforge API server started in background. >> start_service.bat
echo echo Check logs\api.log for details. >> start_service.bat

echo.
echo Creating MongoDB setup script...
echo db = db.getSiblingDB('csreforge'); > mongodb_setup.js
echo db.createCollection('users'); >> mongodb_setup.js
echo db.createCollection('skins'); >> mongodb_setup.js
echo db.createCollection('cases'); >> mongodb_setup.js
echo db.skins.createIndex({ "name": 1 }); >> mongodb_setup.js
echo db.users.createIndex({ "steam_id": 1 }, { unique: true }); >> mongodb_setup.js

echo.
echo Creating seed database script...
mkdir backend 2>nul
python -c "import os; open(os.path.join('backend', '__init__.py'), 'a').close()"

echo.
echo Initializing database...
python backend/seed_database.py

echo.
echo ======================================
echo INSTALLATION COMPLETE
echo ======================================
echo.
echo To start the CSReforge API server:
echo   1. Run "start_service.bat"
echo.
echo To initialize the MongoDB database:
echo   1. Make sure MongoDB is running
echo   2. Run "mongosh < mongodb_setup.js"
echo.
echo Thank you for installing CSReforge!
echo.
echo ======================================

REM Pause at the end to see output
pause