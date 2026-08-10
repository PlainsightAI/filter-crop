# syntax=docker/dockerfile:1.4
FROM python:3.13.14-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip + filter-crop at version from VERSION file
RUN --mount=type=bind,source=VERSION,target=/tmp/VERSION,ro \
    set -eux; \
    RAW="$(head -n1 /tmp/VERSION)"; \
    # strip optional leading v/V and whitespace
    PKG_VERSION="$(printf '%s' "$RAW" | tr -d ' \t\r\n' | sed 's/^[vV]//')"; \
    [ -n "$PKG_VERSION" ] || { echo "VERSION file is empty"; exit 1; }; \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --index-url https://python.openfilter.io/simple \
    --extra-index-url https://pypi.org/simple \
    "filter-crop==${PKG_VERSION}"

# openfilter-base = python:3.13-slim + all outstanding Debian security patches (rebuilt
# weekly). It provides the PYTHONDONTWRITEBYTECODE/PYTHONUNBUFFERED env, the appuser account,
# and /app (WORKDIR) + /app/logs — so none of that is repeated here. No system libs are
# installed: filter-crop uses openfilter[all]'s opencv-python-headless (no imshow/GUI), so the
# old libxcb/libx11/libgl1/libglib2.0-0 are not needed.
FROM plainsightai/openfilter-base:py3.13

USER appuser

COPY --from=builder /usr/local /usr/local

CMD ["python", "-m", "filter_crop.filter"]
