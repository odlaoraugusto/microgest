@echo off
title MicroGest
cd /d "%~dp0"

echo Desligando o MicroGest...
docker compose stop

echo Pronto.
timeout /t 2 /nobreak >nul
exit
