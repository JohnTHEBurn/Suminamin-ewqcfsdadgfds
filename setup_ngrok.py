import os
import json
import subprocess
import time
import requests
from dotenv import load_dotenv, set_key

def setup_ngrok():
    print("Setting up ngrok tunnel for HTTPS access...")
    
    # Start ngrok process
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", "5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give ngrok time to start
    time.sleep(3)
    
    # Get the ngrok public URL from the API
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        data = response.json()
        
        # Extract the HTTPS URL
        ngrok_url = None
        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                ngrok_url = tunnel["public_url"]
                break
        
        if not ngrok_url:
            print("Error: Could not find HTTPS tunnel in ngrok")
            return False
        
        print(f"ngrok HTTPS URL: {ngrok_url}")
        
        # Update the .env file with the new URL
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        
        # Set the new SERVER_URL in .env
        with open(dotenv_path, 'r') as file:
            lines = file.readlines()
        
        with open(dotenv_path, 'w') as file:
            for line in lines:
                if line.startswith('SERVER_URL='):
                    file.write(f'SERVER_URL={ngrok_url}\n')
                else:
                    file.write(line)
        
        print("Updated .env file with ngrok URL")
        return ngrok_process
    
    except Exception as e:
        print(f"Error setting up ngrok: {e}")
        ngrok_process.terminate()
        return False

if __name__ == "__main__":
    ngrok_process = setup_ngrok()
    
    if ngrok_process:
        print("ngrok tunnel established successfully!")
        print("Press Ctrl+C to stop ngrok and exit")
        try:
            # Keep the script running while ngrok is active
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ngrok_process.terminate()
            print("ngrok tunnel closed")