#!/bin/sh
set -eu

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LIB_DIR="$BUNDLE_ROOT/libcamicaz"
YCAM_DIR="$BUNDLE_ROOT/yCamicaz"
YORICK_ROOT="$BUNDLE_ROOT/yorick/relocate"

if ! command -v make >/dev/null 2>&1; then
  echo "make is required on the Linux test machine." >&2
  exit 1
fi

if ! command -v g++ >/dev/null 2>&1; then
  echo "g++ is required on the Linux test machine." >&2
  exit 1
fi

if [ ! -d "$YORICK_ROOT" ]; then
  echo "Portable Yorick tree not found: $YORICK_ROOT" >&2
  exit 1
fi

echo "Rebuilding libcamicaz..."
make -C "$LIB_DIR" clean
make -C "$LIB_DIR" CC=g++

echo "Rebuilding yCamicaz..."
make -C "$YCAM_DIR" clean \
  Y_MAKEDIR="$YORICK_ROOT" \
  Y_EXE="$YORICK_ROOT/bin/yorick" \
  Y_EXE_HOME="$YORICK_ROOT" \
  Y_EXE_SITE="$YORICK_ROOT" \
  LIB_CAMICAZ_DIR="$LIB_DIR"

make -C "$YCAM_DIR" CC=g++ TGT=dll \
  Y_MAKEDIR="$YORICK_ROOT" \
  Y_EXE="$YORICK_ROOT/bin/yorick" \
  Y_EXE_HOME="$YORICK_ROOT" \
  Y_EXE_SITE="$YORICK_ROOT" \
  LIB_CAMICAZ_DIR="$LIB_DIR"

echo
echo "Portable binaries rebuilt:"
echo "  $LIB_DIR/libcamicaz.so"
echo "  $YCAM_DIR/yCamicaz.so"
echo
echo "You can now launch the isolated test version with:"
echo "  ./run_spydr_portable.sh"
