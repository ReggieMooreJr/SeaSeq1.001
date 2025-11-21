# After pull / stash pop / etc.

# Stage everything
git add .

# Only commit if there is something to commit
if ! git diff --cached --quiet; then
  git commit -m "Auto-commit from gitsetup.sh"
  git push origin main
  echo "Local changes committed and pushed."
else
  echo "No changes to commit."
fi

