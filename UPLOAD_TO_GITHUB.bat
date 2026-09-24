@echo off
title AURA-Farm GitHub Uploader
color 0A
set "PATH=%LOCALAPPDATA%\MinGit\cmd;%PATH%"
cd /d "C:\Users\Niles\.gemini\antigravity\scratch\aura-farm"

echo ======================================================================
echo    AURA-Farm: Uploading to https://github.com/deshnajain614/aura-farm
echo ======================================================================
echo.

git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git was not found at %LOCALAPPDATA%\MinGit\cmd\git.exe.
    pause
    exit /b 1
)

echo [1/2] Connecting to GitHub repository...
git remote set-url origin https://github.com/deshnajain614/aura-farm.git

echo [2/2] Pushing files to main branch...
echo.
git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ======================================================================
    echo   SUCCESS! Your project is now live on GitHub!
    echo   Visit: https://github.com/deshnajain614/aura-farm
    echo ======================================================================
) else (
    echo ======================================================================
    echo   [NOTICE] If GitHub asked for a password, use a Personal Access Token:
    echo   1. Visit: https://github.com/settings/tokens/new
    echo   2. Check 'repo' box and click Generate Token
    echo   3. Paste that token when prompted for password
    echo ======================================================================
)
echo.
pause
