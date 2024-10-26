#! /bin/bash
set -e

curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
source "$HOME/.rye/env"
rye sync
make sync
make tailwind
make generate_css
make generate
make copy_assets