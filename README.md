# Meme Coin Website Generator Telegram Bot

A Telegram bot that dynamically generates meme coin websites and allows users to preview them directly within Telegram using Web Apps.

## Features

- Generate a unique meme coin landing page by providing a name
- Preview the website directly within Telegram using Web Apps (requires HTTPS)
- Download generated HTML files for self-hosting
- Randomized elements for each site: slogan, tokenomics, roadmap
- Optimized for high-concurrency (thousands of users per second)
- Multiple hosting options: local server with SSL, GitHub Pages, or other cloud options
- **NEW**: Comprehensive customization flow with multiple templates and themes
- **NEW**: Save and resume customization sessions
- **NEW**: Choose from multiple website templates (Meme Coin, NFT Collection, DeFi Platform)

## Technical Stack

- **Bot Framework**: `python-telegram-bot`
- **Backend Server**: Flask with optimized performance
- **Templates**: Jinja2 for HTML generation
- **Hosting Options**: ngrok HTTPS tunnel or GitHub Pages
- **Performance**: Multi-threading, concurrent execution, and caching
- **State Management**: Session-based customization flow with state persistence

## New Customization Features

The enhanced version includes a comprehensive customization system:

### Multiple Templates

Choose from different website templates:
- **Meme Coin**: Modern, animated landing page for meme coins
- **NFT Collection**: Showcase NFT collections with gallery and minting interface
- **DeFi Platform**: Professional DeFi platform with staking and yield farming info

### Customization Flow

The new system features a guided customization flow with multiple steps:
1. Template selection
2. Basic information (name, slogan, description)
3. Visual customization (logo, theme, colors)
4. Social links configuration
5. Template-specific options (tokenomics, NFT settings, DeFi features)
6. Preview and confirmation

### State Management

- Save and resume customization sessions
- Edit any part of your customization at any time
- Full validation of required fields based on template type
- Automatic formatting and optimization of user inputs

### API Endpoints

The new system provides a comprehensive API for programmatic access:
- `/api/templates` - List available templates
- `/api/themes` - List available themes
- `/api/state` - Get/reset user's customization state
- `/api/generate/direct` - Generate a website in a single API call

## Hosting Options

You have two options for hosting the generated websites:

### Option 1: Private GitHub Repositories

- Automatically creates a private GitHub repository for each generated site
- Securely stores your generated sites in private repositories
- Creates a permanent backup of all generated sites

### Option 2: Multiple HTTPS Hosting Options

You have several options for hosting with HTTPS (required for Telegram WebApps):

1. **Netlify** (Recommended)
   - Fast, free hosting with automatic HTTPS
   - Easy deployment API integration
   - Unlimited sites on free tier

2. **Vercel**
   - Another excellent free hosting option with HTTPS
   - Great performance and reliability
   - Unlimited sites on free tier

3. **Firebase Hosting**
   - Google Cloud Platform integration
   - Reliable hosting with HTTPS 
   - Free tier available

See [hosting_setup.md](hosting_setup.md) for detailed setup instructions.

## Quick Start with Docker

The easiest way to run this project is with Docker:

1. Copy `.env.example` to `.env` and configure your preferred hosting method:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Choose ONE hosting method:

# Option 1: ngrok
NGROK_AUTHTOKEN=your_ngrok_authtoken_here

