"""
Customization Flow Module for the Website Creator

This module implements the website customization flow using the state management system
defined in customization_states.py.
"""

import os
import hashlib
import logging
import json
import requests
from customization_states import STATES, CustomizationStateManager

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Server URL from environment or default
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Dictionary to store state managers for each user
user_state_managers = {}

# Dictionary to store hosting URLs
hosting_urls = {}

# Available templates
TEMPLATES = [
    {
        "id": "memecoin",
        "name": "MemeCoin Landing Page",
        "description": "A modern, animated landing page for meme coins with tokenomics and roadmap",
        "image_url": "/static/templates/memecoin_preview.jpg"
    },
    {
        "id": "nft",
        "name": "NFT Collection",
        "description": "Showcase your NFT collection with gallery and minting interface",
        "image_url": "/static/templates/nft_preview.jpg"
    },
    {
        "id": "defi",
        "name": "DeFi Dashboard",
        "description": "Professional DeFi platform with staking and yield farming information",
        "image_url": "/static/templates/defi_preview.jpg"
    }
]

# Available themes
THEMES = [
    {
        "id": "dark",
        "name": "Dark Theme",
        "colors": {"primary": "#2C3E50", "secondary": "#1ABC9C", "accent": "#E74C3C"}
    },
    {
        "id": "light",
        "name": "Light Theme",
        "colors": {"primary": "#ECF0F1", "secondary": "#3498DB", "accent": "#F1C40F"}
    },
    {
        "id": "neon",
        "name": "Neon Theme",
        "colors": {"primary": "#0F0F29", "secondary": "#00FFFF", "accent": "#FF00FF"}
    },
    {
        "id": "nature",
        "name": "Nature Theme",
        "colors": {"primary": "#2C5F2D", "secondary": "#97BC62", "accent": "#FED766"}
    },
    {
        "id": "royal",
        "name": "Royal Theme",
        "colors": {"primary": "#2C3E50", "secondary": "#8E44AD", "accent": "#F1C40F"}
    }
]

def get_or_create_state_manager(user_id):
    """Get an existing state manager or create a new one for the user."""
    if user_id not in user_state_managers:
        user_state_managers[user_id] = CustomizationStateManager(user_id)
    return user_state_managers[user_id]

def get_templates():
    """Get available templates with metadata."""
    return TEMPLATES

def get_themes():
    """Get available themes with color schemes."""
    return THEMES

def handle_template_selection(user_id, template_id):
    """Handle template selection by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_TEMPLATE_SELECTION']:
        return {
            "success": False,
            "message": "Invalid state for template selection",
            "next_prompt": manager.get_prompt()
        }
    
    # Check if template exists
    template_valid = any(t['id'] == template_id for t in TEMPLATES)
    if not template_valid:
        return {
            "success": False,
            "message": "Invalid template selection",
            "next_prompt": manager.get_prompt()
        }
    
    # Update data
    manager.update_data('template_id', template_id)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_COIN_NAME'])
    
    return {
        "success": True,
        "message": f"Selected template: {template_id}",
        "next_prompt": manager.get_prompt()
    }

def handle_coin_name(user_id, coin_name):
    """Handle coin name input by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_COIN_NAME']:
        return {
            "success": False,
            "message": "Invalid state for coin name",
            "next_prompt": manager.get_prompt()
        }
    
    # Validate input
    if not coin_name or len(coin_name.strip()) == 0:
        return {
            "success": False,
            "message": "Coin name cannot be empty",
            "next_prompt": manager.get_prompt()
        }
    
    # Format coin name nicely
    formatted_name = format_coin_name(coin_name)
    
    # Generate symbol
    symbol = generate_symbol(coin_name)
    
    # Update data
    manager.update_data('coin_name', coin_name)
    manager.update_data('formatted_name', formatted_name)
    manager.update_data('symbol', symbol)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_SLOGAN'])
    
    return {
        "success": True,
        "message": f"Set coin name: {coin_name}",
        "data": {
            "formatted_name": formatted_name,
            "symbol": symbol
        },
        "next_prompt": manager.get_prompt()
    }

def format_coin_name(coin_name):
    """Format a coin name to be more readable."""
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
        return formatted_name
    except Exception:
        # If there's any error in formatting, just use the original name
        return coin_name

