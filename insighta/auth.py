import os
import httpx
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from .config import save_tokens, load_tokens, clear_tokens
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

# Will be filled by the callback handler
captured_tokens = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_tokens
        query = parse_qs(urlparse(self.path).query)
        captured_tokens = {
            "access_token": query.get("access_token", [None])[0],
            "refresh_token": query.get("refresh_token", [None])[0],
            "username": query.get("username", [None])[0],
        }

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Login successful! You can close this tab.</h1>")

    def log_message(self, format, *args):
        pass

def login():
    global captured_tokens
    captured_tokens = None

    # 1. Start local server
    server = HTTPServer(("localhost", 8888), CallbackHandler)

    # 2. Open browser to YOUR BACKEND — backend handles all OAuth
    webbrowser.open(f"{BACKEND_URL}/auth/github?redirect_to=http://localhost:8888/callback")

    # 3. Wait for the callback
    server.handle_request()
    server.server_close()

    # 4. Check we got tokens
    if not captured_tokens or not captured_tokens["access_token"]:
        print("Error: Login failed.")
        return

    # 5. Save tokens locally
    save_tokens(captured_tokens["access_token"], captured_tokens["refresh_token"])

    # 6. Confirm
    print(f"Logged in as @{captured_tokens['username']}")

def logout():
    tokens = load_tokens()
    if not tokens:
        print("Not logged in.")
        return
    try:
        httpx.post(f"{BACKEND_URL}/auth/logout", json={
            "refresh_token": tokens["refresh_token"]
        })
    except Exception:
        pass  # Even if the backend call fails, still clear local tokens
    clear_tokens()
    print("Logged out.")


def whoami():
    tokens = load_tokens()
    if not tokens:
        print("Not logged in. Run: insighta login")
        return

    response = httpx.get(f"{BACKEND_URL}/auth/me", headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })

    if response.status_code == 401:
        print("Session expired. Run: insighta login")
        return

    data = response.json()["data"]
    print(f"Username: @{data['username']}")
    print(f"Email:    {data['email']}")
    print(f"Role:     {data['role']}")