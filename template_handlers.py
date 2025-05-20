"""
Template Handlers Module for the Website Creator

This module provides template-specific handling for different website templates.
Each template can have its own customization options, validation rules, and rendering logic.
"""

import logging
import json
import os
from pathlib import Path

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define template metadata
TEMPLATES = {
    "memecoin": {
        "name": "MemeCoin Landing Page",
        "description": "A modern, animated landing page for meme coins with tokenomics and roadmap",
        "preview_image": "/static/templates/memecoin_preview.jpg",
        "required_fields": [
            "coin_name",
            "slogan"
        ],
        "optional_fields": [
            "logo_url",
            "social_links.telegram",
            "social_links.twitter",
            "tokenomics.total_supply",
            "tokenomics.burn",
            "tokenomics.redistribution",
            "tokenomics.liquidity",
            "roadmap"
        ],
        "default_sections": [
            "header",
            "about",
            "tokenomics",
            "roadmap",
            "community"
        ],
        "default_colors": {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "accent": "#FFE66D"
        }
    },
    
    "nft": {
        "name": "NFT Collection",
        "description": "Showcase your NFT collection with gallery and minting interface",
        "preview_image": "/static/templates/nft_preview.jpg",
        "required_fields": [
            "collection_name",
            "description"
        ],
        "optional_fields": [
            "logo_url",
            "social_links.telegram",
            "social_links.twitter",
            "social_links.discord",
            "nft_count",
            "mint_price",
            "max_mint",
            "reveal_date"
        ],
        "default_sections": [
            "header",
            "about",
            "gallery",
            "mint",
            "roadmap",
            "team",
            "faq"
        ],
        "default_colors": {
            "primary": "#6B5B95",
            "secondary": "#FFA500",
            "accent": "#88B04B"
        }
    },
    
    "defi": {
        "name": "DeFi Dashboard",
        "description": "Professional DeFi platform with staking and yield farming information",
        "preview_image": "/static/templates/defi_preview.jpg",
        "required_fields": [
            "platform_name",
            "token_name",
            "token_symbol"
        ],
        "optional_fields": [
            "logo_url",
            "social_links.telegram",
            "social_links.twitter",
            "social_links.discord",
            "social_links.github",
            "annual_yield",
            "tvl",
            "staking_pools",
            "farming_pairs"
        ],
        "default_sections": [
            "header",
            "about",
            "tvl",
            "staking",
            "farms",
            "tokenomics",
            "governance"
        ],
        "default_colors": {
            "primary": "#00A4CC",
            "secondary": "#F95700",
            "accent": "#ADEFD1"
        }
    }
}

# Default repository for template HTML files
TEMPLATE_DIR = Path("templates")

