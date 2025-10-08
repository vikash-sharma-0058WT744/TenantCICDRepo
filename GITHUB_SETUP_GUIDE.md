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

# Create necessary directories
mkdir -p .github/workflows

# Copy the files (make sure you're in the repository directory)
# Note: These files should already be in your current directory
cp download_webmethods_assets.py .
cp .github/workflows/download_webmethods_assets.yml .github/workflows/
cp requirements.txt .
cp README_webmethods_downloader.md .

# Commit and push
git add .
git commit -m "Add WebMethods asset downloader"
git push
```

If you don't have the workflow file in your local directory, you can create it directly:

```bash
# Create the workflow file
mkdir -p .github/workflows
cat > .github/workflows/download_webmethods_assets.yml << 'EOL'
name: Download webMethods.io Assets

on:
  schedule:
    - cron: '0 0 * * *'  # Run daily at midnight
  workflow_dispatch:  # Allow manual triggering

jobs:
  download-assets:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests
      
      - name: Create assets JSON file
        run: |
          cat > assets.json << 'EOL'
          {
            "assets": [
              {
                "name": "FlowService1",
                "type": "flow",
                "description": "Example flow service",
                "version": "1.0",
                "downloadLink": "${{ secrets.WEBMETHODS_ASSET_URL1 }}"
              },
              {
                "name": "FlowService2",
                "type": "flow",
                "description": "Another flow service",
                "version": "1.1",
                "downloadLink": "${{ secrets.WEBMETHODS_ASSET_URL2 }}"
              }
            ]
          }
          EOL
      
      - name: Download webMethods.io assets
        run: |
          python download_webmethods_assets.py \
            --json-file assets.json \
            --output-dir ./downloaded_assets \
            --git-repo .
      
      - name: Configure Git
        run: |
          git config --global user.name "GitHub Action"
          git config --global user.email "action@github.com"
      
      - name: Commit and push changes
        run: |
          git add -A
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update webMethods.io assets [skip ci]" && git push)
EOL

git add .github/workflows/download_webmethods_assets.yml
git commit -m "Add GitHub Actions workflow"
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