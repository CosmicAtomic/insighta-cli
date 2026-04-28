# Insighta CLI

A command-line interface for interacting with the Insighta API. Supports GitHub OAuth login and full profile management from the terminal.

---

## System Architecture

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────┐
│   insighta CLI  │◄──────►│  Insighta Backend│◄──────►│  GitHub OAuth   │
│  (this project) │  HTTP  │  (FastAPI/Python) │  OAuth │  (github.com)   │
└─────────────────┘        └──────────────────┘        └─────────────────┘
        │
        ▼
~/.insighta/credentials.json
(access + refresh tokens stored locally)
```

## Related Repositories

- **Backend API:** [name-profiler](https://github.com/CosmicAtomic/name-profiler) — The API this CLI connects to
- **Web Portal:** [insighta-web](https://github.com/CosmicAtomic/insighta-web) — Browser-based interface (link TBD)

**Key modules:**

| File | Responsibility |
|---|---|
| `cli.py` | Command definitions and output rendering |
| `auth.py` | Login, logout, and whoami flows |
| `api.py` | All authenticated HTTP requests to the backend |
| `config.py` | Token persistence to disk |

---

## Authentication Flow

Insighta uses **GitHub OAuth** delegated through the backend. The CLI never talks to GitHub directly.

```
1. insighta login
       │
       ▼
2. CLI starts a local HTTP server on localhost:8888
       │
       ▼
3. CLI opens browser → Backend /auth/github?redirect_to=http://localhost:8888/callback
       │
       ▼
4. Backend redirects user to GitHub login
       │
       ▼
5. GitHub redirects back to Backend /auth/github/callback
       │
       ▼
6. Backend creates/updates user, issues access + refresh tokens
       │
       ▼
7. Backend redirects to localhost:8888/callback?access_token=...&refresh_token=...&username=...
       │
       ▼
8. CLI captures tokens from the callback URL
       │
       ▼
9. Tokens saved to ~/.insighta/credentials.json
       │
       ▼
10. "Logged in as @username" printed to terminal
```

---

## Token Handling

Tokens are stored locally at `~/.insighta/credentials.json`:

```json
{
    "access_token": "...",
    "refresh_token": "..."
}
```

**Access token** is attached to every API request as a Bearer token:
```
Authorization: Bearer <access_token>
```

**Automatic refresh:** If the backend returns a `401`, the CLI automatically:
1. Posts the refresh token to `/auth/refresh`
2. Saves the new token pair to disk
3. Retries the original request with the new access token

If the refresh also fails, the user is prompted to log in again.

**Logout** invalidates the refresh token on the backend and deletes the local credentials file.

---

## Installation

```bash
git clone <repo-url>
cd insighta-cli

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -e .
```

**Environment variables** (create a `.env` file in the project root):

```env
BACKEND_URL=http://localhost:8000
```

If `BACKEND_URL` is not set, it defaults to `http://localhost:8000`.

---

## CLI Usage

### Authentication

```bash
# Log in via GitHub (opens browser)
insighta login

# Show currently logged-in user
insighta whoami

# Log out
insighta logout
```

### Profiles

```bash
# List profiles (paginated)
insighta profiles list
insighta profiles list --gender female --country NG --page 2 --limit 50

# Available filters for list:
#   --gender      Filter by gender
#   --country     Filter by country
#   --age-group   Filter by age group
#   --min-age     Minimum age
#   --max-age     Maximum age
#   --sort-by     Field to sort by
#   --order       asc (default) or desc
#   --page        Page number (default: 1)
#   --limit       Results per page (default: 20)

# Get a single profile by ID
insighta profiles get-cmd <profile-id>

# Search profiles by keyword
insighta profiles search-cmd "john"

# Create a new profile
insighta profiles create-cmd --name "Jane Doe"

# Export profiles to CSV
insighta profiles export
insighta profiles export --gender male --country NG
# Saves to: profiles_export.csv in the current directory
```

### Other

```bash
# Verify the CLI is working
insighta hello
```

---

## Project Structure

```
insighta-cli/
├── .env                          # Environment variables (not committed)
├── .gitignore
├── pyproject.toml                # Package config and dependencies
└── insighta/
    ├── __init__.py
    ├── cli.py                    # Click commands and Rich output
    ├── auth.py                   # OAuth login/logout/whoami
    ├── api.py                    # Authenticated API calls + token refresh
    └── config.py                 # Token read/write to ~/.insighta/
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `click` | CLI framework |
| `httpx` | HTTP client for API requests |
| `rich` | Terminal tables and status spinners |
| `python-dotenv` | Load `.env` file for environment variables |
