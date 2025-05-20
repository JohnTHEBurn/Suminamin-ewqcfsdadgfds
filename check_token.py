import os, requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {token}"}
response = requests.get("https://api.github.com/user", headers=headers)
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    print("Token is valid")
else:
    print(response.text)

