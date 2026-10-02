import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'pyshort.db'}")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
APP_NAME = os.getenv("APP_NAME", "PyShort")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-before-production")
