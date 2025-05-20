"""
Telegram Bot for Website Creator with Enhanced Customization Flow

This module implements a Telegram bot that guides users through the comprehensive
website customization flow using the state management system.
"""

import os
import logging
import asyncio
import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from customization_states import STATES, CustomizationStateManager
from customization_flow import (
    get_or_create_state_manager, get_templates, get_themes, handle_template_selection,
    handle_coin_name, handle_slogan, handle_description, handle_logo, handle_theme,
    handle_color_scheme, handle_social_link, handle_tokenomics, handle_roadmap, 
    handle_sections_order, handle_confirmation, handle_edit_choice, generate_website, reset_state
)

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

# Startup handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the customization flow."""
    # Reset user state to begin fresh
    user_id = str(update.effective_user.id)
    reset_result = reset_state(user_id)
    
    # Get the state manager and ensure it's in the right state
    manager = get_or_create_state_manager(user_id)
    
    # Make sure we're in the IDLE state first
    if manager.get_current_state() != STATES['IDLE']:
        manager.reset()  # Force reset if needed
    
    # Transition to template selection state
    manager.transition_to(STATES['WAITING_FOR_TEMPLATE_SELECTION'])
    
    # Get available templates
    templates = get_templates()
    
    # Create inline keyboard with template options
    keyboard = []
    for template in templates:
        keyboard.append([InlineKeyboardButton(
            template["name"], 
            callback_data=f"template_{template['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to Website Creator! 🚀\n\n"
        "Let's create your custom website. First, please select a template:",
        reply_markup=reply_markup
    )

# Help handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    await update.message.reply_text(
        "🌐 *Website Creator Bot* 🌐\n\n"
        "*Commands:*\n"
        "/start - Start the customization flow\n"
        "/help - Show this help message\n"
        "/reset - Reset your current progress\n\n"
        "This bot will guide you through creating a custom website with your own branding, content, and style.",
        parse_mode='Markdown'
    )

# Reset handler
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset the customization flow."""
    user_id = str(update.effective_user.id)
    reset_result = reset_state(user_id)
    
    await update.message.reply_text(
        "Your customization progress has been reset. Send /start to begin again."
    )

# Handler for text input - multi-step form
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for the customization flow."""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # Get the current state manager
    manager = get_or_create_state_manager(user_id)
    current_state = manager.get_current_state()
    
    # Handle each state
    if current_state == STATES['WAITING_FOR_COIN_NAME']:
        result = handle_coin_name(user_id, text)
        if result["success"]:
            await update.message.reply_text(
                f"Great! Your project is named *{text}*.\n\n{result['next_prompt']}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_SLOGAN']:
        result = handle_slogan(user_id, text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_DESCRIPTION']:
        result = handle_description(user_id, text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_LOGO']:
        # Handle text option for logo (skip)
        if text.lower() == 'skip':
            result = handle_logo(user_id, "skip")
            if result["success"]:
                # Show theme options after skipping logo
                await show_theme_options(update, context)
            else:
                await update.message.reply_text(f"Error: {result['message']}")
        else:
            await update.message.reply_text(
                "Please upload an image for your logo, or type 'skip' to use a generated logo."
            )
    
    elif current_state == STATES['WAITING_FOR_TELEGRAM']:
        result = handle_social_link(user_id, "telegram", text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_TWITTER']:
        result = handle_social_link(user_id, "twitter", text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_DISCORD']:
        result = handle_social_link(user_id, "discord", text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_MEDIUM']:
        result = handle_social_link(user_id, "medium", text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_GITHUB']:
        result = handle_social_link(user_id, "github", text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_CUSTOM_SOCIAL']:
        # Handle custom social input (format: "name:url")
        if text.lower() == 'skip':
            result = handle_social_link(user_id, "custom", "skip")
        else:
            try:
                name, url = text.split(':', 1)
                result = handle_social_link(user_id, "custom", {"name": name.strip(), "url": url.strip()})
            except ValueError:
                await update.message.reply_text(
                    "Please use the format 'name:url' for custom social links, or type 'skip'."
                )
                return
                
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_SUPPLY']:
        result = handle_tokenomics(user_id, "total_supply", text)
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_TAX_INFO']:
        # Parse tax input (format: "buy:5%,sell:7%,burn:2%,redistribution:3%")
        if text.lower() == 'skip':
            result = handle_tokenomics(user_id, "tax", "skip")
        else:
            try:
                tax_parts = text.split(',')
                tax_data = {}
                for part in tax_parts:
                    key, value = part.split(':', 1)
                    tax_data[key.strip()] = value.strip()
                result = handle_tokenomics(user_id, "tax", tax_data)
            except ValueError:
                await update.message.reply_text(
                    "Please use the format 'buy:5%,sell:7%' for tax info, or type 'skip'."
                )
                return
                
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_DISTRIBUTION']:
        # Handle distribution in simplified format
        if text.lower() == 'skip':
            result = handle_tokenomics(user_id, "distribution", "skip")
        else:
            try:
                dist_parts = text.split(',')
                dist_data = []
                for part in dist_parts:
                    name, percentage = part.split(':', 1)
                    dist_data.append({"name": name.strip(), "percentage": percentage.strip()})
                result = handle_tokenomics(user_id, "distribution", dist_data)
            except ValueError:
                await update.message.reply_text(
                    "Please use the format 'Team:10%,Marketing:20%' for distribution, or type 'skip'."
                )
                return
                
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_ROADMAP']:
        # Handle roadmap in simplified format
        if text.lower() == 'skip':
            result = handle_roadmap(user_id, "skip")
        else:
            try:
                roadmap_phases = []
                phases = text.split(';')
                for phase in phases:
                    items = [item.strip() for item in phase.split(',')]
                    roadmap_phases.append(items)
                result = handle_roadmap(user_id, roadmap_phases)
            except ValueError:
                await update.message.reply_text(
                    "Please use the format 'Item1, Item2, Item3; Item4, Item5, Item6' for roadmap phases, or type 'skip'."
                )
                return
                
        if result["success"]:
            await update.message.reply_text(result['next_prompt'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['WAITING_FOR_SECTIONS_ORDER']:
        # Handle sections order input
        if text.lower() == 'skip':
            result = handle_sections_order(user_id, "skip")
        else:
            try:
                sections = [section.strip() for section in text.split(',')]
                result = handle_sections_order(user_id, sections)
            except ValueError:
                await update.message.reply_text(
                    "Please list sections in order, separated by commas, or type 'skip'."
                )
                return
                
        if result["success"]:
            # Show the confirmation dialog
            await show_confirmation(update, context, result['data'])
        else:
            await update.message.reply_text(f"Error: {result['message']}")
    
    elif current_state == STATES['READY_TO_GENERATE']:
        # Trigger website generation
        await update.message.reply_text("Starting website generation. Please wait...")
        
        # Show a progress message
        progress_msg = await update.message.reply_text("⏳ Generating your website (0%)...")
        
        try:
            # Update progress periodically
            for i in range(1, 5):
                await asyncio.sleep(1)
                await context.bot.edit_message_text(
                    f"⏳ Generating your website ({i*25}%)...",
                    chat_id=update.effective_chat.id,
                    message_id=progress_msg.message_id
                )
            
            # Generate the website
            result = generate_website(user_id)
            
            # Delete the progress message
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=progress_msg.message_id
            )
            
            if result["success"]:
                # Get the URLs
                site_hash = result["data"]["site_hash"]
                urls = result["data"]["urls"]
                
                # Create a keyboard with the URLs
                keyboard = []
                
                # Add preview button
                if "preview_url" in urls and urls["preview_url"]:
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
                
                # Add generate another button
                keyboard.append([InlineKeyboardButton(
                    "🔄 Create Another Website", 
                    callback_data="create_another"
                )])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "✅ Your website has been generated successfully!\n\n"
                    "You can preview it, download the HTML file, or share it using the buttons below.",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(f"Error generating website: {result['message']}")
        
        except Exception as e:
            logger.error(f"Error in website generation: {str(e)}")
            await update.message.reply_text(f"Error generating website: {str(e)}")
    
    else:
        # If we're not in a recognized state, restart
        await update.message.reply_text(
            "I'm not sure what to do next. Let's start over.\n\n"
            "Send /start to begin creating your website."
        )

# Photo handler for logo uploads
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads for logos."""
    user_id = str(update.effective_user.id)
    
    # Get the current state manager
    manager = get_or_create_state_manager(user_id)
    current_state = manager.get_current_state()
    
    # Check if we're expecting a logo
    if current_state == STATES['WAITING_FOR_LOGO']:
        try:
            # Get the largest photo
            photo = update.message.photo[-1]
            file_id = photo.file_id
            
            # Download the file
            file = await context.bot.get_file(file_id)
            
            # Create the uploads directory if it doesn't exist
            os.makedirs('uploads', exist_ok=True)
            
            # Generate a unique filename
            filename = f"uploads/{user_id}_{file_id}.jpg"
            
            # Download the file
            await file.download_to_drive(filename)
            
            # Handle the logo with the file path - pass only the path, not a file object
            result = handle_logo(user_id, filename)
            
            if result["success"]:
                # Show theme options after logo upload
                await show_theme_options(update, context)
            else:
                await update.message.reply_text(f"Error uploading logo: {result['message']}")
        except Exception as e:
            logger.error(f"Error processing photo: {str(e)}")
            await update.message.reply_text(
                f"Sorry, there was an error processing your photo. Please try again or type 'skip'."
            )
    else:
        await update.message.reply_text(
            "I received your photo, but I'm not currently expecting a logo upload. "
            "Use /start to begin creating your website."
        )

# Button callback handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    
    # Template selection
    if query.data.startswith("template_"):
        template_id = query.data.replace("template_", "")
        
        # Get state manager and verify it's in the right state
        manager = get_or_create_state_manager(user_id)
        if manager.get_current_state() != STATES['WAITING_FOR_TEMPLATE_SELECTION']:
            # Force the correct state if needed
            manager.transition_to(STATES['WAITING_FOR_TEMPLATE_SELECTION'])
        
        result = handle_template_selection(user_id, template_id)
        
        if result["success"]:
            await query.edit_message_text(
                f"Selected template: {template_id}\n\n{result['next_prompt']}"
            )
        else:
            # If there's still an error, print more diagnostic info
            current_state = manager.get_current_state()
            await query.edit_message_text(
                f"Error selecting template: {result['message']}\n"
                f"Current state: {current_state}"
            )
    
    # Theme selection
    elif query.data.startswith("theme_"):
        theme_id = query.data.replace("theme_", "")
        result = handle_theme(user_id, theme_id)
        
        if result["success"]:
            # Skip the color scheme step entirely and proceed to the next step
            # The theme already has default colors so we don't need to ask again
            color_result = handle_color_scheme(user_id, {})
            
            if color_result["success"]:
                await query.edit_message_text(color_result['next_prompt'])
            else:
                await query.edit_message_text(
                    f"Selected theme: {theme_id}\n\n"
                    "There was an issue proceeding to the next step. Please try again."
                )
        else:
            await query.edit_message_text(f"Error selecting theme: {result['message']}")
    
    # Confirmation actions
    elif query.data == "confirm_website":
        result = handle_confirmation(user_id, True)
        
        if result["success"]:
            await query.edit_message_text(
                "Great! Your website details have been confirmed.\n\n"
                "Send any message to generate your website."
            )
        else:
            await query.edit_message_text(f"Error confirming website: {result['message']}")
    
    elif query.data == "edit_website":
        result = handle_confirmation(user_id, False)
        
        if result["success"] and "data" in result and "edit_options" in result["data"]:
            # Show edit options
            keyboard = []
            for option in result["data"]["edit_options"]:
                keyboard.append([InlineKeyboardButton(
                    option["label"], 
                    callback_data=f"edit_{option['field']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "What would you like to edit?",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(f"Error preparing edit options: {result['message']}")
    
    # Edit options
    elif query.data.startswith("edit_"):
        field = query.data.replace("edit_", "")
        result = handle_edit_choice(user_id, field)
        
        if result["success"]:
            await query.edit_message_text(result['next_prompt'])
        else:
            await query.edit_message_text(f"Error selecting edit option: {result['message']}")
    
    # Share website
    elif query.data.startswith("share_"):
        site_hash = query.data.replace("share_", "")
        
        # Get the state manager to access URLs
        manager = get_or_create_state_manager(user_id)
        website_data = manager.get_website_data()
        
        if "urls" in website_data:
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
        # Reset state and start over
        reset_state(user_id)
        
        # Show template options again
        templates = get_templates()
        
        # Create inline keyboard with template options
        keyboard = []
        for template in templates:
            keyboard.append([InlineKeyboardButton(
                template["name"], 
                callback_data=f"template_{template['id']}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Let's create another website! Please select a template:",
            reply_markup=reply_markup
        )

# Helper function to show theme options
async def show_theme_options(update, context):
    """Show theme selection options."""
    user_id = str(update.effective_user.id)
    
    # Get available themes
    themes = get_themes()
    
    # Create inline keyboard with theme options
    keyboard = []
    for theme in themes:
        keyboard.append([InlineKeyboardButton(
            theme["name"], 
            callback_data=f"theme_{theme['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select a theme for your website:",
        reply_markup=reply_markup
    )

# Helper function to show confirmation dialog
async def show_confirmation(update, context, data):
    """Show confirmation dialog with website details."""
    # Format the data for display
    formatted_name = data.get("formatted_name", data.get("coin_name", ""))
    template_id = data.get("template_id", "")
    slogan = data.get("slogan", "[Random slogan]")
    theme = data.get("theme", "")
    
    # Social links
    social_links = data.get("social_links", {})
    social_text = ""
    if social_links.get("telegram"):
        social_text += f"• Telegram: {social_links['telegram']}\n"
    if social_links.get("twitter"):
        social_text += f"• Twitter: {social_links['twitter']}\n"
    if social_links.get("discord"):
        social_text += f"• Discord: {social_links['discord']}\n"
    if not social_text:
        social_text = "• [None]"
    
    # Create the confirmation message
    message = (
        f"📋 *Website Details Summary*\n\n"
        f"*Name:* {formatted_name}\n"
        f"*Template:* {template_id}\n"
        f"*Slogan:* {slogan}\n"
        f"*Theme:* {theme}\n\n"
        f"*Social Links:*\n{social_text}\n\n"
        f"Please confirm these details or choose to edit them."
    )
    
    # Create inline keyboard for confirmation
    keyboard = [
        [InlineKeyboardButton("✅ Confirm & Generate", callback_data="confirm_website")],
        [InlineKeyboardButton("✏️ Edit Details", callback_data="edit_website")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
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
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()