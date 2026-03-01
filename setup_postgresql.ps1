#!/usr/bin/env powershell
# PostgreSQL Quick Setup Script for Windows
# This script helps you set up PostgreSQL after installation

# Check if PostgreSQL is installed
Write-Host "=== PostgreSQL Quick Setup ===" -ForegroundColor Cyan
Write-Host "`nChecking PostgreSQL installation..." -ForegroundColor Yellow

$pgFound = $false
try {
    $version = & psql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] PostgreSQL found: $version" -ForegroundColor Green
        $pgFound = $true
    }
}
catch {
    Write-Host "[ERROR] PostgreSQL not found in PATH" -ForegroundColor Red
    Write-Host "`nPlease install PostgreSQL first:" -ForegroundColor Yellow
    Write-Host "  1. Download: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host "  2. Run installer and remember the superuser password" -ForegroundColor Cyan
    Write-Host "  3. Add to PATH: C:\Program Files\PostgreSQL\16\bin" -ForegroundColor Cyan
    Write-Host "  4. Restart PowerShell and run this script again" -ForegroundColor Cyan
    exit 1
}

# Check if database exists
Write-Host "`nChecking for hospital_db database..." -ForegroundColor Yellow

$output = & psql -U postgres -t -c "SELECT 1 FROM pg_database WHERE datname = 'hospital_db';" 2>&1

if ($output -contains "1") {
    Write-Host "[OK] Database 'hospital_db' already exists" -ForegroundColor Green
}
else {
    Write-Host "[INFO] Creating 'hospital_db' database..." -ForegroundColor Yellow
    
    # Prompt for postgres password
    $password = Read-Host "Enter PostgreSQL superuser password for 'postgres' user"
    
    # Create database
    $env:PGPASSWORD = $password
    & psql -U postgres -c "CREATE DATABASE hospital_db;" 2>&1 | Write-Host
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database created successfully" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Failed to create database" -ForegroundColor Red
        exit 1
    }
    
    # Clean up
    $env:PGPASSWORD = $null
}

# Check Python environment
Write-Host "`nChecking Python environment..." -ForegroundColor Yellow

$pythonPath = & where python 2>&1 | Select-Object -First 1
if ($pythonPath) {
    Write-Host "[OK] Python found: $pythonPath" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
$backendPath = "e:\project\POC 1st\backend"

if (Test-Path "$backendPath\requirements.txt") {
    Set-Location $backendPath
    & pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[ERROR] requirements.txt not found at $backendPath" -ForegroundColor Red
    exit 1
}

# Run database migrations
Write-Host "`nInitializing database tables..." -ForegroundColor Yellow
& python init_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database initialized successfully" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Failed to initialize database" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check if PostgreSQL is running: Get-Service postgresql-x64-16 | Start-Service" -ForegroundColor Cyan
    Write-Host "  2. Verify credentials in .env file" -ForegroundColor Cyan
    Write-Host "  3. Check DATABASE_URL setting" -ForegroundColor Cyan
    exit 1
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend: cd '$backendPath' && python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "  2. Start frontend: cd 'e:\project\POC 1st\frontend' && npm run dev" -ForegroundColor White
Write-Host "  3. Open: http://localhost:3000" -ForegroundColor White