# Option 2: GitHub Pages
USE_GITHUB=true
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username_here
```

2. Start the container:

```bash
docker-compose up -d
```

## Manual Setup

### Prerequisites

- Python 3.8+
- A Telegram Bot Token (obtain from @BotFather)

For ngrok hosting:
- ngrok account and authtoken (sign up at ngrok.com)

For GitHub Pages hosting:
- GitHub account and personal access token with repo permissions

### Installation

1. Clone this repository
2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set up environment variables (see `.env.example`)

### Running the Application

For the original version:
```bash
python run.py
```

For the enhanced version with full customization:
```bash
python enhanced_server.py
```

## Getting Required Tokens

### 1. Telegram Bot Token
- Message @BotFather on Telegram
- Send `/newbot` and follow instructions
- Copy the API token provided

### 2. ngrok Authtoken (if using ngrok)
- Create an account at https://ngrok.com/
- Go to https://dashboard.ngrok.com/get-started/your-authtoken
- Copy your authtoken

### 3. GitHub Token (if using GitHub Pages)
- Log in to GitHub
- Go to Settings > Developer settings > Personal access tokens
- Create a token with 'repo' permissions
- Copy the generated token

## Usage

### Original Bot Flow
1. Start a chat with your bot on Telegram
2. Send the `/start` command to begin
3. Send a meme coin name (e.g., "FlokiElonMoon")
4. Click the "Preview Your MemeCoin Site" button to see your generated website
5. Use "Generate Another" to create a new site or "Share This Site" to share with friends

### Enhanced Customization Flow
1. Start a chat with your bot on Telegram
2. Send the `/start` command to begin
3. Choose a template for your website
4. Follow the step-by-step customization prompts
5. Provide details such as:
   - Name, slogan, description
   - Logo image
   - Theme and colors
   - Social media links
   - Template-specific options
6. Review and confirm your choices
7. Generate your website and receive links to view and share

## Web Interface

The enhanced version also includes a web interface for customization:
1. Access the server at `/customize`
2. Complete the customization form
3. Preview and generate your website
4. Get shareable links to your creation

## Extending the Project

The project is designed with modularity in mind:

- To add new site templates, create a new HTML template in the `templates` directory
- To add a new template type, update the `TEMPLATES` dictionary in `template_handlers.py`
- To modify the customization flow, edit the state transitions in `customization_states.py`
- To add more bot commands, extend the handlers in `bot.py`

### Adding a New Template

1. Create a new HTML template in the `templates` directory (e.g., `portfolio_template.html`)
2. Add the template metadata to `TEMPLATES` in `template_handlers.py`
3. Add a custom processor method for your template in `TemplateManager`

## API Documentation

### State Management API

- `GET /api/state?user_id=USER_ID` - Get current customization state
- `POST /api/state/reset` - Reset state to beginning
  - Requires: `{"user_id": "..."}` 

### Customization Flow API

- `POST /api/template/select` - Select a template
  - Requires: `{"user_id": "...", "template_id": "..."}`
- `POST /api/coin/name` - Set coin name
  - Requires: `{"user_id": "...", "coin_name": "..."}`
- `POST /api/theme` - Set template theme
  - Requires: `{"user_id": "...", "theme_id": "..."}`
- `POST /api/confirm` - Confirm selections
  - Requires: `{"user_id": "...", "confirmed": true}`
- `POST /api/generate` - Generate website
  - Requires: `{"user_id": "..."}`

### Direct Generation API

- `POST /api/generate/direct` - Generate website in one API call
  - Requires template-specific data and a `site_hash`

## Troubleshooting

### "Preview requires HTTPS server" message
This means your server is not using HTTPS, which is required for Telegram's WebApp feature. You have two options:

1. **Set up SSL for your local server**:
   ```bash
   python generate_ssl_certs.py
   ```
   Then update your `.env` file to use HTTPS:
   ```
   SERVER_URL=https://localhost:5000
   ```

2. **Enable GitHub hosting**:
   Set the following in your `.env` file:
   ```
   USE_GITHUB=true
   GITHUB_TOKEN=your_github_token
   GITHUB_USERNAME=your_github_username
   ```

### No download button appears
If the download button is missing:
- Make sure your GitHub token is valid and has the correct permissions
- Check that the `has_github` flag is being set correctly in the bot.py code
- If using local server, make sure the download button is visible even without GitHub integration

### GitHub Pages are not working
- It can take a few minutes for GitHub Pages to become available after creating a new repository
- Check if your GitHub token has the required permissions
- Make sure the `_enable_github_pages` method is working correctly in the `github_uploader.py` file

### Customization flow is not progressing
- Check the server logs for any errors in state transitions
- Make sure all required fields are provided for the current state
- Verify that the state manager is properly initialized for the user

## License

MIT License