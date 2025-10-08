# GitHub Token and Repository Configuration Guide

This guide explains how to configure the GitHub token and repository for pushing downloaded WebMethods assets.

## GitHub Actions Token Configuration

When running in GitHub Actions, you don't need to explicitly configure a token for pushing to the same repository. GitHub Actions automatically provides a `GITHUB_TOKEN` secret that has permissions to push to the repository where the workflow is running.

The workflow is already configured to use this token implicitly when pushing changes:

```yaml
- name: Commit and push changes
  run: |
    git add -A
    git diff --quiet && git diff --staged --quiet || (git commit -m "Update webMethods.io assets [skip ci]" && git push)
```

## Pushing to a Different Repository

If you want to push the assets to a different repository, you need to:

1. **Create a Personal Access Token (PAT)**:
   - Go to your GitHub account settings
   - Click on "Developer settings" in the left sidebar
   - Click on "Personal access tokens" > "Tokens (classic)"
   - Click "Generate new token"
   - Give it a name (e.g., "WebMethods Asset Downloader")
   - Select the `repo` scope to allow pushing to repositories
   - Click "Generate token"
   - **Copy the token** - you won't be able to see it again!

2. **Add the token as a secret in your repository**:
   - Go to your repository settings
   - Click on "Secrets and variables" > "Actions"
   - Click "New repository secret"
   - Name: `GH_PAT` (or any name you prefer)
   - Value: Paste the token you copied
   - Click "Add secret"

3. **Modify the workflow file to use the token**:

```yaml
- name: Checkout target repository
  uses: actions/checkout@v3
  with:
    repository: username/target-repo
    token: ${{ secrets.GH_PAT }}
    path: target-repo

- name: Copy assets to target repository
  run: |
    cp -r ./downloaded_assets/* ./target-repo/
    cd ./target-repo
    git config user.name "GitHub Action"
    git config user.email "action@github.com"
    git add -A
    git diff --quiet && git diff --staged --quiet || (git commit -m "Update webMethods.io assets [skip ci]" && git push)
```

## Configuring the Target Repository in the Script

If you want to specify the target repository in the script itself, modify the workflow file:

```yaml
- name: Download webMethods.io assets
  run: |
    python download_webmethods_assets.py \
      --json-file assets.json \
      --output-dir ./downloaded_assets \
      --git-repo ./target-repo
  env:
    GIT_REPOSITORY: ${{ secrets.TARGET_REPOSITORY }}
    GIT_TOKEN: ${{ secrets.GH_PAT }}
```

And add these secrets to your repository:
- `TARGET_REPOSITORY`: The repository name (e.g., `username/repo-name`)
- `GH_PAT`: Your Personal Access Token

Then modify the `download_webmethods_assets.py` script to use these environment variables:

```python
def git_operations(repo_path, files_to_add, branch_name, commit_message):
    """Add, commit and push files to Git repository."""
    try:
        # In GitHub Actions, check if we're pushing to a different repo
        if os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GIT_REPOSITORY'):
            target_repo = os.environ.get('GIT_REPOSITORY')
            git_token = os.environ.get('GIT_TOKEN')
            
            if git_token:
                remote_url = f"https://x-access-token:{git_token}@github.com/{target_repo}.git"
                
                # Clone the target repository
                target_dir = os.path.join(os.getcwd(), "target-repo")
                subprocess.run(['git', 'clone', remote_url, target_dir], check=True)
                
                # Copy files to target repo
                for file_path in files_to_add:
                    filename = os.path.basename(file_path)
                    target_path = os.path.join(target_dir, filename)
                    shutil.copy2(file_path, target_path)
                
                # Commit and push to target repo
                os.chdir(target_dir)
                subprocess.run(['git', 'config', 'user.name', 'GitHub Action'], check=True)
                subprocess.run(['git', 'config', 'user.email', 'action@github.com'], check=True)
                subprocess.run(['git', 'add', '.'], check=True)
                
                # Check if there are changes to commit
                result = subprocess.run(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, text=True)
                if result.stdout.strip():
                    subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                    subprocess.run(['git', 'push'], check=True)
                    logger.info(f"Pushed changes to target repository: {target_repo}")
                else:
                    logger.info("No changes to commit in target repository")
                
                return True
```

## Summary

1. **For pushing to the same repository** where the GitHub Action is running:
   - No additional configuration needed
   - The workflow uses the default `GITHUB_TOKEN` automatically

2. **For pushing to a different repository**:
   - Create a Personal Access Token with `repo` scope
   - Add it as a secret in your repository
   - Modify the workflow to use this token when checking out and pushing to the target repository