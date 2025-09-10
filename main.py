import subprocess
import sys
from pathlib import Path
from NonSteamGameRepository import NonSteamGameRepository
import steamclient


if len(sys.argv) <2:
    print("Error: enter a games path")
    exit()

# forcefully kill Steam
subprocess.run(["taskkill", "/IM", "Steam.exe", "/F"])

games_path = Path(sys.argv[1])

# grab users
users: list[steamclient.User] = steamclient.get_users()
main_user = users[0]

SHORTCUTS_VDF_PATH = Path(f"{steamclient.STEAM_PATH}\\userdata\\{main_user.id}\\config\\shortcuts.vdf")
SHORTCUTS_VDF_SAVING_DIR = Path(Path("H:/CodingNShit/steam/shortcuts.vdf"))

game_repo = NonSteamGameRepository(user_id=main_user.id)

if SHORTCUTS_VDF_PATH.exists():
    game_repo.load_games_from_vdf(SHORTCUTS_VDF_PATH)
else:
    print("No shortcuts.vdf file found, defaulting to empty repo")

game_repo.load_games_from_directory(games_path)

for game in game_repo:
    print(game)

while True:
    ans = input("Are you sure you want to install these games (Y/n) ").lower()
    if ans in ("y", "ye", "yes", ""):
        break
    elif ans in ("n", "no"):
        exit()


# save new shortcuts file
game_repo.save_games_as_vdf()
game_repo.save_game_images()