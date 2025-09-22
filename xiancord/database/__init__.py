from .manager import SpreadsheetManager
from pathlib import Path
from ..logger import terminal
import json
import asyncio
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 這是 __init__.py 所在資料夾
credentials_path = os.path.join(BASE_DIR, "./credentials.json")

db = SpreadsheetManager()

async def db_init():
    with open(credentials_path , "r", encoding="utf-8") as f:
        creds = json.load(f)
    await db.init(creds)
    await db.add_spreadsheet("遊戲資料庫")