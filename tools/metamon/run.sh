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

SECRET_URL=$1
KMS_PROJECT=$2
KMS_KEYRING=$3
KMS_KEY=$4

# Retrieve and install secrets.
gsutil cp $SECRET_URL "$HOME/secrets.tar.gz.enc" || { exit 1; }
gcloud kms decrypt \
    --location=global \
    --project=$KMS_PROJECT \
    --keyring=$KMS_KEYRING \
    --key=$KMS_KEY \
    --ciphertext-file="$HOME/secrets.tar.gz.enc" \
    --plaintext-file="$HOME/secrets.tar.gz" || { exit 1; }
tar -C "$HOME" -xzf "$HOME/secrets.tar.gz" || { exit 1; }

# Run long-lived service.
python3 /usr/sbin/meta_monitor.py --meta_poll_interval=3600
