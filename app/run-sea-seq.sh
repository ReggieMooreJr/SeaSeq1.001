#!/bin/bash
set -e

MODE=${1:-all}
TIMESTAMP=$(date +"%m_%d_%y")
REPORT_DIR="reports"
TARGET_SITE_URL_DEFAULT="https://jsonplaceholder.typicode.com"
TARGET_SITE_URL="${TARGET_SITE_URL:-$TARGET_SITE_URL_DEFAULT}"

mkdir -p $REPORT_DIR

echo "🔧 SEA-SEQ Mode: $MODE"
echo "🌐 Target: $TARGET_SITE_URL"
echo "📁 Reports directory: $REPORT_DIR"

case "$MODE" in
  scrape)
    echo "🕷️ Running metadata scraper..."
    python3 -m crawler --url "$TARGET_SITE_URL" --out "$REPORT_DIR/REPORT_${TIMESTAMP}_metadata.json"
    ;;
  cli)
    echo "⚡ Running SEA-SEQ CLI..."
    ./seaseq --spec tests/examples/jsonplaceholder/suite.yaml \
             --env tests/examples/jsonplaceholder/env.json \
             --openapi tests/examples/jsonplaceholder/openapi.json \
             --out $REPORT_DIR/REPORT_${TIMESTAMP}_seaseq.html -v
    ;;
  api)
    echo "🚀 Starting FastAPI server on port 8000 and 7107..."
    uvicorn app:app --host 0.0.0.0 --port 8000 &
    uvicorn app:app --host 0.0.0.0 --port 7107
    ;;
  dashboard)
    echo "🖥️ Serving dashboard (HTML reports) on port 8080..."
    python3 -m http.server 8080 --directory reports
    ;;
  all)
    echo "🚀 Full workflow: Scrape → Test → Dashboard"
    python3 -m crawler --url "$TARGET_SITE_URL" --out "$REPORT_DIR/REPORT_${TIMESTAMP}_metadata.json"
    if [ -f ./seaseq ]; then
      ./seaseq --spec tests/examples/jsonplaceholder/suite.yaml \
               --env tests/examples/jsonplaceholder/env.json \
               --openapi tests/examples/jsonplaceholder/openapi.json \
               --out $REPORT_DIR/REPORT_${TIMESTAMP}_seaseq.html -v
    fi
    echo "📊 Reports generated in $REPORT_DIR/"
    python3 -m http.server 8080 --directory reports
    ;;
  *)
    echo "❌ Unknown mode: $MODE"
    echo "Usage: ./run-sea-seq.sh [scrape|cli|api|dashboard|all]"
    exit 1
    ;;
esac
echo "✅ Done!"
echo "Reports are available in the '$REPORT_DIR' directory."
echo "Access the dashboard at http://localhost:8080 if running in dashboard mode."
echo "Press Ctrl+C to stop any running servers."
echo "🔚 Exiting."
echo "Thank you for using SEA-SEQ! I hope you enjoyed the wave! 🌊 "
# End of script