class TemplateManager:
    """
    Manages website templates and their specific handling requirements.
    
    This class is responsible for:
    - Loading template definitions
    - Validating template data
    - Processing template-specific variables
    - Generating HTML from templates with the right data structure
    """
    
    def __init__(self):
        """Initialize the template manager."""
        self.templates = TEMPLATES
        
        # Ensure template directory exists
        if not TEMPLATE_DIR.exists():
            os.makedirs(TEMPLATE_DIR, exist_ok=True)
            logger.info(f"Created template directory: {TEMPLATE_DIR}")
    
    def get_templates(self):
        """Get a list of available templates."""
        return [
            {
                "id": template_id,
                "name": template_data["name"],
                "description": template_data["description"],
                "preview_image": template_data["preview_image"]
            }
            for template_id, template_data in self.templates.items()
        ]
    
    def get_template_metadata(self, template_id):
        """Get metadata for a specific template."""
        if template_id not in self.templates:
            return None
        
        return self.templates[template_id]
    
    def validate_template_data(self, template_id, data):
        """
        Validate that the provided data contains all required fields for the template.
        
        Args:
            template_id (str): The ID of the template to validate against
            data (dict): The website data to validate
            
        Returns:
            dict: Validation result with success flag and error message if applicable
        """
        if template_id not in self.templates:
            return {
                "valid": False,
                "error": f"Unknown template: {template_id}"
            }
        
        template_data = self.templates[template_id]
        required_fields = template_data["required_fields"]
        
        missing_fields = []
        
        for field in required_fields:
            if "." in field:
                # Check nested fields
                parts = field.split(".")
                current = data
                field_exists = True
                
                for part in parts:
                    if part not in current or current[part] is None:
                        field_exists = False
                        break
                    current = current[part]
                
                if not field_exists:
                    missing_fields.append(field)
            elif field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        return {
            "valid": True
        }
    
    def process_template_data(self, template_id, raw_data):
        """
        Process and transform raw data into the format expected by the template.
        
        Args:
            template_id (str): The ID of the template
            raw_data (dict): The raw website data
            
        Returns:
            dict: The processed data structure ready for template rendering
        """
        if template_id not in self.templates:
            raise ValueError(f"Unknown template: {template_id}")
        
        template_meta = self.templates[template_id]
        
        # Create a base structure with defaults
        processed_data = {}
        
        if template_id == "memecoin":
            return self._process_memecoin_template(raw_data, template_meta)
        elif template_id == "nft":
            return self._process_nft_template(raw_data, template_meta)
        elif template_id == "defi":
            return self._process_defi_template(raw_data, template_meta)
        else:
            # Generic processor for other templates
            return raw_data
    
    def _process_memecoin_template(self, raw_data, template_meta):
        """Process data specifically for the memecoin template."""
        processed_data = {
            "name": raw_data.get("coin_name", ""),
            "formatted_name": raw_data.get("formatted_name", raw_data.get("coin_name", "")),
            "symbol": raw_data.get("symbol", ""),
            "slogan": raw_data.get("slogan", "To the Moon! 🚀"),
            "has_custom_logo": "logo_url" in raw_data and raw_data["logo_url"] is not None,
            "logo_url": raw_data.get("logo_url", ""),
            "theme": {
                "primary": raw_data.get("colors", {}).get("primary", template_meta["default_colors"]["primary"]),
                "secondary": raw_data.get("colors", {}).get("secondary", template_meta["default_colors"]["secondary"]),
                "accent": raw_data.get("colors", {}).get("accent", template_meta["default_colors"]["accent"])
            }
        }
        
        # Process social links
        social_links = raw_data.get("social_links", {})
        processed_data["has_telegram"] = "telegram" in social_links and social_links["telegram"] is not None
        processed_data["telegram_url"] = social_links.get("telegram", "#")
        processed_data["has_twitter"] = "twitter" in social_links and social_links["twitter"] is not None
        processed_data["twitter_url"] = social_links.get("twitter", "#")
        
        # Process tokenomics
        tokenomics = raw_data.get("tokenomics", {})
        processed_data["tokenomics"] = {
            "total_supply": tokenomics.get("total_supply", "1,000,000,000,000"),
            "burn": tokenomics.get("burn", "2%"),
            "redistribution": tokenomics.get("redistribution", "2%"),
            "liquidity": tokenomics.get("liquidity", "1%"),
            "marketing": tokenomics.get("marketing", "1%")
        }
        
        # Process roadmap
        roadmap = raw_data.get("roadmap", [])
        if roadmap:
            processed_data["roadmap"] = roadmap[0] if roadmap else []
        else:
            # Default roadmap
            processed_data["roadmap"] = [
                "Launch Website", 
                "Create Social Media", 
                "Token Launch", 
                "CoinGecko Listing"
            ]
        
        return processed_data
    
    def _process_nft_template(self, raw_data, template_meta):
        """Process data specifically for the NFT template."""
        processed_data = {
            "collection_name": raw_data.get("collection_name", ""),
            "description": raw_data.get("description", ""),
            "has_custom_logo": "logo_url" in raw_data and raw_data["logo_url"] is not None,
            "logo_url": raw_data.get("logo_url", ""),
            "theme": {
                "primary": raw_data.get("colors", {}).get("primary", template_meta["default_colors"]["primary"]),
                "secondary": raw_data.get("colors", {}).get("secondary", template_meta["default_colors"]["secondary"]),
                "accent": raw_data.get("colors", {}).get("accent", template_meta["default_colors"]["accent"])
            },
            "nft_count": raw_data.get("nft_count", 10000),
            "mint_price": raw_data.get("mint_price", "0.08 ETH"),
            "max_mint": raw_data.get("max_mint", 10),
            "reveal_date": raw_data.get("reveal_date", "TBA")
        }
        
        # Process social links
        social_links = raw_data.get("social_links", {})
        processed_data["has_telegram"] = "telegram" in social_links and social_links["telegram"] is not None
        processed_data["telegram_url"] = social_links.get("telegram", "#")
        processed_data["has_twitter"] = "twitter" in social_links and social_links["twitter"] is not None
        processed_data["twitter_url"] = social_links.get("twitter", "#")
        processed_data["has_discord"] = "discord" in social_links and social_links["discord"] is not None
        processed_data["discord_url"] = social_links.get("discord", "#")
        
        # Process gallery items (placeholder for real NFTs)
        processed_data["gallery_items"] = raw_data.get("gallery_items", [
            {"id": 1, "name": "NFT #1", "image": "/static/placeholders/nft1.jpg"},
            {"id": 2, "name": "NFT #2", "image": "/static/placeholders/nft2.jpg"},
            {"id": 3, "name": "NFT #3", "image": "/static/placeholders/nft3.jpg"},
            {"id": 4, "name": "NFT #4", "image": "/static/placeholders/nft4.jpg"}
        ])
        
        # Process team members
        processed_data["team_members"] = raw_data.get("team_members", [
            {"name": "Founder", "role": "Lead Artist", "bio": "NFT enthusiast and digital artist", "image": "/static/placeholders/team1.jpg"},
            {"name": "Developer", "role": "Smart Contract Developer", "bio": "Blockchain expert", "image": "/static/placeholders/team2.jpg"}
        ])
        
        # Process FAQ
        processed_data["faq_items"] = raw_data.get("faq_items", [
            {"question": "When is the mint date?", "answer": "TBA, follow our social media for announcements"},
            {"question": "What is the mint price?", "answer": processed_data["mint_price"]},
            {"question": "How many can I mint?", "answer": f"You can mint up to {processed_data['max_mint']} NFTs per transaction."}
        ])
        
        return processed_data
    
    def _process_defi_template(self, raw_data, template_meta):
        """Process data specifically for the DeFi template."""
        processed_data = {
            "platform_name": raw_data.get("platform_name", ""),
            "token_name": raw_data.get("token_name", ""),
            "token_symbol": raw_data.get("token_symbol", ""),
            "description": raw_data.get("description", "A decentralized finance platform for staking and yield farming"),
            "has_custom_logo": "logo_url" in raw_data and raw_data["logo_url"] is not None,
            "logo_url": raw_data.get("logo_url", ""),
            "theme": {
                "primary": raw_data.get("colors", {}).get("primary", template_meta["default_colors"]["primary"]),
                "secondary": raw_data.get("colors", {}).get("secondary", template_meta["default_colors"]["secondary"]),
                "accent": raw_data.get("colors", {}).get("accent", template_meta["default_colors"]["accent"])
            },
            "annual_yield": raw_data.get("annual_yield", "Up to 120% APY"),
            "tvl": raw_data.get("tvl", "$10,000,000")
        }
        
        # Process social links
        social_links = raw_data.get("social_links", {})
        processed_data["has_telegram"] = "telegram" in social_links and social_links["telegram"] is not None
        processed_data["telegram_url"] = social_links.get("telegram", "#")
        processed_data["has_twitter"] = "twitter" in social_links and social_links["twitter"] is not None
        processed_data["twitter_url"] = social_links.get("twitter", "#")
        processed_data["has_discord"] = "discord" in social_links and social_links["discord"] is not None
        processed_data["discord_url"] = social_links.get("discord", "#")
        processed_data["has_github"] = "github" in social_links and social_links["github"] is not None
        processed_data["github_url"] = social_links.get("github", "#")
        
        # Process staking pools
        processed_data["staking_pools"] = raw_data.get("staking_pools", [
            {"name": "Flexible Staking", "apy": "40%", "lockup": "None", "min_amount": "100", "token": processed_data["token_symbol"]},
            {"name": "3-Month Staking", "apy": "80%", "lockup": "3 months", "min_amount": "500", "token": processed_data["token_symbol"]},
            {"name": "6-Month Staking", "apy": "120%", "lockup": "6 months", "min_amount": "1000", "token": processed_data["token_symbol"]}
        ])
        
        # Process farming pairs
        processed_data["farming_pairs"] = raw_data.get("farming_pairs", [
            {"name": f"{processed_data['token_symbol']}-ETH", "apy": "150%", "tvl": "$2,500,000", "risk": "Medium"},
            {"name": f"{processed_data['token_symbol']}-USDT", "apy": "100%", "tvl": "$4,000,000", "risk": "Low"},
            {"name": f"{processed_data['token_symbol']}-WBTC", "apy": "200%", "tvl": "$1,500,000", "risk": "High"}
        ])
        
        # Process tokenomics
        tokenomics = raw_data.get("tokenomics", {})
        processed_data["tokenomics"] = {
            "total_supply": tokenomics.get("total_supply", "100,000,000"),
            "circulating_supply": tokenomics.get("circulating_supply", "65,000,000"),
            "burned": tokenomics.get("burned", "5,000,000"),
            "distribution": tokenomics.get("distribution", [
                {"name": "Liquidity", "percentage": "40%"},
                {"name": "Team", "percentage": "15%"},
                {"name": "Community", "percentage": "25%"},
                {"name": "Treasury", "percentage": "20%"}
            ])
        }
        
        return processed_data
    
    def get_template_html_path(self, template_id):
        """Get the path to the template HTML file."""
        if template_id not in self.templates:
            raise ValueError(f"Unknown template: {template_id}")
        
        template_path = TEMPLATE_DIR / f"{template_id}_template.html"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        return template_path
    
    def save_generated_site(self, site_hash, html_content):
        """
        Save generated HTML content to a file.
        
        Args:
            site_hash (str): Unique hash for the website
            html_content (str): The generated HTML content
            
        Returns:
            str: The path to the saved file
        """
        sites_dir = Path("sites")
        if not sites_dir.exists():
            os.makedirs(sites_dir, exist_ok=True)
            logger.info(f"Created sites directory: {sites_dir}")
        
        file_path = sites_dir / f"{site_hash}.html"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Saved generated site to {file_path}")
        
        return str(file_path)

