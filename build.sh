#!/bin/bash

set -e

echo "Building video-frame-extractor..."

rm -rf build/ dist/ *.egg-info/

python -m build --sdist

python -m build --wheel

echo "Build completed successfully!"
echo "Files created:"
ls -la dist/