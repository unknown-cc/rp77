from google.auth import credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import gspread_asyncio
from gspread_asyncio import AsyncioGspreadClientManager
from typing import Dict
from ..logger import terminal
class SpreadsheetManager:
    def __init__(self):
        self._clients: Dict[str, gspread_asyncio.AsyncioGspreadSpreadsheet] = {}
        self._agcm = None

    async def init(self, credentials: dict):
        creds = service_account.Credentials.from_service_account_info(
            credentials, scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ])
        def get_creds():
            return creds
        self._agcm = AsyncioGspreadClientManager(get_creds)

    async def add_spreadsheet(self, name: str):
        if not self._agcm:
            raise RuntimeError("SpreadsheetManager 尚未初始化，請先呼叫 init()")
        agc = await self._agcm.authorize()
        ss = await agc.open(name)
        self._clients[name] = ss
        terminal(f"spreadsheet : {name} 已載入" , "資料庫")

    def get(self, name: str):
        if name not in self._clients:
            raise ValueError(f"Spreadsheet '{name}' 尚未加入，請先呼叫 add_spreadsheet")
        terminal(f"讀取了 spreadsheet : {name}" , "資料庫")        
        return SpreadsheetWrapper(self._clients[name])


class SpreadsheetWrapper:
    def __init__(self, spreadsheet : gspread_asyncio.gspread.Spreadsheet):
        self._spreadsheet = spreadsheet

    async def get_sheet(self, sheet_name: str) -> gspread_asyncio.gspread.Worksheet:
        worksheet = await self._spreadsheet.worksheet(sheet_name)
        terminal(f"讀取了 worksheet : {sheet_name}" , "資料庫")
        return worksheet