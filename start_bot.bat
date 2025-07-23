@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo Iniciando bot...
python manage.py start_telegram_bot --debug
pause
