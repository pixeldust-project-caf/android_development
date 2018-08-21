# Keystone META monitor

A service to ingest META updates for Keystone supported SoC platforms.

[TOC]

# Setup

The Keystone META monitor service is delivered via Docker container image. The
container currently assumes that credentials are secured and delivered by the
Google Cloud KMS and Google Cloud Storage services.

## Add secrets

Follow the Google Cloud KMS directions on [Storing
secrets](https://cloud.google.com/kms/docs/store-secrets). This involves
creating a separate Google Cloud project to host the key management service.
These Cloud KMS settings are passed to the `run.sh` script in the Docker
container's `KMS_PROJECT`, `KMS_KEYRING` and `KMS_KEY` environment variables.

The `run.sh` script assumes that credentials are stored encrypted in a `.tar.gz`
archive stored in a Cloud Storage bucket. The URL to this file is passed in the
Docker container's `SECRET_URL` environment variable.

## Build the container

To create a new container image follow the instructions below.

1. [Install Docker CE](https://www.docker.com/products/docker-engine).
2. Build the Keystone META monitor container.
  ```shell
  $ docker build . --tag keystone-meta-monitor \
      --build-arg SECRET_URL=<cloud_storage_secret_url> \
      --build-arg KMS_PROJECT=<cloud_kms_project> \
      --build-arg KMS_KEYRING=<cloud_kms_keyring> \
      --build-arg KMS_KEY=<cloud_kms_key>
```

## Configure the cloud

Configure a Google Cloud service account with `Reader` access to the secret
archive stored at `SECRET_URL` and `Decrypter` access to the encryption key at
`KMS_KEY`. Create a Compute Engine virtual machine instance and choose an
appropriate image for the VM. The Keystone META monitor container has been
tested on the most recent Container Optimized stable image. When fetching META
repositories for all supported Keystone targets, a disk size of at least 100 GB
is recommended.

# Run

Most deployments to Google Cloud just need to use the Keystone META monitor
container's default entrypoint. This will automatically download, decrypt and
extract credentials before starting the service. The container can be manually
started as follows.

```shell
$ docker run keystone-meta-monitor
```
