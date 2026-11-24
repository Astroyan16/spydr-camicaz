#!/bin/sh
set -eu

BUNDLE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ ! -f "$BUNDLE_ROOT/run_spydr.sh" ]; then
  echo "Incomplete release: run_spydr.sh is missing." >&2
  exit 1
fi

# Update the command only after the isolated build has succeeded.
sh "$BUNDLE_ROOT/rebuild_with_existing_yorick.sh"
mkdir -p "$HOME/bin"
LAUNCHER_TMP=$(mktemp "$HOME/bin/.spydr-new.XXXXXX")
trap 'rm -f "$LAUNCHER_TMP"' 0
trap 'exit 1' 1 2 15
QUOTED_ROOT=$(printf '%s' "$BUNDLE_ROOT" | sed "s/'/'\\\\''/g")
printf '%s\n' '#!/bin/sh' "exec /bin/sh '$QUOTED_ROOT/run_spydr.sh' \"\$@\"" > "$LAUNCHER_TMP"
chmod +x "$LAUNCHER_TMP"
mv -f "$LAUNCHER_TMP" "$HOME/bin/spydr-new"

echo "Installed: $HOME/bin/spydr-new"
echo "Launch with: $HOME/bin/spydr-new"
case ":$PATH:" in
  *":$HOME/bin:"*) ;;
  *) echo 'To use the short command, add $HOME/bin to PATH in ~/.bash_profile.' ;;
esac
