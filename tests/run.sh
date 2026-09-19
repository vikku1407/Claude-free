#!/bin/sh
# Both suites, straight from a clean checkout:
#   sh tests/run.sh
# jsdom is installed outside the repo so the checkout stays clean (a sandbox or
# CI wipes /tmp between runs, so the install is checked rather than assumed).
set -e
cd "$(dirname "$0")/.."
JSDOM_DIR=${JSDOM_DIR:-/tmp/erp-tests}
if [ ! -d "$JSDOM_DIR/node_modules/jsdom" ]; then
    echo "installing jsdom into $JSDOM_DIR ..."
    mkdir -p "$JSDOM_DIR"
    ( cd "$JSDOM_DIR" && npm i --silent jsdom@24 )
fi
ln -sfn "$JSDOM_DIR/node_modules" node_modules   # so `import 'jsdom'` from tests/ resolves
node tests/palette-click.mjs
echo
node tests/standalone-file.mjs
