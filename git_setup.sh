

#!/usr/bin/env bash
set -euo pipefail

# Usage: ./setup_git_repo.sh <remote-url>
# Example: ./setup_git_repo.sh https://github.com/YourUser/YourRepo.git

REMOTE_URL="${1:-}"

if [[ -z "$REMOTE_URL" ]]; then
  echo "Usage: $0 <remote-url>"
  exit 1
fi

# 0. If this is not yet a git repo, initialize it and set main + origin
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "No git repo found. Initializing..."
  git init

  # Create main branch
  git checkout -b main || git branch -M main

  # Add all files and make an initial commit (if there is anything to commit)
  if [[ -n "$(git status --porcelain)" ]]; then
    git add .
    git commit -m "Initial commit"
  fi

  # Add remote origin
  git remote add origin "$REMOTE_URL"
else
  # If repo exists but origin not set, add it
  if ! git remote get-url origin >/dev/null 2>&1; then
    echo "No 'origin' remote found. Adding origin..."
    git remote add origin "$REMOTE_URL"
  fi
fi

echo "Using remote origin: $(git remote get-url origin)"

# 1. Make sure you’re on main
git checkout main

# 2. Fetch the latest from GitHub
git fetch origin

# 3. Pull the remote main history into your main (rebasing keeps history tidy)
git pull --rebase origin main

# 4. Now push your updated main branch
git push origin main

echo "Done: directory is a git repo and main is synced with origin/main."
