#!/bin/sh

set -eu
eval `ssh-agent -s`
echo "$INPUT_REMOTE_KEY" | ssh-add -

rsync -r --delete-after -e 'ssh -o StrictHostKeyChecking=no' output/* eczrvsmy@50.6.153.225:/home1/eczrvsmy/public_html/website_287658e3/
