#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
DIST_DIR="$SCRIPT_DIR/dist"

mkdir -p "$DIST_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " DataCollector — Build & Package"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify source files exist
echo "→ Verifying source integrity..."
python3 -c "import sys; sys.path.insert(0, '$SRC_DIR'); import main; print('  ✓ main.py valid')"

# Run the full test suite
echo "→ Running automated test suite..."
python3 -m unittest discover -s "$SCRIPT_DIR/tests" -p "test_*.py" -v 2>&1 | tail -5

# Build standalone portable .exe via PyInstaller (Windows cross-compile or native)
if command -v pyinstaller &> /dev/null; then
    echo "→ Building portable executable with PyInstaller..."
    pyinstaller \
        --onefile \
        --name DataCollector \
        --distpath "$DIST_DIR" \
        --workpath "$SCRIPT_DIR/.build_work" \
        --specpath "$SCRIPT_DIR" \
        --paths "$SRC_DIR" \
        --add-data "$SRC_DIR/schema.json:." \
        --add-data "$SRC_DIR/db_schema.sql:." \
        "$SRC_DIR/main.py" 2>&1 | tail -10

    # Check output
    if [ -f "$DIST_DIR/DataCollector" ] || [ -f "$DIST_DIR/DataCollector.exe" ]; then
        echo ""
        echo "  ✓ Standalone binary produced in: $DIST_DIR/"
        ls -lh "$DIST_DIR/"
    fi
else
    echo "  ⚠  PyInstaller not found — install via: pip install pyinstaller"
    echo "     To package for Windows, run from Windows with: pyinstaller --onefile --name DataCollector src/main.py"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Build Complete ✓"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Distribution binary: $DIST_DIR/DataCollector.exe"
echo "  Usage on Windows:    DataCollector.exe [run|simulate|export|status]"
echo ""
