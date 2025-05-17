# Common variables
PYPI_REPO ?= https://us-west1-python.pkg.dev/plainsightai-prod/python/simple/
VERSION ?= $(shell cat VERSION)
CONTAINER_EXEC := docker
GOOGLE_APPLICATION_CREDENTIALS ?= $(HOME)/.config/gcloud/application_default_credentials.json

export IMAGE
export VERSION

check-tag = !(git rev-parse -q --verify "refs/tags/v${VERSION}" > /dev/null 2>&1) || \
	(echo "the version: ${VERSION} has been released already" && exit 1)


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: check-version
check-version:  ## Check if VERSION has already been released/tagged
	@$(check-tag)


.PHONY: publish
publish:  ## Tag with VERSION and git push
	@$(check-tag)
	git tag v${VERSION}
	git push origin v${VERSION}


.PHONY: build-wheel
build-wheel:  ## Build python wheel
	python -m pip install setuptools build wheel twine setuptools-scm --index-url https://pypi.org/simple
	python -m build --wheel


.PHONY: publish-wheel
publish-wheel:  ## Publish python wheel
	TWINE_USERNAME=${PYPI_USERNAME} TWINE_PASSWORD=${PYPI_API_KEY} twine upload --repository-url ${PYPI_REPO} dist/*


.PHONY: build-image
build-image:  ## Build docker image
	${CONTAINER_EXEC} build \
		-t ${IMAGE}:${VERSION} \
		--secret id=google_credentials,src=${GOOGLE_APPLICATION_CREDENTIALS} \
		.

.PHONY: publish-image
publish-image:  ## Publish docker image
	${CONTAINER_EXEC} push ${IMAGE}:${VERSION}


.PHONY: run-image
run-image:  ## Run image in docker container
	${CONTAINER_EXEC} compose up


.PHONY: run
run:  ## Run locally with supporting Filters in other processes
	filter_runtime run ${PIPELINE}


.PHONY: test
test:  ## Run unit tests
	pytest -vv -s tests/ --junitxml=results/pytest-results.xml


.PHONY: test-coverage
test-coverage:  ## Run unit tests and generate coverage report
	@mkdir -p Reports
	@pytest -vv --cov=tests --junitxml=Reports/coverage.xml --cov-report=json:Reports/coverage.json -s tests/
	@jq -r '["File Name", "Statements", "Missing", "Coverage%"], (.files | to_entries[] | [.key, .value.summary.num_statements, .value.summary.missing_lines, .value.summary.percent_covered_display]) | @csv'  Reports/coverage.json >  Reports/coverage_report.csv
	@jq -r '["TOTAL", (.totals.num_statements // 0), (.totals.missing_lines // 0), (.totals.percent_covered_display // "0")] | @csv'  Reports/coverage.json >>  Reports/coverage_report.csv


.PHONY: clean
clean:  ## Delete all generated files and directories
	sudo rm -rf build/ cache/ dist/ $(REPO_NAME_SNAKECASE).egg-info/ telemetry/
	find . -name __pycache__ -type d -exec rm -rf {} +

