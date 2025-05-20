"""
Enhanced Server Module for the Website Creator

This module extends the original server.py with the new customization features.
It demonstrates how to integrate the customization flow into the existing server.
"""

import os
import json
import random
import re
import traceback
import logging
from flask import Flask, request, render_template, jsonify, send_from_directory
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Import the customization API
from customization_api import init_app
from template_handlers import TemplateManager

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

# Initialize template manager
template_manager = TemplateManager()

# Placeholder data for website generation
slogans = [
    "To the Moon! 🚀",
    "The Next 1000x Gem 💎",
    "Community-Driven Revolution 🔥",
    "The Future of Decentralized Memes 🌐",
    "Join the Movement! 💪",
    "Bark at the Moon 🐕",
    "Better Than Bitcoin? Maybe! 👀",
    "Elon Would Approve 👍",
    "Deflationary Tokenomics 📉"
]

tokenomics = [
    {"total_supply": "1,000,000,000,000", "burn": "2%", "redistribution": "2%", "liquidity": "1%"},
    {"total_supply": "100,000,000,000,000", "burn": "5%", "redistribution": "5%", "liquidity": "5%"},
    {"total_supply": "1,000,000,000,000,000", "burn": "3%", "redistribution": "3%", "marketing": "4%"},
    {"total_supply": "42,069,000,000,000", "burn": "4.2%", "redistribution": "6.9%", "marketing": "2%"}
]

roadmap_phases = [
    ["Launch Website", "Create Social Media", "Token Launch", "CoinGecko Listing"],
    ["1,000 Holders", "MemeCoin Partnership", "NFT Collection", "Trending on Twitter"],
    ["10,000 Holders", "Major Exchange Listing", "Mobile App", "Mainstream Media Coverage"],
    ["100,000 Holders", "Meme DEX Launch", "Meme Merchandise Store", "Global Adoption"]
]

themes = [
    {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D"},
    {"primary": "#6B5B95", "secondary": "#FFA500", "accent": "#88B04B"},
    {"primary": "#00A4CCFF", "secondary": "#F95700FF", "accent": "#ADEFD1FF"},
    {"primary": "#00539CFF", "secondary": "#EEA47FFF", "accent": "#D198C5FF"},
    {"primary": "#2C5F2D", "secondary": "#97BC62FF", "accent": "#FE5F55"},
    {"primary": "#990011FF", "secondary": "#FCF6F5FF", "accent": "#8AAAE5"}
]

# Generate website content - Original implementation
def generate_site_content(coin_name, custom_data=None):
    # Initialize custom data if not provided
    if custom_data is None:
        custom_data = {}
    
    # Select random elements or use custom values
    slogan = custom_data.get('slogan') or random.choice(slogans)
    tokenomic = random.choice(tokenomics)
    roadmap = random.choice(roadmap_phases)
    theme = random.choice(themes)
    
    # Format coin name for display
    formatted_name = coin_name
    
    # Try to format the coin name nicely (e.g., FlokiElonMoon -> Floki Elon Moon)
    try:
        import re
        # Look for camel case or pascal case
        formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', coin_name)
        # Look for words stuck together (all caps or all lowercase)
        if formatted_name == formatted_name.upper() or formatted_name == formatted_name.lower():
            # Try to split by common token suffixes/prefixes
            for term in ['Inu', 'Moon', 'Elon', 'Doge', 'Shib', 'Floki', 'Coin', 'Token', 'Baby', 'Safe']:
                formatted_name = formatted_name.replace(term, f" {term} ")
            formatted_name = ' '.join(formatted_name.split())
        # Capitalize each word
        formatted_name = ' '.join(word.capitalize() for word in formatted_name.split())
    except Exception:
        # If there's any error in formatting, just use the original name
        pass
    
    # Generate symbol
    symbol = ''.join(word[0] for word in re.findall(r'[A-Z][a-z]*', coin_name)) or coin_name[:4].upper()
    
    # Get social links if provided
    social_links = custom_data.get('social_links', {})
    
    # Get logo if provided
    has_custom_logo = 'logo_url' in custom_data and custom_data['logo_url'] is not None
    logo_url = custom_data.get('logo_url', '')
    
    # Create site data
    site_data = {
        "name": coin_name,
        "formatted_name": formatted_name,
        "slogan": slogan,
        "symbol": symbol,
        "tokenomics": tokenomic,
        "roadmap": roadmap,
        "theme": theme,
        "has_custom_logo": has_custom_logo,
        "logo_url": logo_url,
        "has_telegram": "telegram" in social_links,
        "telegram_url": social_links.get("telegram", "#"),
        "has_twitter": "twitter" in social_links,
        "twitter_url": social_links.get("twitter", "#")
    }
    
    return site_data

# Routes
@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "MemeCoin Website Generator API"})

@app.route('/sites/<path:filename>')
def serve_site(filename):
    return send_from_directory('sites', filename)

# Legacy endpoint for backward compatibility
@app.route('/generate', methods=['POST'])
def generate_site():
    data = request.json
    
    if not data or 'coin_name' not in data or 'site_hash' not in data:
        return jsonify({"error": "Missing coin_name or site_hash"}), 400
    
    coin_name = data['coin_name']
    site_hash = data['site_hash']
    
    # Check if template_id is provided - if so, use the new system
    if 'template_id' in data:
        try:
            # Use the template system for generation
            template_id = data['template_id']
            
            # Validate data against template requirements
            validation = template_manager.validate_template_data(template_id, data)
            
            if not validation['valid']:
                return jsonify({"error": validation['error']}), 400
            
            # Process data for the selected template
            processed_data = template_manager.process_template_data(template_id, data)
            
            # Render the template
            template_path = template_manager.get_template_html_path(template_id)
            template_filename = os.path.basename(template_path)
            
            html_content = render_template(template_filename, **processed_data)
            
            # Save the generated site
            filepath = os.path.join(os.path.abspath('sites'), f"{site_hash}.html")
            logging.debug(f"Writing to file: {filepath}")
            with generation_lock:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            logging.debug(f"File written successfully")
            
            return jsonify({"status": "success", "site_hash": site_hash})
        
        except Exception as e:
            logging.error(f"Error in template-based generation: {e}")
            logging.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
    
    # Original code path for backward compatibility
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

# Frontend routes for customization UI
@app.route('/customize')
def customize_page():
    """
    Render the main customization UI page.
    This provides a user-friendly web interface for customizing websites.
    """
    return render_template('customize.html')

@app.route('/preview/<site_hash>')
def preview_site(site_hash):
    """
    Preview a generated website.
    """
    return send_from_directory('sites', f"{site_hash}.html")

# Ensure the sites directory exists
def ensure_dirs():
    os.makedirs('sites', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)

# Call ensure_dirs() at module level to ensure directories exist
ensure_dirs()

# Initialize the customization API
init_app(app)

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