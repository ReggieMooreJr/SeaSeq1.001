#!/usr/bin/env bash
set -euo pipefail

REMOTE_URL="${1:-}"

if [[ -z "$REMOTE_URL" ]]; then
  echo "Usage: $0 <remote-url>"
  exit 1
fi

# Initialize repo if necessary
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Initializing new git repository..."
  git init
  git checkout -b main || git branch -M main

  if [[ -n "$(git status --porcelain)" ]]; then
    git add .
    git commit -m "Initial commit"
  fi

  git remote add origin "$REMOTE_URL"
else
  # Add origin if missing
  if ! git remote get-url origin >/dev/null 2>&1; then
    echo "No 'origin' remote found. Adding origin..."
    git remote add origin "$REMOTE_URL"
  fi
fi

echo "Using remote origin: $(git remote get-url origin)"

# Make sure we’re on main
git checkout main

# Check for unstaged or staged changes
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Local changes detected — stashing before pull..."
  git stash push -m "auto-stash-for-rebase"
  STASHED=true
else
  STASHED=false
fi

# Fetch and rebase
git fetch origin
git pull --rebase origin main

# Pop stash back if needed
if [[ "$STASHED" == true ]]; then
  echo "Restoring stashed changes..."
  git stash pop || echo "Warning: merge conflicts may need manual fixing."
fi

# Push local commits upstream
git push origin main

echo "Done! Repo synced and local changes preserved."

