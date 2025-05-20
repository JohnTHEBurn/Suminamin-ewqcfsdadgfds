import os
import sys
import time
import subprocess
import requests
from pyngrok import ngrok, conf
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()

def setup_ngrok():
    """Set up ngrok tunnel and update .env file with the URL"""
    print("Setting up ngrok tunnel for HTTPS access...")
    
    # Get token from env
    auth_token = os.getenv('NGROK_AUTHTOKEN')
    if not auth_token or auth_token == 'your_ngrok_authtoken_here':
        print("Warning: No valid NGROK_AUTHTOKEN found in .env file.")
        print("The tunnel will still work but with limitations.")
    else:
        # Set auth token
        ngrok.set_auth_token(auth_token)
    
    # Configure ngrok
    conf.get_default().region = 'us'
    
    # Open a tunnel
    try:
        # Kill any existing ngrok processes
        if sys.platform == 'win32':
            os.system('taskkill /f /im ngrok.exe 2>nul')
        else:
            os.system('pkill -f ngrok > /dev/null 2>&1')
        
        # Start tunnel
        tunnel = ngrok.connect(5000, 'http')
        ngrok_url = tunnel.public_url
        
        print(f"ngrok tunnel established: {ngrok_url}")
        
        # Update .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Read current .env file
        with open(dotenv_path, 'r') as file:
            lines = file.readlines()
        
        # Update SERVER_URL line
        with open(dotenv_path, 'w') as file:
            for line in lines:
                if line.startswith('SERVER_URL='):
                    file.write(f'SERVER_URL={ngrok_url}\n')
                else:
                    file.write(line)
        
        print(f"Updated .env file with ngrok URL: {ngrok_url}")
        return ngrok_url
    
    except Exception as e:
        print(f"Error setting up ngrok: {e}")
        return None

def run_app():
    """Run the Flask server and Telegram bot"""
    try:
        # Start the Flask server in background
        print("Starting Flask server...")
        flask_process = subprocess.Popen(["python", "server.py"], 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        
        # Give the server time to start
        time.sleep(3)
        
        # Start the bot
        print("Starting Telegram bot...")
        bot_process = subprocess.Popen(["python", "bot.py"],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        
        # Keep the main thread alive
        try:
            while flask_process.poll() is None and bot_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            flask_process.terminate()
            bot_process.terminate()
    
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    # Ensure the bot token is set
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token or bot_token == 'your_telegram_bot_token_here':
        print("Error: TELEGRAM_BOT_TOKEN not set in .env file")
        sys.exit(1)
    
    # Setup ngrok
    ngrok_url = setup_ngrok()
    if not ngrok_url:
        print("Failed to set up ngrok tunnel. Exiting.")
        sys.exit(1)
    
    # Run the application
    run_app()