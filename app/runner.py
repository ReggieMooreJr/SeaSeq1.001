#!/usr/bin/env python3
"""
runner_cli.py – Run SEA-SEQ CLI (`seaseq`) inside Docker.
"""

import subprocess
import sys
import logging

logging.basicConfig(
    filename="/var/log/sea-seq/runner_cli.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def main():
    try:
        logging.info("Starting SEASEQ CLI runner... - runner.py:18")
        result = subprocess.run(
            ["seaseq"] + sys.argv[1:], capture_output=True, text=True, check=True
        )
        logging.info("CLI output:\n%s - runner.py:22", result.stdout)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("CLI failed with exit code %s: %s - runner.py:25", e.returncode, e.stderr)
        print(f"[ERROR] CLI failed: {e.stderr} - runner.py:26", file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