# Example usage
if __name__ == "__main__":
    # Create template manager
    manager = TemplateManager()
    
    # Get available templates
    templates = manager.get_templates()
    print(f"Available templates: {json.dumps(templates, indent=2)}")
    
    # Example data for memecoin template
    memecoin_data = {
        "coin_name": "MoonElonDoge",
        "formatted_name": "Moon Elon Doge",
        "symbol": "MED",
        "slogan": "To the Moon and Beyond! 🚀",
        "description": "The next generation of meme coins with revolutionary tokenomics.",
        "colors": {
            "primary": "#0F0F29",
            "secondary": "#00FFFF", 
            "accent": "#FF00FF"
        },
        "social_links": {
            "telegram": "https://t.me/moonelon",
            "twitter": "https://twitter.com/moonelon"
        },
        "tokenomics": {
            "total_supply": "1,000,000,000,000",
            "burn": "2%",
            "redistribution": "3%",
            "liquidity": "5%"
        },
        "roadmap": [
            ["Website Launch", "Social Media Creation", "Community Building"],
            ["Exchange Listings", "Partnership Announcements", "Marketing Campaign"],
            ["NFT Integration", "Utility Expansion", "Global Adoption"]
        ]
    }
    
    # Validate template data
    validation = manager.validate_template_data("memecoin", memecoin_data)
    print(f"Validation result: {validation}")
    
    # Process template data
    processed_data = manager.process_template_data("memecoin", memecoin_data)
    print(f"Processed data: {json.dumps(processed_data, indent=2)}")
    
    # Here you would normally:
    # 1. Get the template HTML
    # 2. Render it with the processed data (e.g., using Jinja2)
    # 3. Save the generated site
    # 
    # For demonstration, we'll just print a message
    print("In a real implementation, you would render the template with the processed data here.")