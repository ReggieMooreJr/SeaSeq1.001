#!/usr/bin/env bash
set -Eeuo pipefail

echo "🚦 Running smoke tests..."

# 1. Check if containers are up
echo "🔍 Checking running containers..."
if ! docker compose ps | grep -q "Up"; then
  echo "❌ No containers are running."
  exit 1
fi
echo "✅ Containers are running."

# 2. Check API health
echo "🔍 Checking API health endpoint..."
if curl -sSf http://localhost:8000/health >/dev/null; then
  echo "✅ API responded on /health."
else
  echo "⚠️ API /health not found. Retrying root..."
  if curl -sSf http://localhost:8000/ >/dev/null; then
    echo "✅ API root responded."
  else
    echo "❌ API did not respond."
    exit 2
  fi
fi

# 3. Check seaseq-cli is callable
echo "🔍 Checking seaseq-cli..."
if ! docker compose exec -T seaseq-cli /seaseq --help >/dev/null 2>&1; then
  echo "❌ seaseq-cli failed to respond."
  exit 3
fi
echo "✅ seaseq-cli responds."

# 4. Check reports directory
echo "🔍 Checking reports directory..."
if [ -d "./reports" ] && [ "$(ls -A ./reports)" ]; then
  echo "✅ Reports directory exists and has files."
else
  echo "⚠️ Reports directory missing or empty."
fi

echo "🎉 Smoke tests completed."
# End of script