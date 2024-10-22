#!/bin/sh

set -eu
eval `ssh-agent -s`
echo "$INPUT_REMOTE_KEY" | SSH_PASS="$INPUT_REMOTE_KEY_PASS" agent-add

rsync -r --delete-after -e 'ssh -o StrictHostKeyChecking=no' output/* eczrvsmy@50.6.153.225:/home1/eczrvsmy/public_html/website_287658e3/
