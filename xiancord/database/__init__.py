from .manager import SpreadsheetManager
from pathlib import Path
from ..logger import terminal
import json
import asyncio
import os


db = SpreadsheetManager()

async def db_init():
    BASE_DIR = "/etc/secrets/"
    credentials_path = BASE_DIR / "credentials.json"
    with open(credentials_path , "r", encoding="utf-8") as f:
        creds = json.load(f)
    await db.init(creds)
    await db.add_spreadsheet("黑曜國際")

async def db_init_local():
    BASE_DIR = Path(__file__).resolve().parent
    credentials_path = BASE_DIR / "credentials.json"
    with open(credentials_path , "r", encoding="utf-8") as f:
        creds = json.load(f)
    await db.init(creds)
    await db.add_spreadsheet("黑曜國際")