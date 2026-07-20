#!/usr/bin/env bash
set -e

if ! command -v npx &> /dev/null
then
    echo "npx could not be found. Please install Node.js."
    exit 1
fi

echo -e "\033[36mStarting Igrish Dev Environment (Melissa Backend & Tauri Frontend)...\033[0m"

BACKEND_CMD="cd melissa-service && source venv/bin/activate && uvicorn app.main:app --reload"
FRONTEND_CMD="cd companion-app && pnpm tauri dev"

npx concurrently -c "blue,magenta" -n "BACKEND,FRONTEND" "$BACKEND_CMD" "$FRONTEND_CMD"
