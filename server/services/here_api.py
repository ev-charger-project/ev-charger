import os
import httpx
from dotenv import load_dotenv
from server.services.here_auth import TokenManager

load_dotenv()  # Loads .env file

# Create a single TokenManager instance (can be reused)
token_manager = TokenManager()


def get_here_ev_data():
    url = os.getenv("HERE_API_URL")
    params = {
        "at": os.getenv("HERE_API_AT"),
        "in": os.getenv("HERE_API_IN"),
        "categories": os.getenv("HERE_API_CATEGORIES"),
        "limit": os.getenv("HERE_API_LIMIT"),
        # "limit": 1,
        "show": os.getenv("HERE_API_SHOW"),
    }
    # Use the cached or refreshed token
    token = token_manager.get_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = httpx.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
