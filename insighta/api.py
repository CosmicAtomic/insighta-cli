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

def list_profiles(gender=None, country_id=None, age_group=None, min_age=None, max_age=None, sort_by=None, order=None, page=1, limit=10):
    params = {"page": page, "limit": limit}
    if gender:
        params["gender"] = gender
    if country_id:
        params["country_id"] = country_id
    if age_group:
        params["age_group"] = age_group
    if min_age:
        params["min_age"] = min_age
    if max_age:
        params["max_age"] = max_age
    if sort_by:
        params["sort_by"] = sort_by
    if order:
        params["order"] = order

    response = make_request("GET", "/api/profiles", params=params)
    if response:
        return response.json()
    
    
def get_profile(profile_id):
    response = make_request("GET", f"/api/profiles/{profile_id}")
    if response:
        return response.json()

def search_profiles(query, page=1, limit=10):
    response = make_request("GET", "/api/profiles/search", params={"q": query, "page": page, "limit": limit})
    if response:
        return response.json()

def create_profile(name):
    response = make_request("POST", "/api/profiles", json={"name": name})
    if response:
        return response.json()

def export_profiles(format="csv", **filters):
    params = {"format": format, **filters}
    response = make_request("GET", "/api/profiles/export", params=params)
    if response:
        return response.content  # raw bytes, not JSON



