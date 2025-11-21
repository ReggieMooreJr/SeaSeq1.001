#!/usr/bin/env bash
# BOOK: SEA-SEC Psalms of Startup (Docker)

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

[ -f .env ] || { echo ".env missing"; exit 1; }

docker compose build
docker compose up -d
sleep 6
docker compose ps

echo "Trigger manual run if needed:"
echo "curl -X POST http://localhost:8000/run -H 'content-type: application/json' -d '{\"url\":\"'${TEST_URL:-https://example.org}'\",\"capture\":false}'"
#!/usr/bin/env bash
# BOOK: SEA-SEC Lamentations of Shutdown (Docker)

set -euo pipefail
docker compose down

if [ "${1:-}" = "--prune" ]; then
  docker system prune -f
fi

echo "Docker stack down."
