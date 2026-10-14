#!/bin/sh
set -eu

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CAMTOP="$BUNDLE_ROOT/yCamicaz"
SPYDR_DIR="$CAMTOP/yorick/spydr"
YORICK_ROOT="$BUNDLE_ROOT/yorick/relocate"
YORICK_BIN="$YORICK_ROOT/bin/yorick"

if [ ! -x "$YORICK_BIN" ]; then
  echo "Portable Yorick not found: $YORICK_BIN" >&2
  exit 1
fi

if [ ! -f "$BUNDLE_ROOT/libcamicaz/libcamicaz.so" ] || [ ! -f "$CAMTOP/yCamicaz.so" ]; then
  echo "Portable binaries are missing." >&2
  echo "Run ./rebuild_portable.sh once on the original Linux machine before launching Spydr." >&2
  exit 1
fi

export CAMTOP
export STYCTOP="$CAMTOP"
# Yorick find_in_path concatenates directory and filename verbatim.
export Y_PYTHON="$SPYDR_DIR/"
export Y_GLADE="$SPYDR_DIR/"
export LD_LIBRARY_PATH="$BUNDLE_ROOT/libcamicaz${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cd "$SPYDR_DIR"
SPYDR_VERSION=$(cat "$SPYDR_DIR/VERSION")
echo "Spydr / Camicaz v$SPYDR_VERSION (test)"

if command -v rlwrap >/dev/null 2>&1; then
  exec rlwrap "$YORICK_BIN" -i spydr.i "$@"
fi

exec "$YORICK_BIN" -i spydr.i "$@"
