#! /bin/bash

curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
source "$HOME/.rye/env"
rye sync
make tailwind
make generate_css
make sync
make generate
make copy_assets