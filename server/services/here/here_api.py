import os
import httpx
from dotenv import load_dotenv
from server.services.here.here_auth import TokenManager

load_dotenv()  # Loads .env file

# Create a single TokenManager instance (can be reused)
token_manager = TokenManager()


def get_here_ev_data(lat=None, lon=None, radius_km=None):
    url = os.getenv("HERE_API_URL")
    params = {
        "categories": os.getenv("HERE_API_CATEGORIES"),
        "limit": os.getenv("HERE_API_LIMIT", 100),
        "show": os.getenv("HERE_API_SHOW"),
    }
    if lat is not None and lon is not None and radius_km is not None:
        params["at"] = f"{lat},{lon}"
        params["in"] = f"circle:{lat},{lon};r={int(radius_km*1000)}"
    else:
        params["at"] = os.getenv("HERE_API_AT")
        params["in"] = os.getenv("HERE_API_IN")

    token = token_manager.get_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = httpx.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
