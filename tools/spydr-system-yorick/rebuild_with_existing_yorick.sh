#!/bin/sh
set -eu

resolve_link() {
  target=$1
  if command -v readlink >/dev/null 2>&1; then
    readlink -f "$target" 2>/dev/null && return 0
  fi
  printf '%s\n' "$target"
}

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LIB_DIR="$BUNDLE_ROOT/libcamicaz"
YCAM_DIR="$BUNDLE_ROOT/yCamicaz"

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

YORICK_BIN=$(resolve_link "$YORICK_BIN")
YORICK_ROOT=${SPYDR_TEST_YORICK_ROOT:-$(CDPATH= cd -- "$(dirname -- "$YORICK_BIN")/.." && pwd)}

if [ ! -f "$YORICK_ROOT/Make.cfg" ]; then
  echo "Cannot locate Yorick build files in $YORICK_ROOT" >&2
  echo "Set SPYDR_TEST_YORICK_ROOT=/path/to/yorick/relocate and retry." >&2
  exit 1
fi

if ! command -v make >/dev/null 2>&1; then
  echo "make is required on the test machine." >&2
  exit 1
fi

if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ is required on the test machine." >&2
  exit 1
fi

echo "Using existing Yorick:"
echo "  bin  : $YORICK_BIN"
echo "  root : $YORICK_ROOT"
echo
echo "This rebuild stays inside the copied test folder."
echo "No file from the existing stable Yorick / Spydr installation is modified."
echo

echo "Rebuilding libcamicaz in the test bundle..."
make -C "$LIB_DIR" clean
make -C "$LIB_DIR" CC=g++

echo "Rebuilding yCamicaz in the test bundle..."
make -C "$YCAM_DIR" clean \
  Y_MAKEDIR="$YORICK_ROOT" \
  Y_EXE="$YORICK_BIN" \
  Y_EXE_HOME="$YORICK_ROOT" \
  Y_EXE_SITE="$YORICK_ROOT" \
  LIB_CAMICAZ_DIR="$LIB_DIR"

make -C "$YCAM_DIR" CC=g++ TGT=dll \
  Y_MAKEDIR="$YORICK_ROOT" \
  Y_EXE="$YORICK_BIN" \
  Y_EXE_HOME="$YORICK_ROOT" \
  Y_EXE_SITE="$YORICK_ROOT" \
  LIB_CAMICAZ_DIR="$LIB_DIR"

echo
echo "Test bundle rebuilt successfully:"
echo "  $LIB_DIR/libcamicaz.so"
echo "  $YCAM_DIR/yCamicaz.so"
echo
echo "Launch with:"
echo "  ./run_spydr_test.sh"
