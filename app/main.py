from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from .database import Base, engine, get_db
from .models import ShortLink, LinkVisit
from .schemas import LinkCreate
from .security import generate_code, validate_alias
from .config import BASE_URL, APP_NAME

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=f"{APP_NAME} URL Shortener API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def is_expired(link: ShortLink) -> bool:
    if not link.expires_at:
        return False
    exp = link.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp <= datetime.now(timezone.utc)

def link_payload(link: ShortLink):
    return {
        "code": link.code,
        "original_url": link.original_url,
        "short_url": f"{BASE_URL}/{link.code}",
        "title": link.title,
        "clicks": link.clicks,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
        "is_active": link.is_active,
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    links = db.scalars(select(ShortLink).order_by(desc(ShortLink.created_at)).limit(50)).all()
    total_clicks = sum(link.clicks for link in links)
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"app_name": APP_NAME, "base_url": BASE_URL, "links": links,
                 "total_links": len(links), "total_clicks": total_clicks}
    )

@app.post("/api/links", status_code=201)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    code = payload.custom_alias
    if code:
        if not validate_alias(code):
            raise HTTPException(422, "Alias must be 3–32 letters, numbers, hyphens or underscores.")
        if db.scalar(select(ShortLink).where(ShortLink.code == code)):
            raise HTTPException(409, "That custom alias is already in use.")
    else:
        for _ in range(10):
            candidate = generate_code()
            if not db.scalar(select(ShortLink).where(ShortLink.code == candidate)):
                code = candidate
                break
        if not code:
            raise HTTPException(503, "Could not allocate a short code. Please retry.")
    link = ShortLink(code=code, original_url=payload.url, title=payload.title,
                     expires_at=payload.expires_at, is_active=True, clicks=0)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link_payload(link)

@app.get("/api/links")
def list_links(db: Session = Depends(get_db)):
    links = db.scalars(select(ShortLink).order_by(desc(ShortLink.created_at)).limit(100)).all()
    return [link_payload(link) for link in links]

@app.get("/api/links/{code}")
def get_link(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(ShortLink).where(ShortLink.code == code))
    if not link:
        raise HTTPException(404, "Short link not found.")
    return {**link_payload(link), "expired": is_expired(link), "recent_visits": [
        {"visited_at": v.visited_at, "referrer": v.referrer}
        for v in db.scalars(select(LinkVisit).where(LinkVisit.link_id == link.id)
                            .order_by(desc(LinkVisit.visited_at)).limit(20)).all()
    ]}

@app.delete("/api/links/{code}", status_code=204)
def deactivate_link(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(ShortLink).where(ShortLink.code == code))
    if not link:
        raise HTTPException(404, "Short link not found.")
    link.is_active = False
    db.commit()
    return None

@app.get("/{code}")
def redirect_short_link(code: str, request: Request, db: Session = Depends(get_db)):
    link = db.scalar(select(ShortLink).where(ShortLink.code == code))
    if not link or not link.is_active or is_expired(link):
        raise HTTPException(404, "This short link is unavailable or has expired.")
    visit = LinkVisit(link_id=link.id,
                      referrer=(request.headers.get("referer") or "")[:500] or None,
                      user_agent=(request.headers.get("user-agent") or "")[:500] or None)
    link.clicks += 1
    db.add(visit)
    db.commit()
    return RedirectResponse(url=link.original_url, status_code=307)

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME}

