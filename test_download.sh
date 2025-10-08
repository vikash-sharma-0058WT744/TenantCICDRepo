#!/bin/bash
# Test script for WebMethods asset downloader

# Create test directory
mkdir -p ./test_downloads

# Run the downloader in mock mode
echo "Testing WebMethods asset downloader in mock mode..."
python3 download_webmethods_assets.py \
  --json-file assets.json \
  --output-dir ./test_downloads \
  --mock

# Check if files were created
if [ -d "./test_downloads" ] && [ "$(ls -A ./test_downloads)" ]; then
  echo "✅ Test passed: Files were created in test_downloads directory"
else
  echo "❌ Test failed: No files were created in test_downloads directory"
  exit 1
fi

# Clean up
echo "Cleaning up test files..."
rm -rf ./test_downloads

echo "All tests completed successfully!"

# Made with Bob
