@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_docker_postgres.ps1"
echo.
if errorlevel 1 (
  echo La configuracion no se completo. Revisa el mensaje anterior.
) else (
  echo PostgreSQL 17 esta listo en Docker.
)
echo.
pause
endlocal
