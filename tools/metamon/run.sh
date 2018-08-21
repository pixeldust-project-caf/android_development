#!/bin/bash
# Usage:
#  $ run.sh <secret_url> <kms_project> <kms_keyring> <kms_key>

# Add gsutil command to PATH.
source /usr/google-cloud-sdk/path.bash.inc

if [[ $# != 4 ]]; then
  echo "Usage"
  echo "  $ run.sh <secret_url> <kms_project> <kms_keyring> <kms_key>"
  exit 1
fi

readonly SECRET_URL=$1
readonly KMS_PROJECT=$2
readonly KMS_KEYRING=$3
readonly KMS_KEY=$4

# Retrieve and install secrets.
echo "Copy encrypted credentials from Cloud Storage"
gsutil cp "$SECRET_URL" "$HOME/secrets.tar.gz.enc" || { exit 1; }

echo "Decrypt credentials to $HOME"
gcloud kms decrypt \
    --location=global \
    --project="$KMS_PROJECT" \
    --keyring="$KMS_KEYRING" \
    --key="$KMS_KEY" \
    --ciphertext-file="$HOME/secrets.tar.gz.enc" \
    --plaintext-file="$HOME/secrets.tar.gz" || { exit 1; }

echo "Extract credentials to $HOME"
tar -C "$HOME" -xzf "$HOME/secrets.tar.gz" || { exit 1; }

# Run long-lived service.
echo "Start Keystone META monitor"
exec python3 /usr/sbin/meta_monitor.py \
    --meta_poll_interval=3600 \
    --log=INFO
