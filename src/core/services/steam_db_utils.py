import requests
import sqlite3
import threading
import re
from contextlib import contextmanager
STEAM_APP_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

ILLEGAL_CHARS = r'[<>:"/\\|?*]'
def safe_name(name: str) -> str:
    return re.sub(ILLEGAL_CHARS, '', name).strip()

class SteamDatabase:
    def __init__(self, db_path="steam.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        
        # Initialize the database schema
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY, name TEXT, safe_name TEXT UNIQUE)"
            )
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def sync(self, progress_callback=None):
        """Synchronize local database with Steam's game list.
        
        Args:
            progress_callback: Optional callback function that takes (progress_percent, status_message)
        """
        if progress_callback:
            progress_callback(10, "Fetching game data from Steam...")
        else:
            print("Fetching game data from steam...")
            
        apps = requests.get(STEAM_APP_URL).json()["applist"]["apps"]
        
        if progress_callback:
            progress_callback(50, "Game data fetched successfully")
        else:
            print("Json data fetched successfully")

        if progress_callback:
            progress_callback(60, "Loading games into local database...")
        else:
            print("Loading games into local database...")
        
        with self._get_connection() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO games (id, name, safe_name) VALUES (?, ?, ?)",
                [(app["appid"], app["name"], safe_name(app["name"])) for app in apps],
            )
            conn.commit()
            
        if progress_callback:
            progress_callback(100, "Games loaded successfully into database")
        else:
            print("Games loaded successfully into db")
    
    def get_steam_id_from_name(self, name: str) -> int:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT id FROM games WHERE safe_name = ?", (safe_name(name),))
            row = cur.fetchone()
            return row[0] if row else None 
    
    def close(self):
        """Close method for compatibility - connections are auto-closed by context manager."""
        pass


if __name__ == "__main__":
    db = SteamDatabase()
    db.sync()
    db.close()