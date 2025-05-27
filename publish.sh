#!/bin/bash

set -e

echo "Publishing video-frame-extractor to PyPI..."

echo "Running tests..."
pytest

echo "Checking package..."
twine check dist/*

echo "Uploading to PyPI..."
twine upload dist/*

echo "Published successfully!"