#!/bin/bash
# =============================================================================
# FILE: run-docker-tests.sh
# PURPOSE: Build, run, and test the MCP Site Scanner inside Docker with full HTML reports.
# -----------------------------------------------------------------------------
# 📖 DEVELOPER NOTES — READ LIKE SCRIPTURE
# 1. This script is the high priest of CI — it builds, tests, and chronicles every run.
# 2. Unit and feature tests both testify; their truths are written in HTML.
# 3. Every run is recorded, every success counted.
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  DECLARATIONS: Paths, image, container, and directories
# ─────────────────────────────────────────────────────────────────────────────
IMAGE_NAME="mcp-scanner"
CONTAINER_NAME="mcp-scanner-test"
REPORT_DIR="reports/tests"
HISTORY_FILE="$REPORT_DIR/test_history.log"
TIMESTAMP=$(date +"%m_%d_%y_%H%M")

# Ensure directories exist
mkdir -p "$REPORT_DIR"

# ─────────────────────────────────────────────────────────────────────────────
#  FUNCTION: log_and_print
#  PURPOSE: Mirror each action to both console and history log
# ─────────────────────────────────────────────────────────────────────────────
log_and_print() {
  echo "$1" | tee -a "$HISTORY_FILE"
}

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1: Build Docker image
# ─────────────────────────────────────────────────────────────────────────────
log_and_print "🐳 Building Docker image: $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" . || { log_and_print "❌ Docker build failed."; exit 1; }

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2: Run tests inside Docker
# ─────────────────────────────────────────────────────────────────────────────
log_and_print "🧪 Running tests in container: $CONTAINER_NAME..."
docker run --rm -it \
  -v "$(pwd)/reports:/app/reports" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME" bash -c "
    mkdir -p /app/reports/tests &&
    echo '📘 Running behave feature tests...' &&
    behave tests/features --format pretty --format html --outfile /app/reports/tests/behave_report_${TIMESTAMP}.html || true &&
    echo '🧩 Running pytest unit tests...' &&
    pytest tests/unit --maxfail=1 --disable-warnings -q \
      --html=/app/reports/tests/pytest_report_${TIMESTAMP}.html \
      --self-contained-html || true
  "

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3: Generate summary dashboard (HTML + console)
# ─────────────────────────────────────────────────────────────────────────────
log_and_print "🧾 Compiling test summary..."

# Parse report counts
TOTAL_FEATURES=$(grep -o "Feature:" reports/tests/behave_report_${TIMESTAMP}.html | wc -l | tr -d ' ')
TOTAL_UNIT=$(grep -o "class=" reports/tests/pytest_report_${TIMESTAMP}.html | wc -l | tr -d ' ')
TOTAL_PASSED=$(grep -o "passed" reports/tests/pytest_report_${TIMESTAMP}.html | wc -l | tr -d ' ')
TOTAL_FAILED=$(grep -o "failed" reports/tests/pytest_report_${TIMESTAMP}.html | wc -l | tr -d ' ')
SUCCESS_RATE=0
if [ "$TOTAL_UNIT" -gt 0 ]; then
  SUCCESS_RATE=$((100 * TOTAL_PASSED / (TOTAL_UNIT + TOTAL_FAILED)))
fi

# Record this run
echo "RUN_DATE: $(date) | PASSED: $TOTAL_PASSED | FAILED: $TOTAL_FAILED | SUCCESS_RATE: ${SUCCESS_RATE}%" >> "$HISTORY_FILE"

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4: Generate test summary HTML report
# ─────────────────────────────────────────────────────────────────────────────
SUMMARY_FILE="$REPORT_DIR/test_summary_${TIMESTAMP}.html"

cat <<EOF > "$SUMMARY_FILE"
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MCP Site Scanner Test Summary</title>
<style>
body { font-family: Arial, sans-serif; background: #f8f9fa; color: #333; padding: 20px; }
h1 { color: #004085; border-bottom: 2px solid #004085; padding-bottom: 5px; }
table { border-collapse: collapse; width: 100%; margin-top: 15px; }
th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
th { background: #e9ecef; }
.pass { color: green; font-weight: bold; }
.fail { color: red; font-weight: bold; }
</style>
</head>
<body>
<h1>Test Automation Summary — ${TIMESTAMP}</h1>
<p><strong>Test Purpose:</strong> Validate the core scanner logic, link validation, form detection, and report generation integrity.</p>

<table>
  <tr><th>Feature Tests Executed</th><td>${TOTAL_FEATURES}</td></tr>
  <tr><th>Unit Tests Executed</th><td>${TOTAL_UNIT}</td></tr>
  <tr><th>Tests Passed</th><td class="pass">${TOTAL_PASSED}</td></tr>
  <tr><th>Tests Failed</th><td class="fail">${TOTAL_FAILED}</td></tr>
  <tr><th>Success Rate</th><td>${SUCCESS_RATE}%</td></tr>
</table>

<h2>Historical Success Record</h2>
<pre>
$(tail -n 10 "$HISTORY_FILE")
</pre>

<p>🧩 Detailed reports:</p>
<ul>
  <li><a href="behave_report_${TIMESTAMP}.html">Feature Test Report (behave)</a></li>
  <li><a href="pytest_report_${TIMESTAMP}.html">Unit Test Report (pytest)</a></li>
</ul>

</body>
</html>
EOF

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5: Display results in console
# ─────────────────────────────────────────────────────────────────────────────
log_and_print "✅ Test summary generated: $SUMMARY_FILE"
log_and_print "📘 Behave report: reports/tests/behave_report_${TIMESTAMP}.html"
log_and_print "📘 Pytest report: reports/tests/pytest_report_${TIMESTAMP}.html"
log_and_print "📊 Success rate this run: ${SUCCESS_RATE}%"
log_and_print "📜 History stored in: $HISTORY_FILE"

# =============================================================================
#  END OF run-docker-tests.sh
# =============================================================================
