# WebMethods Asset Downloader

This tool downloads WebMethods assets from URLs specified in a JSON file and pushes them to a Git repository. It's designed to work both locally and in GitHub Actions workflows.

## Features

- Download WebMethods assets from URLs
- Automatically push downloaded assets to a Git repository
- Works in GitHub Actions environment
- Supports mock mode for testing

## Usage in GitHub Actions

The workflow file `.github/workflows/download_webmethods_assets.yml` is set up to:

1. Run daily at midnight (configurable)
2. Allow manual triggering
3. Download assets from URLs specified in GitHub Secrets
4. Push the downloaded assets to the repository

### Setting Up GitHub Secrets

Add the following secrets to your GitHub repository:

- `WEBMETHODS_ASSET_URL1`: URL to download the first asset
- `WEBMETHODS_ASSET_URL2`: URL to download the second asset
- Add more as needed

### Customizing the Workflow

Edit the `.github/workflows/download_webmethods_assets.yml` file to:

- Change the schedule
- Add more assets
- Modify the output directory
- Change the commit message

## Local Usage

You can also run the script locally:

```bash
# Install dependencies
pip install requests

# Run with a JSON file
python download_webmethods_assets.py --json-file assets.json --output-dir ./downloads

# Run with mock mode (for testing)
python download_webmethods_assets.py --json-file assets.json --output-dir ./downloads --mock

# Push to a specific Git repository
python download_webmethods_assets.py --json-file assets.json --git-repo ./my-repo --git-branch main
```

## JSON Format

The JSON file should have the following structure:

```json
{
  "assets": [
    {
      "name": "AssetName",
      "type": "assetType",
      "description": "Description",
      "version": "1.0",
      "downloadLink": "https://example.com/download/asset.zip"
    }
  ]
}
```

## Troubleshooting

- If downloads fail, check if the URLs are accessible and valid
- For testing purposes, use the `--mock` flag to create mock files instead of actual downloads
- Check GitHub Actions logs for detailed error messages