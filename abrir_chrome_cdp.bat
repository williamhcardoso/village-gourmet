@echo off
echo ============================================
echo  Abrindo Chrome com depuracao remota (CDP)
echo  Porta: 9222
echo ============================================
echo.
echo 1. Chrome vai abrir
echo 2. Faca login em painel.yooga.com.br
echo 3. Depois execute: python coletor_yooga.py
echo.

taskkill /f /im chrome.exe >nul 2>&1
timeout /t 2 >nul

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%TEMP%\chrome-yooga-session" ^
  https://painel.yooga.com.br

echo Chrome aberto! Faca login e depois volte aqui.
pause
