$ErrorActionPreference = "Stop"

# Ensure npx is available
if (!(Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Error "npx is not installed or not in PATH. Please install Node.js."
    exit 1
}

# Define the commands
$backendCmd = "cd melissa-service && .\venv\Scripts\activate && uvicorn app.main:app --reload"
$frontendCmd = "cd companion-app && pnpm tauri dev"

Write-Host "Starting Igrish Dev Environment (Melissa Backend & Tauri Frontend)..." -ForegroundColor Cyan

# We use npx concurrently to multiplex the output and handle process lifecycle cleanly
npx concurrently -c "blue,magenta" -n "BACKEND,FRONTEND" "$backendCmd" "$frontendCmd"
