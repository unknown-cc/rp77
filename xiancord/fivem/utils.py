import traceback
import requests
from xiancord.logger import terminal

class PlayerMonitor:
    def __init__(self, server_url):
        self.server_url = server_url
        self.players = {}  # {player_name: id}

    def detect_online(self, new_players:dict):
        return {name: id for name, id in new_players.items() if name not in self.players}

    def detect_offline(self, new_players:dict):
        return {name: id for name, id in self.players.items() if name not in new_players}

    def update_players(self, new_players:dict):
        self.players = new_players

    def fetch_players_sync(self)->dict:
        try:
            response = requests.get(self.server_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {p.get("name", None) : p.get("id" , None) for p in data}
        except Exception as e:
            traceback.print_exc()
            return {}

    def check_players(self):
        new_players = self.fetch_players_sync()
        online = self.detect_online(new_players)
        offline = self.detect_offline(new_players)
        self.update_players(new_players)
        return online, offline
