#!/usr/bin/bash

TIMESTAMP="$(date +%Y-%m-%dT%H%M%S)";
tar \
  --exclude='ui/node_modules/*' \
  --exclude='node_modules/*' \
  --exclude='__pycache__/*' \
  --exclude=".git*" \
  --exclude='fromGPT' \
  --exclude="dist/*" \
  --exclude=".idea/*" \
  --exclude="*.tgz" \
  --exclude="venv" \
  --exclude="*.py[cdio]" \
  --exclude=".mypy_cache/*" \
  --exclude=".jupyter/*" \
  --exclude="ui_old/*" \
  --exclude="branding/*" \
  --exclude="*.ipynb" \
  --exclude=".ipynb_checkpoints/*" \
  --exclude=".pytest_cache/*" \
  --exclude=".nox/*" \
  --exclude=".ruff_cache/*" \
  --exclude=".benchmarks/*" \
  --exclude=".coverage" \
  -zcvf \
  archive-${TIMESTAMP}.tgz .
