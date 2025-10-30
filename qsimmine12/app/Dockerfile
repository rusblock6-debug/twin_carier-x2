FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /project


ARG CI_COMMIT_REF_SLUG
ARG CI_REGISTRY_USER
ARG CI_REGISTRY_PASSWORD

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      highs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN set -eux; \
    python -m pip install --upgrade pip; \
    if [ "$CI_COMMIT_REF_SLUG" = "dev" ]; then \
      INDEX_URL="https://${CI_REGISTRY_USER}:${CI_REGISTRY_PASSWORD}@nexus.dmi-msk.ru/repository/pypi-dev-group/simple"; \
    elif [ "$CI_COMMIT_REF_SLUG" = "staging" ]; then \
      INDEX_URL="https://${CI_REGISTRY_USER}:${CI_REGISTRY_PASSWORD}@nexus.dmi-msk.ru/repository/pypi-staging-group/simple"; \
    elif [ "$CI_COMMIT_REF_SLUG" = "main" ]; then \
      INDEX_URL="https://${CI_REGISTRY_USER}:${CI_REGISTRY_PASSWORD}@nexus.dmi-msk.ru/repository/pypi-main-group/simple"; \
    else \
        INDEX_URL="https://pypi.org/simple"; \
    fi; \
    echo "Using INDEX_URL=$INDEX_URL"; \
    mkdir -p /root/.config/pip; \
    printf "[global]\nindex-url = %s\n" "$INDEX_URL" > /root/.config/pip/pip.conf; \
    pip install --no-cache-dir -r requirements.txt; \
    rm -f /root/.config/pip/pip.conf

COPY . /project/app
