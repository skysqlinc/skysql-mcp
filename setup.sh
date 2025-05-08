#!/bin/bash
# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    curl -sSf https://astral.sh/uv/install.sh | sh
fi

# Install dependencies using uv
uv pip install -e .
