# ---------------------------------
# Repo-specific variables
# ---------------------------------

IMAGE ?= us-west1-docker.pkg.dev/plainsightai-prod/oci/filter-crop

# Define these variables for consistency in the repo
REPO_NAME ?= filter-crop
REPO_NAME_SNAKECASE ?= filter_crop
REPO_NAME_PASCALCASE ?= FilterCrop

# Unique pipeline configuration for this repo
# TODO: Add GAR source support via dlCache
PIPELINE := \
	- VideoIn \
		--sources 'file://filter_example_video.mp4!loop' \
	- $(REPO_NAME_SNAKECASE).filter.$(REPO_NAME_PASCALCASE) \
		--mq_log pretty \
	- Webvis
# ---------------------------------
# Repo-specific targets
# ---------------------------------

.PHONY: install
install:  ## Install package with dev dependencies from GAR
	@if [ -n "$$GOOGLE_APPLICATION_CREDENTIALS" ]; then \
		echo "Using GOOGLE_APPLICATION_CREDENTIALS to authenticate"; \
		pip install --upgrade keyrings.google-artifactregistry-auth; \
		PIP_INDEX_URL="https://us-west1-python.pkg.dev/plainsightai-prod/python/simple/" \
		PIP_EXTRA_INDEX_URL="https://pypi.org/simple" \
		pip install .[dev]; \
	else \
		echo "Using gcloud access token"; \
		ACCESS_TOKEN=$$(gcloud auth print-access-token) && \
		PIP_INDEX_URL="https://oauth2accesstoken:$${ACCESS_TOKEN}@us-west1-python.pkg.dev/plainsightai-prod/python/simple/" \
		PIP_EXTRA_INDEX_URL="https://pypi.org/simple" \
		pip install .[dev]; \
	fi

.PHONY: compose
compose:  ## Make docker-compose.yaml from command line run PIPELINE
	filter_runtime compose $(PIPELINE) > new-docker-compose.yaml
	mv new-docker-compose.yaml docker-compose.yaml

# ---------------------------------
# Shared makefile include
# ---------------------------------
# Ensure the path matches where `filter.mk` is stored in each repo
include build-include/filter.mk
