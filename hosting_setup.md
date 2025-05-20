# Hosting Options for MemeCoin Website Generator

This guide explains multiple options for hosting your generated meme coin websites with HTTPS (required for Telegram WebApps).

## Option 1: Netlify (Easiest & Recommended)

1. Create a free Netlify account at https://netlify.com
2. Create a new site from the Netlify dashboard
3. Go to Site settings → Site information to get your Site ID
4. Create a Personal Access Token:
   - Go to User settings → Applications → Personal access tokens
   - Create a new token with relevant permissions
5. Add to your `.env` file:
   ```
   USE_REMOTE_HOSTING=true
   NETLIFY_TOKEN=your_netlify_token_here
   NETLIFY_SITE_ID=your_netlify_site_id_here
   ```
6. Install the Netlify CLI:
   ```
   npm install -g netlify-cli
   ```

## Option 2: Vercel (Alternative)

1. Create a free Vercel account at https://vercel.com
2. Create a new project from the Vercel dashboard
3. Generate a token:
   - Go to Settings → Tokens
   - Create a new token
4. Add to your `.env` file:
   ```
   USE_REMOTE_HOSTING=true
   VERCEL_TOKEN=your_vercel_token_here
   ```
5. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```
6. Login to Vercel using CLI:
   ```
   vercel login
   ```

## Option 3: Firebase Hosting (Google Cloud Platform)

1. Create a Firebase account at https://firebase.google.com
2. Create a new project
3. Enable Firebase Hosting for your project
4. Add to your `.env` file:
   ```
   USE_REMOTE_HOSTING=true
   FIREBASE_PROJECT=your_firebase_project_id
   ```
5. Install the Firebase CLI:
   ```
   npm install -g firebase-tools
   ```
6. Login to Firebase using CLI:
   ```
   firebase login
   ```

## Option 4: Custom Domain with GitHub Pages Pro (Paid)

If you have GitHub Pro, you can use GitHub Pages with your private repositories.

1. Upgrade to GitHub Pro
2. Enable GitHub Pages in your repository settings
3. Set a custom domain (optional)
4. Update the GitHub uploader to enable GitHub Pages

## Option 5: Run a Proper HTTPS Server

For a production environment, you should run a proper HTTPS server:

1. Get a domain name
2. Set up a VPS (DigitalOcean, AWS, etc.)
3. Install Nginx with Let's Encrypt for HTTPS
4. Use a proper WSGI server (Gunicorn) for Flask
5. Update your `.env` file with the proper SERVER_URL

---

# Configuration Summary

You can use multiple hosting options together. For example:
- GitHub repositories for code storage/backup
- Netlify for HTTPS hosting

Here's a complete example `.env` configuration:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# GitHub for code storage (private repos)
USE_GITHUB=true
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username_here

# Netlify for HTTPS hosting
USE_REMOTE_HOSTING=true
NETLIFY_TOKEN=your_netlify_token_here
NETLIFY_SITE_ID=your_netlify_site_id_here
```

With this setup, each meme coin site will be:
1. Stored as code in a private GitHub repository
2. Hosted with HTTPS on Netlify
3. Available for Telegram WebApps to display