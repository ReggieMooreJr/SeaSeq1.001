#!/usr/bin/env bash
# BOOK: SEA-SEC Psalms of Startup (Local)

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# CHAPTER 1: Read settings
if [ ! -f ".env" ]; then
  echo ".env not found. Create it first."
  exit 1
fi
set -a; source .env; set +a

# CHAPTER 2: Prepare Python
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# CHAPTER 3: Start API (background)
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
API_PID=$!
sleep 2

# CHAPTER 4: Trigger one test run
python - <<'PY'
import os, requests, json
u = os.getenv("TEST_URL", "https://example.org")
r = requests.post("http://127.0.0.1:8000/run", json={"url": u, "capture": False}, timeout=180)
r.raise_for_status()
print(json.dumps(r.json(), indent=2))
PY

echo "API running as PID $API_PID"
echo "Stop with: kill $API_PID"
