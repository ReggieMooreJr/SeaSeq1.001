#!/usr/bin/env bash
set -Eeuo pipefail

# Always run from the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# -------------------------------
# 1. Find which compose command to use
# -------------------------------
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  echo "❌ ERROR: Neither 'docker-compose' nor 'docker compose' is available on PATH." >&2
  echo "   ➡ Install Docker Compose (or enable Docker Desktop integration) and try again." >&2
  exit 1
fi
echo "✅ Using compose command: $COMPOSE_CMD"

# -------------------------------
# 2. Check if Docker daemon is running
# -------------------------------
if ! docker info >/dev/null 2>&1; then
  echo "❌ ERROR: Docker daemon is not running or not accessible." >&2
  echo "   ➡ Start Docker (systemctl start docker OR open Docker Desktop)." >&2
  exit 2
fi

# -------------------------------
# 3. Ensure a docker-compose file exists
# -------------------------------
COMPOSE_FILE=""
for f in docker-compose.yml docker-compose.yaml compose.yml compose.yaml; do
  if [ -f "$f" ]; then
    COMPOSE_FILE="$f"
    break
  fi
done

if [ -z "$COMPOSE_FILE" ]; then
  echo "❌ ERROR: No docker-compose file found in $(pwd)." >&2
  echo "   ➡ Place docker-compose.yml in this directory or run the script from the repo root." >&2
  exit 3
fi
echo "✅ Found compose file: $COMPOSE_FILE"

# -------------------------------
# 4. Trap errors to show last logs if build fails
# -------------------------------
trap 'echo "⚠️ docker-compose up failed — dumping last 200 lines of logs"; \
      $COMPOSE_CMD logs --no-color --tail=200 || true' ERR

# -------------------------------
# 5. Bring up services
# -------------------------------
echo "🚀 Starting services (build + detached)..."
$COMPOSE_CMD up --build -d

echo "📜 Services started. Now following logs (CTRL-C to quit)..."
$COMPOSE_CMD logs -f
echo "👋 Exited log follow mode. Services are still running in the background.

To stop and remove all services, run: $COMPOSE_CMD down"
exit 0
# -------------------------------
# --- IGNORE ---
