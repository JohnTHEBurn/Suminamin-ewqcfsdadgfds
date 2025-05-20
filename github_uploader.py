import os
import base64
import hashlib
import requests
import logging
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GitHub API Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'MemeCoinSites')
REPO_PREFIX = "meme-site-"
REPO_TTL = 3600  # Time-to-live in seconds (1 hour)

class GitHubUploader:
    def __init__(self):
        self.headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.api_url = 'https://api.github.com'
        self.repos_to_delete = {}  # Store repos with their deletion timestamp
        self.cleanup_thread = None
        self.start_cleanup_thread()
        
    def upload_site(self, site_name, html_content, site_hash, image_path=None):
        """
        Create a GitHub repository with the website and enable GitHub Pages.
        
        Args:
            site_name: Name of the meme coin
            html_content: HTML content of the website (with images already embedded as base64)
            site_hash: Unique hash for the site
            image_path: Optional path to logo image file (deprecated - now handled before upload)
            
        Returns:
            str: URL of the hosted website
        """
        try:
            # Create a unique repository name
            repo_name = f"{REPO_PREFIX}{site_hash.lower()}"
            
            # Create repository
            repo_url = self._create_repository(repo_name, f"Meme coin site for {site_name}")
            if not repo_url:
                return None
                
            # Add HTML file as index.html
            if not self._add_file(repo_name, "index.html", html_content, "Initial site commit"):
                return None
            
            # NOTE: Images are now embedded directly in the HTML as base64 data URLs
            # so we don't need to upload image files separately
                
            # Add a basic README.md
            readme_content = f"# {site_name} Meme Coin\n\nThis is an automatically generated landing page for {site_name} meme coin."
            if not self._add_file(repo_name, "README.md", readme_content, "Add README"):
                logger.warning("Failed to add README, but site is still created")
            
            # Schedule this repo for deletion after TTL seconds
            self.repos_to_delete[repo_name] = time.time() + REPO_TTL
            
            # Return repository URLs
            repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}"  # Repository URL
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/main/index.html"  # Raw HTML file
            
            # With public repos, we can use GitHub Pages immediately
            # Enable GitHub Pages for the repository
            self._enable_github_pages(repo_name)
            
            # Now we can use the GitHub Pages URL
            preview_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"  # GitHub Pages URL with trailing slash
            
            # Images are now embedded in the HTML directly as base64
            # so we don't need to return separate image URLs
            
            logger.info(f"Successfully created public repository: {repo_url} (will be deleted in 1 hour)")
            logger.info(f"GitHub Pages URL should be available shortly at: {preview_url}")
            logger.info(f"Note: GitHub Pages may take 1-2 minutes to become active after setup")
            
            return {
                "repo_url": repo_url,
                "raw_url": raw_url,
                "preview_url": preview_url
            }
            
        except Exception as e:
            logger.error(f"Error uploading to GitHub: {e}")
            return None
    
    def _create_repository(self, repo_name, description):
        """Create a new GitHub repository"""
        try:
            payload = {
                'name': repo_name,
                'description': description,
                'private': False,  # Make repositories public
                'auto_init': False
            }
            
            response = requests.post(
                f"{self.api_url}/user/repos",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code in (201, 200):
                logger.info(f"Created repository: {repo_name}")
                return response.json().get('html_url')
            else:
                logger.error(f"Failed to create repository: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            return None
    
    def _add_file(self, repo_name, file_path, content, commit_message):
        """Add a text file to the repository"""
        try:
            url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
            
            # Encode content to base64
            content_bytes = content.encode('utf-8')
            base64_content = base64.b64encode(content_bytes).decode('utf-8')
            
            payload = {
                'message': commit_message,
                'content': base64_content,
                'branch': 'main'  # or 'master' depending on your default branch
            }
            
            response = requests.put(
                url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code in (201, 200):
                logger.info(f"Added file: {file_path}")
                return True
            else:
                logger.error(f"Failed to add file: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding file: {e}")
            return False
            
    # Binary file and directory creation methods are no longer needed
    # as we embed images directly in the HTML as base64 data URLs
    
    def _enable_github_pages(self, repo_name):
        """Enable GitHub Pages for the repository"""
        try:
            url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}/pages"
            
            # Use the updated GitHub Pages API format (this changed recently)
            # The API now expects a JSON object with branch and path properties
            pages_payload = {
                "source": {
                    "branch": "main",
                    "path": "/"
                }
            }
            
            # Set the correct Accept header for the GitHub Pages API
            pages_headers = self.headers.copy()
            pages_headers['Accept'] = 'application/vnd.github+json'
            
            # Create the GitHub Pages site
            response = requests.post(
                url, 
                headers=pages_headers,
                json=pages_payload
            )
            
            if response.status_code in (201, 200, 204):
                logger.info(f"Enabled GitHub Pages for repository: {repo_name}")
                
                # Update the preview URL to use the correct GitHub Pages URL format
                preview_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
                logger.info(f"GitHub Pages URL: {preview_url}")
                return True
            else:
                # If initial attempt fails, try with different branch
                logger.warning(f"First GitHub Pages attempt failed: {response.status_code}, {response.text}")
                
                # Try alternate method - create gh-pages branch first
                try:
                    # Create an empty gh-pages branch
                    self._create_empty_gh_pages_branch(repo_name)
                    
                    # Then try again with gh-pages branch
                    alternate_payload = {
                        "source": {
                            "branch": "gh-pages",
                            "path": "/"
                        }
                    }
                    
                    alt_response = requests.post(
                        url,
                        headers=pages_headers,
                        json=alternate_payload
                    )
                    
                    if alt_response.status_code in (201, 200, 204):
                        logger.info(f"Enabled GitHub Pages with gh-pages branch: {repo_name}")
                        preview_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
                        logger.info(f"GitHub Pages URL: {preview_url}")
                        return True
                    else:
                        logger.error(f"All GitHub Pages attempts failed: {alt_response.status_code}, {alt_response.text}")
                except Exception as branch_error:
                    logger.error(f"Error with alternate GitHub Pages method: {branch_error}")
                
                # Return True anyway - GitHub Pages might still work
                # GitHub sometimes enables Pages automatically for public repos
                logger.warning("GitHub Pages setup failed, but website may still be accessible shortly")
                return True
                
        except Exception as e:
            logger.error(f"Error enabling GitHub Pages: {e}")
            # Return True anyway since the repo is created
            return True
    
    def _create_empty_gh_pages_branch(self, repo_name):
        """Create an empty gh-pages branch with index.html"""
        try:
            # First, check if main branch exists and get its latest commit SHA
            ref_url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}/git/refs/heads/main"
            ref_response = requests.get(ref_url, headers=self.headers)
            
            if ref_response.status_code != 200:
                logger.warning(f"Main branch not found, creating from scratch")
                return False
            
            sha = ref_response.json()['object']['sha']
            
            # Create gh-pages branch pointing to the same commit
            create_ref_url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}/git/refs"
            create_ref_payload = {
                'ref': 'refs/heads/gh-pages',
                'sha': sha
            }
            
            create_ref_response = requests.post(
                create_ref_url,
                headers=self.headers,
                json=create_ref_payload
            )
            
            if create_ref_response.status_code in (201, 200):
                logger.info(f"Created gh-pages branch for repository: {repo_name}")
                
                # Copy index.html to gh-pages branch
                self._copy_file_to_branch(repo_name, "main", "gh-pages", "index.html")
                return True
            else:
                logger.warning(f"Failed to create gh-pages branch: {create_ref_response.status_code}, {create_ref_response.text}")
                return False
                
        except Exception as e:
            logger.warning(f"Error creating gh-pages branch: {e}")
            return False
            
    def _copy_file_to_branch(self, repo_name, source_branch, target_branch, file_path):
        """Copy a file from one branch to another"""
        try:
            # Get the file content from source branch
            content_url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}?ref={source_branch}"
            content_response = requests.get(content_url, headers=self.headers)
            
            if content_response.status_code != 200:
                logger.warning(f"File not found on source branch: {file_path}")
                return False
            
            # Extract content (base64 encoded)
            content_data = content_response.json()
            content = content_data['content']
            
            # Create/update the file on target branch
            update_url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
            update_payload = {
                'message': f'Copy {file_path} from {source_branch} to {target_branch}',
                'content': content,
                'branch': target_branch
            }
            
            update_response = requests.put(
                update_url,
                headers=self.headers,
                json=update_payload
            )
            
            if update_response.status_code in (201, 200):
                logger.info(f"Copied {file_path} to {target_branch} branch")
                return True
            else:
                logger.warning(f"Failed to copy file: {update_response.status_code}, {update_response.text}")
                return False
                
        except Exception as e:
            logger.warning(f"Error copying file: {e}")
            return False
    
    def delete_repository(self, repo_name):
        """Delete a GitHub repository"""
        try:
            url = f"{self.api_url}/repos/{GITHUB_USERNAME}/{repo_name}"
            
            response = requests.delete(
                url,
                headers=self.headers
            )
            
            if response.status_code in (204, 202):
                logger.info(f"Deleted repository: {repo_name}")
                return True
            else:
                logger.error(f"Failed to delete repository: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting repository: {e}")
            return False
    
    def start_cleanup_thread(self):
        """Start a background thread to clean up old repositories"""
        def cleanup_worker():
            while True:
                try:
                    current_time = time.time()
                    repos_to_remove = []
                    
                    # Check for repos that need to be deleted
                    for repo_name, delete_time in self.repos_to_delete.items():
                        if current_time >= delete_time:
                            if self.delete_repository(repo_name):
                                repos_to_remove.append(repo_name)
                    
                    # Remove deleted repos from the tracking dict
                    for repo_name in repos_to_remove:
                        self.repos_to_delete.pop(repo_name, None)
                    
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
                
                # Sleep for a minute before next check
                time.sleep(60)
        
        # Start the thread if not already running
        if self.cleanup_thread is None or not self.cleanup_thread.is_alive():
            self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
            self.cleanup_thread.start()
            logger.info("Started repository cleanup thread")

# Main function for testing
if __name__ == "__main__":
    # Test the uploader
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN environment variable is not set.")
        exit(1)
        
    uploader = GitHubUploader()
    
    # Create a test site
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Meme Coin</title>
    </head>
    <body>
        <h1>Test Meme Coin</h1>
        <p>This is a test page for the GitHub Pages uploader.</p>
    </body>
    </html>
    """
    
    site_hash = hashlib.md5("test".encode()).hexdigest()[:10]
    site_url = uploader.upload_site("TestCoin", test_html, site_hash)
    
    if site_url:
        print(f"Successfully created site at: {site_url}")
        print("Note: It may take a minute for the GitHub Pages site to be available.")
    else:
        print("Failed to create site.")