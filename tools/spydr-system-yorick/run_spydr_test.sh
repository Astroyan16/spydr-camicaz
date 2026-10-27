#!/bin/sh
set -eu

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CAMTOP="$BUNDLE_ROOT/yCamicaz"
SPYDR_DIR="$CAMTOP/yorick/spydr"

YORICK_BIN=${SPYDR_TEST_YORICK_BIN:-}
if [ -z "${YORICK_BIN}" ]; then
  if command -v yorick >/dev/null 2>&1; then
    YORICK_BIN=$(command -v yorick)
  elif [ -x /home/etudiants/yorick.git/relocate/bin/yorick ]; then
    YORICK_BIN=/home/etudiants/yorick.git/relocate/bin/yorick
  else
    echo "Unable to find an existing Yorick binary." >&2
    echo "Set SPYDR_TEST_YORICK_BIN=/absolute/path/to/yorick and retry." >&2
    exit 1
  fi
fi

if [ ! -x "$YORICK_BIN" ]; then
  echo "Yorick binary is not executable: $YORICK_BIN" >&2
  exit 1
fi

for library in "$BUNDLE_ROOT/libcamicaz/libcamicaz.so" "$CAMTOP/yCamicaz.so"; do
  if [ ! -s "$library" ]; then
    echo "Cannot start: shared library is missing or empty: $library" >&2
    echo "Build this copy with: sh rebuild_with_existing_yorick.sh" >&2
    exit 1
  fi
done

export CAMTOP
export STYCTOP="$CAMTOP"
# Yorick find_in_path concatenates directory and filename verbatim.
export Y_PYTHON="$SPYDR_DIR/"
export Y_GLADE="$SPYDR_DIR/"
export LD_LIBRARY_PATH="$BUNDLE_ROOT/libcamicaz${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cd "$SPYDR_DIR"
SPYDR_VERSION=$(cat "$SPYDR_DIR/VERSION")
echo "Spydr / Camicaz v$SPYDR_VERSION"

if command -v rlwrap >/dev/null 2>&1; then
  exec rlwrap "$YORICK_BIN" -i spydr.i "$@"
fi

exec "$YORICK_BIN" -i spydr.i "$@"
