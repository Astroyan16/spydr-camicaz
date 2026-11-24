#!/bin/sh
# Compatibility entry point for existing test bundles.
set -eu
BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec /bin/sh "$BUNDLE_ROOT/run_spydr.sh" "$@"
