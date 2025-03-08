#! /usr/bin/env bash

# Install uv (system-dependency)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Dependencies
make install
