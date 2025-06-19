@echo off
REM Activate conda env, change to your env name if needed
call %USERPROFILE%\anaconda3\Scripts\activate.bat trading

REM Change to project directory (assumes this .bat is in the project folder)
cd /d %~dp0

REM Start Python bot
start cmd /k python Trading_With_Crypto.py

REM Prompt user to run their ngrok command manually
echo Please run your ngrok tunnel separately:
echo   ngrok http 5000
pause
