import os
import hashlib
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from github_uploader import GitHubUploader

# Try to import remote hosting if available
try:
    from remote_hosting import get_uploader
    remote_uploader = get_uploader()
except ImportError:
    remote_uploader = None

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
USE_GITHUB = os.getenv('USE_GITHUB', 'false').lower() == 'true'
USE_REMOTE_HOSTING = os.getenv('USE_REMOTE_HOSTING', 'false').lower() == 'true'

# Initialize GitHub uploader if configured
github_uploader = GitHubUploader() if USE_GITHUB and os.getenv('GITHUB_TOKEN') else None

# Cache for storing pending user actions, user inputs, and GitHub URLs
user_state = {}
github_urls = {}

# Define website information collection states
STATES = {
    'WAITING_FOR_COIN_NAME': 'waiting_for_coin_name',
    'WAITING_FOR_SLOGAN': 'waiting_for_slogan',
    'WAITING_FOR_LOGO': 'waiting_for_logo',
    'WAITING_FOR_TELEGRAM': 'waiting_for_telegram',
    'WAITING_FOR_TWITTER': 'waiting_for_twitter',
    'WAITING_FOR_CONFIRMATION': 'waiting_for_confirmation',
    'READY_TO_GENERATE': 'ready_to_generate'
}

# Startup handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Determine if the user wants the guided or instant flow
    message_text = update.message.text.strip()
    parts = message_text.split()
    
    # Check if user requested instant mode
    if len(parts) > 1 and parts[0].lower() == '/start' and parts[1].lower() == 'instant':
        await update.message.reply_text(
            """🚀 *Instant Generation Mode* 🚀\n\nSimply send me:\n• Any text message to create a website with that name\n• An image with caption to create a website with custom logo\n\nNo additional questions - your website will be ready immediately!""",
            parse_mode='Markdown'
        )
        return
    
    # Check if user requested guided mode
    if len(parts) > 1 and parts[0].lower() == '/start' and parts[1].lower() == 'guided':
        await update.message.reply_text(
            """Let's create a professional landing page for your meme coin!\n\nFirst, what's the name of your meme coin?"""
        )
        # Initialize user's state with empty website data
        user_state[update.effective_user.id] = {
            'waiting_for': STATES['WAITING_FOR_COIN_NAME'],
            'website_data': {
                'coin_name': None,
                'slogan': None,
                'logo_url': None,  # Will store file_id of uploaded image
                'telegram': None,
                'twitter': None
            }
        }
        return
    
    # Check if user requested menu
    if len(parts) > 1 and parts[0].lower() == '/start' and parts[1].lower() == 'menu':
        # Main menu keyboard
        keyboard = [
            [InlineKeyboardButton("🚀 Quick Creation", callback_data="generate_new")],
            [InlineKeyboardButton("⚙️ Guided Creation", callback_data="mode_guided")],
            [InlineKeyboardButton("📝 See Examples", callback_data="show_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            """🪙 *MemeCoin Website Generator* 🪙\n\nWhat would you like to do? Choose an option below:""",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Default welcome message with mode selection
    keyboard = [
        [InlineKeyboardButton("⚡ Instant (1-step)", callback_data="mode_instant")],
        [InlineKeyboardButton("🧙‍♂️ Guided (multi-step)", callback_data="mode_guided")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        """✨ *Welcome to MemeCoin Website Generator* ✨\n\nCreate professional memecoin websites in seconds!\n\n🔹 *Quick Start:*\n• Simply send the name of your coin\n• Or send an image + caption for a site with your logo\n\n🔹 *Available Commands:*\n• /start - Show this message\n• /menu - Show the main menu\n• /examples - See what you can create\n• /help - View detailed help\n\nChoose a creation mode below:""",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Help handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """🪙 *MemeCoin Website Generator* 🪙\n\n*Commands:*\n• /start - Choose instant or guided mode\n• /start instant - Use instant generation mode\n• /start guided - Use detailed step-by-step mode\n• /menu - Show the main menu options\n• /help - Show this help message\n\n*Instant Website Creation:*\n• Send any text message to generate a website with that name\n• Send an image with caption for a website with custom logo\n\n*Advanced Features:*\nUse guided mode for full customization including social links, slogans, and more!""",
        parse_mode='Markdown'
    )

# Menu command handler
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Main menu keyboard
    keyboard = [
        [InlineKeyboardButton("🚀 Quick Creation", callback_data="generate_new")],
        [InlineKeyboardButton("⚙️ Guided Creation", callback_data="mode_guided")],
        [InlineKeyboardButton("📝 See Examples", callback_data="show_examples")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        """🪙 *MemeCoin Website Generator* 🪙\n\nWhat would you like to do? Choose an option below:""",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Handler for text input - multi-step form
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Check if user wants instant generation
    if text.lower().startswith(('/instant', 'instant')):
        # Extract the coin name after the command
        parts = text.split(None, 1)
        if len(parts) > 1:
            coin_name = parts[1].strip()
        else:
            # No name provided
            coin_name = f"Meme{random.randint(1000, 9999)}"
        
        # Show loading message
        await update.message.reply_text(f"🪙 Creating a website for \"{coin_name}\"...")
        status_msg = await update.message.reply_text("⌛ Generating your website...")
        
        try:
            # Prepare website data
            website_data = {
                'coin_name': coin_name,
                'social_links': {}
            }
            
            # Update initial status
            await asyncio.sleep(2.0)  # Initial delay
            await context.bot.edit_message_text(
                "⏳ Generating your website (25%)...",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            # Generate the website
            site_hash = await generate_website(coin_name, website_data)
            
            # Update status - starting deployment
            await asyncio.sleep(5.0)  # Wait after HTML generation
            await context.bot.edit_message_text(
                "⏳ Preparing deployment environment (50%)...",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            # Add a delay for GitHub setup
            if USE_GITHUB and github_uploader:
                await asyncio.sleep(15.0)  # Longer wait for GitHub setup
                await context.bot.edit_message_text(
                    "⏳ Setting up repository and GitHub Pages (75%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
                
                # Add another delay for GitHub Pages configuration
                await asyncio.sleep(20.0)
                await context.bot.edit_message_text(
                    "⏳ Publishing website to secure hosting (90%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
            else:
                # Shorter wait if not using GitHub
                await asyncio.sleep(3.0)
                await context.bot.edit_message_text(
                    "⏳ Finalizing your website (75%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
            
            # Get URLs for the website
            site_url = f"{SERVER_URL}/sites/{site_hash}.html"
            
            # Check if GitHub is available and the site was uploaded
            has_github = False
            if site_hash in github_urls and github_urls[site_hash]:
                # For GitHub hosting
                raw_url = github_urls[site_hash]['raw_url']
                repo_url = github_urls[site_hash]['repo_url']
                preview_url = github_urls[site_hash]['preview_url']
                site_url = preview_url
                has_github = True
            
            # Create keyboard
            keyboard = []
            if has_github:
                keyboard.append([InlineKeyboardButton("🌐 View Website", web_app=WebAppInfo(url=site_url))])
                keyboard.append([InlineKeyboardButton("⬇️ Download HTML", url=raw_url)])
                keyboard.append([InlineKeyboardButton("📁 View Repository", url=repo_url)])
            else:
                keyboard.append([InlineKeyboardButton("⬇️ Download Website", url=site_url)])
            
            keyboard.append([InlineKeyboardButton("🔄 Create Another", callback_data="generate_another")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send success message
            await context.bot.edit_message_text(
                f"""✅ Website for *{coin_name}* is ready!\n\n""" 
                f"""Your professionally designed meme coin website has been created!\n""" 
                f"""fUse the buttons below to view or download it:\n\n""" 
                f"💡 Tip: Send an image with caption to include your logo!",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            # Show main menu after a short delay
            await asyncio.sleep(1)
            await show_main_menu(update, context, f"""🎉 Website for *{coin_name}* created successfully\!\n\nWhat would you like to do next? Choose an option below:""")
            
        except Exception as e:
            logger.error(f"Error in instant website generation: {e}")
            await context.bot.edit_message_text(
                f"""f❌ Sorry, there was an error creating your website: {str(e)}\n\nPlease try again or use /start for guided setup.""",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
        return
        
    # Check if user is in our state dictionary (normal flow)
    if user_id not in user_state:
        # For simplicity, let's make any text input create a website instantly
        # if the user is not already in the guided flow
        coin_name = text.strip()
        
        # Show loading message
        await update.message.reply_text(f"🪙 Creating a website for \"{coin_name}\"...")
        status_msg = await update.message.reply_text("⌛ Generating your website...")
        
        try:
            # Prepare website data
            website_data = {
                'coin_name': coin_name,
                'social_links': {}
            }
            
            # Update initial status
            await asyncio.sleep(2.0)  # Initial delay
            await context.bot.edit_message_text(
                "⏳ Generating your website (25%)...",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            # Generate the website
            site_hash = await generate_website(coin_name, website_data)
            
            # Update status - starting deployment
            await asyncio.sleep(5.0)  # Wait after HTML generation
            await context.bot.edit_message_text(
                "⏳ Preparing deployment environment (50%)...",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            # Add a delay for GitHub setup
            if USE_GITHUB and github_uploader:
                await asyncio.sleep(15.0)  # Longer wait for GitHub setup
                await context.bot.edit_message_text(
                    "⏳ Setting up repository and GitHub Pages (75%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
                
                # Add another delay for GitHub Pages configuration
                await asyncio.sleep(20.0)
                await context.bot.edit_message_text(
                    "⏳ Publishing website to secure hosting (90%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
            else:
                # Shorter wait if not using GitHub
                await asyncio.sleep(3.0)
                await context.bot.edit_message_text(
                    "⏳ Finalizing your website (75%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
            
            # Get URLs for the website
            site_url = f"{SERVER_URL}/sites/{site_hash}.html"
            
            # Check if GitHub is available and the site was uploaded
            has_github = False
            if site_hash in github_urls and github_urls[site_hash]:
                # For GitHub hosting
                raw_url = github_urls[site_hash]['raw_url']
                repo_url = github_urls[site_hash]['repo_url']
                preview_url = github_urls[site_hash]['preview_url']
                site_url = preview_url
                has_github = True
            
            # Create keyboard
            keyboard = []
            if has_github:
                keyboard.append([InlineKeyboardButton("🌐 View Website", web_app=WebAppInfo(url=site_url))])
                keyboard.append([InlineKeyboardButton("⬇️ Download HTML", url=raw_url)])
                keyboard.append([InlineKeyboardButton("📁 View Repository", url=repo_url)])
            else:
                keyboard.append([InlineKeyboardButton("⬇️ Download Website", url=site_url)])
            
            keyboard.append([InlineKeyboardButton("🔄 Create Another", callback_data="generate_another")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send success message
            await context.bot.edit_message_text(
                f"""✅ Website for *{coin_name}* is ready!\n\n""" 
                f"""Your professionally designed meme coin website has been created!\n""" 
                f"""fUse the buttons below to view or download it:\n\n""" 
                f"💡 Tip: Send an image with caption to include your logo!",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            # Show main menu after a short delay
            await asyncio.sleep(1)
            await show_main_menu(update, context, f"""🎉 Website for *{coin_name}* created successfully\!\n\nWhat would you like to do next? Choose an option below:""")
            
        except Exception as e:
            logger.error(f"Error in instant website generation: {e}")
            await context.bot.edit_message_text(
                f"""f❌ Sorry, there was an error creating your website: {str(e)}\n\nPlease try again or use /start for guided setup.""",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
        return
        
        # Initialize user if not found - original guided flow
        # This path is now only accessible from /start
        user_state[user_id] = {
            'waiting_for': STATES['WAITING_FOR_COIN_NAME'],
            'website_data': {
                'coin_name': None,
                'slogan': None,
                'telegram': None,
                'twitter': None,
                'website': None
            }
        }
    
    # Get the current state
    current_state = user_state[user_id].get('waiting_for')
    
    # Handle different states
    if current_state == STATES['WAITING_FOR_COIN_NAME']:
        # Coin name received, store it
        user_state[user_id]['website_data']['coin_name'] = text
        # Ask for slogan
        await update.message.reply_text(
            f"""Great! Your coin is named *{text}*.\n\n"""
            f"Now, enter a catchy slogan for your coin (or type 'skip' to use a random one):",
            parse_mode='Markdown'
        )
        user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_SLOGAN']
    
    # First WAITING_FOR_SLOGAN handler removed - logo step was being skipped
    
    elif current_state == STATES['WAITING_FOR_TELEGRAM']:
        # Telegram link received, store it
        if text.lower() != 'skip':
            # Add https:// if missing
            if not text.startswith(('http://', 'https://')):
                text = 'https://' + text
            user_state[user_id]['website_data']['telegram'] = text
        # Ask for Twitter link
        await update.message.reply_text(
            "Next, enter your Twitter profile link (or type 'skip'):"
        )
        user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_TWITTER']
    
    elif current_state == STATES['WAITING_FOR_SLOGAN']:
        # Slogan received, store it
        if text.lower() != 'skip':
            user_state[user_id]['website_data']['slogan'] = text
        # Ask for logo
        await update.message.reply_text(
            """Now, send me a logo image for your coin or type 'skip' to use a generated symbol.\n\nThe logo will be displayed prominently on your website."""
        )
        user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_LOGO']
    
    elif current_state == STATES['WAITING_FOR_LOGO']:
        # Handle text input for logo (skip option)
        if text.lower() == 'skip':
            # Continue to next step without setting logo
            await update.message.reply_text(
                "Now, enter your Telegram group link (or type 'skip'):"
            )
            user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_TELEGRAM']
        else:
            # Tell the user we need an image
            await update.message.reply_text(
                "Please send an image file for your logo, or type 'skip' to use a generated symbol."
            )
    
    elif current_state == STATES['WAITING_FOR_TELEGRAM']:
        # Telegram link received, store it
        if text.lower() != 'skip':
            # Add https:// if missing
            if not text.startswith(('http://', 'https://')):
                text = 'https://' + text
            user_state[user_id]['website_data']['telegram'] = text
        # Ask for Twitter link
        await update.message.reply_text(
            "Finally, enter your Twitter profile link (or type 'skip'):"
        )
        user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_TWITTER']
    
    elif current_state == STATES['WAITING_FOR_TWITTER']:
        # Twitter link received, store it
        if text.lower() != 'skip':
            # Add https:// if missing
            if not text.startswith(('http://', 'https://')):
                text = 'https://' + text
            user_state[user_id]['website_data']['twitter'] = text
        
        # Show confirmation with all data
        coin_name = user_state[user_id]['website_data']['coin_name']
        slogan = user_state[user_id]['website_data']['slogan'] or "[Random slogan will be generated]"
        logo_status = "Custom logo uploaded" if user_state[user_id]['website_data']['logo_url'] else "[Generated symbol will be used]"
        telegram = user_state[user_id]['website_data']['telegram'] or "[None]"
        twitter = user_state[user_id]['website_data']['twitter'] or "[None]"
        
        # Create confirmation keyboard
        keyboard = [
            [InlineKeyboardButton("✅ Generate Website", callback_data="confirm_generation")],
            [InlineKeyboardButton("🔄 Start Over", callback_data="start_over")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"""f📋 *Website Information Summary*\n\n"""
            f"""f*Coin Name:* {coin_name}\n"""
            f"""f*Slogan:* {slogan}\n"""
            f"""f*Logo:* {logo_status}\n"""
            f"""f*Telegram:* {telegram}\n"""
            f"""f*Twitter:* {twitter}\n\n"""
            f"Ready to generate your website? Click 'Generate Website' below or 'Start Over' to change your information.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_CONFIRMATION']
    
    elif current_state == STATES['READY_TO_GENERATE']:
        # Start website generation process
        coin_name = user_state[user_id]['website_data']['coin_name']
        
        # Initial processing message with progress bar
        progress_chars = "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜"
        processing_msg = await update.message.reply_text(
            f"""f🚀 Generating website for *{coin_name}*...\n\n"""
            f"Progress: {progress_chars} 0%",
            parse_mode='Markdown'
        )
        
        # Generate website with progress updates
        try:
            # Update progress to 10%
            await asyncio.sleep(0.5)
            progress_chars = "🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜"
            await context.bot.edit_message_text(
                f"""f🚀 Generating website for *{coin_name}*...\n\n"""
                f"""fProgress: {progress_chars} 10%\n"""
                f"_Generating content..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # At this point, start the actual website generation with custom data
            site_hash = await generate_website(
                coin_name, 
                user_state[user_id]['website_data']
            )
            
            # Update progress to 30%
            await asyncio.sleep(0.5)
            progress_chars = "🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜"
            await context.bot.edit_message_text(
                f"""f🚀 Generating website for *{coin_name}*...\n\n"""
                f"""fProgress: {progress_chars} 30%\n"""
                f"_Building HTML template..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Update progress to 50%
            await asyncio.sleep(0.5)
            progress_chars = "🟩🟩🟩🟩🟩⬜⬜⬜⬜⬜"
            await context.bot.edit_message_text(
                f"""f🚀 Generating website for *{coin_name}*...\n\n"""
                f"""fProgress: {progress_chars} 50%\n"""
                f"_Setting up repository..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Get a URL that works with Telegram WebApps (must be HTTPS)
            if site_hash in github_urls and github_urls[site_hash]:
                # For GitHub hosting, use the preview URL for WebApp preview
                raw_url = github_urls[site_hash]['raw_url']        # Direct HTML download - HTTPS
                repo_url = github_urls[site_hash]['repo_url']      # GitHub repo URL - HTTPS
                preview_url = github_urls[site_hash]['preview_url'] # HTML preview URL - HTTPS
                site_url = preview_url                             # Use preview URL for WebApp preview
                hosting_type = "private GitHub repository"
                has_github = True
                
                # Check if we have an image_url from GitHub
                if 'image_url' in github_urls[site_hash]:
                    image_url = github_urls[site_hash]['image_url']
                    logger.info(f"GitHub image URL: {image_url}")
            else:
                # For local server without GitHub (fallback)
                site_url = f"{SERVER_URL}/sites/{site_hash}.html"
                raw_url = site_url
                repo_url = None
                preview_url = None
                hosting_type = "local server"
                has_github = False
            
            # Update progress to 50%
            await asyncio.sleep(3.0)  # Wait longer after HTML generation
            progress_chars = "🟩🟩🟩🟩🟩⬜⬜⬜⬜⬜"
            await context.bot.edit_message_text(
                f"""🚀 Generating website for *{coin_name}*...\n\n"""
                f"""Progress: {progress_chars} 50%\n"""
                f"_Setting up GitHub repository..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Add a longer delay to create suspense
            await asyncio.sleep(8.0)  # Wait 8 seconds for GitHub repo setup
            
            # Update progress to 70%
            progress_chars = "🟩🟩🟩🟩🟩🟩🟩⬜⬜⬜"
            await context.bot.edit_message_text(
                f"""🚀 Generating website for *{coin_name}*...\n\n"""
                f"""Progress: {progress_chars} 70%\n"""
                f"_Configuring GitHub Pages..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Add another long delay for GitHub Pages configuration
            await asyncio.sleep(20.0)  # Wait 20 seconds for GitHub Pages setup
            
            # Update progress to 85%
            progress_chars = "🟩🟩🟩🟩🟩🟩🟩🟩🟩⬜"
            await context.bot.edit_message_text(
                f"""🚀 Generating website for *{coin_name}*...\n\n"""
                f"""Progress: {progress_chars} 85%\n"""
                f"_Finalizing deployment..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Add another delay to allow GitHub Pages to initialize
            await asyncio.sleep(25.0)  # Wait 25 seconds for deployment finalization
            
            # Update progress to 95%
            progress_chars = "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"
            await context.bot.edit_message_text(
                f"""🚀 Website for *{coin_name}* is almost ready!\n\n"""
                f"""Progress: {progress_chars} 95%\n"""
                f"_Finishing deployment and verifying..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Final verification delay
            await asyncio.sleep(10.0)
            
            # Complete the progress bar
            progress_chars = "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"
            await context.bot.edit_message_text(
                f"""🎉 Website for *{coin_name}* is ready!\n\n"""
                f"""Progress: {progress_chars} 100%\n"""
                f"_Preparing your options..._",
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                parse_mode='Markdown'
            )
            
            # Add a short delay before showing results
            await asyncio.sleep(2.0)
            
            # Create inline keyboard with all options
            keyboard = []
            
            # For Telegram WebApp preview (must be HTTPS)
            if has_github:
                # Use raw GitHub URL - it's guaranteed to work with HTTPS
                keyboard.append([InlineKeyboardButton("🌐 Preview Your MemeCoin Site", web_app=WebAppInfo(url=site_url))])
                keyboard.append([InlineKeyboardButton("⬇️ Download HTML File", url=raw_url)])
            else:
                # Use default message for local server (won't work in Telegram but kept for info)
                keyboard.append([InlineKeyboardButton("⚠️ Preview Requires HTTPS Server", callback_data="https_required")])
                # Still provide download button even without GitHub
                keyboard.append([InlineKeyboardButton("⬇️ Download HTML File", url=raw_url)])
            
            # Add GitHub-related buttons if available
            if has_github:
                keyboard.append([InlineKeyboardButton("🌎 View on GitHub Pages", url=preview_url)])
                keyboard.append([InlineKeyboardButton("📁 View on GitHub (1hr)", url=repo_url)])
            
            # Add standard buttons
            keyboard.append([InlineKeyboardButton("🔄 Generate Another", callback_data="generate_another")])
            keyboard.append([InlineKeyboardButton("📤 Share This Site", callback_data=f"share_{site_hash}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Delete progress message and send final response
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
            
            # Create a more informative message
            if has_github:
                message = (
                    f"""✅ Your *{coin_name}* website is ready!\n\n"""
                    f"""f• Preview site directly in Telegram\n"""
                    f"""f• Download the HTML file\n"""
                    f"""f• View the GitHub repository (auto-deletes in 1 hour)\n"""
                    f"• View on GitHub Pages (fully rendered)"
                )
            else:
                message = (
                    f"""✅ Your *{coin_name}* website is ready!\n\n"""
                    f"""f• Preview site directly in Telegram\n"""
                    f"• Download the HTML file"
                )
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Reset state
            user_state[user_id] = {'last_site': site_hash}
            
        except Exception as e:
            logger.error(f"Error generating website: {e}")
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
            await update.message.reply_text("❌ Sorry, there was an error generating your website. Please try again.")
    
    else:
        # If we're not in any recognized state, restart the conversation
        await update.message.reply_text(
            "Let's start over! What's the name of your meme coin?"
        )
        user_state[user_id] = {
            'waiting_for': STATES['WAITING_FOR_COIN_NAME'],
            'website_data': {
                'coin_name': None,
                'slogan': None,
                'logo_url': None,
                'telegram': None,
                'twitter': None
            }
        }

# Button callback handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Handle mode selection
    if query.data == "mode_instant" or query.data == "generate_new":
        await query.edit_message_text(
            """🚀 *Instant Mode Selected* 🚀\n\nSimply send me:\n• Any text message to create a website with that name\n• An image with caption to create a website with custom logo\n\nYour website will be generated immediately!""",
            parse_mode='Markdown'
        )
    
    elif query.data == "mode_guided":
        await query.edit_message_text(
            """Let's create a professional landing page for your meme coin!\n\nFirst, what's the name of your meme coin?"""
        )
        # Initialize user's state with empty website data
        user_state[user_id] = {
            'waiting_for': STATES['WAITING_FOR_COIN_NAME'],
            'website_data': {
                'coin_name': None,
                'slogan': None,
                'logo_url': None,  # Will store file_id of uploaded image
                'telegram': None,
                'twitter': None
            }
        }
    
    elif query.data == "generate_another":
        # Main menu keyboard
        keyboard = [
            [InlineKeyboardButton("🚀 Quick Creation", callback_data="generate_new")],
            [InlineKeyboardButton("⚙️ Guided Creation", callback_data="mode_guided")],
            [InlineKeyboardButton("📝 See Examples", callback_data="show_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """🪙 *What would you like to create next?* 🪙\n\nChoose a creation mode below:""",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "https_required":
        await query.answer("Telegram requires HTTPS URLs for WebApps. Your site is saved locally.")
        
    elif query.data == "show_examples":
        # Show examples directly in the current message
        example_text = """📌 *Website Creation Examples* 📌\n\nJust send one of these to get started immediately:\n\n• Send *text message*: "CosmoToken"\n  ➡️ Creates a basic website for your coin\n\n• Send *image with caption*: "MoonDoge"\n  ➡️ Creates website with your logo and name\n\nOr use these commands for more options:\n\n• */start instant* - Quick website creation\n• */start guided* - Step-by-step customization\n\n👉 Try it right now! Send a coin name or image to create your website."""
        
        # Add a back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            example_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "back_to_menu":
        # Show the main menu again
        keyboard = [
            [InlineKeyboardButton("🚀 Quick Creation", callback_data="generate_new")],
            [InlineKeyboardButton("⚙️ Guided Creation", callback_data="mode_guided")],
            [InlineKeyboardButton("📝 See Examples", callback_data="show_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            """🪙 *MemeCoin Website Generator* 🪙\n\nWhat would you like to do? Choose an option below:""",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "confirm_generation":
        # Set state to generate website
        user_state[user_id]['waiting_for'] = STATES['READY_TO_GENERATE']
        await query.edit_message_text("Great! I'll start generating your website now. Send any message to continue.")
    
    elif query.data == "start_over":
        await query.edit_message_text("Let's start over. Send me the name of your meme coin!")
        user_state[user_id] = {
            'waiting_for': STATES['WAITING_FOR_COIN_NAME'],
            'website_data': {
                'coin_name': None,
                'slogan': None,
                'logo_url': None,
                'telegram': None,
                'twitter': None
            }
        }
        
    elif query.data.startswith("share_"):
        site_hash = query.data.split("_")[1]
        
        # Get the appropriate URLs based on where it's hosted
        if site_hash in github_urls and github_urls[site_hash]:
            raw_url = github_urls[site_hash]['raw_url']
            repo_url = github_urls[site_hash]['repo_url']
            preview_url = github_urls[site_hash]['preview_url']
            
            share_text = (
                f"""f✨ Check out this meme coin website I created! ✨\n\n"""
                f"""f👇 Direct links:\n"""
                f"""f🌎 GitHub Pages: {preview_url} (may take 1-2 minutes to activate)\n"""
                f"""f📄 HTML File: {raw_url}\n"""
                f"📁 GitHub Repo: {repo_url} (temporary - expires in 1 hour)"
            )
        else:
            site_url = f"{SERVER_URL}/sites/{site_hash}.html"
            share_text = f"""f✨ Check out this meme coin website I created! ✨\n\n📄 Link: {site_url}"""
        
        await query.edit_message_text(
            f"""f💬 Share these links with your friends:\n\n{share_text}""",
            disable_web_page_preview=True
        )

# Function to generate website
async def generate_website(coin_name, website_data=None):
    # Create a unique hash for this website
    site_hash = hashlib.md5(f"{coin_name}_{os.urandom(8)}".encode()).hexdigest()[:10]
    
    # Prepare request data
    request_data = {
        "coin_name": coin_name,
        "site_hash": site_hash
    }
    
    # Add custom data if provided
    if website_data:
        # Add custom slogan if provided
        if website_data.get('slogan'):
            request_data["slogan"] = website_data['slogan']
        
        # Add social links if provided
        social_links = {}
        if website_data.get('telegram'):
            social_links["telegram"] = website_data['telegram']
        if website_data.get('twitter'):
            social_links["twitter"] = website_data['twitter']
        if website_data.get('website'):
            social_links["website"] = website_data['website']
        
        if social_links:
            request_data["social_links"] = social_links
        
        # Add logo URL if provided
        if website_data.get('logo_url'):
            # Get the local file path
            local_path = website_data['logo_url']
            if local_path.startswith('uploads/') and os.path.exists(local_path):
                try:
                    # Read the image file as binary data
                    with open(local_path, 'rb') as img_file:
                        image_data = img_file.read()
                    
                    # Determine the MIME type based on file extension
                    import mimetypes
                    mime_type = mimetypes.guess_type(local_path)[0] or 'image/jpeg'
                    
                    # Create base64 data URL
                    import base64
                    b64_image = base64.b64encode(image_data).decode('utf-8')
                    data_url = f"data:{mime_type};base64,{b64_image}"
                    
                    # Use the data URL instead of a server URL
                    request_data["logo_url"] = data_url
                    logger.info(f"Embedded logo as base64 data URL")
                except Exception as e:
                    logger.error(f"Error embedding image: {e}")
                    # Fallback to regular URL if encoding fails
                    request_data["logo_url"] = f"{SERVER_URL}/{local_path}"
    
    # Make request to our Flask server to generate the site
    try:
        response = requests.post(
            f"{SERVER_URL}/generate",
            json=request_data,
            timeout=10
        )
        response.raise_for_status()
        
        # If using GitHub, upload the generated HTML to private repo
        if USE_GITHUB and github_uploader:
            try:
                # Get the HTML content from the generated file
                with open(f"sites/{site_hash}.html", 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Images are already embedded as base64 in the HTML content
                # Simply upload to GitHub
                github_result = github_uploader.upload_site(coin_name, html_content, site_hash)
                if github_result:
                    logger.info(f"Successfully uploaded to private GitHub repository: {github_result['repo_url']}")
                    # Store the GitHub URLs with the site hash
                    github_urls[site_hash] = github_result
            except Exception as github_error:
                logger.error(f"Error uploading to GitHub: {github_error}")
                # Continue with local hosting if GitHub upload fails
        
        # If using remote hosting (Netlify, Vercel, Firebase), upload there for HTTPS URL
        if USE_REMOTE_HOSTING and remote_uploader:
            try:
                # Get the HTML content from the generated file
                with open(f"sites/{site_hash}.html", 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Upload to remote hosting and get the HTTPS URL
                hosting_url = remote_uploader.upload_site(coin_name, html_content, site_hash)
                if hosting_url:
                    logger.info(f"Successfully uploaded to remote hosting: {hosting_url}")
                    # Store the hosting URL with the site hash - will override the GitHub URL
                    github_urls[site_hash] = hosting_url
            except Exception as hosting_error:
                logger.error(f"Error uploading to remote hosting: {hosting_error}")
                # Continue with local hosting if remote hosting fails
        
        return site_hash
    except Exception as e:
        logger.error(f"Error calling generation API: {e}")
        raise

# Error handler
async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")

# Photo handler for logo uploads (now with instant generation option)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if the user is in the logo upload state (normal flow)
    if user_id in user_state and user_state[user_id].get('waiting_for') == STATES['WAITING_FOR_LOGO']:
        # Get the largest photo (best quality)
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Store the file_id in the user's state
        user_state[user_id]['website_data']['logo_url'] = file_id
        
        # Get the file for later download
        file = await context.bot.get_file(file_id)
        
        # Download the file to save it locally for processing
        try:
            # Get file extension from mime type or default to jpg
            file_extension = 'jpg'
            if hasattr(update.message, 'photo') and update.message.photo:
                # Create directory if it doesn't exist
                os.makedirs('uploads', exist_ok=True)
                
                # Download the file locally
                local_file_path = f"uploads/{file_id}.{file_extension}"
                await file.download_to_drive(local_file_path)
                logger.info(f"Downloaded logo to {local_file_path}")
                
                # Store the local path instead of just the file ID
                user_state[user_id]['website_data']['logo_url'] = local_file_path
        except Exception as e:
            logger.error(f"Error downloading logo: {e}")
            # Continue with just the file ID if download fails
        
        # Acknowledge and move to next step
        await update.message.reply_text(
            "✅ Logo received! Now, enter your Telegram group link (or type 'skip'):"
        )
        user_state[user_id]['waiting_for'] = STATES['WAITING_FOR_TELEGRAM']
    else:
        # --- Instant Website Generation Flow ---
        # If not in normal flow, treat this as an instant website generation request
        # Get the caption text or create a default name
        caption = update.message.caption
        
        if not caption:
            # No caption, generate a random name
            coin_name = f"Meme{random.randint(1000, 9999)}"
            await update.message.reply_text(
                f"🪙 Creating a website for \"{coin_name}\"""... \n\n""" 
                f"💡 Tip: Next time, add a caption with the coin name for better results!"
            )
        else:
            # Use the caption as the coin name
            coin_name = caption
            await update.message.reply_text(f"🪙 Creating a website for \"{coin_name}\"...")
        
        # Show loading message
        status_msg = await update.message.reply_text("⌛ Processing your image and generating website...")
        
        try:
            # Get the largest photo (best quality)
            photo = update.message.photo[-1]
            file_id = photo.file_id
            
            # Get the file for download
            file = await context.bot.get_file(file_id)
            
            # Create uploads directory if needed
            os.makedirs('uploads', exist_ok=True)
            
            # Download the file locally
            local_file_path = f"uploads/{file_id}.jpg"
            await file.download_to_drive(local_file_path)
            logger.info(f"Downloaded image to {local_file_path}")
            
            # Prepare website data
            website_data = {
                'coin_name': coin_name,
                'logo_url': local_file_path,
                'social_links': {}
            }
            
            # Update status after image processing
            await asyncio.sleep(3.0)  # Wait for image processing
            await context.bot.edit_message_text(
                "⏳ Processing image and preparing website (25%)...",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            # Generate the website
            site_hash = await generate_website(coin_name, website_data)
            
            # Update status - starting deployment
            await asyncio.sleep(7.0)  # Longer wait after HTML generation with image
            await context.bot.edit_message_text(
                "⏳ Optimizing image and preparing deployment (50%)...",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )
            
            # Add extended delays for GitHub setup
            if USE_GITHUB and github_uploader:
                await asyncio.sleep(15.0)  # Longer wait for GitHub setup
                await context.bot.edit_message_text(
                    "⏳ Setting up secure repository and configuring Pages (75%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
                
                # Add another delay for GitHub Pages configuration
                await asyncio.sleep(20.0)
                await context.bot.edit_message_text(
                    "⏳ Publishing website with image to secure hosting (90%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
            else:
                # Shorter wait if not using GitHub
                await asyncio.sleep(5.0)
                await context.bot.edit_message_text(
                    "⏳ Finalizing your website with logo (75%)...",
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id
                )
            
            # Get URLs for the website
            site_url = f"{SERVER_URL}/sites/{site_hash}.html"
            
            # Check if GitHub is available and the site was uploaded
            has_github = False
            if site_hash in github_urls and github_urls[site_hash]:
                # For GitHub hosting
                raw_url = github_urls[site_hash]['raw_url']
                repo_url = github_urls[site_hash]['repo_url']
                preview_url = github_urls[site_hash]['preview_url']
                site_url = preview_url
                has_github = True
            
            # Create keyboard
            keyboard = []
            if has_github:
                keyboard.append([InlineKeyboardButton("🌐 View Website", web_app=WebAppInfo(url=site_url))])
                keyboard.append([InlineKeyboardButton("⬇️ Download HTML", url=raw_url)])
                keyboard.append([InlineKeyboardButton("📁 View Repository", url=repo_url)])
            else:
                keyboard.append([InlineKeyboardButton("⬇️ Download Website", url=site_url)])
            
            keyboard.append([InlineKeyboardButton("🔄 Create Another", callback_data="generate_another")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send success message
            await context.bot.edit_message_text(
                f"""✅ Website for *{coin_name}* is ready!\n\n""" 
                f"""Your professionally designed meme coin website has been created with your logo!\n""" 
                f"Use the buttons below to view or download it:",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            # Show main menu after a short delay
            await asyncio.sleep(1)
            await show_main_menu(update, context, f"""🎉 Website for *{coin_name}* created successfully\!\n\nWhat would you like to do next? Choose an option below:""")
            
        except Exception as e:
            logger.error(f"Error in instant website generation: {e}")
            await context.bot.edit_message_text(
                f"""f❌ Sorry, there was an error creating your website: {str(e)}\n\nPlease try again or use /start for guided setup.""",
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id
            )

# Examples command handler
async def examples_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send examples with images to illustrate the options
    text = """📌 *Website Creation Examples* 📌

Just send one of these to get started immediately:

• Send *text message*: "CosmoToken"
  ➡️ Creates a basic website for your coin

• Send *image with caption*: "MoonDoge"
  ➡️ Creates website with your logo and name

Or use these commands for more options:

• */start instant* - Quick website creation
• */start guided* - Step-by-step customization

👉 Try it right now! Send a coin name or image to create your website."""
    
    
    # Send message with examples
    message = await update.message.reply_text(
        text,
        parse_mode='Markdown'
    )
    
    # Send an image showing the resulting website (future improvement)
    # This would be a good place to add a sample image of a generated website
    # but we'll leave this for a future enhancement

# Show main menu options
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text=None):
    """
    Shows the main menu options after successful website generation
    """
    # Create main menu keyboard
    keyboard = [
        [InlineKeyboardButton("🚀 Create New Website", callback_data="generate_new")],
        [InlineKeyboardButton("⚙️ Guided Creation", callback_data="mode_guided")],
        [InlineKeyboardButton("📝 See Examples", callback_data="show_examples")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Use default text if none provided
    if not text:
        text = """🤖 *What would you like to do next?*

You can create another website or try a different creation mode!""" 
    
    # Send the menu
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Main function
def main():
    if not BOT_TOKEN:
        logger.error("No bot token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))  # Add menu command
    application.add_handler(CommandHandler("examples", examples_command))  # Add examples command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Add photo handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
