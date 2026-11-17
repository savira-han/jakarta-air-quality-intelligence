
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")

BASE_URL = "https://api.openaq.org/v3"

headers = {
    "X-API-Key": API_KEY
}

def test_connection():

    if not API_KEY:
        raise ValueError("OpenAQ API key is missing.")

    url = f"{BASE_URL}/parameters"

    response = requests.get(
        url,
        headers=headers,
        params={"limit": 5},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    print("OpenAQ API connection successful.")
    print(f"Results returned: {len(data.get('results', []))}")

    for parameter in data.get("results", []):
        print(
            parameter.get("name"),
            parameter.get("units")
        )


if __name__ == "__main__":
    test_connection()
