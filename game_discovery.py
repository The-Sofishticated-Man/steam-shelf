from pathlib import Path
from typing import List, NamedTuple
from steam_db_utils import SteamDatabase
from game_validator import GameValidator
from shortcut_utils import generate_shortcut_appid

class GameCandidate(NamedTuple):
    steam_id: int  # Steam app ID for downloading images (always present - required for discovery)
    shortcut_id: int  # Generated shortcut app ID for file naming
    name: str
    exe_path: Path
    start_dir: Path

class GameDiscoveryService:
    def __init__(self, steam_db: SteamDatabase, validator: GameValidator):
        self.steam_db = steam_db
        self.validator = validator
    
    def discover_games_from_directory(self, path: Path) -> List[GameCandidate]:
        # TODO: handle game names with colons (:)
        """Discover games from a directory structure."""
        candidates = []
        
        for directory in path.iterdir():
            try:
                candidate = self._process_directory(directory)
                if candidate:
                    candidates.append(candidate)
            except Exception as e:
                print(f"Failed to process directory {directory.name}: {e}")
                continue
                
        return candidates
    
    def _process_directory(self, directory: Path) -> GameCandidate:
        """Process a single directory for game discovery."""
        name = directory.name
        
        # Validate directory
        if not self.validator.is_valid_directory(directory):
            return None
        
        # Check if it's a known Steam game - REQUIRED
        steam_id = self.steam_db.get_steam_id_from_name(name)
        if not steam_id:
            return None

        # Find executables
        exe_files = list(directory.rglob("*.exe"))
        valid_exes = self.validator.filter_executables(exe_files)

        if not valid_exes:
            print(f"No valid executables found in {name}")
            return None
        
        # Find main executable
        main_exe = self.validator.find_main_executable(valid_exes, name)
        print(f"Likely main exe for {name}: {main_exe}")
        
        # Generate shortcut app ID using the game name and executable
        shortcut_id = generate_shortcut_appid(name, str(main_exe))
        
        return GameCandidate(
            steam_id=steam_id,
            shortcut_id=shortcut_id,
            name=name,
            exe_path=main_exe.resolve(),
            start_dir=main_exe.parent
        )
