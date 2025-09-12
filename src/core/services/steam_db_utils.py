import requests
import sqlite3

STEAM_APP_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

class SteamDatabase:
    def __init__(self, db_path="steam.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY, name TEXT)"
        )

    def sync(self):
        print("Fetching game data from steam...")
        apps = requests.get(STEAM_APP_URL).json()["applist"]["apps"]
        print("Json data fetched successfully")

        print("Loading games into local database...")
        self.conn.executemany(
            "INSERT OR IGNORE INTO games (id, name) VALUES (?, ?)",
            [(app["appid"], app["name"]) for app in apps],
        )
        self.conn.commit()
        print("Games loaded successfully into db")

    def get_steam_id_from_name(self, name: str) -> bool:
        cur = self.conn.execute("SELECT id FROM games WHERE name = ?", (name,))
        row = cur.fetchone()
        return row[0] if row else None 
    

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = SteamDatabase()
    db.sync()
    print(db.get_steam_id_from_name("Undertale"))  # True if Undertale exists
    db.close()