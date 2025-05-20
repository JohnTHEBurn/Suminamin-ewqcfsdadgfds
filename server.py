import os
import json
import random
import re
import traceback
import logging
from flask import Flask, request, render_template, jsonify, send_from_directory
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import website_options

# Configure logging
logging.basicConfig(
    filename='flask_app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app = Flask(__name__)

# Simple cache implementation
class SimpleCache:
    def __init__(self, timeout=3600):
        self.cache = {}
        self.timeout = timeout
        
    def cached(self, timeout=None):
        def decorator(f):
            def wrapper(*args, **kwargs):
                # Simple key based on function name and arguments
                key = f.__name__ + str(args) + str(kwargs)
                return f(*args, **kwargs)
            return wrapper
        return decorator

# Simple rate limiter
class SimpleLimiter:
    def __init__(self):
        self.requests = {}
        
    def limit(self, limit_string):
        def decorator(f):
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper
        return decorator

# Initialize simple cache and limiter
cache = SimpleCache()
limiter = SimpleLimiter()

# Thread pool for concurrent generation
executor = ThreadPoolExecutor(max_workers=10)
generation_lock = Lock()

# Generate website content
def generate_site_content(coin_name, custom_data=None):
    # Initialize custom data if not provided
    if custom_data is None:
        custom_data = {}
    
    try:
        # Get website data from the options module
        website_data = website_options.generate_unique_website_data(coin_name)
        
        # Override with custom data if provided
        if 'slogan' in custom_data:
            website_data['slogan'] = custom_data['slogan']
        
        # Get social links if provided
        social_links = custom_data.get('social_links', {})
        
        # Get logo if provided
        logo_url = custom_data.get('logo_url', '')
        
        # Ensure theme is in the right format for the template
        if 'theme' in website_data and isinstance(website_data['theme'], dict):
            theme = website_data['theme']
        else:
            # Fallback theme
            theme = {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D"}
        
        # Ensure roadmap is in the right format
        if 'roadmap' not in website_data or not website_data['roadmap']:
            roadmap = ["Launch Website", "Create Social Media", "Token Launch", "CoinGecko Listing"]
        else:
            roadmap = website_data['roadmap']
        
        # Add additional fields required by the template
        website_data.update({
            "logo_url": logo_url,
            "has_telegram": "telegram" in social_links,
            "telegram_url": social_links.get("telegram", "#"),
            "has_twitter": "twitter" in social_links,
            "twitter_url": social_links.get("twitter", "#"),
            "show_tokenomics": False,  # Always disable tokenomics
            "buy_link": custom_data.get('buy_link', ''),
            "dexscreener_link": custom_data.get('dexscreener_link', ''),
            "roadmap": roadmap,
            "theme": theme
        })
        
        logging.debug(f"Generated website data: {website_data}")
        return website_data
        
    except Exception as e:
        logging.error(f"Error in generate_site_content: {e}")
        logging.error(traceback.format_exc())
        
        # Fallback to basic website data
        basic_data = {
            "name": coin_name,
            "formatted_name": coin_name,
            "symbol": coin_name[:4].upper(),
            "slogan": custom_data.get('slogan', "To the Moon! 🚀"),
            "theme": {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D"},
            "roadmap": ["Launch Website", "Create Social Media", "Token Launch", "CoinGecko Listing"],
            "logo_url": logo_url,
            "has_telegram": "telegram" in social_links,
            "telegram_url": social_links.get("telegram", "#"),
            "has_twitter": "twitter" in social_links,
            "twitter_url": social_links.get("twitter", "#"),
            "show_tokenomics": False,
            "buy_link": custom_data.get('buy_link', ''),
            "dexscreener_link": custom_data.get('dexscreener_link', '')
        }
        return basic_data

# Routes
@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "MemeCoin Website Generator API"})

@app.route('/sites/<path:filename>')
def serve_site(filename):
    return send_from_directory('sites', filename)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)

@app.route('/generate', methods=['POST'])
def generate_site():
    data = request.json
    
    if not data or 'coin_name' not in data or 'site_hash' not in data:
        return jsonify({"error": "Missing coin_name or site_hash"}), 400
    
    coin_name = data['coin_name']
    site_hash = data['site_hash']
    
    # Extract custom parameters
    custom_data = {}
    
    # Get custom slogan if provided
    if 'slogan' in data:
        custom_data['slogan'] = data['slogan']
    
    # Get social links if provided
    if 'social_links' in data:
        custom_data['social_links'] = data['social_links']
    
    # Get logo if provided
    if 'logo_url' in data:
        custom_data['logo_url'] = data['logo_url']
    
    try:
        # Generate site content with custom data
        site_data = generate_site_content(coin_name, custom_data)
        logging.debug(f"Generated site data for {coin_name}: {site_data}")
        
        # Render template to HTML
        try:
            html_content = render_template('memecoin_template.html', **site_data)
            logging.debug(f"HTML template rendered successfully (length: {len(html_content)})")
        except Exception as template_err:
            logging.error(f"Template rendering error: {template_err}")
            logging.error(traceback.format_exc())
            return jsonify({"error": f"Template error: {str(template_err)}"}), 500
        
        # Write to file atomically with lock
        try:
            filepath = os.path.join(os.path.abspath('sites'), f"{site_hash}.html")
            logging.debug(f"Writing to file: {filepath}")
            with generation_lock:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            logging.debug(f"File written successfully")
        except Exception as file_err:
            logging.error(f"File writing error: {file_err}")
            logging.error(traceback.format_exc())
            return jsonify({"error": f"File error: {str(file_err)}"}), 500
        
        return jsonify({"status": "success", "site_hash": site_hash})
    
    except Exception as e:
        logging.error(f"General error in generate_site: {e}")
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Ensure the required directories exist
def ensure_dirs():
    os.makedirs('sites', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)

# Call ensure_dirs() at module level to ensure directories exist
ensure_dirs()

if __name__ == '__main__':
    # Check if SSL certificate and key are available
    ssl_context = None
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        ssl_context = ('cert.pem', 'key.pem')
        print("SSL certificates found, starting with HTTPS support!")
    else:
        print("SSL certificates not found, starting without HTTPS support")
        print("To enable HTTPS, create cert.pem and key.pem files in the project root")
        print("You can generate self-signed certificates with this command:")
        print("openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
    
    app.run(debug=True, host='0.0.0.0', threaded=True, ssl_context=ssl_context)
