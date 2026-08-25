#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
mkdir -p "$DIST_DIR"

echo "Building DataCollector..."
echo "Target output: $DIST_DIR/DataCollector.exe"

# If rustc/cargo target is available, build standalone executable
if command -v cargo &> /dev/null; then
    echo "Compiling with Cargo..."
    cargo build --release --manifest-path "$SCRIPT_DIR/Cargo.toml"
fi

echo "Build process completed successfully."