def generate_symbol(coin_name):
    """Generate a symbol from a coin name."""
    try:
        import re
        # Get first letters of words in CamelCase
        symbol = ''.join(word[0] for word in re.findall(r'[A-Z][a-z]*', coin_name))
        if not symbol:
            # If no camel case, use first 3-4 letters
            symbol = coin_name[:4].upper()
        return symbol
    except Exception:
        # If there's any error, just use the first 3-4 letters
        return coin_name[:4].upper()

def handle_slogan(user_id, slogan):
    """Handle slogan input by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_SLOGAN']:
        return {
            "success": False,
            "message": "Invalid state for slogan",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if slogan.lower() == 'skip':
        slogan = None
    
    # Update data
    manager.update_data('slogan', slogan)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_DESCRIPTION'])
    
    return {
        "success": True,
        "message": "Slogan set" if slogan else "Using random slogan",
        "next_prompt": manager.get_prompt()
    }

def handle_description(user_id, description):
    """Handle description input by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_DESCRIPTION']:
        return {
            "success": False,
            "message": "Invalid state for description",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if description.lower() == 'skip':
        description = None
    
    # Update data
    manager.update_data('description', description)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_LOGO'])
    
    return {
        "success": True,
        "message": "Description set" if description else "Using default description",
        "next_prompt": manager.get_prompt()
    }

def handle_logo(user_id, logo_url=None):
    """Handle logo upload by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_LOGO']:
        return {
            "success": False,
            "message": "Invalid state for logo upload",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if logo_url and isinstance(logo_url, str) and logo_url.lower() == 'skip':
        logo_url = None
    
    # Update data - logo_url can be either None (skip) or a path to an already saved file
    manager.update_data('logo_url', logo_url)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_THEME'])
    
    return {
        "success": True,
        "message": "Logo uploaded" if logo_url else "Using generated symbol",
        "next_prompt": manager.get_prompt()
    }

def handle_theme(user_id, theme_id):
    """Handle theme selection by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_THEME']:
        return {
            "success": False,
            "message": "Invalid state for theme selection",
            "next_prompt": manager.get_prompt()
        }
    
    # Check if theme exists
    theme_data = next((t for t in THEMES if t['id'] == theme_id), None)
    if not theme_data:
        return {
            "success": False,
            "message": "Invalid theme selection",
            "next_prompt": manager.get_prompt()
        }
    
    # Update data
    manager.update_data('theme', theme_id)
    
    # Update colors with theme defaults
    manager.update_data('colors.primary', theme_data['colors']['primary'])
    manager.update_data('colors.secondary', theme_data['colors']['secondary'])
    manager.update_data('colors.accent', theme_data['colors']['accent'])
    
    # We'll keep the WAITING_FOR_COLOR_SCHEME state in the flow,
    # but the UI will automatically skip it by calling handle_color_scheme
    # right after this function completes
    manager.transition_to(STATES['WAITING_FOR_COLOR_SCHEME'])
    
    return {
        "success": True,
        "message": f"Selected theme: {theme_data['name']}",
        "data": theme_data['colors'],
        "next_prompt": "Now, enter your Telegram group link (or type 'skip'):"
    }

def handle_color_scheme(user_id, colors):
    """Handle color scheme customization by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_COLOR_SCHEME']:
        return {
            "success": False,
            "message": "Invalid state for color scheme customization",
            "next_prompt": manager.get_prompt()
        }
    
    # Validate colors if provided
    if colors and isinstance(colors, dict):
        # Update individual colors if provided
        if 'primary' in colors:
            manager.update_data('colors.primary', colors['primary'])
        if 'secondary' in colors:
            manager.update_data('colors.secondary', colors['secondary'])
        if 'accent' in colors:
            manager.update_data('colors.accent', colors['accent'])
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_TELEGRAM'])
    
    return {
        "success": True,
        "message": "Color scheme updated",
        "next_prompt": manager.get_prompt()
    }

def handle_social_link(user_id, platform, url):
    """Handle social media link input by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Determine current state and expected platform
    current_state = manager.get_current_state()
    expected_platform = None
    
    if current_state == STATES['WAITING_FOR_TELEGRAM']:
        expected_platform = 'telegram'
        next_state = STATES['WAITING_FOR_TWITTER']
    elif current_state == STATES['WAITING_FOR_TWITTER']:
        expected_platform = 'twitter'
        next_state = STATES['WAITING_FOR_DISCORD']
    elif current_state == STATES['WAITING_FOR_DISCORD']:
        expected_platform = 'discord'
        next_state = STATES['WAITING_FOR_MEDIUM']
    elif current_state == STATES['WAITING_FOR_MEDIUM']:
        expected_platform = 'medium'
        next_state = STATES['WAITING_FOR_GITHUB']
    elif current_state == STATES['WAITING_FOR_GITHUB']:
        expected_platform = 'github'
        next_state = STATES['WAITING_FOR_CUSTOM_SOCIAL']
    elif current_state == STATES['WAITING_FOR_CUSTOM_SOCIAL']:
        expected_platform = 'custom'
        next_state = STATES['WAITING_FOR_SUPPLY']
    else:
        return {
            "success": False,
            "message": f"Invalid state for {platform} link",
            "next_prompt": manager.get_prompt()
        }
    
    # Check if the provided platform matches the expected one
    if platform != expected_platform:
        return {
            "success": False,
            "message": f"Expected {expected_platform} link, but received {platform}",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if url.lower() == 'skip':
        url = None
    elif url and not (url.startswith('http://') or url.startswith('https://')):
        # Add https:// if missing
        url = 'https://' + url
    
    # Update data
    if platform == 'custom':
        # For custom social, expect a name and URL
        if isinstance(url, dict) and 'name' in url and 'url' in url:
            custom_socials = manager.website_data.get('social_links', {}).get('custom', [])
            custom_socials.append(url)
            manager.update_data('social_links.custom', custom_socials)
        else:
            # If not properly formatted, just skip
            pass
    else:
        # For standard social platforms
        manager.update_data(f'social_links.{platform}', url)
    
    # Transition to next state
    manager.transition_to(next_state)
    
    return {
        "success": True,
        "message": f"{platform.capitalize()} link set" if url else f"No {platform} link provided",
        "next_prompt": manager.get_prompt()
    }

def handle_tokenomics(user_id, field, value):
    """Handle tokenomics information input by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Determine current state and expected field
    current_state = manager.get_current_state()
    expected_field = None
    
    if current_state == STATES['WAITING_FOR_SUPPLY']:
        expected_field = 'total_supply'
        next_state = STATES['WAITING_FOR_TAX_INFO']
    elif current_state == STATES['WAITING_FOR_TAX_INFO']:
        expected_field = 'tax'
        next_state = STATES['WAITING_FOR_DISTRIBUTION']
    elif current_state == STATES['WAITING_FOR_DISTRIBUTION']:
        expected_field = 'distribution'
        next_state = STATES['WAITING_FOR_ROADMAP']
    else:
        return {
            "success": False,
            "message": f"Invalid state for tokenomics {field}",
            "next_prompt": manager.get_prompt()
        }
    
    # Check if the provided field matches the expected one
    if field != expected_field:
        return {
            "success": False,
            "message": f"Expected {expected_field}, but received {field}",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if isinstance(value, str) and value.lower() == 'skip':
        # Skip but continue to next state
        pass
    else:
        # Process and update based on field type
        if field == 'total_supply':
            manager.update_data('tokenomics.total_supply', value)
        elif field == 'tax':
            if isinstance(value, dict):
                if 'buy' in value:
                    manager.update_data('tokenomics.buy_tax', value['buy'])
                if 'sell' in value:
                    manager.update_data('tokenomics.sell_tax', value['sell'])
                if 'burn' in value:
                    manager.update_data('tokenomics.burn', value['burn'])
                if 'redistribution' in value:
                    manager.update_data('tokenomics.redistribution', value['redistribution'])
                if 'liquidity' in value:
                    manager.update_data('tokenomics.liquidity', value['liquidity'])
                if 'marketing' in value:
                    manager.update_data('tokenomics.marketing', value['marketing'])
        elif field == 'distribution':
            if isinstance(value, list):
                manager.update_data('tokenomics.distribution', value)
    
    # Transition to next state
    manager.transition_to(next_state)
    
    return {
        "success": True,
        "message": f"Tokenomics {field} updated",
        "next_prompt": manager.get_prompt()
    }

def handle_roadmap(user_id, roadmap):
    """Handle roadmap information input by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_ROADMAP']:
        return {
            "success": False,
            "message": "Invalid state for roadmap",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if isinstance(roadmap, str) and roadmap.lower() == 'skip':
        # Skip but continue to next state
        pass
    elif isinstance(roadmap, list):
        manager.update_data('roadmap', roadmap)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_SECTIONS_ORDER'])
    
    return {
        "success": True,
        "message": "Roadmap updated",
        "next_prompt": manager.get_prompt()
    }

def handle_sections_order(user_id, sections_order):
    """Handle sections ordering by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_SECTIONS_ORDER']:
        return {
            "success": False,
            "message": "Invalid state for sections ordering",
            "next_prompt": manager.get_prompt()
        }
    
    # Handle skip option
    if isinstance(sections_order, str) and sections_order.lower() == 'skip':
        # Use default order
        pass
    elif isinstance(sections_order, list):
        # Validate that all required sections are included
        required_sections = ['header', 'about', 'tokenomics', 'roadmap', 'community']
        missing_sections = [s for s in required_sections if s not in sections_order]
        
        if missing_sections:
            return {
                "success": False,
                "message": f"Missing required sections: {', '.join(missing_sections)}",
                "next_prompt": manager.get_prompt()
            }
        
        manager.update_data('sections_order', sections_order)
    
    # Transition to next state
    manager.transition_to(STATES['WAITING_FOR_CONFIRMATION'])
    
    return {
        "success": True,
        "message": "Sections order updated",
        "next_prompt": manager.get_prompt(),
        "data": manager.get_website_data()  # Include full data for confirmation
    }

def handle_confirmation(user_id, confirmed):
    """Handle confirmation of website details by the user."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_CONFIRMATION']:
        return {
            "success": False,
            "message": "Invalid state for confirmation",
            "next_prompt": manager.get_prompt()
        }
    
    if confirmed:
        # Transition to generation state
        manager.transition_to(STATES['READY_TO_GENERATE'])
        
        return {
            "success": True,
            "message": "Website details confirmed",
            "next_prompt": manager.get_prompt()
        }
    else:
        # Go to edit choice state
        manager.transition_to(STATES['WAITING_FOR_EDIT_CHOICE'])
        
        return {
            "success": True,
            "message": "Please select what you would like to edit",
            "next_prompt": manager.get_prompt(),
            "data": {
                "edit_options": [
                    {"field": "coin_name", "label": "Coin Name"},
                    {"field": "slogan", "label": "Slogan"},
                    {"field": "description", "label": "Description"},
                    {"field": "logo", "label": "Logo"},
                    {"field": "theme", "label": "Theme & Colors"},
                    {"field": "social_links", "label": "Social Media Links"},
                    {"field": "tokenomics", "label": "Tokenomics"},
                    {"field": "roadmap", "label": "Roadmap"},
                    {"field": "sections_order", "label": "Sections Order"}
                ]
            }
        }

def handle_edit_choice(user_id, field):
    """Handle user's choice of what to edit."""
    manager = get_or_create_state_manager(user_id)
    
    # Check if we're in the correct state
    if manager.get_current_state() != STATES['WAITING_FOR_EDIT_CHOICE']:
        return {
            "success": False,
            "message": "Invalid state for edit choice",
            "next_prompt": manager.get_prompt()
        }
    
    # Map field to appropriate state
    field_to_state = {
        "coin_name": STATES['WAITING_FOR_COIN_NAME'],
        "slogan": STATES['WAITING_FOR_SLOGAN'],
        "description": STATES['WAITING_FOR_DESCRIPTION'],
        "logo": STATES['WAITING_FOR_LOGO'],
        "theme": STATES['WAITING_FOR_THEME'],
        "social_links": STATES['WAITING_FOR_TELEGRAM'],
        "tokenomics": STATES['WAITING_FOR_SUPPLY'],
        "roadmap": STATES['WAITING_FOR_ROADMAP'],
        "sections_order": STATES['WAITING_FOR_SECTIONS_ORDER']
    }
    
    if field not in field_to_state:
        return {
            "success": False,
            "message": f"Invalid edit field: {field}",
            "next_prompt": manager.get_prompt()
        }
    
    # Transition to the selected edit state
    next_state = field_to_state[field]
    manager.transition_to(next_state)
    
    return {
        "success": True,
        "message": f"Editing {field}",
        "next_prompt": manager.get_prompt()
    }

def generate_website(user_id):
    """Generate the website using the collected data."""
    manager = get_or_create_state_manager(user_id)
    
    # For AI-driven generation, we allow generation from any state
    current_state = manager.get_current_state()
    
    # If not in READY_TO_GENERATE, force the state
    if current_state != STATES['READY_TO_GENERATE']:
        # Force the state transition
        manager.current_state = STATES['READY_TO_GENERATE']
    
    # Transition to generating state
    manager.transition_to(STATES['GENERATING'])
    
    try:
        # Extract necessary data
        website_data = manager.get_website_data()
        coin_name = website_data['coin_name']
        
        # Create a unique hash for this website
        site_hash = hashlib.md5(f"{coin_name}_{os.urandom(8)}".encode()).hexdigest()[:10]
        
        # Store the site hash
        manager.update_data('site_hash', site_hash)
        
        # Prepare request data
        request_data = {
            "coin_name": coin_name,
            "site_hash": site_hash
        }
        
        # Add custom data
        if website_data['slogan']:
            request_data["slogan"] = website_data['slogan']
        
        # Add social links if provided
        social_links = {}
        if website_data['social_links']['telegram']:
            social_links["telegram"] = website_data['social_links']['telegram']
        if website_data['social_links']['twitter']:
            social_links["twitter"] = website_data['social_links']['twitter']
        
        if social_links:
            request_data["social_links"] = social_links
        
        # Add logo if provided
        if website_data['logo_url']:
            request_data["logo_url"] = website_data['logo_url']
        
        # Add additional data for advanced templates
        request_data["template_id"] = website_data['template_id']
        request_data["colors"] = website_data['colors']
        
        # Make request to the Flask server to generate the site
        response = requests.post(
            f"{SERVER_URL}/generate",
            json=request_data,
            timeout=30
        )
        response.raise_for_status()
        
        # If hosting is needed, handle that here based on selected hosting method
        # This is a placeholder for actual hosting implementation
        hosting_method = website_data['hosting']['method']
        
        if hosting_method == "github":
            # Placeholder for GitHub Pages hosting
            hosting_urls[site_hash] = {
                "raw_url": f"{SERVER_URL}/sites/{site_hash}.html",
                "preview_url": f"https://example.github.io/{site_hash}",
                "repo_url": f"https://github.com/example/{site_hash}"
            }
        elif hosting_method == "netlify":
            # Placeholder for Netlify hosting
            hosting_urls[site_hash] = {
                "raw_url": f"{SERVER_URL}/sites/{site_hash}.html",
                "preview_url": f"https://{site_hash}.netlify.app",
                "repo_url": None
            }
        elif hosting_method == "vercel":
            # Placeholder for Vercel hosting
            hosting_urls[site_hash] = {
                "raw_url": f"{SERVER_URL}/sites/{site_hash}.html",
                "preview_url": f"https://{site_hash}.vercel.app",
                "repo_url": None
            }
        else:
            # Default local hosting
            hosting_urls[site_hash] = {
                "raw_url": f"{SERVER_URL}/sites/{site_hash}.html",
                "preview_url": f"{SERVER_URL}/sites/{site_hash}.html",
                "repo_url": None
            }
        
        # Update URLs
        manager.update_data('urls.raw_url', hosting_urls[site_hash]['raw_url'])
        manager.update_data('urls.preview_url', hosting_urls[site_hash]['preview_url'])
        manager.update_data('urls.repo_url', hosting_urls[site_hash]['repo_url'])
        
        # Transition to completed state
        manager.transition_to(STATES['COMPLETED'])
        
        return {
            "success": True,
            "message": "Website generated successfully",
            "data": {
                "site_hash": site_hash,
                "urls": hosting_urls[site_hash]
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating website: {str(e)}")
        
        # Transition to error state
        manager.transition_to(STATES['ERROR'])
        
        return {
            "success": False,
            "message": f"Error generating website: {str(e)}",
            "next_prompt": manager.get_prompt()
        }

def reset_state(user_id):
    """Reset the user's state to the beginning."""
    if user_id in user_state_managers:
        user_state_managers[user_id].reset()
    else:
        user_state_managers[user_id] = CustomizationStateManager(user_id)
    
    # Ensure we start in the IDLE state
    manager = user_state_managers[user_id]
    
    # Explicitly reset to IDLE state
    manager.current_state = STATES['IDLE']
    manager.website_data = manager.website_data.copy()
    manager.error_message = None
    
    # Return the initial prompt
    return {
        "success": True,
        "message": "State reset",
        "next_prompt": manager.get_prompt(),
        "current_state": manager.get_current_state()
    }

def get_state_summary(user_id):
    """Get a summary of the current state and collected data."""
    if user_id not in user_state_managers:
        return {
            "success": False,
            "message": "No active customization session",
            "data": None
        }
    
    manager = user_state_managers[user_id]
    
    return {
        "success": True,
        "current_state": manager.get_current_state(),
        "prompt": manager.get_prompt(),
        "data": manager.get_website_data()
    }

# Example usage:
if __name__ == "__main__":
    # Simulate a user interaction flow
    user_id = "test_user_123"
    
    # Start a new session
    reset_state(user_id)
    
    # Select template
    result = handle_template_selection(user_id, "memecoin")
    print(f"Template selection: {result['message']}")
    
    # Set coin name
    result = handle_coin_name(user_id, "MoonElonDoge")
    print(f"Coin name: {result['message']}")
    print(f"Formatted name: {result['data']['formatted_name']}")
    print(f"Symbol: {result['data']['symbol']}")
    
    # Set slogan
    result = handle_slogan(user_id, "To the Moon and Beyond! 🚀")
    print(f"Slogan: {result['message']}")
    
    # Set description
    result = handle_description(user_id, "The next generation of meme coins with revolutionary tokenomics.")
    print(f"Description: {result['message']}")
    
    # Skip logo
    result = handle_logo(user_id, "skip")
    print(f"Logo: {result['message']}")
    
    # Select theme
    result = handle_theme(user_id, "neon")
    print(f"Theme: {result['message']}")
    
    # Customize colors
    result = handle_color_scheme(user_id, {"accent": "#FF00FF"})
    print(f"Colors: {result['message']}")
    
    # Set social links
    result = handle_social_link(user_id, "telegram", "https://t.me/moonelon")
    print(f"Telegram: {result['message']}")
    
    result = handle_social_link(user_id, "twitter", "https://twitter.com/moonelon")
    print(f"Twitter: {result['message']}")
    
    result = handle_social_link(user_id, "discord", "skip")
    print(f"Discord: {result['message']}")
    
    result = handle_social_link(user_id, "medium", "skip")
    print(f"Medium: {result['message']}")
    
    result = handle_social_link(user_id, "github", "skip")
    print(f"GitHub: {result['message']}")
    
    result = handle_social_link(user_id, "custom", {"name": "Reddit", "url": "https://reddit.com/r/moonelon"})
    print(f"Custom social: {result['message']}")
    
    # Set tokenomics
    result = handle_tokenomics(user_id, "total_supply", "1,000,000,000,000")
    print(f"Total supply: {result['message']}")
    
    result = handle_tokenomics(user_id, "tax", {"buy": "5%", "sell": "7%", "burn": "2%", "redistribution": "3%"})
    print(f"Tax info: {result['message']}")
    
    result = handle_tokenomics(user_id, "distribution", [
        {"name": "Presale", "percentage": "40%"},
        {"name": "Liquidity", "percentage": "30%"},
        {"name": "Team", "percentage": "10%"},
        {"name": "Marketing", "percentage": "20%"}
    ])
    print(f"Distribution: {result['message']}")
    
    # Set roadmap
    result = handle_roadmap(user_id, [
        ["Website Launch", "Social Media Creation", "Community Building"],
        ["Exchange Listings", "Partnership Announcements", "Marketing Campaign"],
        ["NFT Integration", "Utility Expansion", "Global Adoption"]
    ])
    print(f"Roadmap: {result['message']}")
    
    # Set sections order
    result = handle_sections_order(user_id, ["header", "about", "tokenomics", "roadmap", "community"])
    print(f"Sections order: {result['message']}")
    
    # Confirm and generate
    result = handle_confirmation(user_id, True)
    print(f"Confirmation: {result['message']}")
    
    # Generate website
    result = generate_website(user_id)
    print(f"Generation: {result['message']}")
    
    if result['success']:
        print(f"Site URL: {result['data']['urls']['preview_url']}")
    
    # Print final state summary
    summary = get_state_summary(user_id)
    print(f"Final state: {summary['current_state']}")