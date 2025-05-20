import os
import subprocess
import threading
import signal
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_server():
    print("Starting Flask server...")
    server_process = subprocess.Popen(["python", "server.py"])
    return server_process

def run_bot():
    print("Starting Telegram bot...")
    
    # Choose which bot implementation to use
    # - ai_bot.py: AI-powered single-step website generation 
    # - bot.py: Our enhanced bot with both instant and guided flows
    bot_file = "bot.py"  # Using our enhanced bot with instant generation
    
    bot_process = subprocess.Popen(["python", bot_file])
    return bot_process

def signal_handler(sig, frame):
    print("\nShutting down services...")
    if 'server_process' in globals():
        server_process.terminate()
    if 'bot_process' in globals():
        bot_process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Ensure sites directory exists
    os.makedirs('sites', exist_ok=True)
    
    # Check for required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
        print("Please create a .env file with your Telegram bot token.")
        sys.exit(1)
    
    # Start server
    server_process = run_server()
    
    # Give the server time to start
    import time
    time.sleep(2)
    
    # Start bot
    bot_process = run_bot()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        server_process.terminate()
        bot_process.terminate()