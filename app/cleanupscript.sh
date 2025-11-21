#!/bin/bash

# remove_swp.sh - Removes all .swp files recursively from a given directory

# Usage:
#   ./remove_swp.sh [directory]
#   If no directory is specified, it defaults to the current directory.

TARGET_DIR="${1:-.}"

echo "Scanning for .swp files in: $TARGET_DIR"

# Find and remove .swp files
find "$TARGET_DIR" -type f -name "*.sw" -print -delete

echo "Cleanup complete."
