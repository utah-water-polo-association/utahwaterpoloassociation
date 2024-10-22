#!/bin/sh

set -eu
eval `ssh-agent -s`
echo "$INPUT_REMOTE_KEY"
echo "$INPUT_REMOTE_KEY" | ssh-add -
ssh-add -l
ssh -o StrictHostKeyChecking=No -o AddKeysToAgent=Yes -o UseKeychain=Yes -v eczrvsmy@50.6.153.225
rsync -r --delete-after -e 'ssh -o StrictHostKeyChecking=No -o AddKeysToAgent=Yes -o UseKeychain=Yes' output/* eczrvsmy@50.6.153.225:/home1/eczrvsmy/public_html/website_287658e3/
