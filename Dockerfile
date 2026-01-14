# syntax=docker/dockerfile:1.4
FROM python:3.13-slim AS builder

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

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser
WORKDIR /app

# create a writable logs dir and hand over /app to appuser
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

USER appuser

COPY --from=builder /usr/local /usr/local

CMD ["python", "-m", "filter_crop.filter"]
