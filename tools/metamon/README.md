# Keystone META monitor

A service to ingest META updates for Keystone supported SoC platforms.

[TOC]

## Setup

The Keystone META monitor service is delivered via Docker container image. The
container currently assumes that credentials are secured and delivered by the
Google Cloud KMS and Google Cloud Storage services.

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

## Cloud

Configure a Google Cloud service account with `Reader` access to the secret
archive stored at `<cloud_storage_secret_url>` and `Decrypter` access to the
encryption key at `<cloud_kms_key>`.

## Run

Most deployments to Google Cloud just need to do the following.

```shell
$ docker run keystone-meta-monitor
```
