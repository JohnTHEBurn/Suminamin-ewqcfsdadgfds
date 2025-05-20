import os
import json
import hashlib
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Netlify API Configuration - Alternative to GitHub Pages
NETLIFY_TOKEN = os.getenv('NETLIFY_TOKEN')
SITE_ID = os.getenv('NETLIFY_SITE_ID')

class NetlifyUploader:
    """Upload sites to Netlify (Alternative to GitHub Pages)"""
    
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {NETLIFY_TOKEN}',
            'Content-Type': 'application/json'
        }
        self.api_url = 'https://api.netlify.com/api/v1'
        
    def upload_site(self, site_name, html_content, site_hash):
        """Upload a site to Netlify and return the URL"""
        try:
            # Create deploy folder path
            deploy_path = f"sites/{site_hash}"
            os.makedirs(deploy_path, exist_ok=True)
            
            # Write index.html
            with open(f"{deploy_path}/index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Deploy to Netlify
            site_url = self._deploy_site(site_name, deploy_path, site_hash)
            
            return site_url
        
        except Exception as e:
            logger.error(f"Error uploading to Netlify: {e}")
            return None
    
    def _deploy_site(self, site_name, folder_path, site_hash):
        """Deploy a folder to Netlify"""
        try:
            # For direct API deployment, we'd need to zip the folder and use the direct deploy endpoint
            # This is a simplified version using netlify-cli (which should be installed)
            import subprocess
            
            result = subprocess.run(
                [
                    "netlify", "deploy", 
                    "--dir", folder_path,
                    "--site", SITE_ID,
                    "--auth", NETLIFY_TOKEN,
                    "--json"
                ], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Netlify deploy failed: {result.stderr}")
                return None
            
            # Parse the JSON output to get the URL
            try:
                output = json.loads(result.stdout)
                deploy_url = output.get('deploy_url')
                logger.info(f"Successfully deployed to Netlify: {deploy_url}")
                return deploy_url
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Netlify output: {result.stdout}")
                return None
                
        except Exception as e:
            logger.error(f"Error deploying to Netlify: {e}")
            return None

# Firebase Hosting Configuration - Another alternative
FIREBASE_PROJECT = os.getenv('FIREBASE_PROJECT')

class FirebaseUploader:
    """Upload sites to Firebase Hosting (Another HTTPS option)"""
    
    def upload_site(self, site_name, html_content, site_hash):
        """Upload a site to Firebase and return the URL"""
        try:
            # Create deploy folder path
            deploy_path = f"sites/{site_hash}"
            os.makedirs(deploy_path, exist_ok=True)
            
            # Write index.html
            with open(f"{deploy_path}/index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create firebase.json config file
            firebase_config = {
                "hosting": {
                    "public": deploy_path,
                    "ignore": [
                        "firebase.json"
                    ]
                }
            }
            
            with open("firebase.json", 'w') as f:
                json.dump(firebase_config, f)
            
            # Deploy to Firebase
            import subprocess
            
            # First login (might need interaction)
            # subprocess.run(["firebase", "login"])
            
            # Then deploy
            result = subprocess.run(
                [
                    "firebase", "deploy", 
                    "--only", "hosting",
                    "--project", FIREBASE_PROJECT
                ], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Firebase deploy failed: {result.stderr}")
                return None
            
            # Return the Firebase hosting URL
            site_url = f"https://{FIREBASE_PROJECT}.web.app"
            logger.info(f"Successfully deployed to Firebase: {site_url}")
            return site_url
            
        except Exception as e:
            logger.error(f"Error deploying to Firebase: {e}")
            return None

# Vercel Configuration - Another option
VERCEL_TOKEN = os.getenv('VERCEL_TOKEN')

class VercelUploader:
    """Upload sites to Vercel (Yet another HTTPS option)"""
    
    def upload_site(self, site_name, html_content, site_hash):
        """Upload a site to Vercel and return the URL"""
        try:
            # Create deploy folder path
            deploy_path = f"sites/{site_hash}"
            os.makedirs(deploy_path, exist_ok=True)
            
            # Write index.html
            with open(f"{deploy_path}/index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Deploy to Vercel using CLI
            import subprocess
            
            # Deploy
            result = subprocess.run(
                [
                    "vercel", "--confirm", "--token", VERCEL_TOKEN,
                    deploy_path
                ], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Vercel deploy failed: {result.stderr}")
                return None
            
            # Extract URL from output
            # Usually in format "Deployment complete! https://project-id.vercel.app"
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "https://" in line:
                    url = line.split("https://")[1].strip()
                    site_url = f"https://{url}"
                    logger.info(f"Successfully deployed to Vercel: {site_url}")
                    return site_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error deploying to Vercel: {e}")
            return None

# Choose the appropriate uploader based on environment variables
def get_uploader():
    """Factory function to return the appropriate uploader"""
    if NETLIFY_TOKEN and SITE_ID:
        return NetlifyUploader()
    elif FIREBASE_PROJECT:
        return FirebaseUploader()
    elif VERCEL_TOKEN:
        return VercelUploader()
    else:
        return None

# Main function for testing
if __name__ == "__main__":
    uploader = get_uploader()
    
    if not uploader:
        print("No uploader configured. Please set environment variables for one of the hosting options.")
        exit(1)
    
    # Test deploy
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Meme Coin</title>
    </head>
    <body>
        <h1>Test Meme Coin</h1>
        <p>This is a test page.</p>
    </body>
    </html>
    """
    
    site_hash = hashlib.md5("test".encode()).hexdigest()[:10]
    site_url = uploader.upload_site("TestCoin", test_html, site_hash)
    
    if site_url:
        print(f"Successfully created site at: {site_url}")
    else:
        print("Failed to create site.")