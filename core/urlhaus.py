import httpx
from urllib.parse import urlparse

URLHAUS_API_URL = "https://urlhaus-api.abuse.ch/v1/url/"

def check_urlhaus(url: str, timeout: float = 2.0) -> bool:
    """
    Checks a URL against the URLHaus database.
    Returns True if the URL is listed (malicious), False otherwise.
    """
    if not url:
        return False

    try:
        # URLHaus expects a URL, hostname, or MD5 hash. We'll send the URL.
        data = {'url': url}
        with httpx.Client(timeout=timeout) as client:
            response = client.post(URLHAUS_API_URL, data=data)

            if response.status_code == 200:
                json_response = response.json()
                # "ok" means the query was successful.
                if json_response.get("query_status") == "ok":
                    # If "id" is present, the URL is in the database.
                    return "id" in json_response
            # Handle rate limiting gracefully
            elif response.status_code == 429:
                print("Warning: URLHaus rate limit exceeded.")
            else:
                print(f"Warning: URLHaus API returned status {response.status_code}")

    except httpx.RequestError as e:
        print(f"Error querying URLHaus: {e}")

    return False
