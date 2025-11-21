#!/bin/bash
# =============================================================================
# FILE: run-scan.sh
# PURPOSE: Run the MCP Site Scanner in API, CLI, One-Off, or Test modes.
# -----------------------------------------------------------------------------
# 📖 DEVELOPER NOTES — READ LIKE SCRIPTURE
# 1. Every run must yield a report named by its time — truth written in HTML.
# 2. Logs mirror each step so no run is silent.
# 3. Failures must speak clearly; successes must name their report.
# =============================================================================

APP="mcp_site_scanner.py"
VENV_DIR=".venv"
LOG_DIR="logs"
REPORT_DIR="reports"
MODE="$1"
TARGET_URL="$2"
START_TIME=$(date +%s)
TIMESTAMP=$(date +"%m_%d_%y_%H%M")  # Format: MM_DD_YY_HHMM
REPORT_FILE="$REPORT_DIR/REPORT_${TIMESTAMP}.html"
LOG_FILE="$LOG_DIR/scan_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR" "$REPORT_DIR"
cd "$(dirname "$0")" || exit 1

log_and_print() {
  echo "$1" | tee -a "$LOG_FILE"
}

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Ensure virtual environment and dependencies
# ─────────────────────────────────────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
  log_and_print "🔧 Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if [ ! -f "requirements.txt" ]; then
  log_and_print "⚠️  Missing requirements.txt — creating default."
  cat <<EOF > requirements.txt
flask
requests
beautifulsoup4
lxml
PyYAML
behave
pytest
EOF
fi

pip install -r requirements.txt > /dev/null

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2: Run mode logic — each path leads to a report
# ─────────────────────────────────────────────────────────────────────────────
if [ "$MODE" == "api" ]; then
  log_and_print "🚀 Starting API server..."
  python3 "$APP" --host 0.0.0.0 --port 8020 2>&1 | tee -a "$LOG_FILE"

elif [ "$MODE" == "cli" ]; then
  if [ -z "$TARGET_URL" ]; then
    log_and_print "❌ Missing target URL. Example: ./run-scan.sh cli https://example.com"
    exit 1
  fi
  log_and_print "🔍 Running interactive CLI scan on $TARGET_URL..."
  python3 "$APP" --target "$TARGET_URL" 2>&1 | tee -a "$LOG_FILE"
  mv reports/report.html "$REPORT_FILE" 2>/dev/null || true

elif [ "$MODE" == "once" ]; then
  if [ -z "$TARGET_URL" ]; then
    log_and_print "❌ Missing target URL. Example: ./run-scan.sh once https://example.com"
    exit 1
  fi
  log_and_print "⚡ Running one-off scan on $TARGET_URL..."
  python3 "$APP" --target "$TARGET_URL" --once 2>&1 | tee -a "$LOG_FILE"
  mv reports/report.html "$REPORT_FILE" 2>/dev/null || true

elif [ "$MODE" == "test" ]; then
  log_and_print "🧪 Running cucumber + unit tests..."
  behave tests/features 2>&1 | tee -a "$LOG_FILE"
  pytest tests/unit 2>&1 | tee -a "$LOG_FILE"

else
  log_and_print "Usage:"
  echo "  ./run-scan.sh api               # Run API server"
  echo "  ./run-scan.sh cli <URL>         # Run CLI interactive scan"
  echo "  ./run-scan.sh once <URL>        # Run one-off scan"
  echo "  ./run-scan.sh test              # Run tests"
  exit 0
fi

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3: Log completion summary
# ─────────────────────────────────────────────────────────────────────────────
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
if [ -f "$REPORT_FILE" ]; then
  log_and_print "✅ Report created: $REPORT_FILE"
else
  log_and_print "⚠️  No report file detected — check logs for details."
fi
log_and_print "🕒 Duration: ${DURATION}s"
log_and_print "📘 Logs saved in: $LOG_FILE"

# --- PATCH: Ensure consistent report name for tests ---
# If a timestamped report was created, also copy it as reports/report.html
if [ -d "reports" ]; then
  LATEST_REPORT=$(ls -t reports/REPORT_*.html 2>/dev/null | head -n 1)
  if [ -n "$LATEST_REPORT" ]; then
    cp "$LATEST_REPORT" "reports/report.html"
    echo "✅ Standard test report created at reports/report.html"
  fi
fi
# --- END PATCH ---

# =============================================================================
#  END OF run-scan.sh
# =============================================================================

# =============================================================================