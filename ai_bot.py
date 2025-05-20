"""
AI-Powered Website Generator Bot

This module implements a Telegram bot where Claude handles the full website generation
process based on minimal user input. It uses natural language understanding to extract
requirements and intelligently creates websites with sensible defaults.
"""

import os
import re
import logging
import asyncio
import hashlib
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from customization_states import STATES, CustomizationStateManager
from customization_flow import (get_or_create_state_manager, get_templates, get_themes, 
                               handle_template_selection, generate_website, reset_state)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
USE_GITHUB = os.getenv('USE_GITHUB', 'false').lower() == 'true'

# Initialize GitHub uploader if configured
try:
    if USE_GITHUB:
        from github_uploader import GitHubUploader
        github_uploader = GitHubUploader() if os.getenv('GITHUB_TOKEN') else None
        logger.info("GitHub integration enabled")
    else:
        github_uploader = None
except ImportError:
    logger.warning("GitHub uploader module not available")
    github_uploader = None
    USE_GITHUB = False

# Template types mapping
TEMPLATE_TYPES = {
    'meme': 'memecoin',
    'memecoin': 'memecoin',
    'token': 'memecoin',
    'coin': 'memecoin',
    'crypto': 'memecoin',
    'nft': 'nft',
    'collection': 'nft',
    'art': 'nft',
    'defi': 'defi',
    'finance': 'defi',
    'staking': 'defi',
    'yield': 'defi'
}

# Default themes for each template
DEFAULT_THEMES = {
    'memecoin': 'neon',
    'nft': 'royal',
    'defi': 'dark'
}

# Track user state for collecting additional information
user_conversation_state = {}

# Startup handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the AI-powered website creation flow."""
    # Reset user state to begin fresh
    user_id = str(update.effective_user.id)
    reset_state(user_id)
    
    # Initialize context data if not present
    if 'generation_data' not in context.user_data:
        context.user_data['generation_data'] = {}
    
    await update.message.reply_text(
        "🚀 *Welcome to AI Website Creator!* 🚀\n\n"
        "I'll create a custom website for you with just a few details!\n\n"
        "Simply tell me what you want to build in natural language. For example:\n\n"
        "• \"Create a meme coin site for MoonElonDoge\"\n"
        "• \"Make an NFT collection page for Bored Pixel Punks\"\n"
        "• \"Build a DeFi website for YieldHub with blue theme\"\n\n"
        "I'll ask a few follow-up questions to customize it perfectly for you!",
        parse_mode='Markdown'
    )

# Help handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    await update.message.reply_text(
        "🌐 *AI Website Creator Bot* 🌐\n\n"
        "*Commands:*\n"
        "/start - Start a new website project\n"
        "/help - Show this help message\n"
        "/examples - Show example prompts\n\n"
        "Just tell me what kind of website you want to build in everyday language.\n"
        "I'll understand your requirements and create a beautiful website automatically!",
        parse_mode='Markdown'
    )

