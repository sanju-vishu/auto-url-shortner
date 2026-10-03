# PyShort — Python URL Shortener SaaS Starter

A responsive URL-shortening app built with **FastAPI, SQLAlchemy, SQLite/PostgreSQL, Jinja2 and vanilla JavaScript**. It includes a web dashboard, custom aliases, click tracking, expiry support, a JSON API, Docker support and automated tests.

> This is an MVP/starter, not a complete multi-tenant commercial SaaS. Before public launch, add authentication, per-user ownership, rate limiting, abuse reporting, domain verification, migrations and production monitoring.

## Features

- Shorten HTTP/HTTPS URLs into compact shareable links.
- Optional custom alias (3–32 letters, digits, `_` or `-`).
- Optional title and expiry timestamp.
- Redirect tracking: click count, timestamp, referrer and user-agent.
- Enable/disable a link through the API.
- Responsive dashboard with recent links and copy-to-clipboard.
- FastAPI interactive API docs at `/docs`.
- SQLite out of the box; PostgreSQL supported by setting `DATABASE_URL`.
- Dockerfile and Docker Compose included.

## Run locally (Windows 10/11)

1. Install Python 3.11 or 3.12 from python.org and enable **Add Python to PATH**.
2. Extract this ZIP and open PowerShell in the `pyshort_saas` folder.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
4. Start the development server:

   ```powershell
   uvicorn app.main:app --reload
   ```
5. Open:
   - Dashboard: http://127.0.0.1:8000
   - API documentation: http://127.0.0.1:8000/docs
   - Health check: http://127.0.0.1:8000/health

The SQLite database `pyshort.db` is created automatically on first start.

## API

### Create a short link

`POST /api/links`

```json
{
  "url": "https://www.example.com/articles/how-to-build-a-product",
  "custom_alias": "product-guide",
  "title": "Product guide"
}
```

`custom_alias` and `title` are optional. `expires_at` can be an ISO-8601 timestamp, for example `"2027-01-01T00:00:00Z"`.

Example response:

```json
{
  "code": "product-guide",
  "original_url": "https://www.example.com/articles/how-to-build-a-product",
  "short_url": "http://127.0.0.1:8000/product-guide",
  "title": "Product guide",
  "clicks": 0,
  "created_at": "2026-10-02T12:00:00",
  "expires_at": null,
  "is_active": true
}
```

### List recent links

`GET /api/links` — returns up to 100 links.

### Get link details and recent visits

`GET /api/links/{code}`

### Deactivate a link

`DELETE /api/links/{code}` — disables redirects while retaining the record.

### Redirect

`GET /{code}` — records the visit and redirects to the destination.

### Health

`GET /health`

## Configuration

Set environment variables before running the app:

- `APP_NAME`: dashboard and API title.
- `BASE_URL`: public origin used to build share links. Set this to your deployed domain, e.g. `https://s.example.com`.
- `DATABASE_URL`: optional SQLAlchemy connection URL. Default is local SQLite.
- `SECRET_KEY`: placeholder for future authentication/session integration; replace it with a strong secret for production.

For PostgreSQL, install dependencies from `requirements.txt` and set:

```text
DATABASE_URL=postgresql+psycopg://pyshort:YOUR_PASSWORD@localhost:5432/pyshort
```

Do not commit `.env` files or credentials.

## Daily Windows Git sync

To publish local changes from this Windows checkout to `origin/main` once per day at a randomized time, run this once in PowerShell:

```powershell
.\scripts\register-daily-deploy.ps1
```

The scheduled task uses the current Windows account and Git Credential Manager; it does not store a Git token or password in the repository. Before pushing, it fetches `origin/main`, commits changed non-ignored files, and rebases local commits onto the latest remote branch. Non-conflicting changes merge automatically. If files conflict, it aborts the rebase without overwriting either side and records a failure. Review the log at `%LOCALAPPDATA%\SmartUrl\deploy-logs`.

Keep `.env`, private keys, and credentials out of Git. `.gitignore` blocks common secret/config files, and the sync script rejects credential-like staged files and common token/private-key patterns. GitHub branch protection may reject direct pushes; in that case the log records failure and the branch policy must be followed.

This task publishes Git changes; it does not start or update a running Docker/server deployment. A hosting target and its deployment method must be configured separately for that.

## Docker

```bash
docker compose up --build -d
```

Then open http://localhost:8000. Update the example `SECRET_KEY` and `BASE_URL` before deployment.

## Tests

```bash
pip install pytest httpx
pytest -q
```

The included tests cover short-code generation and alias validation. Add integration tests for database and API behavior before production.

## Production checklist

- [ ] Add authentication (OAuth/OIDC or secure email login).
- [ ] Add `user_id` / tenant ownership and enforce it in every list, detail, edit and delete operation.
- [ ] Add per-IP and per-account rate limiting and bot/abuse controls.
- [ ] Block private/internal IP destinations if fetching URLs for previews; this starter does not fetch destination URLs.
- [ ] Add link abuse reports, phishing review, domain blocklists and an admin moderation workflow.
- [ ] Add Alembic migrations instead of relying on `create_all`.
- [ ] Use HTTPS, secure secrets, structured logs, metrics, backups and error monitoring.
- [ ] Configure a custom domain and proxy headers correctly.
- [ ] Review privacy requirements before storing IP addresses or user-agent data. This starter does **not** store IP addresses.
- [ ] Add CAPTCHA or verification for public anonymous link creation.
- [ ] Consider Redis for rate limiting/cache and a queue for analytics at scale.

## Project structure

```text
pyshort_saas/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── templates/index.html
│   └── static/{style.css,app.js}
├── tests/test_security.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## License

MIT — see `LICENSE`.
