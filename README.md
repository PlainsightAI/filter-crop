# Crop Filter

**IMPORTANT!** This repo is not meant to be cloned, it is meant to be used as a template for your own repo.

**IMPORTANT!** You need to get access to GCP and ensure that `gcloud` CLI installed and authenticated with your Google SSO credentials.

**IMPORTANT!** Do **NOT** try to run the `templateize` script under Windows.

**IMPORTANT!** `make run` is only for development, **NOT** for deployment to customers, for that please create a docker-compose.yaml to run with docker.

The **VERY FIRST** thing you **MUST** do before even creating `venv` or any other files in this drectory is run the templatize script:

    ./templatize

Note: running templatize will:
- Overwrite `.github/workflows/ci.yaml` with `.github/disabled-workflows/ci.yaml`, effictevly replacing the `template`'s CI with the `filter`'s CI. `template`'s CI tests the templatization, while `filter`'s CI tests, builds and publishes the actual filter and its docs.
- Replace all place holders with the proper repo/filter names

## Requirements

To follow these instructions there are a few prerequisites. You must:

- Be authenticated to GAR:
```
gcloud auth login
gcloud auth application-default login
```

- Set your gcloud project to plainsightai-prod and configure docker to use gcloud:
```
gcloud config set project plainsightai-prod
gcloud auth configure-docker us-west1-docker.pkg.dev
```

It is assumed you will be running this on a GPU. If not then you will have to comment out the `deploy:` section in the `docker-compose.yaml` file and the unit test will fail since it compares against GPU numbers.

## Install

In order to run the filter locally or build/publish the Python wheel we need to install properly:

    virtualenv venv
    source venv/bin/activate
    make install

## Run locally

Now to run the filter locally do:

    make run

Then navigate to `http://localhost:8000` and you should see the video looping.

## Run in docker

**IMPORTANT!** If your filter uses the GPU and `make compose` doesn't autmatically add it to the `docker-compose.yaml` then make sure to add the following to your filter's section in the compose file:

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

First, build the filter docker image:

    make build-image

If you changed the PIPELINE in the Makefile (if not then skip this step), then rebuild the docker-compose.yaml (you may have to tweak the generated docker-compose.yaml):

    make compose

Now run it:

    make run-image

Again, navigating to `http://localhost:8000` will show you the video.

## Unit tests

It is assumed you have installed the packages necessary to run locally (not in docker). Run:

    make test

## Publish releases

- Ensure the `VERSION` file at root has a production semver tag (i.e. `v1.2.3`)
    - If you intend to release a non-production version such as a development, release candidate or an internal release then add a build number and a classifcation to your version tag (i.e. `v1.2.3.4-dev`, `v1.2.3.0-rc` or `v1.2.3.47-int`)
- Ensure the version tag of newest entry in `RELEASE.md` matches the tag in `VERSION`
    - Important: Our releases are documentation driven. Not updating `RELEASE.md` will not trigger a release. Filters cannot be merged to main unless `RELEASE.md` is updated. The `RELEASE.md` file is validated by our CI and requires version enteries to be in the correct decending order.
- Simple merge to main. When a new version is detected in `RELEASE.md` the CI will:
  - Build and publish the docker image to the GAR OCI registery
  - Build and publish the python wheel to the GAR python registery
  - Push the docs to both production and development docuemntation sites

## Publish documentation
- Renaming `_PUBLISHING_PATH` to `PUBLISHING_PATH` will activate automatic publishing
- When automatic publishing is active, `RELEASE.md` from at the repository's root and the `docs` directory will be merged and pushed to the `PlainsightAI/docs-prod` and `PlainsightAI/docs-dev` on every new release
- Upon receiving a commit, `PlainsightAI/docs-prod` will compile a docs preview and open a PR. Once the PR is manually merged, the docs will be published to the production documentation site (https://plainsightai.info)
- `PlainsightAI/docs-dev` will compile a docs preview and open a PR. The PR will be automatically merged and the docs will be published to the internal documentation site (https://dev.plainsightai.info)
- The content of `docs/~internal` will only be published to the internal documentation website and excluded from production
- Any `[Unreleased]` or non production release info in `RELEASE.md` will only be published to the internal docs website. The production docs site will only contain production tags (i.e. v1.2.3) and exclude non-production tags (i.e. `v1.2.3.4-dev`, `v1.2.3.0-rc` or `v1.2.3.47-int`)