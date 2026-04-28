import httpx
import os
from .config import load_tokens, save_tokens

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

def make_request(method, path, **kwargs):
    tokens = load_tokens()
    if not tokens:
        print("Not logged in. Run: insighta login")
        return None

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {tokens['access_token']}"
    headers["X-API-Version"] = "1"

    # Try the request
    response = httpx.request(method, f"{BACKEND_URL}{path}", headers=headers, **kwargs)

    # If 401, try refreshing
    if response.status_code == 401:
        refresh_response = httpx.post(f"{BACKEND_URL}/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })

        if refresh_response.status_code != 200:
            print("Session expired. Run: insighta login")
            return None

        new_tokens = refresh_response.json()
        save_tokens(new_tokens["access_token"], new_tokens["refresh_token"])

        # Retry with new token
        headers["Authorization"] = f"Bearer {new_tokens['access_token']}"
        response = httpx.request(method, f"{BACKEND_URL}{path}", headers=headers, **kwargs)

    return response