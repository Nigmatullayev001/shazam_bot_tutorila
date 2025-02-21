import requests
from data.config import API_KEY  # Import API Key from config


def search_track(query, limit=10):
    """Search for a song using Shazam API by title."""
    url = "https://shazam-api6.p.rapidapi.com/shazam/search_track/"
    querystring = {"query": query, "limit": str(limit)}

    headers = {
        "x-rapidapi-key": API_KEY,  # Use API key from config
        "x-rapidapi-host": "shazam-api6.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        data = response.json()
        print("🔍 API Response:", data)  # API javobini konsolga chiqaramiz

        if "result" in data:
            return data["result"]

        print("❌ No tracks found in API response!")
        return None


    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")  # Print error message
        return None
