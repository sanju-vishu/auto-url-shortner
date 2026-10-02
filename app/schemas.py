from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    url: str = Field(min_length=8, max_length=4000)
    custom_alias: Optional[str] = Field(default=None, min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    title: Optional[str] = Field(default=None, max_length=160)
    expires_at: Optional[datetime] = None

    @field_validator("url")
    @classmethod
    def valid_http_url(cls, value: str):
        from urllib.parse import urlparse
        parsed = urlparse(value.strip())
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Enter a complete URL starting with http:// or https://")
        return value.strip()

class LinkOut(BaseModel):
    code: str
    original_url: str
    short_url: str
    title: Optional[str] = None
    clicks: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
