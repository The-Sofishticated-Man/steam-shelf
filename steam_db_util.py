import requests
import sqlite3

STEAM_APP_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

def sync_database():
    conn = sqlite3.connect("steam.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY,name TEXT)"
    )
    print("Fetching game data from steam...")
    apps = requests.get(STEAM_APP_URL).json()["applist"]["apps"]
    print("Json data fetched successfully")
    print("Loading games into local database...")
    for app in apps:
        id = app["appid"]
        name = app["name"]
        conn.execute("INSERT INTO games (id, name) VALUES (?,?)",(id,name))
    print("Games loaded successfully into db")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    sync_database()