# Examples handler
async def examples_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show example prompts."""
    await update.message.reply_text(
        "🌟 *Example Prompts* 🌟\n\n"
        "*Meme Coin / Token Websites:*\n"
        "• \"Create a meme coin site for DogeX with a space theme\"\n"
        "• \"Make me a token website for FlokiMoon with rocket imagery\"\n"
        "• \"I need a coin site for CatCoin with a cute pink theme no tokenomics\"\n\n"
        "*NFT Collection Websites:*\n"
        "• \"Build an NFT gallery for Crypto Monkeys with 10k items\"\n"
        "• \"Create an NFT collection site for Pixel Dragons\"\n"
        "• \"Make a site for my digital art collection called Ethereal Dreams\"\n\n"
        "*DeFi Websites:*\n"
        "• \"Create a DeFi platform website for YieldFarm\"\n"
        "• \"Build a staking platform site for StakeX Token\"\n"
        "• \"Make a finance site for Swap Protocol with a dark blue theme\"\n\n"
        "Try any of these or create your own prompt!",
        parse_mode='Markdown'
    )

# Photo handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads."""
    user_id = str(update.effective_user.id)
    
    # Check if we're in the middle of collecting information
    if user_id in user_conversation_state:
        state = user_conversation_state[user_id]
        current_state = state.get('waiting_for', '')
        
        if current_state == 'logo':
            try:
                # Process the uploaded logo
                photo = update.message.photo[-1]  # Get largest photo
                file_id = photo.file_id
                file = await context.bot.get_file(file_id)
                
                # Create uploads directory if needed
                os.makedirs('uploads', exist_ok=True)
                
                # Generate a unique filename
                filename = f"uploads/{user_id}_{file_id}.jpg"
                
                # Download the file
                await file.download_to_drive(filename)
                
                # Store the logo URL
                state['website_data']['logo_url'] = filename
                
                # Continue to next step (buy link)
                await update.message.reply_text(
                    "Great! I've saved your logo. What's the buy button link for your token? (or type 'skip'):"
                )
                state['waiting_for'] = 'buy_link'
            except Exception as e:
                logger.error(f"Error processing photo: {str(e)}")
                await update.message.reply_text(
                    "Sorry, I couldn't process your photo. Please try again or type 'skip' to continue without a logo."
                )
            return
    
    # Get the caption text or use a default
    caption = update.message.caption or "Create a website"
    
    # Process the photo
    await update.message.reply_text(
        "🧠 Understanding your requirements and processing image...",
        parse_mode='Markdown'
    )
    
    # Processing indicator
    thinking_msg = await update.message.reply_text("⏳ Thinking...")
    
    try:
        # Get the photo file
        photo = update.message.photo[-1]  # Get largest photo
        file_id = photo.file_id
        file = await context.bot.get_file(file_id)
        
        # Create uploads directory if needed
        os.makedirs('uploads', exist_ok=True)
        
        # Generate a unique filename
        filename = f"uploads/{user_id}_{file_id}.jpg"
        
        # Download the file
        await file.download_to_drive(filename)
        
        # AI analysis of request - extract key information
        website_data = analyze_request(caption)
        
        # Add the logo URL
        website_data["logo_url"] = filename
        
        # Update tokenomics display based on the caption
        if 'no tokenomics' in caption.lower() or 'remove tokenomics' in caption.lower():
            website_data['show_tokenomics'] = False
        
        # Update with extracted information
        context.user_data['generation_data'] = website_data
        
        # Format what we understood
        understood_msg = format_understanding(website_data)
        
        # Update the thinking message and start collecting more information
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id
        )
        
        await update.message.reply_text(
            f"✅ I understand! Here's what I'll create:\n\n{understood_msg}\n\n"
            f"🖼️ Using your uploaded image as logo\n\n"
            f"Let's collect a few more details to customize your website.",
            parse_mode='Markdown'
        )
        
        # Store the website data and start collecting additional information
        user_conversation_state[user_id] = {
            'website_data': website_data,
            'waiting_for': 'buy_link'
        }
        
        # Ask for buy link
        await update.message.reply_text(
            "What's the buy button link for your token? (or type 'skip'):"
        )
    
    except Exception as e:
        logger.error(f"Error processing photo: {str(e)}")
        if 'thinking_msg' in locals():
            await context.bot.edit_message_text(
                f"❌ Sorry, I encountered an error processing your image: {str(e)}",
                chat_id=update.effective_chat.id,
                message_id=thinking_msg.message_id
            )

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and generate websites with AI."""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # Check if we're in the middle of collecting information
    if user_id in user_conversation_state:
        state = user_conversation_state[user_id]
        
        if state['waiting_for'] == 'buy_link':
            # User provided buy link
            if text.lower() == 'skip':
                state['website_data']['buy_link'] = ''
            else:
                # Add https:// if missing
                if not text.startswith(('http://', 'https://')):
                    text = 'https://' + text
                state['website_data']['buy_link'] = text
            
            # Now ask for Telegram
            await update.message.reply_text(
                "Great! Now, enter your Telegram group link (or type 'skip'):"
            )
            state['waiting_for'] = 'telegram'
            return
            
        elif state['waiting_for'] == 'telegram':
            # User provided Telegram link
            if text.lower() == 'skip':
                # Don't add if skipped
                pass
            else:
                # Add https:// if missing
                if not text.startswith(('http://', 'https://')):
                    text = 'https://' + text
                state['website_data']['social_links']['telegram'] = text
            
            # Now ask for Twitter
            await update.message.reply_text(
                "Now, enter your Twitter profile link (or type 'skip'):"
            )
            state['waiting_for'] = 'twitter'
            return
            
        elif state['waiting_for'] == 'twitter':
            # User provided Twitter link
            if text.lower() == 'skip':
                # Don't add if skipped
                pass
            else:
                # Add https:// if missing
                if not text.startswith(('http://', 'https://')):
                    text = 'https://' + text
                state['website_data']['social_links']['twitter'] = text
            
            # Now ask for DexScreener
            await update.message.reply_text(
                "Finally, enter your DexScreener link (or type 'skip'):"
            )
            state['waiting_for'] = 'dexscreener'
            return
            
        elif state['waiting_for'] == 'dexscreener':
            # User provided DexScreener link
            if text.lower() == 'skip':
                # Don't add if skipped
                pass
            else:
                # Add https:// if missing
                if not text.startswith(('http://', 'https://')):
                    text = 'https://' + text
                state['website_data']['dexscreener_link'] = text
                
                # Also ask about tokenomics
                if 'no tokenomics' in text.lower() or 'remove tokenomics' in text.lower():
                    state['website_data']['show_tokenomics'] = False
            
            # Now generate the website with collected information
            website_data = state['website_data']
            
            # Create thinking message
            thinking_msg = await update.message.reply_text(
                "⏳ Generating your website with all the provided information..."
            )
            
            # Delete user from conversation state
            del user_conversation_state[user_id]
            
            # Generate website
            site_result = await generate_website_from_data(user_id, website_data, update, context, thinking_msg)
            return
    
    # Start fresh website generation flow
    # Process the user's input
    await update.message.reply_text(
        "🧠 Understanding your requirements...",
        parse_mode='Markdown'
    )
    
    # Processing indicator
    thinking_msg = await update.message.reply_text("⏳ Thinking...")
    
    try:
        # AI analysis of request - extract key information
        website_data = analyze_request(text)
        
        # Update tokenomics display based on the text
        if 'no tokenomics' in text.lower() or 'remove tokenomics' in text.lower():
            website_data['show_tokenomics'] = False
        
        # Update with extracted information
        context.user_data['generation_data'] = website_data
        
        # Format what we understood
        understood_msg = format_understanding(website_data)
        
        # Update the thinking message and start collecting more information
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=thinking_msg.message_id
        )
        
        await update.message.reply_text(
            f"✅ I understand! Here's what I'll create:\n\n{understood_msg}\n\n"
            f"Let's collect a few more details to customize your website.",
            parse_mode='Markdown'
        )
        
        # Store the website data and start collecting additional information
        user_conversation_state[user_id] = {
            'website_data': website_data,
            'waiting_for': 'buy_link'
        }
        
        # Ask for buy link
        await update.message.reply_text(
            "What's the buy button link for your token? (or type 'skip'):"
        )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        if 'thinking_msg' in locals():
            await context.bot.edit_message_text(
                "❌ Sorry, I encountered an error processing your request. Please try again with a simpler description.",
                chat_id=update.effective_chat.id,
                message_id=thinking_msg.message_id
            )

def analyze_request(text):
    """
    Analyze the user's request and extract key information.
    This is a simplified version of what Claude would do with more sophisticated NLP.
    """
    text = text.lower()
    
    # Initialize with default values
    website_data = {
        "template_type": "memecoin",  # Default to memecoin
        "name": "",
        "theme": "",
        "color_scheme": "",
        "features": [],
        "social_links": {},
        "buy_link": "",     # Added buy button link
        "show_tokenomics": True,  # Control tokenomics display
        "dexscreener_link": ""    # Added dexscreener link
    }
    
    # Detect template type
    template_found = False
    for keyword, template in TEMPLATE_TYPES.items():
        if keyword in text:
            website_data["template_type"] = template
            template_found = True
            break
    
    # Extract name - look for common patterns
    name_patterns = [
        r"for\s+([A-Za-z0-9]+(?:[A-Za-z0-9\s]*[A-Za-z0-9]+)?)",
        r"called\s+([A-Za-z0-9]+(?:[A-Za-z0-9\s]*[A-Za-z0-9]+)?)",
        r"named\s+([A-Za-z0-9]+(?:[A-Za-z0-9\s]*[A-Za-z0-9]+)?)",
        r"site\s+for\s+([A-Za-z0-9]+(?:[A-Za-z0-9\s]*[A-Za-z0-9]+)?)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            website_data["name"] = match.group(1).strip()
            break
    
    # If no name found, create one based on template type
    if not website_data["name"]:
        prefixes = {
            "memecoin": ["Moon", "Doge", "Shib", "Elon", "Pepe", "Floki", "Rocket", "Star", "Coin", "Token"],
            "nft": ["Bored", "Crypto", "Pixel", "Punk", "Ape", "Dragon", "Cat", "Alien", "Robot", "Ghost"],
            "defi": ["Yield", "Stake", "Swap", "Farm", "Lend", "Pool", "Dao", "Safe", "Earn", "Vault"]
        }
        
        suffixes = {
            "memecoin": ["Moon", "Doge", "Coin", "Token", "Rocket", "Inu", "Star", "Cash", "Finance", "X"],
            "nft": ["Club", "Collection", "Gallery", "Art", "Space", "World", "Verse", "Labs", "Studio", "NFT"],
            "defi": ["Finance", "Protocol", "Network", "Exchange", "Hub", "DAO", "Capital", "Money", "Bank", "DeFi"]
        }
        
        prefix = random.choice(prefixes[website_data["template_type"]])
        suffix = random.choice(suffixes[website_data["template_type"]])
        website_data["name"] = f"{prefix}{suffix}"
    
    # Detect color themes
    color_keywords = {
        "blue": "dark",
        "red": "royal",
        "green": "nature",
        "purple": "royal",
        "pink": "royal", 
        "yellow": "nature",
        "orange": "neon",
        "black": "dark",
        "white": "light",
        "dark": "dark",
        "light": "light",
        "neon": "neon",
        "bright": "neon",
        "modern": "dark",
        "elegant": "royal",
        "professional": "royal",
        "fun": "neon",
        "serious": "dark"
    }
    
    for color, theme in color_keywords.items():
        if color in text:
            website_data["theme"] = theme
            break
    
    # If no theme specified, use default for template type
    if not website_data["theme"]:
        website_data["theme"] = DEFAULT_THEMES[website_data["template_type"]]
    
    # Extract social links if mentioned
    if "telegram" in text or "tg" in text:
        website_data["social_links"]["telegram"] = "https://t.me/" + website_data["name"].lower().replace(" ", "")
    
    if "twitter" in text or "x" in text:
        website_data["social_links"]["twitter"] = "https://twitter.com/" + website_data["name"].lower().replace(" ", "")
    
    if "discord" in text:
        website_data["social_links"]["discord"] = "https://discord.gg/" + website_data["name"].lower().replace(" ", "")
    
    # Check for tokenomics settings
    if "no tokenomics" in text or "remove tokenomics" in text or "without tokenomics" in text:
        website_data["show_tokenomics"] = False
    
    # Set more detailed defaults based on template type
    if website_data["template_type"] == "memecoin":
        slogan = random.choice([
            "To The Moon! 🚀",
            "The Next 1000x Gem 💎",
            "Community-Driven Revolution 🔥",
            "Join The Movement! 💪",
            "Better Than Bitcoin? Maybe! 👀"
        ])
        website_data["slogan"] = slogan
        
        # Random tokenomics
        supply = random.choice(["1,000,000,000", "1,000,000,000,000", "100,000,000,000"])
        website_data["tokenomics"] = {
            "total_supply": supply,
            "burn": f"{random.randint(1, 5)}%",
            "redistribution": f"{random.randint(1, 4)}%",
            "liquidity": f"{random.randint(2, 6)}%",
            "marketing": f"{random.randint(1, 5)}%"
        }
    
    elif website_data["template_type"] == "nft":
        website_data["nft_count"] = "10,000"
        website_data["mint_price"] = f"{random.choice(['0.05', '0.08', '0.1', '0.2'])} ETH"
        website_data["description"] = f"A unique collection of {website_data['nft_count']} digital collectibles living on the Ethereum blockchain."
    
    elif website_data["template_type"] == "defi":
        apy = random.choice(["Up to 120%", "20-200%", "High Yields", "Market-Leading"])
        website_data["annual_yield"] = apy
        website_data["tvl"] = f"${random.choice(['1,000,000', '5,000,000', '10,000,000', '25,000,000'])}"
        website_data["description"] = f"The most innovative DeFi platform with {apy} APY and secure, audited smart contracts."
    
    return website_data

def format_understanding(data):
    """Format what we understood from the user's request."""
    template_names = {
        "memecoin": "Meme Coin/Token",
        "nft": "NFT Collection",
        "defi": "DeFi Platform"
    }
    
    theme_names = {
        "dark": "Dark Modern",
        "light": "Light & Clean",
        "neon": "Vibrant Neon",
        "royal": "Royal Purple",
        "nature": "Natural Green"
    }
    
    msg = (
        f"*Project Name:* {data['name']}\n"
        f"*Website Type:* {template_names[data['template_type']]}\n"
        f"*Theme:* {theme_names[data['theme']]}\n"
    )
    
    # Add template-specific information
    if data["template_type"] == "memecoin":
        msg += f"*Slogan:* {data['slogan']}\n"
        
        # Add tokenomics info if showing
        if data.get('show_tokenomics', True) and "tokenomics" in data:
            msg += (
                f"*Total Supply:* {data['tokenomics']['total_supply']}\n"
                f"*Tokenomics:* {data['tokenomics']['burn']} burn, "
                f"{data['tokenomics']['redistribution']} redistribution, "
                f"{data['tokenomics']['liquidity']} liquidity\n"
            )
        else:
            msg += "*Tokenomics Section:* Hidden\n"
    
    elif data["template_type"] == "nft":
        msg += (
            f"*Collection Size:* {data['nft_count']}\n"
            f"*Mint Price:* {data['mint_price']}\n"
        )
    
    elif data["template_type"] == "defi":
        msg += (
            f"*Advertised APY:* {data['annual_yield']}\n"
            f"*Total Value Locked:* {data['tvl']}\n"
        )
    
    # Add social links if any
    social_links = []
    if "telegram" in data["social_links"]:
        social_links.append("Telegram")
    if "twitter" in data["social_links"]:
        social_links.append("Twitter") 
    if "discord" in data["social_links"]:
        social_links.append("Discord")
    
    if social_links:
        msg += f"*Social Media:* {', '.join(social_links)}\n"
    
    return msg

