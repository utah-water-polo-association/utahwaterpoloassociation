#!/bin/sh

set -eu

SSH_OPTS="-o IgnoreUnknown=UseKeychain -o StrictHostKeyChecking=no -o AddKeysToAgent=yes -o UseKeychain=yes"
REMOTE="eczrvsmy@50.6.153.225"

eval "$(ssh-agent -s)"
echo "$INPUT_REMOTE_KEY" | ssh-add -

rsync -r --delete-after -e "ssh $SSH_OPTS" output/* "$REMOTE:/home1/eczrvsmy/public_html/website_287658e3/"
rsync -r --delete-after -e "ssh $SSH_OPTS" output/* "$REMOTE:/home1/eczrvsmy/public_html/"
ssh $SSH_OPTS "$REMOTE" "chmod 755 /home1/eczrvsmy/public_html/uploads"