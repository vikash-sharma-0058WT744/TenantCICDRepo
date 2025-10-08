#!/usr/bin/env python3
"""
WebMethods Asset Downloader

This script downloads assets from WebMethods based on a JSON response,
saves them locally, and pushes them to a Git repository.
Designed to work in GitHub Actions environment.
"""

import json
import os
import sys
import requests
import logging
import html
import argparse
import subprocess
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('asset_downloader')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Download WebMethods assets and push to Git')
    parser.add_argument('--json-file', type=str, help='Path to JSON file containing assets')
    parser.add_argument('--json-string', type=str, help='JSON string containing assets')
    parser.add_argument('--output-dir', type=str, default='./downloaded_assets', help='Directory to save downloaded assets')
    parser.add_argument('--git-repo', type=str, default='.', help='Git repository path')
    parser.add_argument('--git-branch', type=str, default='main', help='Git branch name')
    parser.add_argument('--commit-message', type=str, 
                        default=f'Update WebMethods assets {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                        help='Git commit message')
    parser.add_argument('--mock', action='store_true', help='Mock downloads for testing')
    return parser.parse_args()

def load_json_data(json_file=None, json_string=None):
    """Load JSON data from file or string."""
    if json_file:
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON from file: {e}")
            return None
    elif json_string:
        try:
            return json.loads(json_string)
        except Exception as e:
            logger.error(f"Failed to parse JSON string: {e}")
            return None
    else:
        logger.error("No JSON input provided")
        return None

def download_file(url, output_path, mock=False):
    """Download a file from URL and save it to the specified path."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if mock:
            # Create a mock file for testing
            with open(output_path, 'w') as f:
                f.write(f"Mock content for {url}\n")
                f.write(f"This is a mock file created for testing purposes.\n")
                f.write(f"In a real scenario, this would be the downloaded content from {url}.\n")
            logger.info(f"Mock downloaded: {output_path}")
            return True
        else:
            # Real download
            logger.info(f"Downloading from: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {output_path}")
            return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"URL not found: {url}")
            logger.info("If you're testing with example URLs, use the --mock flag to create mock files.")
        else:
            logger.error(f"Failed to download {url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def git_operations(repo_path, files_to_add, branch_name, commit_message):
    """Add, commit and push files to Git repository."""
    try:
        # In GitHub Actions, we're already in the repository
        # and git is already configured
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            logger.info("Running in GitHub Actions environment")
            
            # Add files
            for file_path in files_to_add:
                # Get relative path to repo
                rel_path = os.path.relpath(file_path, repo_path)
                subprocess.run(['git', 'add', rel_path], check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                   stdout=subprocess.PIPE, text=True)
            
            if result.stdout.strip():
                # Commit changes
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                logger.info(f"Committed changes with message: {commit_message}")
                
                # Push to remote
                subprocess.run(['git', 'push'], check=True)
                logger.info(f"Pushed changes to remote repository")
            else:
                logger.info("No changes to commit")
                
            return True
        else:
            # Store original directory before changing
            original_dir = os.getcwd()
            
            try:
                # Initialize repository if it doesn't exist
                if not os.path.exists(os.path.join(repo_path, '.git')):
                    subprocess.run(['git', 'init', repo_path], check=True)
                    logger.info(f"Initialized new Git repository at {repo_path}")
                
                # Change to repository directory
                os.chdir(repo_path)
                
                try:
                    # Check if branch exists
                    result = subprocess.run(['git', 'rev-parse', '--verify', branch_name], 
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if result.returncode != 0:
                        # Create branch if it doesn't exist
                        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
                        logger.info(f"Created and checked out new branch: {branch_name}")
                    else:
                        # Checkout existing branch
                        subprocess.run(['git', 'checkout', branch_name], check=True)
                        logger.info(f"Checked out existing branch: {branch_name}")
                    
                    # Add files
                    for file_path in files_to_add:
                        # Get relative path to repo
                        rel_path = os.path.relpath(file_path, repo_path)
                        subprocess.run(['git', 'add', rel_path], check=True)
                    
                    # Check if there are changes to commit
                    result = subprocess.run(['git', 'status', '--porcelain'], 
                                           stdout=subprocess.PIPE, text=True)
                    
                    if result.stdout.strip():
                        # Commit changes
                        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                        logger.info(f"Committed changes with message: {commit_message}")
                        
                        # Check if remote exists
                        result = subprocess.run(['git', 'remote'], 
                                               stdout=subprocess.PIPE, text=True)
                        
                        if 'origin' in result.stdout:
                            # Push to remote
                            subprocess.run(['git', 'push', 'origin', branch_name], check=True)
                            logger.info(f"Pushed changes to remote repository")
                        else:
                            logger.warning("No remote repository configured, skipping push")
                    else:
                        logger.info("No changes to commit")
                
                finally:
                    # Return to original directory
                    os.chdir(original_dir)
                    
                return True
            except Exception as e:
                logger.error(f"Git operation failed: {e}")
                # Return to original directory in case of error
                if os.getcwd() != original_dir:
                    os.chdir(original_dir)
                return False
    except Exception as e:
        logger.error(f"Git operation failed: {e}")
        return False

def process_assets(json_data, output_dir, git_repo=None, git_branch='main', commit_message=None, mock=False):
    """Process assets from JSON data, download files and update Git repository."""
    if not json_data:
        logger.error("No valid JSON data to process")
        return False
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_files = []
    
    # Process each asset in the JSON response
    try:
        # Handle different possible JSON structures
        assets = json_data
        if isinstance(json_data, dict):
            # Try common keys that might contain the array
            for key in ['assets', 'items', 'data', 'results']:
                if key in json_data and isinstance(json_data[key], list):
                    assets = json_data[key]
                    break
        
        if not isinstance(assets, list):
            logger.error("Could not find asset array in JSON data")
            return False
        
        for asset in assets:
            # Look for download link in the asset
            download_url = None
            
            # Try common keys that might contain the download URL
            for key in ['downloadLink', 'download_link', 'url', 'link', 'downloadUrl']:
                if key in asset:
                    download_url = asset[key]
                    break
            
            if not download_url:
                logger.warning(f"No download link found in asset: {asset}")
                continue
            
            # Clean URL if needed (unescape HTML entities)
            download_url = html.unescape(download_url)
            
            # Determine filename from URL or asset metadata
            filename = os.path.basename(download_url.split('?')[0])
            
            # Try to get a better filename from asset metadata if available
            if 'name' in asset and 'type' in asset:
                ext = os.path.splitext(filename)[1] or '.zip'  # Default to .zip if no extension
                filename = f"{asset['name']}.{asset['type']}{ext}"
            elif 'filename' in asset:
                filename = asset['filename']
            elif 'name' in asset:
                filename = f"{asset['name']}.zip"
            
            # Clean filename to avoid path issues
            filename = ''.join(c for c in filename if c.isalnum() or c in '._- ')
            
            # Determine output path
            output_path = os.path.join(output_dir, filename)
            
            # Download the file
            if download_file(download_url, output_path, mock):
                downloaded_files.append(output_path)
    
    except Exception as e:
        logger.error(f"Error processing assets: {e}")
        return False
    
    # If Git repository is specified, push changes
    if git_repo and downloaded_files:
        if not commit_message:
            commit_message = f"Added {len(downloaded_files)} assets on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return git_operations(git_repo, downloaded_files, git_branch, commit_message)
    
    return len(downloaded_files) > 0

def main():
    """Main function to run the script."""
    args = parse_arguments()
    
    # Load JSON data
    json_data = load_json_data(args.json_file, args.json_string)
    
    # Process assets
    success = process_assets(
        json_data, 
        args.output_dir, 
        args.git_repo, 
        args.git_branch, 
        args.commit_message,
        args.mock
    )
    
    if success:
        logger.info("Asset download and Git operations completed successfully")
        return 0
    else:
        logger.error("Asset download or Git operations failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