async def generate_website_from_data(user_id, website_data, update, context, status_msg):
    """Generate a website using the AI-extracted data."""
    try:
        # Initialize state manager
        manager = get_or_create_state_manager(user_id)
        
        # Reset to IDLE and clear through all state transitions
        manager.reset()
        
        # Force IDLE state
        manager.current_state = STATES['IDLE']
        
        # Update status
        await context.bot.edit_message_text(
            f"⏳ Generating website (10%)...",
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id
        )
        
        # 1. Select template - transition to template selection first
        manager.transition_to(STATES['WAITING_FOR_TEMPLATE_SELECTION'])
        handle_template_selection(user_id, website_data["template_type"])
        
        # Skip through all required states to reach WAITING_FOR_CONFIRMATION
        # This ensures all proper state transitions occur
        
        # Update status
        await context.bot.edit_message_text(
            f"⏳ Generating website (20%)...",
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id
        )
        
        # 2. Populate all the required data
        # Set coin name
        manager.update_data('coin_name', website_data["name"])
        
        # Set formatted name (e.g., "MoonDoge" -> "Moon Doge")
        formatted_name = ' '.join(re.findall(r'[A-Z][a-z]*', website_data["name"]))
        if not formatted_name:
            formatted_name = website_data["name"]
        manager.update_data('formatted_name', formatted_name)
        
        # Generate symbol if not present
        symbol = ''.join(word[0] for word in re.findall(r'[A-Z][a-z]*', website_data["name"]))
        if not symbol:
            symbol = website_data["name"][:4].upper()
        manager.update_data('symbol', symbol)
        
        # Update status
        await context.bot.edit_message_text(
            f"⏳ Generating website (30%)...",
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id
        )
        
        # Set theme and colors
        manager.update_data('theme', website_data["theme"])
        
        theme_data = next((t for t in get_themes() if t['id'] == website_data["theme"]), None)
        if theme_data:
            manager.update_data('colors.primary', theme_data['colors']['primary'])
            manager.update_data('colors.secondary', theme_data['colors']['secondary'])
            manager.update_data('colors.accent', theme_data['colors']['accent'])
        
        # Handle logo if provided
        if 'logo_url' in website_data and website_data['logo_url']:
            manager.update_data('logo_url', website_data['logo_url'])
            manager.update_data('has_custom_logo', True)
        
        # Handle buy link if provided
        if 'buy_link' in website_data and website_data['buy_link']:
            manager.update_data('buy_link', website_data['buy_link'])
        
        # Handle DexScreener link if provided
        if 'dexscreener_link' in website_data and website_data['dexscreener_link']:
            manager.update_data('dexscreener_link', website_data['dexscreener_link'])
        
        # Set tokenomics visibility
        manager.update_data('show_tokenomics', website_data.get('show_tokenomics', True))
        
        # Update status
        await context.bot.edit_message_text(
            f"⏳ Generating website (50%)...",
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id
        )
        
        # Set template-specific data
        if website_data["template_type"] == "memecoin":
            # Set slogan
            manager.update_data('slogan', website_data.get('slogan', ''))
            
            # Set tokenomics
            if 'tokenomics' in website_data:
                for key, value in website_data['tokenomics'].items():
                    manager.update_data(f'tokenomics.{key}', value)
        
        elif website_data["template_type"] == "nft":
            # Set NFT-specific data
            manager.update_data('collection_name', website_data["name"])
            manager.update_data('description', website_data.get('description', ''))
            manager.update_data('nft_count', website_data.get('nft_count', '10,000'))
            manager.update_data('mint_price', website_data.get('mint_price', '0.08 ETH'))
        
        elif website_data["template_type"] == "defi":
            # Set DeFi-specific data
            manager.update_data('platform_name', website_data["name"])
            manager.update_data('token_name', website_data["name"] + " Token")
            manager.update_data('token_symbol', symbol)
            manager.update_data('annual_yield', website_data.get('annual_yield', 'Up to 120% APY'))
            manager.update_data('tvl', website_data.get('tvl', '$10,000,000'))
        
        # Set social links
        for platform, url in website_data.get('social_links', {}).items():
            manager.update_data(f'social_links.{platform}', url)
        
        # Update status
        await context.bot.edit_message_text(
            f"⏳ Generating website (80%)...",
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id
        )
        
        # Force the state to READY_TO_GENERATE directly
        # This bypasses the normal state flow for AI-driven generation
        manager.current_state = STATES['READY_TO_GENERATE']
        
        # Generate a unique hash for this website
        site_hash = hashlib.md5(f"{website_data['name']}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        manager.update_data('site_hash', site_hash)
        
        # Call the generate_website function
        result = generate_website(user_id)
        
        # Update status based on result
        if result["success"]:
            # Get the URLs
            site_hash = result["data"]["site_hash"]
            
            # Handle GitHub upload if enabled
            if USE_GITHUB and github_uploader:
                try:
                    await context.bot.edit_message_text(
                        f"⏳ Uploading to GitHub for secure hosting (90%)...",
                        chat_id=update.effective_chat.id,
                        message_id=status_msg.message_id
                    )
                    
                    # Read the generated HTML file
                    with open(f"sites/{site_hash}.html", 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Embed the logo image directly in the HTML as a base64 data URL if it exists
                    if 'logo_url' in website_data and website_data['logo_url'] and os.path.exists(website_data['logo_url']):
                        try:
                            logo_path = website_data['logo_url']
                            
                            # Read the image as binary data
                            with open(logo_path, 'rb') as img_file:
                                image_data = img_file.read()
                            
                            # Determine the MIME type based on file extension
                            import mimetypes
                            mime_type = mimetypes.guess_type(logo_path)[0] or 'image/jpeg'
                            
                            # Create base64 data URL
                            import base64
                            b64_image = base64.b64encode(image_data).decode('utf-8')
                            data_url = f"data:{mime_type};base64,{b64_image}"
                            
                            # Replace all instances of the logo path with the data URL
                            html_content = html_content.replace(f"{SERVER_URL}/{logo_path}", data_url)
                            html_content = html_content.replace(logo_path, data_url)
                            
                            # Write the updated HTML back to the file
                            with open(f"sites/{site_hash}.html", 'w', encoding='utf-8') as f:
                                f.write(html_content)
                                
                            logger.info("Logo image embedded directly in HTML as base64 data URL")
                        except Exception as e:
                            logger.error(f"Error embedding logo image: {str(e)}")
                    
                    # Wait longer at 90% to allow GitHub Pages to initialize (20 seconds)
                    await asyncio.sleep(20)
                    
                    # Update message to show we're still working
                    await context.bot.edit_message_text(
                        f"⏳ Setting up GitHub Pages for HTTPS access (90%)...\n"
                        f"This may take a moment to prepare secure hosting.",
                        chat_id=update.effective_chat.id,
                        message_id=status_msg.message_id
                    )
                    
                    # Upload the modified HTML to GitHub (without needing to handle image file separately)
                    github_result = github_uploader.upload_site(website_data["name"], html_content, site_hash)
                    
                    # If successful, use GitHub URLs
                    if github_result:
                        urls = {
                            "raw_url": github_result['raw_url'],           # Direct HTML download URL
                            "preview_url": github_result['preview_url'],   # Preview URL 
                            "repo_url": github_result['repo_url']          # GitHub repo URL
                        }
                        logger.info(f"Successfully uploaded to GitHub: {github_result['preview_url']}")
                        
                        # If image was uploaded successfully and has a URL, update the HTML
                        if 'image_url' in github_result and logo_path:
                            try:
                                # Update the HTML content with the GitHub Pages URL for the image
                                updated_html = html_content.replace(
                                    logo_path, 
                                    github_result['image_url']
                                )
                                
                                # Write the updated HTML back to the file
                                with open(f"sites/{site_hash}.html", 'w', encoding='utf-8') as f:
                                    f.write(updated_html)
                                    
                                # Update the GitHub repo with the new HTML
                                github_uploader._add_file(
                                    f"meme-site-{site_hash.lower()}", 
                                    "index.html", 
                                    updated_html, 
                                    "Update image URLs to GitHub Pages"
                                )
                                logger.info(f"Updated HTML with GitHub image URL: {github_result['image_url']}")
                            except Exception as img_err:
                                logger.error(f"Error updating image URL: {str(img_err)}")
                                # Continue with existing HTML if update fails
                    else:
                        # Fallback to local URLs
                        urls = result["data"]["urls"]
                except Exception as e:
                    logger.error(f"Error uploading to GitHub: {str(e)}")
                    urls = result["data"]["urls"]
            else:
                # Use local URLs
                urls = result["data"]["urls"]
            
            # Create a keyboard with the URLs
            keyboard = []
            
            # Add preview button only if using HTTPS
            preview_url = urls.get("preview_url", "")
            if preview_url and isinstance(preview_url, str) and preview_url.startswith("https://"):
                keyboard.append([InlineKeyboardButton(
                    "🌐 Preview Website", 
                    web_app=WebAppInfo(url=urls["preview_url"])
                )])
            
            # Add download button
            if "raw_url" in urls and urls["raw_url"]:
                keyboard.append([InlineKeyboardButton(
                    "⬇️ Download HTML", 
                    url=urls["raw_url"]
                )])
            
            # Add repository button
            if "repo_url" in urls and urls["repo_url"]:
                keyboard.append([InlineKeyboardButton(
                    "📁 View Repository", 
                    url=urls["repo_url"]
                )])
            
            # Add share button
            keyboard.append([InlineKeyboardButton(
                "📤 Share Website", 
                callback_data=f"share_{site_hash}"
            )])
            
            # Add create another button
            keyboard.append([InlineKeyboardButton(
                "🔄 Create Another Website", 
                callback_data="create_another"
            )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Message text - adjust based on whether HTTPS is available
            success_message = (
                f"✅ Your website has been generated!\n\n"
                f"I've created a complete *{website_data['template_type'].capitalize()}* website for *{website_data['name']}* with a *{website_data['theme']}* theme."
            )
            
            # Add HTTPS note if needed
            preview_url = urls.get("preview_url") or ""
            repo_url = urls.get("repo_url") or ""
            
            has_https = (preview_url.startswith("https://") if preview_url else False) or \
                      (repo_url.startswith("https://") if repo_url else False)
                
            if not has_https:
                success_message += (
                    "\n\n⚠️ **Note:** Direct preview in Telegram requires HTTPS. "
                    "You can download the HTML and host it on a secure site, or check server logs for instructions to enable HTTPS."
                )
            
            await context.bot.edit_message_text(
                success_message + "\n\nUse the buttons below to download or share your website:",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return {
                "success": True,
                "message": "Website generated successfully",
                "site_hash": site_hash,
                "urls": urls
            }
        else:
            await context.bot.edit_message_text(
                f"❌ Sorry, there was an error generating your website: {result['message']}",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            return {
                "success": False,
                "message": result["message"]
            }
            
    except Exception as e:
        logger.error(f"Error generating website: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

# Button callback handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    
    # Share website
    if query.data.startswith("share_"):
        site_hash = query.data.replace("share_", "")
        
        # Get the state manager to access URLs
        manager = get_or_create_state_manager(user_id)
        website_data = manager.get_website_data()
        
        if "urls" in website_data and website_data["urls"]:
            urls = website_data["urls"]
            share_text = f"✨ Check out my website: {urls.get('preview_url', '')}"
            
            await query.edit_message_text(
                f"Share this link with others:\n\n{share_text}",
                disable_web_page_preview=True
            )
        else:
            await query.edit_message_text("Website information not found.")
    
    # Create another website
    elif query.data == "create_another":
        await query.edit_message_text(
            "Let's create another website! Please tell me what you'd like to build.\n\n"
            "For example: \"Create a meme coin site for MoonElonDoge\" or \"Make an NFT collection page for Bored Pixel Punks\""
        )

# Main function
def main():
    """Run the bot."""
    if not BOT_TOKEN:
        logger.error("No bot token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("examples", examples_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Add photo handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()