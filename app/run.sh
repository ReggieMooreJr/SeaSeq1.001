#!/bin/bash
set -e

# -----------------------------
# SEA-SEQ Unified Runner
# -----------------------------
# Usage:
#   ./run.sh compose
#   ./run.sh reports [suite env openapi]
#
# Examples:
#   ./run.sh compose
#   ./run.sh reports tests/examples/jsonplaceholder/suite.yaml \
#                     tests/examples/jsonplaceholder/env.json \
#                     tests/examples/jsonplaceholder/openapi.json
# -----------------------------

MODE=$1
shift || true

IMAGE_NAME="seaseq_runner"
CONTAINER_NAME="seaseq_runner"
REPORTS_DIR="$(pwd)/reports"
TARGET_SITE_URL_DEFAULT="https://mlbam-park.b12sites.com/"
TARGET_SITE_URL="${TARGET_SITE_URL:-$TARGET_SITE_URL_DEFAULT}"

case "$MODE" in
  compose)
    echo "🔧 Building + starting docker-compose stack..."
    docker-compose up --build -d
    echo "📡 Streaming logs (Ctrl+C to stop)..."
    docker-compose logs -f
    ;;

  reports)
    # Defaults if no args provided
    SUITE_FILE=${1:-tests/examples/jsonplaceholder/suite.yaml}
    ENV_FILE=${2:-tests/examples/jsonplaceholder/env.json}
    OPENAPI_FILE=${3:-tests/examples/jsonplaceholder/openapi.json}

    mkdir -p "$REPORTS_DIR"

    echo "🔧 Building Docker image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME .

    echo "🚀 Running SEA-SEQ functional tests AND pentest (if available)"
    # We mount the project into /app inside container. The command:
    # 1) runs seaseq to generate reports
    # 2) attempts to run security/pentest_runner.py (if it exists) using python3
    #    with config pentest.yaml and writes findings to reports/sec-findings.json
    docker run --rm -it \
      -e TARGET_SITE_URL="$TARGET_SITE_URL" \
      -v "$REPORTS_DIR:/app/reports" \
      -v "$(pwd):/app" \
      --name $CONTAINER_NAME \
      $IMAGE_NAME \
      /bin/bash -lc "\
        set -e; \
        echo '[step] running seaseq CLI'; \
        ./seaseq \
          --spec \"$SUITE_FILE\" \
          --env \"$ENV_FILE\" \
          --openapi \"$OPENAPI_FILE\" \
          --out reports -v --parallel 4; \
        echo '[step] seaseq finished'; \
        if [ -f security/pentest_runner.py ]; then \
          echo '[step] running security/pentest_runner.py with pentest.yaml'; \
          python3 security/pentest_runner.py --config pentest.yaml --out reports/sec-findings.json || echo 'pentest runner exited non-zero'; \
        else \
          echo '[notice] security/pentest_runner.py not found — skipping pentest runner' > reports/sec-findings-not-run.txt; \
        fi; \
        echo '[done] test + pentest steps completed'"

    echo "✅ Reports generated (if any) in ./reports/"
    ;;

  *)
    echo "❌ Unknown mode: $MODE"
    echo "Usage: ./run.sh {compose|reports}"
    exit 1
    ;;
esac
# Step 3: Notify user of completion and report location
echo "🎯 SEA-SEQ Demo was run and is completed!   "
echo "Congratulations! Bravo Zulu! Your SEA-SEQ tests have finished running."
echo "You can find the generated reports in the 'reports' directory."
echo "✅ Reports generated in ./reports/"
echo "🔗 Target Site URL: $TARGET_SITE_URL
echo "📂 Reports Directory: $REPORTS_DIR
echo "🎉 MLBAM For LIFE!



Notes

The container runs a small shell sequence: ./seaseq first, then conditionally runs python3 security/pentest_runner.py --config pentest.yaml --out reports/sec-findings.json.

If security/pentest_runner.py is missing, a small marker file reports/sec-findings-not-run.txt will appear in ./reports/ to indicate pentest didn't run.

This is non-destructive (--rm), mounts the repo and reports directory to preserve artifacts on the host.