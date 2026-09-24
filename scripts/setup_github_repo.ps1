<#
.SYNOPSIS
  Helper script to connect and push AURA-Farm OS to your GitHub repository.

.DESCRIPTION
  Initializes Git (if needed), adds all files, commits, sets remote origin,
  and pushes code to your GitHub repository.

.EXAMPLE
  .\scripts\setup_github_repo.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/aura-farm.git"
#>

param(
    [Parameter(Mandatory=$false, Position=0)]
    [string]$RepoUrl
)

# Ensure MinGit or Git in PATH
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    if (Test-Path "$env:LOCALAPPDATA\MinGit\cmd\git.exe") {
        $env:PATH = "$env:LOCALAPPDATA\MinGit\cmd;$env:PATH"
    } else {
        Write-Error "Git was not found in PATH or at $env:LOCALAPPDATA\MinGit\cmd\git.exe"
        exit 1
    }
}

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  🌱 AURA-Farm OS: GitHub Repository Setup & Push" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Project Directory: $projectRoot"

# Initialize Git if not present
if (-not (Test-Path "$projectRoot\.git")) {
    Write-Host "[1/5] Initializing local git repository..." -ForegroundColor Yellow
    git init -b main
} else {
    Write-Host "[1/5] Git repository already initialized." -ForegroundColor Green
    git branch -M main
}

# Configure Git user if not set
$userName = git config user.name
$userEmail = git config user.email
if (-not $userName) {
    git config user.name "AURA-Farm Automator"
}
if (-not $userEmail) {
    git config user.email "bot@aura-farm.ai"
}

Write-Host "[2/5] Staging files..." -ForegroundColor Yellow
git add .

Write-Host "[3/5] Creating initial commit..." -ForegroundColor Yellow
$commitMsg = "feat: initial commit of AURA-Farm autonomous robotic hydroponic farm operating system"
git commit -m $commitMsg

# Prompt for repo URL if not provided
if (-not $RepoUrl) {
    Write-Host ""
    Write-Host "Please create a new repository on GitHub (e.g., https://github.com/new)" -ForegroundColor Yellow
    Write-Host "Then enter your repository URL below (HTTPS or SSH):" -ForegroundColor Cyan
    $RepoUrl = Read-Host "GitHub Repository URL"
}

if ($RepoUrl) {
    Write-Host "[4/5] Setting remote origin to $RepoUrl..." -ForegroundColor Yellow
    $remotes = git remote
    if ($remotes -contains "origin") {
        git remote set-url origin $RepoUrl
    } else {
        git remote add origin $RepoUrl
    }

    Write-Host "[5/5] Pushing to GitHub (main branch)..." -ForegroundColor Yellow
    git push -u origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "SUCCESS! Your AURA-Farm project is now published on GitHub:" -ForegroundColor Green
        Write-Host "$RepoUrl" -ForegroundColor Cyan
    } else {
        Write-Warning "Git push returned exit code $LASTEXITCODE. If authentication is needed, run: git push -u origin main"
    }
} else {
    Write-Host ""
    Write-Host "No repository URL entered. Your local git repository is prepared!" -ForegroundColor Green
    Write-Host "When you create your GitHub repo, run:" -ForegroundColor Cyan
    Write-Host "  git remote add origin <YOUR_GITHUB_REPO_URL>"
    Write-Host "  git push -u origin main"
}
