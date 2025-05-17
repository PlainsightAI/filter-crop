# Shared Makefile Assets

This repository contains the shared Makefile logic (in `Include.mk`) and any other common CI/CD or build assets used by multiple repositories. By using **git subtree**, each dependent repository can reference this repo’s contents under a subdirectory.

### Why Use a Subtree?

* **Single Source of Truth**: All common targets, environment variables, and build steps live in one place.
* **Simplicity**: No more duplicating logic across repos.
* **Autonomy**: Each repo includes the shared files but can still function if the subtree is temporarily out of sync.
* **Control Updates**: Teams can choose when to pull changes from this repo, ensuring stable builds.

***

## Filter Make Include
### Usage

#### 1. Adding the Subtree

First, decide on a subdirectory name in your dependent repo (e.g., `build-include`). Then, from within the dependent repo folder:

```bash
git subtree add \
  --prefix=build-include \
  https://github.com/PlainsightAI/make-python-base.git \
  main \
  --squash
```

Explanation:

* `--prefix=build-include`: The subdirectory within your dependent repo where these shared files will live.
* `https://github.com/PlainsightAI/make-python-base.git`: The URL to this repo containing the shared assets.
* `main`: The branch in this (shared) repo that you want to track.
* `--squash`: Combines all of this repo’s commit history into a single commit in the dependent repo’s history.

After running that command, you should see `build-include/Include.mk` and possibly other files in your dependent repo.

#### 2. Referencing `filter.mk` from Your Makefile

Inside your filter repo’s `Makefile`:

```make
# Repo-specific variables
IMAGE ?= docker-repo.example.com/make-python-base/my-filter
REPO_NAME ?= my-service
REPO_NAME_SNAKECASE ?= my_service
REPO_NAME_PASCALCASE ?= MyService
PIPELINE := \
  - VideoIn \
    --sources 'example_video.mp4!loop' \
  - $(REPO_NAME_SNAKECASE).filter.$(REPO_NAME_PASCALCASE) \
    --mq_log pretty \
  - Webvis

# Include the shared Makefile
include build-include/filter.mk
```

> **Tip:** Make sure you keep the relative path consistent (`build-include/filter.mk` in this example).

#### 3. Pulling Updates from the Shared Repo

Whenever you want to bring in upstream changes from the `make-python-base` repo:

```bash
git subtree pull \
  --prefix=build-include \
     https://github.com/PlainsightAI/make-python-base.git \
      main \
  --squash
```

This updates the contents of `build-include` to match the latest from the `main` branch of `make-python-base`, combining them into a single new commit.

#### 4. Contributing Changes Back

If you make changes to `filter.mk` (or other shared assets) inside a dependent repo and want to contribute them back to the shared repo:

1. Commit your changes normally in the dependent repo.
2.  Push your changes to the shared repo via subtree:

    ```bash
    git subtree push \
      --prefix=build-include \
      https://github.com/PlainsightAI/make-python-base.git \
      main
    ```
3. This will create a new commit in the `make-python-base` repo’s `main` branch with the changes you made in your dependent repo.

> **Note:** If you often push changes back from multiple different repos, it’s usually best to coordinate these updates, or work directly in the shared repo first, then pull into each project. You can do whichever flow your team prefers.

***

### Making Changes Safely

1. **Work in a Feature Branch**
   * Clone this repo directly (`make-python-base`), create a feature branch (e.g., `feature/better-build-targets`), and push changes there.
   * Merge changes to `main` when they’re stable and tested.
2. **Pull into Dependent Repos**
   * In each dependent repo, use `git subtree pull` to bring in the new changes.
   * Ensure your local builds/tests pass before committing.
   * You can find each repo needed using search, or even just looking for repos that start with 'filter'
3. **Release or Tag**
   * If you want to keep track of stable snapshots, create git tags or release branches in the `shared-makefiles` repo.
   * Then have each dependent repo reference that specific tag or branch when pulling, for more stability.

***

### Best Practices

* **Review Process**: Treat `Include.mk` changes like any critical library code. Use pull requests and code reviews so that changes are transparent to all teams.
* **Pin Versions if Needed**: If certain repos need older versions, they can remain on an older commit or branch of this shared repo until they’re ready to upgrade.
* **Document Breaking Changes**: If you remove or rename a Make target, include a note in the commit message and/or `CHANGELOG.md` so that dependent repos know how to adjust.
* **Automate Pulls**: You can set up a script or small CI step that regularly checks if `shared-makefiles` has changed and automatically opens a pull request in the dependent repos to update the subtree. This can help keep everything in sync without manual steps.

***

### Example Directory Layout

```
make-python-base/                  (this repo)
├── README.md
└── filter.mk

filter-example/                   (dependent repo)
├── Makefile
├── build-include/
│   └── filter.mk                 (pulled in from shared-makefiles)
└── ...
```
