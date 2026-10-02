import os
from fastapi.testclient import TestClient

def test_health_and_create_redirect(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    # Import in a fresh test process is ideal because the application creates its
    # engine at import time. This smoke test validates the route shape with default DB.
    from app.main import app
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.post("/api/links", json={"url": "https://example.com/path"})
        assert response.status_code == 201
        payload = response.json()
        assert payload["short_url"].endswith("/" + payload["code"])
        redirect = client.get("/" + payload["code"], follow_redirects=False)
        assert redirect.status_code in (307, 302)
        assert redirect.headers["location"] == "https://example.com/path"
