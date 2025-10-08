# GitHub Setup Guide for WebMethods Asset Downloader

Follow these steps to set up the WebMethods Asset Downloader in your GitHub repository:

## Step 1: Create a New Repository (if needed)

1. Go to GitHub and click on the "+" icon in the top right corner
2. Select "New repository"
3. Name your repository (e.g., "webmethods-assets")
4. Choose public or private visibility
5. Click "Create repository"

## Step 2: Push the Required Files

Push the following files to your repository:

- `download_webmethods_assets.py` - The main script
- `.github/workflows/download_webmethods_assets.yml` - GitHub Actions workflow
- `requirements.txt` - Dependencies
- `README_webmethods_downloader.md` - Documentation

You can do this using Git commands:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Copy the files
cp /path/to/download_webmethods_assets.py .
mkdir -p .github/workflows
cp /path/to/download_webmethods_assets.yml .github/workflows/
cp /path/to/requirements.txt .
cp /path/to/README_webmethods_downloader.md .

# Commit and push
git add .
git commit -m "Add WebMethods asset downloader"
git push
```

## Step 3: Set Up GitHub Secrets

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" > "Actions"
4. Click on "New repository secret"
5. Add the following secrets:

   - Name: `WEBMETHODS_ASSET_URL1`
     Value: URL to your first WebMethods asset
   
   - Name: `WEBMETHODS_ASSET_URL2`
     Value: URL to your second WebMethods asset
   
   Add more secrets as needed for additional assets.

## Step 4: Run the Workflow

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. You should see the "Download webMethods.io Assets" workflow
4. Click on it
5. Click on "Run workflow" button on the right side
6. Click the green "Run workflow" button in the dropdown

The workflow will now run and:
1. Check out your repository
2. Set up Python
3. Install dependencies
4. Create a JSON file with your asset URLs from the secrets
5. Download the assets
6. Commit and push the downloaded assets to your repository

## Step 5: Verify the Results

1. After the workflow completes, go to the main page of your repository
2. You should see a new commit with the message "Update webMethods.io assets [skip ci]"
3. The downloaded assets should be in the `downloaded_assets` directory

## Step 6: Schedule Automatic Downloads (Optional)

The workflow is already set to run daily at midnight. You can modify the schedule in the `.github/workflows/download_webmethods_assets.yml` file:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Run daily at midnight
  workflow_dispatch:  # Allow manual triggering
```

Change the cron expression as needed. For example:
- `0 */6 * * *` - Run every 6 hours
- `0 0 * * 1-5` - Run at midnight on weekdays only
- `0 8,17 * * *` - Run at 8 AM and 5 PM every day

## Troubleshooting

If the workflow fails:

1. Check the workflow run logs for error messages
2. Verify that your asset URLs are correct and accessible
3. Make sure the GitHub token has sufficient permissions
4. Check if the repository has enough space for the assets